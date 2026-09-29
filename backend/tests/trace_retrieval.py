import os
import sys
import json

sys.path.append(os.path.dirname(__file__))
from app.services.rag_retrieval_service import rag_retrieval_service
from app.services.query_understanding import query_understanding_service

def trace_query(query: str, desc: str):
    print(f"\n{'='*80}")
    print(f"TRACING: {desc}")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    # 1. Query Understanding
    try:
        qu_result = query_understanding_service.parse(query)
        print("\n--- 1. Query Understanding ---")
        print(f"Entities: {qu_result.all_entity_refs}")
    except Exception as e:
        print(f"QU Failed: {e}")
        return

    # 2. Retrieval Execution
    try:
        ctx = rag_retrieval_service._build_investigation_context(query, qu_result, scenario_id="S01")
        has_exact_ids = bool(qu_result and qu_result.all_entity_refs)
        mode = "hybrid" if has_exact_ids else "semantic"
        print(f"\n--- 2. Retrieval Context ---")
        print(f"Mode chosen: {mode}")
        print(f"investigation_context.known_entity_refs: {ctx.known_entity_refs}")
        
        api = rag_retrieval_service._retrieval_api
        
        # What does _extract_identifiers actually return?
        exact_ids, semantic_text = api._extract_identifiers(query)
        print(f"\n--- 3. RetrievalAPI internal regex ---")
        print(f"Regex extracted exact_ids: {exact_ids}")
        print(f"Regex remaining semantic_text: {semantic_text}")
        
        # Run actual search
        print("\n--- 4. Hybrid Candidate Fusion Mathematical Check ---")
        raw_results = api.search(
            query=query,
            top_k=10,
            investigation_context=ctx,
            retrieval_mode=mode,
            entity_expansion=False,
            rerank=True
        )
        
        for r in raw_results:
            pid = r.get("payload", {}).get("document_id", "unknown")
            print(json.dumps({
                "record_id": pid,
                "exact_match": r.get("exact_match", False),
                "semantic_score": round(r.get("score", 0.0), 4),
                "fusion_score": round(r.get("combined_score", r.get("score", 0.0)), 4),
                "rerank_score": round(r.get("rerank_score", 0.0), 4),
                "retrieval_sources": r.get("retrieval_signals", [])
            }))
            
    except Exception as e:
        print(f"Retrieval Failed: {e}")

if __name__ == "__main__":
    os.environ['RAG_USE_QDRANT'] = 'true'
    os.environ['HF_HOME'] = 'D:/hf_cache'
    rag_retrieval_service._initialize()
    
    trace_query("bank transactions involving account 3189", "GQ-001")
    trace_query("FIR-100/2026/NE", "GQ-006")
    trace_query("+91-9836352800 mobile phone activity", "GQ-014")
    trace_query("FNOTE-S01-0003 financial intelligence Vasant Kunj", "GQ-016")
    trace_query("all records related to account 3189 financial activity", "GQ-017")
    trace_query("BR-001042 branch banking transactions", "GQ-024")
    trace_query("suspicious money transfers and UPI payments", "GQ-003")
