import os
import sqlite3
import hashlib

conn = sqlite3.connect('D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/demo_sih26190.db')
cursor = conn.cursor()

storage_dir = 'D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/storage/CASE-2026-001'

docs = {
    'DOC-001-001': 'Initial FIR filed at Connaught Place Police Station, New Delhi. Suspect apprehended with 200,000 INR in suspected black money. Ongoing investigation to uncover the broader network.',
    'DOC-001-002': 'Follow-up Raid Report: Seized financial ledgers from the suspects residence in Karol Bagh. The ledgers indicate a monthly cash flow of over 1.5 Crore INR routed through shell companies in Mumbai and Dubai.'
}

for doc_id, text in docs.items():
    file_path = os.path.join(storage_dir, f"{doc_id}.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    sha256_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    cursor.execute(f"UPDATE document_versions SET sha256_hash='{sha256_hash}' WHERE document_id='{doc_id}'")
    cursor.execute(f"UPDATE documents SET title='Investigation Report {doc_id[-1]}' WHERE document_id='{doc_id}'")

conn.commit()
conn.close()
print("Updated other reports.")
