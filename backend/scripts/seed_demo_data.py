import os
import sys
import shutil
import hashlib
from datetime import datetime
import json
import random

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'investigation_dataset_engine')))

from app.database import engine, Base, SessionLocal
from app.models import User, Case, Document, DocumentVersion, CaseAccess
from app.auth import get_password_hash

# Set up storage
STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'storage')
if os.path.exists(STORAGE_DIR):
    shutil.rmtree(STORAGE_DIR)
os.makedirs(STORAGE_DIR)

def calculate_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def seed_db():
    print("Initializing Database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("Creating Users...")
    admin = User(username="admin", hashed_password=get_password_hash("admin123"), role="Admin", full_name="Admin User")
    so = User(username="officer", hashed_password=get_password_hash("officer123"), role="Senior Officer", full_name="Senior Officer Ramesh")
    inv = User(username="investigator", hashed_password=get_password_hash("investigator123"), role="Investigator", full_name="Investigator Suresh")
    
    db.add_all([admin, so, inv])
    db.commit()

    print("Creating Cases...")
    cases_data = [
        {"id": "CASE-2026-001", "title": "Operation Red Shadow", "desc": "Investigation into illegal arms smuggling network."},
        {"id": "CASE-2026-002", "title": "Cyber Fraud Syndicate", "desc": "Phishing and bank fraud across 3 states."},
        {"id": "CASE-2026-003", "title": "Narcotics Route Alpha", "desc": "Tracking contraband moving through port."},
        {"id": "CASE-2026-004", "title": "VIP Extortion", "desc": "High profile extortion case involving local politicians."} # Restricted
    ]
    
    for c in cases_data:
        case = Case(case_id=c["id"], title=c["title"], description=c["desc"], classification="CONFIDENTIAL", status="OPEN")
        db.add(case)
        os.makedirs(os.path.join(STORAGE_DIR, c["id"]))

    db.commit()

    print("Setting Permissions...")
    # Admin has all cases automatically
    # Senior Officer has 001, 002, 003, 004
    for c in cases_data:
        db.add(CaseAccess(user_id=so.id, case_id=c["id"]))
    
    # Investigator has 001, 002
    db.add(CaseAccess(user_id=inv.id, case_id="CASE-2026-001"))
    db.add(CaseAccess(user_id=inv.id, case_id="CASE-2026-002"))
    db.commit()

    print("Creating Documents...")
    qdrant_documents = []
    
    docs_per_case = 7
    doc_id_counter = 1
    
    for c in cases_data:
        case_id = c["id"]
        for i in range(1, docs_per_case + 1):
            doc_id = f"DOC-{case_id[-3:]}-{i:03d}"
            title = f"Investigation Report {i} for {case_id}"
            file_name = f"{doc_id}.txt"
            file_path = os.path.join(STORAGE_DIR, case_id, file_name)
            
            content = f"This is {title}.\nDetailed findings regarding the suspects and timeline of events in {case_id}."
            content_bytes = content.encode('utf-8')
            
            with open(file_path, "wb") as f:
                f.write(content_bytes)
                
            file_hash = calculate_sha256(content_bytes)
            
            doc = Document(
                document_id=doc_id,
                case_id=case_id,
                title=title,
                document_type="Investigation Report" if i % 2 == 0 else "FIR",
                classification="RESTRICTED" if i == 7 else "CONFIDENTIAL",
                owner="Admin",
                uploaded_by="Admin"
            )
            db.add(doc)
            db.commit() # commit to get doc in db
            
            # Create version
            v1 = DocumentVersion(
                version_id=f"V-{doc_id}-1",
                document_id=doc_id,
                version_number=1,
                file_path=file_path,
                sha256_hash=file_hash,
                created_by="Admin",
                change_description="Initial Upload"
            )
            db.add(v1)
            db.commit()

            qdrant_documents.append({
                "document_id": doc_id,
                "case_refs": [case_id],
                "source_record_id": doc_id,
                "source_type": "cctns_fir_records",
                "normalized_text": content
            })

    print("Mocking Qdrant index...")
    # Attempt to load QdrantClient
    try:
        from investigation_dataset_engine.rag.vectorstore.qdrant_client import QdrantEvidenceClient
        
        qc = QdrantEvidenceClient(path=os.path.join(os.path.dirname(__file__), '..', '..', 'investigation_dataset_engine', 'output', 'qdrant_storage'), collection_name="sih26189_evidence")
        qc.ensure_collection(vector_size=1024) # BGE-M3 dimension
        
        embeddings = [[random.random() for _ in range(1024)] for _ in range(len(qdrant_documents))]
        qc.upsert_batch(qdrant_documents, embeddings)
        print(f"Upserted {len(qdrant_documents)} mock vectors to Qdrant.")
        
        # Save corpus json for fallback
        corpus_path = os.path.join(os.path.dirname(__file__), '..', '..', 'investigation_dataset_engine', 'output', 'RAG_CORPUS')
        os.makedirs(corpus_path, exist_ok=True)
        with open(os.path.join(corpus_path, "corpus_small.jsonl"), "w") as f:
            for doc in qdrant_documents:
                f.write(json.dumps(doc) + "\n")
        
    except Exception as e:
        print(f"Skipping Qdrant actual indexing (using mock): {e}")

    print("Seed complete.")
    db.close()

if __name__ == "__main__":
    seed_db()
