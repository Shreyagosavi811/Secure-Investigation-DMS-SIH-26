import json

corpus_path = 'd:/Antigravity/SIH-26-Criminal-Network-Analysis/investigation_dataset_engine/output/RAG_CORPUS/corpus_small.jsonl'
source_type_stats = {}
loc_present = 0
loc_empty = 0
branch_in_loc = 0
branch_in_entity = 0

with open(corpus_path) as f:
    for line in f:
        d = json.loads(line)
        st = d.get('source_type', 'unknown')
        loc = d.get('location_refs') or []
        ent = d.get('entity_refs') or []
        if st not in source_type_stats:
            source_type_stats[st] = {'total': 0, 'has_location': 0}
        source_type_stats[st]['total'] += 1
        if loc:
            source_type_stats[st]['has_location'] += 1
            loc_present += 1
        else:
            loc_empty += 1
        for l in loc:
            if l.startswith('BR-'):
                branch_in_loc += 1
        for e in ent:
            if e.startswith('BR-'):
                branch_in_entity += 1

print('=== location_refs population by source_type ===')
for st, stats in sorted(source_type_stats.items()):
    pct = 100 * stats['has_location'] / stats['total']
    print(f"  {st}: {stats['total']} total, {stats['has_location']} with location ({pct:.0f}%)")
print(f'Total with location_refs: {loc_present}, empty: {loc_empty}')
print(f'Branch IDs in location_refs: {branch_in_loc}, in entity_refs: {branch_in_entity}')

# Also sample CBS-S01-00001 to see what fields are set
print()
print('=== CBS-S01-00001 sample ===')
with open(corpus_path) as f:
    for line in f:
        d = json.loads(line)
        if d.get('source_record_id') == 'CBS-S01-00001':
            print(f"  entity_refs: {d.get('entity_refs')}")
            print(f"  location_refs: {d.get('location_refs')}")
            print(f"  case_refs: {d.get('case_refs')}")
            print(f"  normalized_text: {d.get('normalized_text', '')[:120]}")
            break

print()
print('=== FNOTE-S01-0003 sample ===')
with open(corpus_path) as f:
    for line in f:
        d = json.loads(line)
        if d.get('source_record_id') == 'FNOTE-S01-0003':
            print(f"  entity_refs: {d.get('entity_refs')}")
            print(f"  location_refs: {d.get('location_refs')}")
            print(f"  case_refs: {d.get('case_refs')}")
            print(f"  normalized_text: {d.get('normalized_text', '')[:200]}")
            break

print()
print('=== FNOTE-S01-0005 sample ===')
with open(corpus_path) as f:
    for line in f:
        d = json.loads(line)
        if d.get('source_record_id') == 'FNOTE-S01-0005':
            print(f"  entity_refs: {d.get('entity_refs')}")
            print(f"  location_refs: {d.get('location_refs')}")
            print(f"  normalized_text: {d.get('normalized_text', '')[:200]}")
            break
