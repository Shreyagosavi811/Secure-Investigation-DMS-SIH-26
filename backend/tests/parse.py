import re

with open('tests/diagnostic_output.txt') as f:
    content = f.read()

queries = ['GQ-001', 'GQ-003', 'GQ-005', 'GQ-006', 'GQ-012', 'GQ-014', 'GQ-016', 'GQ-017', 'GQ-022', 'GQ-024']

for query_id in queries:
    match = re.search(r'TRACING: ' + query_id + r'.*?(?=TRACING: |$)', content, re.DOTALL)
    if match:
        block = match.group(0)
        lines = block.strip().split('\n')
        missed = [l for l in lines if l.startswith('MISSED:')]
        mode = [l for l in lines if l.startswith('Mode chosen:')]
        entities = [l for l in lines if l.startswith('  All Entity Refs:')]
        status = missed[0] if missed else "HIT!"
        print(f'{query_id} -> {mode[0]} | {entities[0]} | {status}')
        if missed:
            res = [l for l in lines if '| Exact:' in l][:3]
            for r in res:
                print('  ' + r)
