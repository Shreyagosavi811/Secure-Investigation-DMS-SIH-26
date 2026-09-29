"""
main.py

SIH26190 FastAPI backend.

Phase 11: Full RAG pipeline wired to /api/ai/query:
  Query Understanding → BGE-M3 Semantic → Qdrant Exact → Entity Expansion →
  Temporal/Spatial Filter → Reranking → Evidence Pack → Grok LLM →
  Anti-hallucination Validation → Structured Response
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Must import path setup before any rag.* imports happen downstream
from app.rag_path_setup import setup_rag_path
setup_rag_path()

from app.schemas import (
    AIQueryRequest,
    AIQueryResponse,
    EvidencePackItem,
    NetworkLink,
    RetrievalInfo,
    TimingInfo,
)
from app.services.corpus_service import corpus_service
from app.services.network_service import build_network
from app.services.query_understanding import query_understanding_service
from app.services.rag_retrieval_service import rag_retrieval_service
from app.services.llm_service import llm_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

from app.routers import auth, cases, documents, audit, analytics

app = FastAPI(
    title="SIH26190 Secure Document Management API",
    description="Secure Digital Document Management System for Legal and Investigation Documents",
    version="1.0.0"
)

# Configure CORS for Vite dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(documents.router)
app.include_router(audit.router)
app.include_router(analytics.router)


# ---------------------------------------------------------------------------
# Health & Info
# ---------------------------------------------------------------------------

@app.get("/api/health")
def get_health():
    """Backend health check."""
    corpus_info = corpus_service.get_corpus_info()
    rag_status = rag_retrieval_service.get_status()
    
    return {
        "status": "ok",
        "service": "SIH26190 Secure Document Management API",
        "version": "1.0.0",
        "corpus": corpus_info['corpus_path'],
        "corpus_mode": corpus_info['corpus_mode'],
        "records": corpus_info['records'],
        "rag": {
            "qdrant_available": rag_status['qdrant_available'],
            "document_count": rag_status['document_count'],
            "collection": rag_status['qdrant_collection'],
        }
    }


@app.get("/api/scenarios")
def get_scenarios():
    """List available investigation scenarios."""
    scenarios = corpus_service.get_scenarios()
    return [
        {"scenario_id": sid, "record_count": count}
        for sid, count in scenarios.items()
    ]


@app.get("/api/records")
def get_records(
    scenario_id: Optional[str] = None,
    source_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get corpus records with optional filters."""
    if limit > 200:
        limit = 200

    records = corpus_service.get_records(
        scenario_id=scenario_id,
        source_type=source_type,
        entity_id=entity_id,
        limit=limit,
        offset=offset
    )
    return {"total": len(records), "records": records}


@app.get("/api/entities/{entity_id}/records")
def get_entity_records(entity_id: str):
    """Get all records mentioning a specific entity."""
    records = corpus_service.get_records(entity_id=entity_id, limit=200)
    return {"entity_id": entity_id, "total": len(records), "records": records}


@app.get("/api/network/{scenario_id}")
def get_network(scenario_id: str):
    """Get entity relationship network for a scenario."""
    scenarios = corpus_service.get_scenarios()
    if scenario_id not in scenarios:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return build_network(scenario_id)


# ---------------------------------------------------------------------------
# AI Query — Full RAG Pipeline
# ---------------------------------------------------------------------------

from app.auth import get_current_user, get_authorized_cases
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from app.models import User

@app.post("/api/ai/query")
def ai_query(
    req: AIQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Full investigative RAG pipeline with RBAC:
    """
    t_total = time.time()
    timing = {}

    # ----- Step 0: Conversational Intercept -----
    conversational_greetings = ["hi", "hello", "hey", "help", "who are you", "what can you do"]
    if req.query.strip().lower() in conversational_greetings:
        return {
            "status": "success",
            "message": "Namaste! I am the OmniGuard Evidence Assistant.",
            "query": req.query,
            "results": [],
            "llm_response": {
                "answer": "Namaste! I am the OmniGuard Evidence Assistant, securely bound to your authorized case files. Please provide an investigative query, such as 'Summarize the documents', 'Check for conflicts', or 'Verify integrity'.",
                "citations": [],
                "evidence_basis": None,
                "confidence": "none",
                "mode": "conversational"
            }
        }

    authorized_case_ids = get_authorized_cases(current_user, db)

    # ----- Step 1: Query Understanding -----
    t_qu = time.time()
    qu = query_understanding_service.parse(req.query)
    timing['query_understanding_ms'] = round((time.time() - t_qu) * 1000, 1)

    logger.info(
        "Query understanding: query='%s' entities=%s intent=%s",
        req.query[:80],
        qu.all_entity_refs,
        qu.primary_intent
    )

    # ----- Step 2-5: RAG Retrieval -----
    top_k = req.top_k or int(os.environ.get("RAG_TOP_K", "10"))

    retrieval_result = rag_retrieval_service.retrieve(
        query=req.query,
        query_understanding=qu,
        scenario_id=req.scenario_id,
        top_k=top_k,
        use_entity_expansion=req.use_entity_expansion,
        use_rerank=req.use_rerank,
        authorized_case_ids=authorized_case_ids,
    )
    timing.update(retrieval_result.get('timing', {}))

    evidence_pack = retrieval_result.get('evidence', [])

    logger.info(
        "Retrieval complete: mode=%s, evidence=%d, semantic=%d, exact=%d",
        retrieval_result['mode'],
        len(evidence_pack),
        retrieval_result['semantic_candidates'],
        retrieval_result['exact_candidates'],
    )

    # ----- Step 6: Evidence Confidence Scoring -----
    evidence_strength = 0.0
    if evidence_pack:
        try:
            from app.rag_path_setup import setup_rag_path
            setup_rag_path()
            from confidence.model import EvidenceConfidenceCalculator
            source_types = [e.get('source_type', '') for e in evidence_pack if e.get('source_type')]
            evidence_strength = EvidenceConfidenceCalculator.calculate_confidence(
                evidence_sources=source_types
            )
        except Exception as e:
            logger.warning("Could not compute evidence confidence: %s", e)
            # Fallback: simple count-based score
            evidence_strength = min(1.0, len(evidence_pack) / top_k)

    # ----- Step 7-8: Grok LLM + Validation -----
    t_llm = time.time()
    llm_result = llm_service.generate_grounded_response(
        query=req.query,
        evidence=evidence_pack,
    )
    timing['llm_ms'] = round((time.time() - t_llm) * 1000, 1)

    # ----- Build Response -----
    timing['total_ms'] = round((time.time() - t_total) * 1000, 1)

    # Serialize evidence pack (convert to schema-compatible format)
    evidence_items = []
    for e in evidence_pack:
        try:
            evidence_items.append(EvidencePackItem(
                record_id=e.get('record_id', ''),
                document_id=e.get('document_id', ''),
                source_type=e.get('source_type', ''),
                timestamp=e.get('timestamp'),
                entity_refs=e.get('entity_refs', []),
                location_refs=e.get('location_refs', []),
                case_refs=e.get('case_refs', []),
                normalized_text=e.get('normalized_text', ''),
                semantic_score=e.get('semantic_score', 0.0),
                entity_match_score=e.get('entity_match_score', 0.0),
                combined_score=e.get('combined_score', 0.0),
                retrieval_reasons=e.get('retrieval_reasons', []),
                retrieval_mode=e.get('retrieval_mode', 'hybrid'),
                expansion_depth=e.get('expansion_depth', 0),
            ))
        except Exception as ex:
            logger.warning("Could not serialize evidence item: %s", ex)

    # Network links from LLM output
    network_links = [
        NetworkLink(
            source=link['source'],
            target=link['target'],
            relationship=link.get('relationship', 'UNKNOWN'),
            confidence=link.get('confidence', 0.0),
            source_record_ids=link.get('source_record_ids', []),
        )
        for link in llm_result.get('network_links', [])
    ]

    # Entities extracted from query
    entities = []
    if qu.all_entity_refs:
        for ref in qu.all_entity_refs:
            etype = _classify_entity_type(ref)
            entities.append({'id': ref, 'type': etype})

    # Timing
    timing_info = TimingInfo(
        embedding_ms=timing.get('retrieval_ms', 0.0),  # embedding is part of retrieval
        retrieval_ms=timing.get('retrieval_ms', 0.0),
        reranking_ms=0.0,  # included in retrieval
        llm_ms=timing.get('llm_ms', 0.0),
        total_ms=timing.get('total_ms', 0.0),
    )

    # Backward-compatible response format (keeps existing tests passing)
    # while also returning rich new fields
    structured = llm_result.get('structured', {})
    
    return {
        # Backward compat fields (keep existing frontend working)
        "status": "success",
        "message": llm_result.get('answer', 'No answer generated.'),
        "query": req.query,
        "results": [e.model_dump() for e in evidence_items],
        "llm_response": {
            "answer": llm_result.get('answer', ''),
            "citations": llm_result.get('citations', []),
            "evidence_basis": llm_result.get('evidence_basis', {}),
            "confidence": llm_result.get('confidence', 'insufficient'),
            "mode": llm_result.get('mode', 'retrieval_fallback'),
        },
        # New rich fields
        "answer": structured,
        "retrieval": {
            "mode": retrieval_result['mode'],
            "semantic_candidates": retrieval_result['semantic_candidates'],
            "exact_candidates": retrieval_result['exact_candidates'],
            "final_evidence_count": len(evidence_pack),
            "qdrant_available": retrieval_result['qdrant_available'],
        },
        "evidence": [e.model_dump() for e in evidence_items],
        "entities": entities,
        "network_links": [link.model_dump() for link in network_links],
        "evidence_strength": evidence_strength,
        "timing": {
            "embedding_ms": timing_info.embedding_ms,
            "retrieval_ms": timing_info.retrieval_ms,
            "reranking_ms": timing_info.reranking_ms,
            "llm_ms": timing_info.llm_ms,
            "total_ms": timing_info.total_ms,
        },
        # Debug info (only if requested)
        **({"debug": {
            "query_understanding": qu.to_dict(),
            "retrieval_error": retrieval_result.get('error'),
        }} if req.debug else {}),
    }


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _classify_entity_type(entity_id: str) -> str:
    """Classify an entity ID string into a type."""
    if entity_id.startswith('P-'):
        return 'person'
    if entity_id.startswith('+91-') or entity_id.startswith('PHONE-'):
        return 'phone'
    if entity_id.startswith('VEH-') or (len(entity_id) == 10 and entity_id[:2].isalpha()):
        return 'vehicle'
    if entity_id.startswith('ACC-') or entity_id.isdigit():
        return 'account'
    if entity_id.startswith('FIR-'):
        return 'fir'
    if entity_id.startswith('TOWER-'):
        return 'location'
    if entity_id.startswith('BR-'):
        return 'location'
    if any(entity_id.startswith(p) for p in ['CBS-', 'CDR-', 'FIU-', 'FNOTE-', 'CRIM-', 'TDUMP-', 'ANPR-']):
        return 'record'
    return 'entity'
