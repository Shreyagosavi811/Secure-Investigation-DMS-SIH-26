import os
import sys
import json
from pprint import pprint

# Setup paths
sys.path.append(os.path.dirname(__file__))
from app.services.rag_retrieval_service import rag_retrieval_service
from app.services.query_understanding import query_understanding_service
from rag.investigation.context import InvestigationContext

def trace_query(query: str, desc: str):
    print(f"\n{'='*80}")
    print(f"TRACING: {desc}")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    # 1. Query Understanding
    try:
        qu_result = query_understanding_service.analyze_query(query)
        print("\n--- Query Understanding ---")
        print(f"Core Intent: {qu_result.core_intent}")
        print(f"Entities: {qu_result.entities}")
        print(f"Exact Refs: {qu_result.all_entity_refs}")
    except Exception as e:
        print(f"QU Failed: {e}")
        return

    # 2. Retrieval Execution
    try:
        ctx = rag_retrieval_service._build_investigation_context(query, qu_result, scenario_id="S01")
        has_exact_ids = bool(qu_result and qu_result.all_entity_refs)
        mode = "hybrid" if has_exact_ids else "semantic"
        print(f"\n--- Retrieval Context ---")
        print(f"Mode chosen: {mode}")
        
        # We need to trace internal RetrievalAPI logic
        api = rag_retrieval_service._retrieval_api
        
        # Let's run the search but intercept the candidates
        raw_results = api.search(
            query=query,
            top_k=10,
            investigation_context=ctx,
            retrieval_mode=mode,
            entity_expansion=True,
            rerank=True
        )
        
        print("\n--- Final Results (Top 10) ---")
        for i, r in enumerate(raw_results):
            print(f"[{i+1}] {r.get('document_id', 'unknown')} | Score: {r.get('combined_score', 0):.4f} | Source: {r.get('retrieval_signals', [])}")
            
    except Exception as e:
        print(f"Retrieval Failed: {e}")

if __name__ == "__main__":
    os.environ['RAG_USE_QDRANT'] = 'true'
    rag_retrieval_service._initialize()
    
    trace_query("bank transactions involving account 3189", "GQ-001")
    trace_query("FIR-100/2026/NE", "GQ-006")
    trace_query("+91-9836352800 mobile phone activity", "GQ-014")
    trace_query("FNOTE-S01-0003 financial intelligence Vasant Kunj", "GQ-016")
    trace_query("BR-001042 branch banking transactions", "GQ-024")
    
