import os
import sqlite3
import hashlib
from datetime import datetime

conn = sqlite3.connect('D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/demo_sih26190.db')
cursor = conn.cursor()

now = datetime.utcnow()
case_id = 'CASE-2026-001'
doc_id = 'DOC-FIR-DEMO'
title = 'FIR - First Information Report (Official)'

content = """# First Information Report (FIR)
**FIR No:** 2026/09/DL-402
**Date:** 01 Sept 2026
**Police Station:** Connaught Place, New Delhi

## Complainant Details
**Name:** Anonymous Informant
**Occupation:** Business Owner

## Incident Details
**Date of Occurrence:** 28 Aug 2026
**Place of Occurrence:** Outer Ring Road, Near Cyber Hub
**Offense:** Suspected Money Laundering and Extortion under IPC Section 384, 420.

## Statement
The complainant alleges that an organized group led by an individual named 'Ravi Kumar' has been extorting local business owners. The cash is collected in black duffel bags and transported via a red Maruti Swift to an unknown location for hawala routing.

## Police Action
FIR registered. Case assigned to ACP Rahul Sharma for immediate covert investigation. Surveillance teams dispatched to monitor the suspect's known aliases and shell companies.

*Note: This document is classified. Unauthorized access or modification will trigger an immediate system alert.*
"""

# Write to disk
storage_dir = f'D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/storage/{case_id}'
os.makedirs(storage_dir, exist_ok=True)
file_path = os.path.join(storage_dir, f"{doc_id}.txt")
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

sha256_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

# Check if exists
res = cursor.execute(f"SELECT document_id FROM documents WHERE document_id='{doc_id}'").fetchone()
if not res:
    cursor.execute('''
        INSERT INTO documents (document_id, case_id, title, document_type, classification, owner, uploaded_by, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (doc_id, case_id, title, 'FIR', 'CONFIDENTIAL', 'Police Dept', 'admin', now.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S')))

    cursor.execute('''
        INSERT INTO document_versions (version_id, document_id, version_number, file_path, sha256_hash, created_by, created_at, change_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (f"{doc_id}-v1", doc_id, 1, file_path, sha256_hash, 'admin', now.strftime('%Y-%m-%d %H:%M:%S'), 'FIR Initially Filed'))
else:
    cursor.execute(f"UPDATE document_versions SET sha256_hash='{sha256_hash}' WHERE document_id='{doc_id}'")

conn.commit()
conn.close()
print("Successfully generated FIR demo document.")
