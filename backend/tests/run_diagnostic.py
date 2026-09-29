import os
import sys
import json
import re
from typing import List, Dict, Any

sys.path.insert(0, '.')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_retrieval_service import rag_retrieval_service
from app.services.query_understanding import QueryUnderstandingService
from golden_evaluation import GOLDEN_QUERIES, hit_rate_at_k

rag_retrieval_service._initialize()
client = rag_retrieval_service._retrieval_api.qdrant_client
qu_service = QueryUnderstandingService()
retrieval_api = rag_retrieval_service._retrieval_api

def categorize_query(query: str) -> str:
    # A simple heuristic based on the presence of explicit patterns vs natural language
    # We will refine this in the analysis
    pass

def trace_query(gq: dict):
    qid = gq["id"]
    query = gq["query"]
    expected = gq["expected_record_ids"]
    
    print(f"\n{'='*80}")
    print(f"TRACING: {qid}")
    print(f"Query: {query}")
    print(f"Expected: {expected}")
    print(f"{'='*80}")
    
    # 1. Query Understanding
    qu = qu_service.parse(query)
    print("\n--- 1. Query Understanding ---")
    print(f"Original Query: {qu.original_query}")
    print(f"Extracted Entities:")
    print(f"  Person: {qu.person_ids}")
    print(f"  Phone: {qu.phone_ids}")
    print(f"  Vehicle: {qu.vehicle_ids}")
    print(f"  FIR: {qu.fir_ids}")
    print(f"  Account: {qu.account_ids}")
    print(f"  Record: {qu.record_ids}")
    print(f"  Case: {qu.case_ids}")
    print(f"  Tower: {qu.tower_ids}")
    print(f"  Branch: {qu.branch_ids}")
    print(f"  All Entity Refs: {qu.all_entity_refs}")
    
    # 2. Context Building
    ctx = rag_retrieval_service._build_investigation_context(query, qu, scenario_id="S01")
    print("\n--- 2. Retrieval Context ---")
    retrieval_mode = "hybrid" if qu.all_entity_refs else "semantic"
    print(f"Mode chosen: {retrieval_mode}")
    print(f"investigation_context.case_ids: {ctx.case_ids}")
    print(f"investigation_context.source_type_filters: {ctx.source_type_filters}")
    print(f"investigation_context.known_entity_refs: {ctx.known_entity_refs}")
    
    # 3. RetrievalAPI Search (Mocking inside RetrievalAPI to see exact vs semantic candidates)
    # We will replicate the logic to see the counts
    print("\n--- 3. Candidate Retrieval ---")
    exact_ids = ctx.known_entity_refs if ctx and ctx.known_entity_refs else []
    semantic_text = query
    if exact_ids:
        for eid in exact_ids:
            semantic_text = semantic_text.replace(eid, "").strip()
        semantic_text = re.sub(r'\s+', ' ', semantic_text)
    
    print(f"Remaining semantic text: '{semantic_text}'")
    
    filters = {}
    top_k = 10
    
    semantic_results = []
    if semantic_text or not exact_ids:
        query_vector = retrieval_api.model.encode(semantic_text if semantic_text else " ", convert_to_numpy=True).tolist()
        semantic_results = retrieval_api.qdrant_client.search(
            query_vector=query_vector, 
            top_k=top_k * 2 if retrieval_mode == "hybrid" else top_k,
            filters=filters,
            investigation_context=ctx
        )
    print(f"Semantic candidates retrieved: {len(semantic_results)}")
    
    exact_results = []
    if retrieval_mode == "hybrid" and exact_ids:
        expanded_exact_ids = retrieval_api._normalize_identifiers(exact_ids)
        print(f"Expanded exact IDs: {expanded_exact_ids}")
        exact_results = retrieval_api.qdrant_client.search_exact(
            identifiers=expanded_exact_ids,
            top_k=top_k * 2,
            filters=filters,
            investigation_context=ctx
        )
    print(f"Exact candidates retrieved: {len(exact_results)}")
    
    # Let's run full retrieval to see fusion
    raw_results = retrieval_api.search(
        query=query,
        top_k=top_k,
        investigation_context=ctx,
        retrieval_mode=retrieval_mode,
        entity_expansion=True,
        rerank=True,
    )
    
    print("\n--- 4. Hybrid Candidate Fusion Mathematical Check ---")
    final_ids = []
    for r in raw_results:
        doc_id = r.get("payload", {}).get("document_id", "")
        # For evaluation, we only check the source_record_id part of document_id usually, but let's see
        # Wait, expected_ids are source_record_id.
        source_record_id = r.get("payload", {}).get("source_record_id", "")
        final_ids.append(source_record_id)
        
        is_expected = source_record_id in expected
        marker = ">> " if is_expected else "   "
        
        # print specific metrics
        print(f"{marker} {source_record_id} | Exact: {r.get('exact_match', False)} | Semantic Score: {r.get('semantic_score', 0):.4f} | Fusion Score: {r.get('fusion_score', 0):.4f} | Rerank Score: {r.get('rerank_score', 0):.4f} | Sources: {r.get('retrieval_signals', [])}")

    hr = hit_rate_at_k(final_ids, expected, 10)
    print(f"\nFinal HitRate@10: {hr} (Expected found: {[e for e in expected if e in final_ids]})")
    if expected:
        missed = [e for e in expected if e not in final_ids]
        if missed:
            print(f"MISSED: {missed}")

if __name__ == "__main__":
    os.environ['RAG_USE_QDRANT'] = 'true'
    for gq in GOLDEN_QUERIES:
        trace_query(gq)
