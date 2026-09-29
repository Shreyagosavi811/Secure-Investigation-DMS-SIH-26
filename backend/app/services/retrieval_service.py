import re
from typing import List, Dict, Any, Optional
from app.services.corpus_service import corpus_service

class RetrievalService:
    def __init__(self):
        pass

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        # Simple lowercase alphanumeric tokenization
        tokens = re.findall(r'\b\w+\b', str(text).lower())
        return tokens

    def _calculate_score(self, query: str, record: Dict[str, Any]) -> tuple[float, List[str]]:
        score = 0.0
        matched_terms = set()
        
        # Original query lowercased for exact matches
        q_lower = query.lower().strip()
        
        # Tokens for partial matches
        q_tokens = self._tokenize(query)
        if not q_tokens and not q_lower:
            return 0.0, []

        # 1. Exact entity match (strong weight: +10.0)
        entity_refs = [str(e).lower() for e in record.get("entity_refs", [])]
        if q_lower in entity_refs:
            score += 10.0
            matched_terms.add(q_lower)
        else:
            # Token match in entities
            for token in q_tokens:
                for ent in entity_refs:
                    if token in ent:
                        score += 3.0
                        matched_terms.add(token)

        # 2. Exact source_record_id match (strong weight: +10.0)
        record_id = str(record.get("source_record_id", "")).lower()
        if q_lower == record_id:
            score += 10.0
            matched_terms.add(q_lower)
        elif any(token in record_id for token in q_tokens):
            for token in q_tokens:
                if token in record_id:
                    score += 5.0
                    matched_terms.add(token)

        # 3. Exact location match (strong weight: +8.0)
        location_refs = [str(l).lower() for l in record.get("location_refs", [])]
        if q_lower in location_refs:
            score += 8.0
            matched_terms.add(q_lower)
        else:
            for token in q_tokens:
                for loc in location_refs:
                    if token in loc:
                        score += 2.0
                        matched_terms.add(token)

        # 4. Source_type match (moderate weight: +5.0)
        source_type = str(record.get("source_type", "")).lower()
        # source_type usually has underscores, replace with spaces for token matching
        source_type_clean = source_type.replace("_", " ")
        if q_lower in source_type_clean:
            score += 5.0
            matched_terms.add(source_type)
        else:
            for token in q_tokens:
                if token in source_type:
                    score += 2.0
                    matched_terms.add(token)

        # 5. Normalized text keyword match (moderate weight: +1.0 per term)
        norm_text = str(record.get("normalized_text", "")).lower()
        if q_lower in norm_text:
            score += 5.0
            matched_terms.add(q_lower)
        
        for token in q_tokens:
            if token in norm_text:
                score += 1.0
                matched_terms.add(token)

        # 6. Raw content keyword match (lower weight: +0.5 per term)
        raw_content = str(record.get("raw_content", {})).lower()
        for token in q_tokens:
            if token in raw_content:
                score += 0.5
                matched_terms.add(token)
                
        return score, list(matched_terms)

    def retrieve(
        self, 
        query: str, 
        top_k: int = 5, 
        scenario_id: Optional[str] = None,
        authorized_case_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        # Retrieve all records from the pre-loaded corpus
        records = corpus_service.get_all_records()

        if scenario_id:
            records = [r for r in records if r.get("scenario_instance_id") == scenario_id]

        if authorized_case_ids is not None:
            records = [r for r in records if any(c in authorized_case_ids for c in r.get("case_refs", []))]

        scored_results = []
        for record in records:
            # Ensure ground truth isolation at the retrieval level
            if "GROUND_TRUTH" in str(record.get("provenance", {}).get("source_path", "")):
                continue

            score, matched_terms = self._calculate_score(query, record)
            
            if score > 0:
                scored_results.append({
                    "document_id": record.get("document_id", ""),
                    "source_record_id": record.get("source_record_id", ""),
                    "source_type": record.get("source_type", ""),
                    "timestamp": record.get("timestamp", ""),
                    "normalized_text": record.get("normalized_text", ""),
                    "entity_refs": record.get("entity_refs", []),
                    "location_refs": record.get("location_refs", []),
                    "case_refs": record.get("case_refs", []),
                    "relevance_score": score,
                    "matched_terms": matched_terms
                })

        # Deterministic ranking: Sort by score (desc), then by document_id (asc) for tie-breaking
        scored_results.sort(key=lambda x: (-x["relevance_score"], x["document_id"]))

        return scored_results[:top_k]

retrieval_service = RetrievalService()
