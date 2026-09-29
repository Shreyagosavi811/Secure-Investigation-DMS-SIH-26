import json

with open('eval_keyword.json', encoding='utf-8') as f:
    kw = json.load(f)['query_results']
with open('eval_hybrid.json', encoding='utf-8') as f:
    hy = json.load(f)['query_results']

kw_misses = [q['query_id'] for q in kw if q['hit_at_10'] == False]
hy_misses = [q['query_id'] for q in hy if q['hit_at_10'] == False]

print('Keyword missed:', kw_misses)
print('Hybrid missed:', hy_misses)

print('\nHybrid details for missed queries:')
for q in hy:
    if q['query_id'] in hy_misses:
        print(f"{q['query_id']}: {q['query']}")
        print(f"  Expected: {q['expected_records']}")
        print(f"  Found: {[r['id'] for r in q['retrieved'][:3]]}")
