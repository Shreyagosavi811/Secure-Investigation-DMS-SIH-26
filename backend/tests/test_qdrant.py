import os
import sys

sys.path.append(os.path.dirname(__file__))
from app.services.rag_retrieval_service import rag_retrieval_service
from rag.investigation.context import InvestigationContext

def test_qdrant_exact(query: str, exact_ids: list):
    rag_retrieval_service._initialize()
    client = rag_retrieval_service._retrieval_api.qdrant_client
    
    print(f"Testing exact search for: {exact_ids} with context")
    ctx = InvestigationContext(
        investigation_id="INV-001",
        source_type_filters=["cctns_fir_records"],
        case_ids=["S01"]
    )
    results = client.search_exact(identifiers=exact_ids, investigation_context=ctx)
    print(f"Found {len(results)} exact matches.")
    for r in results:
        payload = r.get("payload", {})
        print(f"Match: {payload.get('source_record_id')}")

if __name__ == "__main__":
    os.environ['RAG_USE_QDRANT'] = 'true'
    test_qdrant_exact("", ["FIR-100/2026/NE"])
