"""
rag_retrieval_service.py

Production RAG retrieval service for SIH26190.
Wraps the existing RetrievalAPI (BGE-M3 + Qdrant) and provides:
  - Hybrid retrieval (semantic + exact)
  - Entity-aware expansion (Phase 9C)
  - Temporal/spatial filtering (Phase 9D)
  - Deterministic reranking (Phase 9E)
  - Fallback to corpus keyword search if Qdrant is unavailable

IMPORTANT: This module must import rag_path_setup BEFORE importing from rag.*
"""

import os
import sys
import time
import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path setup — must happen before any rag.* imports
# ---------------------------------------------------------------------------
from app.rag_path_setup import setup_rag_path
_engine_path = setup_rag_path()

# ---------------------------------------------------------------------------
# Resolve Qdrant path (relative to investigation_dataset_engine/output)
# ---------------------------------------------------------------------------
def _resolve_qdrant_path() -> str:
    env_path = os.environ.get("QDRANT_PATH", "")
    if env_path:
        return env_path
    # Default: investigation_dataset_engine/output/qdrant_storage
    return os.path.join(_engine_path, "output", "qdrant_storage")

def _resolve_corpus_path() -> str:
    mode = os.environ.get("CORPUS_MODE", "small").lower()
    env_path = os.environ.get("CORPUS_PATH", "")
    if env_path:
        return env_path
    filename = "corpus_small.jsonl" if mode == "small" else "corpus_full.jsonl"
    return os.path.join(_engine_path, "output", "RAG_CORPUS", filename)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "10"))
RAG_USE_QDRANT = os.environ.get("RAG_USE_QDRANT", "true").lower() == "true"
RAG_COLLECTION = os.environ.get("QDRANT_COLLECTION", "sih26189_evidence")
DEBUG_RAG = os.environ.get("DEBUG_RAG", "false").lower() == "true"

# Hybrid scoring weights
SEMANTIC_WEIGHT = float(os.environ.get("SEMANTIC_WEIGHT", "0.6"))
ENTITY_WEIGHT = float(os.environ.get("ENTITY_WEIGHT", "0.3"))
LEXICAL_WEIGHT = float(os.environ.get("LEXICAL_WEIGHT", "0.1"))


class RAGRetrievalService:
    """
    Production RAG retrieval service.
    
    Lazy-initializes BGE-M3 + Qdrant on first use.
    Falls back to corpus keyword search if Qdrant is unavailable.
    """

    _instance = None
    _retrieval_api = None
    _initialized: bool = False
    _init_error: Optional[str] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _initialize(self) -> bool:
        """
        Lazily initialize RetrievalAPI.
        Returns True if Qdrant/BGE-M3 is available, False if using fallback.
        """
        if self._initialized:
            return self._retrieval_api is not None

        self._initialized = True

        if not RAG_USE_QDRANT:
            logger.info("RAG_USE_QDRANT=false — using corpus keyword fallback only")
            return False

        try:
            # Import here after path setup
            from rag.vectorstore.retrieval import RetrievalAPI
            from rag.vectorstore.config import VectorStoreConfig

            qdrant_path = _resolve_qdrant_path()

            if not os.path.isdir(qdrant_path):
                logger.warning("Qdrant storage not found at %s — using fallback", qdrant_path)
                self._init_error = f"Qdrant storage not found at {qdrant_path}"
                return False

            config = VectorStoreConfig()
            # Override collection to point at the main evidence collection
            config.qdrant_collection = RAG_COLLECTION
            # Override path
            config.qdrant_path = qdrant_path

            logger.info(
                "Initializing RetrievalAPI with model=%s, collection=%s, path=%s",
                config.embedding_model, config.qdrant_collection, config.qdrant_path
            )

            # This triggers BGE-M3 model load (may take 30-60s first time)
            t0 = time.time()
            self._retrieval_api = RetrievalAPI(config=config)
            elapsed = time.time() - t0

            # Verify collection exists and has documents
            count = self._retrieval_api.qdrant_client.count()
            logger.info(
                "RetrievalAPI ready in %.1fs. Qdrant collection '%s' has %d documents.",
                elapsed, RAG_COLLECTION, count
            )

            if count == 0:
                logger.warning(
                    "Qdrant collection is empty. Falling back to corpus keyword search. "
                    "Run the indexing pipeline to populate the vector store."
                )
                self._retrieval_api = None
                self._init_error = "Qdrant collection is empty"
                return False

            return True

        except ImportError as e:
            logger.error("Failed to import rag.* modules: %s", e)
            self._init_error = f"Import error: {e}"
            return False
        except Exception as e:
            logger.error("Failed to initialize RetrievalAPI: %s", e)
            self._init_error = str(e)
            return False

    def _load_corpus_for_fallback(self) -> List[Dict[str, Any]]:
        """Load corpus records for keyword fallback retrieval."""
        try:
            from app.services.corpus_service import corpus_service
            return corpus_service.get_all_records()
        except Exception as e:
            logger.error("Failed to load corpus for fallback: %s", e)
            return []

    def _keyword_fallback(
        self,
        query: str,
        scenario_id: Optional[str],
        top_k: int,
        authorized_case_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Keyword-based retrieval fallback when Qdrant is unavailable.
        Uses the existing corpus_service scorer.
        """
        try:
            from app.services.retrieval_service import retrieval_service
            results = retrieval_service.retrieve(
                query=query, 
                top_k=top_k, 
                scenario_id=scenario_id,
                authorized_case_ids=authorized_case_ids
            )
            
            # Normalize to evidence pack format
            normalized = []
            for r in results:
                normalized.append({
                    'record_id': r.get('source_record_id', ''),
                    'document_id': r.get('document_id', ''),
                    'source_type': r.get('source_type', ''),
                    'timestamp': r.get('timestamp', ''),
                    'entity_refs': r.get('entity_refs', []),
                    'location_refs': r.get('location_refs', []),
                    'normalized_text': r.get('normalized_text', ''),
                    'semantic_score': 0.0,
                    'entity_match_score': 0.0,
                    'lexical_score': float(r.get('relevance_score', 0.0)),
                    'combined_score': float(r.get('relevance_score', 0.0)),
                    'retrieval_reasons': r.get('matched_terms', []),
                    'retrieval_mode': 'keyword_fallback',
                    'expansion_depth': 0,
                })
            return normalized
        except Exception as e:
            logger.error("Keyword fallback failed: %s", e)
            return []

    def retrieve(
        self,
        query: str,
        query_understanding=None,
        scenario_id: Optional[str] = None,
        top_k: int = None,
        use_entity_expansion: bool = True,
        use_rerank: bool = True,
        authorized_case_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Main retrieval method.
        
        Returns a structured result dict with:
          - evidence: List of evidence pack items
          - mode: retrieval mode used
          - timing: per-stage timing in ms
          - semantic_candidates: count
          - exact_candidates: count
          - final_count: count after ranking
          - qdrant_available: bool
          - error: optional error message
        """
        top_k = top_k or RAG_TOP_K
        timing = {}
        t_total_start = time.time()

        # Try to initialize Qdrant
        t_init = time.time()
        qdrant_available = self._initialize()
        timing['init_ms'] = round((time.time() - t_init) * 1000, 1)

        if not qdrant_available:
            # Fallback path
            logger.info("Using keyword fallback for query: %s", query[:60])
            t_fallback = time.time()
            evidence = self._keyword_fallback(query, scenario_id, top_k, authorized_case_ids)
            timing['retrieval_ms'] = round((time.time() - t_fallback) * 1000, 1)
            timing['total_ms'] = round((time.time() - t_total_start) * 1000, 1)
            return {
                'evidence': evidence,
                'mode': 'keyword_fallback',
                'semantic_candidates': 0,
                'exact_candidates': 0,
                'final_count': len(evidence),
                'qdrant_available': False,
                'error': self._init_error,
                'timing': timing,
            }

        # Full RAG pipeline
        try:
            from rag.investigation.context import InvestigationContext
            
            # Build investigation context from query understanding
            ctx = self._build_investigation_context(query, query_understanding, scenario_id, authorized_case_ids)

            # Determine retrieval mode
            has_exact_ids = bool(
                query_understanding and query_understanding.all_entity_refs
            )
            retrieval_mode = "hybrid" if has_exact_ids else "semantic"

            if DEBUG_RAG:
                logger.info(
                    "[DEBUG] mode=%s, entity_refs=%s, time_start=%s, time_end=%s",
                    retrieval_mode,
                    query_understanding.all_entity_refs if query_understanding else [],
                    ctx.time_start,
                    ctx.time_end
                )

            # Execute retrieval
            t_retrieval = time.time()
            raw_results = self._retrieval_api.search(
                query=query,
                top_k=top_k,
                investigation_context=ctx,
                retrieval_mode=retrieval_mode,
                entity_expansion=use_entity_expansion,
                rerank=use_rerank,
            )
            timing['retrieval_ms'] = round((time.time() - t_retrieval) * 1000, 1)

            # Filter out useless zero-score matches (e.g. from MockEncoder)
            raw_results = [r for r in raw_results if r.get('score', 0) > 0.0]

            # Count semantic vs exact
            semantic_count = sum(
                1 for r in raw_results
                if 'semantic' in r.get('retrieval_signals', [])
            )
            exact_count = sum(
                1 for r in raw_results
                if r.get('exact_match', False)
            )

            if DEBUG_RAG:
                logger.info(
                    "[DEBUG] raw_results=%d, semantic=%d, exact=%d",
                    len(raw_results), semantic_count, exact_count
                )

            # Enrich with corpus text (Qdrant payload excludes normalized_text)
            t_enrich = time.time()
            evidence = self._enrich_with_corpus_text(raw_results, scenario_id)
            timing['enrich_ms'] = round((time.time() - t_enrich) * 1000, 1)

            # Auto-fallback for prototype MockEncoder limitation
            if len(evidence) == 0:
                logger.info("Semantic/Exact retrieval returned 0 results. Triggering keyword fallback.")
                t_fallback = time.time()
                evidence = self._keyword_fallback(query, scenario_id, top_k, authorized_case_ids)
                retrieval_mode = "keyword_fallback"
                timing['fallback_ms'] = round((time.time() - t_fallback) * 1000, 1)

            timing['total_ms'] = round((time.time() - t_total_start) * 1000, 1)

            return {
                'evidence': evidence,
                'mode': retrieval_mode,
                'semantic_candidates': semantic_count,
                'exact_candidates': exact_count,
                'final_count': len(evidence),
                'qdrant_available': True,
                'error': None,
                'timing': timing,
            }

        except Exception as e:
            logger.error("RAG retrieval failed: %s", e, exc_info=True)
            # Graceful fallback
            evidence = self._keyword_fallback(query, scenario_id, top_k, authorized_case_ids)
            timing['total_ms'] = round((time.time() - t_total_start) * 1000, 1)
            return {
                'evidence': evidence,
                'mode': 'keyword_fallback_on_error',
                'semantic_candidates': 0,
                'exact_candidates': 0,
                'final_count': len(evidence),
                'qdrant_available': True,  # Qdrant connected but retrieval failed
                'error': str(e),
                'timing': timing,
            }

    def _build_investigation_context(
        self,
        query: str,
        query_understanding,
        scenario_id: Optional[str],
        authorized_case_ids: Optional[List[str]] = None
    ):
        """Build InvestigationContext from query understanding."""
        from rag.investigation.context import InvestigationContext

        ctx_kwargs = {
            'investigation_id': f"runtime_{int(time.time())}",
            'investigator_query': query,
        }

        # Scenario isolation: always a hard MUST condition, never relaxed.
        # scenario_id is the dataset scope, separate from investigative case references.
        if scenario_id:
            ctx_kwargs['scenario_ids'] = [scenario_id]

        if query_understanding:
            qu = query_understanding

            # Entity refs
            if qu.person_ids:
                ctx_kwargs['person_ids'] = qu.person_ids
            if qu.phone_ids:
                ctx_kwargs['phone_ids'] = qu.phone_ids
            if qu.vehicle_ids:
                ctx_kwargs['vehicle_ids'] = qu.vehicle_ids
            if qu.account_ids:
                ctx_kwargs['account_ids'] = qu.account_ids
            existing_case_ids = ctx_kwargs.get('case_ids', [])
            if qu.fir_ids:
                ctx_kwargs['case_ids'] = existing_case_ids + qu.fir_ids + qu.case_ids
            else:
                ctx_kwargs['case_ids'] = existing_case_ids + qu.case_ids

            if qu.all_entity_refs:
                ctx_kwargs['known_entity_refs'] = qu.all_entity_refs

            # Temporal
            if qu.time_start:
                ctx_kwargs['time_start'] = qu.time_start
            if qu.time_end:
                ctx_kwargs['time_end'] = qu.time_end

            # Spatial
            if qu.location_refs:
                ctx_kwargs['location_ids'] = qu.location_refs

        if authorized_case_ids:
            ctx_kwargs['authorized_case_ids'] = authorized_case_ids

        return InvestigationContext(**ctx_kwargs)


    def _enrich_with_corpus_text(
        self,
        raw_results: List[Dict[str, Any]],
        scenario_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Qdrant payloads exclude normalized_text to save space.
        We re-join with the corpus to get text content for the LLM evidence pack.
        """
        # Build a lookup from source_record_id -> corpus record
        corpus_lookup = {}
        try:
            from app.services.corpus_service import corpus_service
            for rec in corpus_service.get_all_records():
                rid = rec.get('source_record_id', '')
                if rid:
                    corpus_lookup[rid] = rec
        except Exception as e:
            logger.warning("Could not load corpus for text enrichment: %s", e)

        evidence = []
        for raw in raw_results:
            payload = raw.get('payload', {})
            source_record_id = payload.get('source_record_id', '')
            
            # Lookup corpus record for text
            corpus_rec = corpus_lookup.get(source_record_id, {})
            normalized_text = corpus_rec.get('normalized_text', '')
            raw_content = corpus_rec.get('raw_content', {})

            # Build score breakdown
            semantic_score = float(raw.get('score', 0.0))
            exact_match = raw.get('exact_match', False)
            expansion_depth = raw.get('expansion_depth', 0)
            rerank_score = raw.get('rerank_score', semantic_score)
            retrieval_signals = raw.get('retrieval_signals', [])

            # Annotate retrieval reasons
            reasons = []
            if 'exact_identifier' in retrieval_signals:
                reasons.append('exact_entity_match')
            if 'semantic' in retrieval_signals:
                reasons.append('semantic_similarity')
            if 'entity_expansion' in retrieval_signals:
                reasons.append('entity_expansion')

            evidence.append({
                'record_id': source_record_id,
                'document_id': payload.get('document_id', ''),
                'source_type': payload.get('source_type', ''),
                'timestamp': payload.get('timestamp', ''),
                'entity_refs': payload.get('entity_refs', []),
                'location_refs': payload.get('location_refs', []),
                'case_refs': payload.get('case_refs', []),
                'normalized_text': normalized_text,
                'raw_content': raw_content,
                'semantic_score': round(semantic_score, 4),
                'entity_match_score': 1.0 if exact_match else 0.0,
                'combined_score': round(rerank_score, 4),
                'retrieval_reasons': reasons,
                'retrieval_mode': raw.get('retrieval_mode', 'semantic'),
                'expansion_depth': expansion_depth,
            })

        return evidence

    def get_status(self) -> Dict[str, Any]:
        """Return service health status."""
        return {
            'qdrant_available': self._retrieval_api is not None,
            'initialized': self._initialized,
            'error': self._init_error,
            'qdrant_collection': RAG_COLLECTION,
            'qdrant_path': _resolve_qdrant_path(),
            'top_k': RAG_TOP_K,
            'document_count': (
                self._retrieval_api.qdrant_client.count()
                if self._retrieval_api else 0
            ),
        }


# Singleton — lazy initialization on first use
rag_retrieval_service = RAGRetrievalService()
