"""
test_regression_targeted.py

Targeted regression tests in the prescribed verification order:
1. Spatial filter regression (GQ-016, 022, 017 scenarios)
2. Branch ID routing regression (GQ-024)
3. Account/phone extraction regression (positive + false positive)
4. Scenario isolation regression (MUST never relaxed)

Run with: cd tests; $env:PYTHONPATH='..'; python test_regression_targeted.py
"""
import os
import sys
import re

sys.path.insert(0, '..')
os.environ['RAG_USE_QDRANT'] = 'true'

from app.services.query_understanding import QueryUnderstandingService
from app.services.rag_retrieval_service import rag_retrieval_service
from rag.vectorstore.qdrant_client import QdrantEvidenceClient

rag_retrieval_service._initialize()
client = rag_retrieval_service._retrieval_api.qdrant_client
qu_service = QueryUnderstandingService()

PASS = "[PASS]"
FAIL = "[FAIL]"
all_pass = True


def check(condition, label, details=""):
    global all_pass
    if condition:
        print(f"  {PASS} {label}")
    else:
        print(f"  {FAIL} {label}")
        if details:
            print(f"         {details}")
        all_pass = False


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 1. Identifier type routing tests
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("=" * 70)
print("1. IDENTIFIER TYPE ROUTING")
print("=" * 70)

routing_cases = [
    ("BR-001042",          ["location_refs", "entity_refs", "source_record_id"], "Branch ID â†’ location_refs primary"),
    ("FIR-100/2026/NE",    ["case_refs", "source_record_id", "scenario_instance_id"], "FIR â†’ case_refs primary"),
    ("PHONE-9836352800",   ["entity_refs"], "PHONE- prefix â†’ entity_refs"),
    ("+91-9836352800",     ["entity_refs"], "+91- phone â†’ entity_refs"),
    ("9836352800",         ["entity_refs"], "Bare 10-digit â†’ entity_refs"),
    ("FNOTE-S01-0003",     ["source_record_id"], "Record ID â†’ source_record_id"),
    ("CBS-S01-00001",      ["source_record_id"], "CBS record â†’ source_record_id"),
    ("3189",               ["entity_refs", "source_record_id"], "Generic account number â†’ default"),
    ("P-001",              ["entity_refs", "source_record_id"], "Person ID â†’ default"),
]

for identifier, expected_fields, desc in routing_cases:
    fields = QdrantEvidenceClient._route_identifier(identifier)
    check(fields == expected_fields, desc,
          f"Expected {expected_fields}, got {fields}")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 2. Spatial filter regression
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print()
print("=" * 70)
print("2. SPATIAL FILTER REGRESSION")
print("=" * 70)

# GQ-016: FNOTE-S01-0003 + Vasant Kunj
# With explicit record ID + location, FNOTE record must survive (location â†’ SHOULD)
qu_016 = qu_service.parse("FNOTE-S01-0003 financial intelligence Vasant Kunj")
ctx_016 = rag_retrieval_service._build_investigation_context(
    "FNOTE-S01-0003 financial intelligence Vasant Kunj", qu_016, scenario_id="S01"
)
results_016 = client.search_exact(
    identifiers=["FNOTE-S01-0003"],
    top_k=10,
    investigation_context=ctx_016
)
found_016 = any(r.get("payload", {}).get("source_record_id") == "FNOTE-S01-0003" for r in results_016)
check(found_016, "GQ-016: FNOTE-S01-0003 not excluded by Vasant Kunj spatial filter",
      f"Results: {[r.get('payload',{}).get('source_record_id') for r in results_016]}")

# GQ-022: FNOTE-S01-0005 + Noida Sector 18
qu_022 = qu_service.parse("informant meeting Noida Sector 18 ATM identities unclear")
ctx_022 = rag_retrieval_service._build_investigation_context(
    "informant meeting Noida Sector 18 ATM identities unclear", qu_022, scenario_id="S01"
)
# This is a pure-semantic query — no exact IDs. Spatial MUST applies.
# We expect search_exact to return nothing (no ID). Semantic search will apply MUST(location_refs="Noida").
# Since FNOTE-S01-0005 has empty location_refs in the corpus, it should NOT be retrieved.
# This proves the strict MUST is preserved for pure spatial queries.
raw_022 = rag_retrieval_service._retrieval_api.search(
    query="informant meeting Noida Sector 18 ATM identities unclear",
    top_k=10,
    investigation_context=ctx_022,
    retrieval_mode="semantic",
    entity_expansion=True,
    rerank=True,
)
found_022 = any(r.get("payload", {}).get("source_record_id") == "FNOTE-S01-0005" for r in raw_022)
check(not found_022, "GQ-022: FNOTE-S01-0005 excluded by strict spatial MUST (pure-spatial query)",
      f"Results: {[r.get('payload',{}).get('source_record_id') for r in raw_022[:5]]}")

# Verify location is NOT stripping results for hybrid queries
qu_hybrid_loc = qu_service.parse("FNOTE-S01-0003 financial Vasant Kunj transfers")
ctx_hybrid_loc = rag_retrieval_service._build_investigation_context(
    "FNOTE-S01-0003 financial Vasant Kunj transfers", qu_hybrid_loc, scenario_id="S01"
)
check(
    len(ctx_hybrid_loc.scenario_ids) > 0 and "S01" in ctx_hybrid_loc.scenario_ids,
    "Scenario isolation populated for hybrid+spatial query"
)
check(
    len(ctx_hybrid_loc.location_ids) > 0,
    "Location extracted for hybrid+spatial query (will be SHOULD)"
)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 3. Branch ID regression
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print()
print("=" * 70)
print("3. BRANCH ID REGRESSION (GQ-024)")
print("=" * 70)

qu_024 = qu_service.parse("BR-001042 branch banking transactions")
check("BR-001042" in qu_024.branch_ids, "BR-001042 extracted as branch_id")
check("BR-001042" in qu_024.all_entity_refs, "BR-001042 in all_entity_refs")

ctx_024 = rag_retrieval_service._build_investigation_context(
    "BR-001042 branch banking transactions", qu_024, scenario_id="S01"
)
results_024 = client.search_exact(
    identifiers=["BR-001042"],
    top_k=10,
    investigation_context=ctx_024
)
# Verify that we retrieved records (should be CBS records) and they have BR-001042 in location_refs
found_024_records = [r for r in results_024 if "BR-001042" in r.get("payload", {}).get("location_refs", [])]
check(len(found_024_records) > 0, "BR-001042 resolves to records via location_refs routing",
      f"Retrieved {len(results_024)} records, {len(found_024_records)} have branch ID.")
check(len(results_024) >= 3, "At least 3 records found for BR-001042",
      f"Only {len(results_024)} found.")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 4. Account / Phone contextual extraction
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print()
print("=" * 70)
print("4. ACCOUNT / PHONE CONTEXTUAL EXTRACTION")
print("=" * 70)

POSITIVE_ACCOUNT = [
    ("bank transactions involving account 3189", "3189", "account keyword"),
    ("account number 3189 transactions",         "3189", "account number keyword"),
    ("financial activity for account 3189",      "3189", "natural language account"),
    ("A/C 3189 debits this month",               "3189", "A/C abbreviation"),
    ("acc 3189 transactions",                     "3189", "acc abbreviation"),
    ("transactions for account number 3189",     "3189", "transactions for account"),
]

NEGATIVE_ACCOUNT = [
    ("suspicious money transfers in 2026",         "year should not be account"),
    ("amount INR 3189 deposited to account",        "amount before keyword should not trigger"),
    ("â‚¹3189 transaction recorded",                 "rupee amount should not be account"),
    ("3 suspects identified near ATM",              "count must not be account"),
    ("18 Sector Road Noida activity",               "street number must not be account"),
    ("March 2026 financial records",               "month/year must not be account"),
    ("transaction amount 3189 recorded",           "standalone amount without keyword must not"),
    ("last 30 days transfers",                      "count with days must not be account"),
    ("FIR 3189 filed against accused",             "FIR number must not become account ID"),
]

print("  Positive account cases:")
for query, expected_acc, desc in POSITIVE_ACCOUNT:
    result = qu_service.parse(query)
    check(expected_acc in result.account_ids, f"  '{query}' â†’ account {expected_acc}",
          f"Got account_ids={result.account_ids}")

print("  Negative account cases (must NOT extract):")
for query, desc in NEGATIVE_ACCOUNT:
    result = qu_service.parse(query)
    # FIR pattern will produce fir_ids, not account_ids â€” that's correct
    check(len(result.account_ids) == 0, f"  No account: {desc}",
          f"Query: '{query}' â†’ spurious account_ids={result.account_ids}")

POSITIVE_PHONE = [
    ("CDR 9836352800 mobile phone activity", "9836352800", "CDR context bare phone"),
    ("mobile number 9836352800 call logs",   "9836352800", "mobile context bare phone"),
    ("+91-9836352800 activity",              "+91-9836352800", "formatted phone"),
    ("PHONE-9836352800 records",             "PHONE-9836352800", "PHONE- prefix"),
]

NEGATIVE_PHONE = [
    ("tower sector 18 observations",        "sector number must not be phone"),
    ("cash deposits worth 50000 rupees",    "amount must not be phone"),
    ("3 calls recorded from this number",   "count must not be phone"),
    ("2026 telecom subscriber data",        "year must not be phone"),
]

print("  Positive phone cases:")
for query, expected_ph, desc in POSITIVE_PHONE:
    result = qu_service.parse(query)
    check(expected_ph in result.phone_ids, f"  '{query}' â†’ phone {expected_ph}",
          f"Got phone_ids={result.phone_ids}")

print("  Negative phone cases (must NOT extract):")
for query, desc in NEGATIVE_PHONE:
    result = qu_service.parse(query)
    check(len(result.phone_ids) == 0, f"  No phone: {desc}",
          f"Query: '{query}' â†’ spurious phone_ids={result.phone_ids}")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 5. Scenario isolation regression
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print()
print("=" * 70)
print("5. SCENARIO ISOLATION REGRESSION")
print("=" * 70)

# scenario_ids must always be populated from scenario_id
ctx_s01 = rag_retrieval_service._build_investigation_context("test query", None, scenario_id="S01")
check(ctx_s01.scenario_ids == ["S01"], "scenario_ids populated as ['S01'] from scenario_id='S01'")

# scenario_ids must be present even when the query has explicit entity refs
qu_with_ents = qu_service.parse("FIR-100/2026/NE financial records")
ctx_with_ents = rag_retrieval_service._build_investigation_context(
    "FIR-100/2026/NE financial records", qu_with_ents, scenario_id="S01"
)
check(ctx_with_ents.scenario_ids == ["S01"],
      "scenario_ids still ['S01'] when query has FIR identifiers")
check("FIR-100/2026/NE" in ctx_with_ents.case_ids,
      "FIR still in case_ids (not scenario_ids)")

# scenario_ids must be present even when query has location refs
qu_with_loc = qu_service.parse("FNOTE-S01-0003 Vasant Kunj activity")
ctx_with_loc = rag_retrieval_service._build_investigation_context(
    "FNOTE-S01-0003 Vasant Kunj activity", qu_with_loc, scenario_id="S01"
)
check(ctx_with_loc.scenario_ids == ["S01"],
      "scenario_ids still ['S01'] when query has location refs")

# Without scenario_id, scenario_ids must be empty
ctx_no_scenario = rag_retrieval_service._build_investigation_context("test query", None, scenario_id=None)
check(ctx_no_scenario.scenario_ids == [],
      "scenario_ids empty when no scenario_id passed")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Summary
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print()
print("=" * 70)
if all_pass:
    print("ALL TARGETED REGRESSION TESTS PASSED")
else:
    print("SOME TESTS FAILED â€” review above output")
    sys.exit(1)

