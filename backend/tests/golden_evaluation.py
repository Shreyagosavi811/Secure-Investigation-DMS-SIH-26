"""
golden_evaluation.py

Golden evaluation set for the SIH26189 RAG pipeline.
~25 investigation queries with expected entities, source types, and relationships.

Metrics computed:
  - Recall@5: % of expected records in top 5
  - Recall@10: % of expected records in top 10
  - MRR: Mean Reciprocal Rank
  - Hit Rate@10: % of queries with at least 1 expected record in top 10
  - Source Diversity: avg number of unique source families retrieved
  - Grounding Rate: % of LLM citations that were actually retrieved

Usage:
  cd backend
  python tests/golden_evaluation.py
  
Or with specific options:
  CORPUS_MODE=small RAG_USE_QDRANT=false python tests/golden_evaluation.py
"""

import os
import sys
import json
import time
import logging

# Set defaults for evaluation run
os.environ.setdefault("CORPUS_MODE", "small")
os.environ.setdefault("RAG_USE_QDRANT", "false")  # keyword fallback for CI

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.WARNING)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Golden Queries
# Based on the S01 corpus (100 records: CBS bank, FIRs, CDR, cell towers,
# criminal history, field notes, FIU, CAF/KYC, OSINT, ANPR)
# ---------------------------------------------------------------------------

GOLDEN_QUERIES = [
    # ---- Financial Queries ----
    {
        "id": "GQ-001",
        "query": "bank transactions involving account 3189",
        "expected_record_ids": ["CBS-S01-00001", "CBS-S01-00002", "CBS-S01-00004"],
        "expected_source_types": ["cbs_bank_transactions"],
        "expected_entities": ["3189"],
        "notes": "Direct account ID lookup"
    },
    {
        "id": "GQ-002",
        "query": "CBS-S01-00001",
        "expected_record_ids": ["CBS-S01-00001"],
        "expected_source_types": ["cbs_bank_transactions"],
        "expected_entities": ["3189", "203195"],
        "notes": "Exact record ID retrieval"
    },
    {
        "id": "GQ-003",
        "query": "suspicious money transfers and UPI payments",
        "expected_record_ids": ["CBS-S01-00001"],
        "expected_source_types": ["cbs_bank_transactions"],
        "expected_entities": [],
        "notes": "Semantic financial query"
    },
    {
        "id": "GQ-004",
        "query": "high value financial transactions large amounts",
        "expected_record_ids": [],
        "expected_source_types": ["cbs_bank_transactions", "fiu_str_alerts"],
        "expected_entities": [],
        "notes": "Semantic query - financial sources"
    },
    {
        "id": "GQ-005",
        "query": "invoice settlement NEFT transfer",
        "expected_record_ids": ["CBS-S01-00002"],
        "expected_source_types": ["cbs_bank_transactions"],
        "expected_entities": [],
        "notes": "Specific transaction type semantic"
    },
    
    # ---- FIR / Criminal History Queries ----
    {
        "id": "GQ-006",
        "query": "FIR-100/2026/NE",
        "expected_record_ids": ["FIR-100/2026/NE"],
        "expected_source_types": ["cctns_fir_records"],
        "expected_entities": ["Nikhil Red", "Nikhil Sharma"],
        "notes": "Exact FIR retrieval"
    },
    {
        "id": "GQ-007",
        "query": "Nikhil Sharma criminal history robbery pending trial",
        "expected_record_ids": ["CRIM-S01-0005", "CRIM-S01-0010"],
        "expected_source_types": ["criminal_history_db"],
        "expected_entities": ["Nikhil Sharma"],
        "notes": "Person name + criminal history"
    },
    {
        "id": "GQ-008",
        "query": "fraudulent bank call cyber fraud complaint",
        "expected_record_ids": ["FIR-100/2026/NE"],
        "expected_source_types": ["cctns_fir_records"],
        "expected_entities": [],
        "notes": "Semantic FIR search"
    },
    {
        "id": "GQ-009",
        "query": "Nikhil Reddy cheating extortion bail",
        "expected_record_ids": ["CRIM-S01-0001", "CRIM-S01-0006"],
        "expected_source_types": ["criminal_history_db"],
        "expected_entities": ["Nikhil Reddy"],
        "notes": "Specific person criminal history"
    },
    {
        "id": "GQ-010",
        "query": "financial fraud IPC 420 bank account compromise",
        "expected_record_ids": ["FIR-100/2026/NE", "FIR-104/2026/NE"],
        "expected_source_types": ["cctns_fir_records"],
        "expected_entities": [],
        "notes": "IPC section semantic query"
    },
    
    # ---- Cell Tower / Telecom Queries ----
    {
        "id": "GQ-011",
        "query": "TDUMP-S01-0001",
        "expected_record_ids": ["TDUMP-S01-0001"],
        "expected_source_types": ["cell_tower_dumps"],
        "expected_entities": [],
        "notes": "Exact tower dump ID"
    },
    {
        "id": "GQ-012",
        "query": "cell tower Connaught Place devices logged",
        "expected_record_ids": ["TDUMP-S01-0001", "TDUMP-S01-0006"],
        "expected_source_types": ["cell_tower_dumps"],
        "expected_entities": [],
        "notes": "Location-based tower query"
    },
    {
        "id": "GQ-013",
        "query": "TOWER-DL-CP-101 phone activity",
        "expected_record_ids": ["TDUMP-S01-0001", "TDUMP-S01-0006"],
        "expected_source_types": ["cell_tower_dumps"],
        "expected_entities": [],
        "notes": "Tower ID entity lookup"
    },
    {
        "id": "GQ-014",
        "query": "+91-9836352800 mobile phone activity",
        "expected_record_ids": ["TDUMP-S01-0001", "TDUMP-S01-0002"],
        "expected_source_types": ["cell_tower_dumps"],
        "expected_entities": ["+91-9836352800"],
        "notes": "Phone number exact lookup"
    },
    
    # ---- Field Intelligence Notes ----
    {
        "id": "GQ-015",
        "query": "unusual vehicle movement field intelligence source tip",
        "expected_record_ids": ["FNOTE-S01-0001"],
        "expected_source_types": ["field_intelligence_notes"],
        "expected_entities": [],
        "notes": "Field note semantic query"
    },
    {
        "id": "GQ-016",
        "query": "FNOTE-S01-0003 financial intelligence Vasant Kunj",
        "expected_record_ids": ["FNOTE-S01-0003"],
        "expected_source_types": ["field_intelligence_notes"],
        "expected_entities": [],
        "notes": "Field note ID + location"
    },
    
    # ---- Multi-source / Network Queries ----
    {
        "id": "GQ-017",
        "query": "all records related to account 3189 financial activity",
        "expected_record_ids": ["CBS-S01-00001", "CBS-S01-00004"],
        "expected_source_types": ["cbs_bank_transactions"],
        "expected_entities": ["3189"],
        "notes": "Account entity + financial"
    },
    {
        "id": "GQ-018",
        "query": "robbery knife knifepoint valuables vehicle stopped",
        "expected_record_ids": ["FIR-102/2026/NE", "FIR-108/2026/NE"],
        "expected_source_types": ["cctns_fir_records"],
        "expected_entities": [],
        "notes": "Semantic robbery FIR"
    },
    {
        "id": "GQ-019",
        "query": "narcotics contraband substance vehicle check forensic analysis",
        "expected_record_ids": ["FIR-103/2026/NE", "FIR-109/2026/NE"],
        "expected_source_types": ["cctns_fir_records"],
        "expected_entities": [],
        "notes": "Semantic narcotics FIR"
    },
    {
        "id": "GQ-020",
        "query": "Karan Kapoor financial fraud absconding",
        "expected_record_ids": ["CRIM-S01-0004", "CRIM-S01-0009"],
        "expected_source_types": ["criminal_history_db"],
        "expected_entities": ["Karan Kapoor"],
        "notes": "Specific person + offence category"
    },
    {
        "id": "GQ-021",
        "query": "Meena Pandey vehicle theft acquitted Gurugram",
        "expected_record_ids": ["CRIM-S01-0002", "CRIM-S01-0007"],
        "expected_source_types": ["criminal_history_db"],
        "expected_entities": ["Meena Pandey"],
        "notes": "Person + location + offence"
    },
    {
        "id": "GQ-022",
        "query": "informant meeting Noida Sector 18 ATM identities unclear",
        "expected_record_ids": ["FNOTE-S01-0005"],
        "expected_source_types": ["field_intelligence_notes"],
        "expected_entities": [],
        "notes": "Specific field note by content"
    },
    {
        "id": "GQ-023",
        "query": "extortion threatening messages demanding money partial payment",
        "expected_record_ids": ["FIR-101/2026/NE", "FIR-107/2026/NE"],
        "expected_source_types": ["cctns_fir_records"],
        "expected_entities": [],
        "notes": "Extortion FIR semantic"
    },
    {
        "id": "GQ-024",
        "query": "BR-001042 branch banking transactions",
        "expected_record_ids": ["CBS-S01-00001", "CBS-S01-00004", "CBS-S01-00007"],
        "expected_source_types": ["cbs_bank_transactions"],
        "expected_entities": ["BR-001042"],
        "notes": "Branch ID location lookup"
    },
    {
        "id": "GQ-025",
        "query": "no evidence no results whatsoever empty",
        "expected_record_ids": [],
        "expected_source_types": [],
        "expected_entities": [],
        "notes": "Empty retrieval test — should handle gracefully"
    },
]


# ---------------------------------------------------------------------------
# Evaluation Functions
# ---------------------------------------------------------------------------

def reciprocal_rank(results: list, expected: list) -> float:
    """Calculate MRR for a single query."""
    if not expected:
        return 1.0  # No expectation, any result is fine
    for i, r in enumerate(results):
        if r in expected:
            return 1.0 / (i + 1)
    return 0.0


def recall_at_k(results: list, expected: list, k: int) -> float:
    """Recall@K for a single query."""
    if not expected:
        return 1.0  # No ground truth to miss
    top_k = set(results[:k])
    hits = sum(1 for e in expected if e in top_k)
    return hits / len(expected)


def hit_rate_at_k(results: list, expected: list, k: int) -> float:
    """Hit rate@K: 1 if at least 1 expected in top K."""
    if not expected:
        return 1.0
    top_k = set(results[:k])
    return 1.0 if any(e in top_k for e in expected) else 0.0


def run_evaluation(verbose: bool = True) -> dict:
    """Run the full golden evaluation set."""
    results = {
        "total": len(GOLDEN_QUERIES),
        "evaluated": 0,
        "errors": 0,
        "recall_at_5": [],
        "recall_at_10": [],
        "mrr": [],
        "hit_rate_at_10": [],
        "source_diversity": [],
        "query_results": [],
    }

    print(f"\n{'='*70}")
    print(f"SIH26189 RAG Golden Evaluation — {len(GOLDEN_QUERIES)} queries")
    print(f"{'='*70}\n")

    for gq in GOLDEN_QUERIES:
        qid = gq["id"]
        query = gq["query"]
        expected_ids = gq["expected_record_ids"]
        expected_types = gq["expected_source_types"]

        try:
            t0 = time.time()
            response = client.post("/api/ai/query", json={
                "query": query,
                "scenario_id": "S01",
                "top_k": 10,
            })
            elapsed_ms = round((time.time() - t0) * 1000, 1)

            if response.status_code != 200:
                print(f"  [{qid}] ERROR: HTTP {response.status_code}")
                results["errors"] += 1
                continue

            data = response.json()
            retrieved = data.get("results", [])
            retrieved_ids = [r.get("record_id", "") for r in retrieved]
            retrieved_types = {r.get("source_type", "") for r in retrieved}

            # Compute metrics
            r5 = recall_at_k(retrieved_ids, expected_ids, 5)
            r10 = recall_at_k(retrieved_ids, expected_ids, 10)
            mrr = reciprocal_rank(retrieved_ids, expected_ids)
            hr10 = hit_rate_at_k(retrieved_ids, expected_ids, 10)
            diversity = len(retrieved_types)

            results["recall_at_5"].append(r5)
            results["recall_at_10"].append(r10)
            results["mrr"].append(mrr)
            results["hit_rate_at_10"].append(hr10)
            results["source_diversity"].append(diversity)
            results["evaluated"] += 1

            # Grounding rate
            llm = data.get("llm_response", {})
            citations = llm.get("citations", [])
            cited_ids = {c.get("source_record_id", "") for c in citations}
            valid_cited = cited_ids & set(retrieved_ids)
            grounding_rate = len(valid_cited) / len(cited_ids) if cited_ids else 1.0

            status = "OK" if hr10 > 0 or not expected_ids else "MISS"

            if verbose:
                try:
                    print(f"  [{status}] [{qid}] {query[:55]:<55}")
                    print(f"       R@5={r5:.2f}  R@10={r10:.2f}  MRR={mrr:.3f}  HR@10={hr10:.0f}  Diversity={diversity}  Ground={grounding_rate:.2f}  ({elapsed_ms}ms)")
                    if expected_ids and r10 < 1.0:
                        missed = [e for e in expected_ids if e not in retrieved_ids[:10]]
                        print(f"       Missed: {missed}")
                except UnicodeEncodeError:
                    print(f"  [{status}] [{qid}] (query display skipped - encoding issue)")

            results["query_results"].append({
                "id": qid,
                "query": query,
                "retrieved_count": len(retrieved_ids),
                "expected_count": len(expected_ids),
                "recall_at_5": r5,
                "recall_at_10": r10,
                "mrr": mrr,
                "hit_rate_at_10": hr10,
                "source_diversity": diversity,
                "grounding_rate": grounding_rate,
                "notes": gq.get("notes", ""),
            })

        except Exception as e:
            print(f"  [{qid}] EXCEPTION: {e}")
            results["errors"] += 1

    # Aggregate metrics
    n = len(results["recall_at_5"])
    if n > 0:
        summary = {
            "Recall@5": round(sum(results["recall_at_5"]) / n, 4),
            "Recall@10": round(sum(results["recall_at_10"]) / n, 4),
            "MRR": round(sum(results["mrr"]) / n, 4),
            "HitRate@10": round(sum(results["hit_rate_at_10"]) / n, 4),
            "AvgSourceDiversity": round(sum(results["source_diversity"]) / n, 2),
            "QueriesEvaluated": n,
            "Errors": results["errors"],
        }
    else:
        summary = {"error": "No queries evaluated"}

    results["summary"] = summary

    print(f"\n{'='*70}")
    print("EVALUATION SUMMARY")
    print(f"{'='*70}")
    for k, v in summary.items():
        print(f"  {k:<25}: {v}")
    print(f"{'='*70}\n")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run SIH26189 golden evaluation")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-query output")
    parser.add_argument("--output", type=str, help="Save results to JSON file")
    args = parser.parse_args()

    results = run_evaluation(verbose=not args.quiet)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
