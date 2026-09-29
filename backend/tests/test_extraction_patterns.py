"""
test_extraction_patterns.py

Verifies that the new contextual patterns:
1. Extract the right identifiers for known good queries
2. Do NOT extract false positives from dates, amounts, years, counts, street numbers
"""
import sys
sys.path.insert(0, '..')

from app.services.query_understanding import QueryUnderstandingService

qu = QueryUnderstandingService()

POSITIVE_CASES = [
    # (query, expected_account_ids, expected_phone_ids, description)
    ("bank transactions involving account 3189", ["3189"], [], "contextual account keyword"),
    ("financial activity for account 3189", ["3189"], [], "natural language account"),
    ("account number 3189 transactions", ["3189"], [], "account number keyword"),
    ("A/C 3189 debits", ["3189"], [], "A/C abbreviation"),
    ("acc 3189 transactions", ["3189"], [], "acc abbreviation"),
    ("CDR 9836352800 mobile phone activity", [], ["9836352800"], "CDR context for bare phone"),
    ("mobile number 9836352800 call logs", [], ["9836352800"], "mobile context for bare phone"),
    ("+91-9836352800 mobile phone activity", [], ["+91-9836352800"], "formatted phone unchanged"),
    ("PHONE-9836352800 records", [], ["PHONE-9836352800"], "PHONE prefix unchanged"),
]

NEGATIVE_CASES = [
    # (query, description, field)
    ("suspicious money transfers in 2026", "year 2026 must not be an account", "account_ids"),
    ("transactions of INR 3189 paid", "amount 3189 must not be an account", "account_ids"),
    ("7 suspects identified near toll gate 18", "toll gate number must not be account", "account_ids"),
    ("FIR registered on 15/08/2026", "date component must not be account", "account_ids"),
    ("last 30 days transaction history", "count 30 must not be account", "account_ids"),
    ("tower sector 18 observations", "sector number must not be phone", "phone_ids"),
    ("cash deposits worth 50000 rupees", "amount must not be phone", "phone_ids"),
    ("branch 1042 activity", "bare branch number without BR- prefix must not be account", "account_ids"),
]

print("=== POSITIVE CASES ===")
all_pass = True
for query, exp_acc, exp_phone, desc in POSITIVE_CASES:
    result = qu.parse(query)
    acc_ok = all(a in result.account_ids for a in exp_acc)
    phone_ok = all(p in result.phone_ids for p in exp_phone)
    status = "PASS" if (acc_ok and phone_ok) else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"  [{status}] {desc}")
    if status == "FAIL":
        print(f"         Query: {query}")
        print(f"         Expected acc: {exp_acc}, Got: {result.account_ids}")
        print(f"         Expected phone: {exp_phone}, Got: {result.phone_ids}")

print()
print("=== NEGATIVE CASES (must NOT extract) ===")
for query, desc, field in NEGATIVE_CASES:
    result = qu.parse(query)
    extracted = getattr(result, field)
    # Any extraction here is a false positive
    if extracted:
        status = "FAIL (false positive)"
        all_pass = False
    else:
        status = "PASS"
    print(f"  [{status}] {desc}")
    if extracted:
        print(f"         Query: {query}")
        print(f"         Spuriously extracted {field}: {extracted}")

print()
if all_pass:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED - review patterns")
    sys.exit(1)
