from typing import List, Dict, Any, Optional
import random

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from .config import VectorStoreConfig
from .qdrant_client import QdrantEvidenceClient
from rag.investigation.context import InvestigationContext

class MockEncoder:
    def __init__(self, dim=1024):
        self.dim = dim
    def get_sentence_embedding_dimension(self):
        return self.dim
    def encode(self, texts, convert_to_numpy=True):
        import numpy as np
        if isinstance(texts, str):
            return np.zeros(self.dim)
        return np.zeros((len(texts), self.dim))

RERANK_WEIGHTS = {
    "semantic_base": 1.0,
    "exact_match_boost": 1.0,
    "expansion_penalty": -0.15,
}

class RetrievalAPI:
    def __init__(self, config: Optional[VectorStoreConfig] = None):
        self.config = config or VectorStoreConfig()
        if SentenceTransformer is not None:
            self.model = SentenceTransformer(self.config.embedding_model, device=self.config.embedding_device)
        else:
            print("WARNING: sentence_transformers missing. Using MockEncoder for Qdrant (Disk space limitation).")
            self.model = MockEncoder()
            
        self.qdrant_client = QdrantEvidenceClient(
            path=self.config.qdrant_path,
            collection_name=self.config.qdrant_collection
        )
        
    def get_embedding_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def _extract_identifiers(self, query: str) -> tuple[List[str], str]:
        """
        Extract deterministic exact identifiers and return (extracted_ids, semantic_text).
        """
        import re
        # Support explicit prefixes (P-123, ACC-123, FIR-123) and actual dataset structures (+91-9836352800, DL05CF1567)
        pattern = re.compile(
            r'(?:^|(?<=\s))('
            r'P-\d+|PHONE-\d+|VEH-[\w-]+|ACC-\d+|FIR-[\d-]+|'
            r'(?:FIU|CAF|CBS|CDR|FIN|OSINT|CH|ANPR)-[\w-]+|'
            r'\+91-\d{10}|'
            r'[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}'
            r')(?=$|\s|[.,!?;])'
        )
        extracted = pattern.findall(query)
        # Remove matched IDs from the semantic text
        semantic_text = pattern.sub('', query).strip()
        # Clean up double spaces left by removal
        semantic_text = re.sub(r'\s+', ' ', semantic_text)
        return extracted, semantic_text

    def _normalize_identifiers(self, identifiers: List[str]) -> List[str]:
        """
        Expands exact identifiers with normalized variants (e.g. phone numbers).
        """
        import re
        expanded = list(identifiers)
        for eid in identifiers:
            # Phone number normalization
            if re.match(r'^(\+91-?|91|PHONE-)?\d{10}$', eid):
                core_num = eid[-10:]
                for variant in [core_num, f"91{core_num}", f"+91-{core_num}", f"PHONE-{core_num}"]:
                    if variant not in expanded:
                        expanded.append(variant)
        return expanded

    def _extract_entity_refs(self, results: List[Dict[str, Any]], max_entities: int = 20) -> List[str]:
        entities = []
        seen = set()
        for res in results:
            payload = res.get("payload", {})
            refs = payload.get("entity_refs", [])
            for ref in refs:
                if ref and isinstance(ref, str):
                    ref_clean = ref.strip()
                    if ref_clean and ref_clean not in seen:
                        seen.add(ref_clean)
                        entities.append(ref_clean)
                        if len(entities) >= max_entities:
                            return entities
        return entities

    def search(
        self, 
        query: str, 
        top_k: int = 10, 
        filters: Optional[Dict[str, str]] = None,
        investigation_context: Optional["InvestigationContext"] = None,
        retrieval_mode: str = "semantic",
        entity_expansion: bool = False,
        rerank: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the top_k evidence documents matching the query.
        retrieval_mode can be "semantic" (default, Phase 8D compat) or "hybrid".
        """
        if retrieval_mode not in ("semantic", "hybrid"):
            raise ValueError(f"Unsupported retrieval_mode: {retrieval_mode}")

        semantic_text = query
        exact_ids = []

        if retrieval_mode == "hybrid":
            if investigation_context and investigation_context.known_entity_refs:
                exact_ids = investigation_context.known_entity_refs
                # Remove exact IDs from the semantic query string
                for eid in exact_ids:
                    semantic_text = semantic_text.replace(eid, "").strip()
                import re
                semantic_text = re.sub(r'\s+', ' ', semantic_text)
            else:
                exact_ids, semantic_text = self._extract_identifiers(query)

        # Build Context Filters (Phase 9B supports source_type_filters and case_ids)
        must_conditions = []
        if filters:
            for k, v in filters.items():
                must_conditions.append({"key": k, "match": {"value": v}})
                
        if investigation_context:
            if investigation_context.source_type_filters:
                # Assuming Qdrant format for IN or multiple MATCH values:
                # Actually, Qdrant FieldCondition match can take Any, which corresponds to exact match.
                # Since we don't have the qdrant models object imported nicely here, we'll build it 
                # inside QdrantEvidenceClient. So we pass them as raw dictionaries or lists.
                pass # Handled below
        
        # 1. Semantic Query
        semantic_results = []
        if semantic_text or not exact_ids:
            query_vector = self.model.encode(semantic_text if semantic_text else " ", convert_to_numpy=True).tolist()
            semantic_results = self.qdrant_client.search(
                query_vector=query_vector, 
                top_k=top_k * 2 if retrieval_mode == "hybrid" else top_k, # over-fetch for fusion
                filters=filters,
                investigation_context=investigation_context
            )
            for res in semantic_results:
                res["exact_match"] = False
                res["matched_identifiers"] = []

        # 2. Exact Match Query (Hybrid Mode)
        exact_results = []
        if retrieval_mode == "hybrid" and exact_ids:
            expanded_exact_ids = self._normalize_identifiers(exact_ids)
            exact_results = self.qdrant_client.search_exact(
                identifiers=expanded_exact_ids,
                top_k=top_k * 2,
                filters=filters,
                investigation_context=investigation_context
            )
            for res in exact_results:
                res["exact_match"] = True
                res["matched_identifiers"] = exact_ids

        # 3. Candidate Fusion (Initial Depth 0)
        fused = {}
        # Merge exact results first (they have higher priority)
        for res in exact_results:
            doc_id = res["payload"]["document_id"]
            if doc_id not in fused:
                fused[doc_id] = res
                fused[doc_id]["expansion_depth"] = 0
                fused[doc_id]["retrieval_signals"] = ["exact_identifier"]

        # Merge semantic results
        for res in semantic_results:
            doc_id = res["payload"]["document_id"]
            if doc_id not in fused:
                fused[doc_id] = res
                fused[doc_id]["expansion_depth"] = 0
                fused[doc_id]["retrieval_signals"] = ["semantic"]
            else:
                fused[doc_id]["score"] = max(fused[doc_id]["score"], res["score"])
                fused[doc_id]["exact_match"] = fused[doc_id].get("exact_match") or res.get("exact_match", False)
                if "semantic" not in fused[doc_id]["retrieval_signals"]:
                    fused[doc_id]["retrieval_signals"].append("semantic")

        # 4. Phase 9C: Entity Expansion (Depth 1)
        if entity_expansion:
            # Sort current initial results to prioritize entities from best matches
            def initial_rank_key(item):
                doc_id = item["payload"]["document_id"]
                return (0 if item.get("exact_match") else 1, -item["score"], doc_id)
            
            initial_ranked = sorted(list(fused.values()), key=initial_rank_key)
            expansion_entities = self._extract_entity_refs(initial_ranked[:top_k], max_entities=20)
            
            if expansion_entities:
                expansion_results = self.qdrant_client.search_exact(
                    identifiers=expansion_entities,
                    top_k=top_k * 3,  # Budget limit for expansion
                    filters=filters,
                    investigation_context=investigation_context
                )
                
                for res in expansion_results:
                    doc_id = res["payload"]["document_id"]
                    if doc_id not in fused:
                        fused[doc_id] = res
                        fused[doc_id]["exact_match"] = False # Expanded is not direct query exact match
                        fused[doc_id]["matched_identifiers"] = []
                        fused[doc_id]["expansion_depth"] = 1
                        fused[doc_id]["retrieval_signals"] = ["entity_expansion"]
                    else:
                        if "entity_expansion" not in fused[doc_id]["retrieval_signals"]:
                            fused[doc_id]["retrieval_signals"].append("entity_expansion")

        # Fallback fields for Phase 8D/9B contract
        for doc_id, item in fused.items():
            if "expansion_depth" not in item:
                item["expansion_depth"] = 0
            if "retrieval_signals" not in item:
                item["retrieval_signals"] = []

        if retrieval_mode == "semantic" and not entity_expansion and not rerank:
            # Preserve strict semantic logic
            for res in semantic_results:
                res["retrieval_mode"] = "semantic"
                if "expansion_depth" not in res:
                    res["expansion_depth"] = 0
                if "retrieval_signals" not in res:
                    res["retrieval_signals"] = ["semantic"]
            return semantic_results[:top_k]

        # 5. Deterministic Ranking
        if rerank:
            for doc_id, item in fused.items():
                score = item["score"] * RERANK_WEIGHTS["semantic_base"]
                if item.get("exact_match"):
                    score += RERANK_WEIGHTS["exact_match_boost"]
                if item.get("expansion_depth", 0) > 0:
                    score += RERANK_WEIGHTS["expansion_penalty"]
                item["rerank_score"] = score
                
            def rank_key(item):
                doc_id = item["payload"]["document_id"]
                return (
                    -item.get("rerank_score", 0.0),
                    item["expansion_depth"],
                    0 if item.get("exact_match") else 1,
                    -item["score"],
                    doc_id
                )
        else:
            # Priority: expansion_depth ASC > exact_match True > semantic_score DESC > document_id ASC
            def rank_key(item):
                doc_id = item["payload"]["document_id"]
                return (
                    item["expansion_depth"],
                    0 if item.get("exact_match") else 1,
                    -item["score"],
                    doc_id
                )

        ranked = sorted(list(fused.values()), key=rank_key)
        
        # Add retrieval_mode to output for contract fulfillment
        for item in ranked:
            item["retrieval_mode"] = retrieval_mode
            item["entity_refs"] = item["payload"].get("entity_refs", [])
            
        return ranked[:top_k]
