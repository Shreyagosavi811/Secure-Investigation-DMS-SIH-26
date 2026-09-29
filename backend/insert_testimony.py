import os
import sqlite3
import hashlib
from datetime import datetime

conn = sqlite3.connect('D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/demo_sih26190.db')
cursor = conn.cursor()

# 1. Prepare Testimony Document
doc_id = 'DOC-001-TESTIMONY-01'
case_id = 'CASE-2026-001'
title = 'Conflicting Testimonies Report'
content = """Conflicting Testimonies Investigation Report for CASE-2026-001.
Witness A (Rahul Sharma) stated that the suspect was seen leaving the premises at 10:30 PM in a red Maruti Swift. However, Witness B (Priya Patel) provided a conflicting testimony, insisting the suspect was present inside the building until midnight and drove away in a white Mahindra Scorpio. These conflicting testimonies regarding the timeline of events require further verification.
"""

# Write to disk
storage_dir = 'D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/storage/CASE-2026-001'
os.makedirs(storage_dir, exist_ok=True)
file_path = os.path.join(storage_dir, f"{doc_id}.txt")
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Calculate SHA256
sha256_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

# 2. Insert into documents
now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

# Check if exists
res = cursor.execute(f"SELECT document_id FROM documents WHERE document_id='{doc_id}'").fetchone()
if not res:
    cursor.execute('''
        INSERT INTO documents (document_id, case_id, title, document_type, classification, owner, uploaded_by, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (doc_id, case_id, title, 'Testimony', 'CONFIDENTIAL', 'investigator', 'investigator', now, now))

# 3. Insert into document_versions
res = cursor.execute(f"SELECT version_id FROM document_versions WHERE document_id='{doc_id}'").fetchone()
if not res:
    version_id = f"{doc_id}-v1"
    cursor.execute('''
        INSERT INTO document_versions (version_id, document_id, version_number, file_path, sha256_hash, created_by, created_at, change_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (version_id, doc_id, 1, file_path, sha256_hash, 'investigator', now, 'Initial witness testimony records added'))

conn.commit()
conn.close()
print("Successfully inserted testimony document into SQLite and disk.")
