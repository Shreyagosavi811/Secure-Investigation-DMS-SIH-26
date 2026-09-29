import os
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/demo_sih26190.db')
cursor = conn.cursor()

# 4. Generate Mass Cases
regions = ["Delhi", "Mumbai", "Kolkata", "Chennai", "Bengaluru", "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Surat"]
crimes = ["Cyber Fraud", "Narcotics", "Extortion", "Money Laundering", "Human Trafficking", "Smuggling", "Terror Funding", "Organized Theft", "Tax Evasion", "Counterfeit Currency"]

now = datetime.utcnow()

for i in range(1, 51):
    case_id = f"CASE-2026-{1000 + i}"
    region = random.choice(regions)
    crime = random.choice(crimes)
    title = f"Operation {random.choice(['Shadow', 'Falcon', 'Trident', 'Storm', 'Lotus', 'Cobra', 'Eagle'])} ({region} {crime})"
    
    # Insert Case if not exists
    res = cursor.execute(f"SELECT case_id FROM cases WHERE case_id='{case_id}'").fetchone()
    if not res:
        cursor.execute('''
            INSERT INTO cases (case_id, title, description, classification, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (case_id, title, f"Investigation into {crime.lower()} ring operating in {region}.", random.choice(["CONFIDENTIAL", "SECRET", "TOP_SECRET"]), random.choice(["OPEN", "OPEN", "CLOSED"]), (now - timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d %H:%M:%S')))

    # Generate 2-5 documents per case
    for j in range(random.randint(2, 5)):
        doc_id = f"DOC-{case_id}-{j}"
        doc_title = f"{random.choice(['FIR', 'Raid Report', 'Witness Statement', 'Financial Ledger', 'Surveillance Log'])} - Part {j}"
        doc_type = random.choice(['Report', 'Testimony', 'Evidence', 'Ledger'])
        
        doc_res = cursor.execute(f"SELECT document_id FROM documents WHERE document_id='{doc_id}'").fetchone()
        if not doc_res:
            cursor.execute('''
                INSERT INTO documents (document_id, case_id, title, document_type, classification, owner, uploaded_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (doc_id, case_id, doc_title, doc_type, "CONFIDENTIAL", "investigator", "investigator", now.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S')))

            # We don't necessarily need to create files for all these dummy cases on disk since they are just to populate the dashboard,
            # but let's create tiny files so they don't break if clicked.
            storage_dir = f'D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/storage/{case_id}'
            os.makedirs(storage_dir, exist_ok=True)
            file_path = os.path.join(storage_dir, f"{doc_id}_v1.txt")
            
            content = f"Standard {doc_title} for {title}."
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            sha256_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            cursor.execute('''
                INSERT INTO document_versions (version_id, document_id, version_number, file_path, sha256_hash, created_by, created_at, change_description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"{doc_id}-v1", doc_id, 1, file_path, sha256_hash, 'investigator', now.strftime('%Y-%m-%d %H:%M:%S'), 'Initial Upload'))

# 5. Inject Master Demo Document into CASE-2026-001
doc_id = 'DOC-DEMO-MASTER'
case_id = 'CASE-2026-001'
title = 'Operation Black Money - Final Executive Report'
content = """# Operation Black Money (Delhi) - Final Executive Report

**Date of Operation:** September 2026
**Lead Investigating Officer:** ACP Rahul Sharma
**Jurisdiction:** Delhi NCR / Mumbai Financial Hub

---

## Executive Summary
This report details the culmination of a 6-month undercover operation targeting a high-level money laundering syndicate operating out of Connaught Place, New Delhi, with offshore routing through shell corporations.

## Confiscated Assets
During the synchronized raids across 4 locations on Sept 15, 2026, the following assets were successfully secured:
1. **Cash:** ₹4.5 Crores (in ₹500 denomination notes)
2. **Gold Bullion:** 12.5 kg (smuggled via sea route)
3. **Vehicles:** 
   - 2x Toyota Fortuner (Black)
   - 1x Range Rover Evoque
4. **Digital Evidence:** 14 encrypted hard drives, 22 burner phones.

## Timeline of Events
- **02 Sept 2026:** First informant tip received regarding bulk cash movement.
- **08 Sept 2026:** Surveillance establishes link between Suspect A (Ravi Kumar) and the hawala operators.
- **12 Sept 2026:** Wiretaps confirm shipment of gold bullion arriving at Mumbai Port.
- **15 Sept 2026 (04:00 AM):** Coordinated raids initiated.
- **15 Sept 2026 (09:00 AM):** Primary suspects apprehended.

## Suspect Matrix

| Name | Role | Status | Bail Status |
|---|---|---|---|
| Ravi Kumar | Syndicate Leader | Custody | Denied |
| Amit Singh | Hawala Operator | Custody | Pending |
| Priya Desai | Shell Co. Director | Absconding | N/A |
| Suresh Patel | Port Customs Inside | Custody | Denied |

---
**END OF REPORT**
*Generated securely by OmniGuard DMS*
"""

# Write to disk
storage_dir = 'D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/storage/CASE-2026-001'
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
    ''', (doc_id, case_id, title, 'Executive Report', 'TOP_SECRET', 'investigator', 'investigator', now.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S')))

    cursor.execute('''
        INSERT INTO document_versions (version_id, document_id, version_number, file_path, sha256_hash, created_by, created_at, change_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (f"{doc_id}-v1", doc_id, 1, file_path, sha256_hash, 'investigator', now.strftime('%Y-%m-%d %H:%M:%S'), 'Final Master Report Generated'))
else:
    cursor.execute(f"UPDATE document_versions SET sha256_hash='{sha256_hash}' WHERE document_id='{doc_id}'")

conn.commit()
conn.close()
print("Successfully generated mass data and master demo document.")
