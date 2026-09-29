from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, require_case_access
from app.models import User, Document, DocumentVersion, AuditEvent
import hashlib
import os

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)

def calculate_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def log_audit(db: Session, user: User, action: str, document_id: str = None, case_id: str = None, result: str = "SUCCESS", version: int = None):
    audit = AuditEvent(
        username=user.username,
        role=user.role,
        action=action,
        document_id=document_id,
        case_id=case_id,
        version=version,
        result=result
    )
    db.add(audit)
    db.commit()

@router.get("/{document_id}")
def get_document(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access
    try:
        require_case_access(doc.case_id, current_user, db)
    except HTTPException:
        log_audit(db, current_user, "VIEW_DOCUMENT", document_id, doc.case_id, "ACCESS_DENIED")
        raise
        
    log_audit(db, current_user, "VIEW_DOCUMENT", document_id, doc.case_id, "SUCCESS")
    
    versions = [{"version_id": v.version_id, "version_number": v.version_number, "created_at": v.created_at, "created_by": v.created_by, "sha256_hash": v.sha256_hash, "change_description": v.change_description} for v in doc.versions]
    return {
        "document_id": doc.document_id,
        "case_id": doc.case_id,
        "title": doc.title,
        "document_type": doc.document_type,
        "classification": doc.classification,
        "owner": doc.owner,
        "uploaded_by": doc.uploaded_by,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
        "versions": versions
    }

@router.get("/{document_id}/content")
def get_document_content(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access
    try:
        require_case_access(doc.case_id, current_user, db)
    except HTTPException:
        log_audit(db, current_user, "VIEW_CONTENT", document_id, doc.case_id, "ACCESS_DENIED")
        raise

    latest_version = doc.versions[0] if doc.versions else None
    if not latest_version:
        raise HTTPException(status_code=404, detail="No versions available for this document")

    if not os.path.exists(latest_version.file_path):
        raise HTTPException(status_code=404, detail="Document file not found on server")

    with open(latest_version.file_path, "r", encoding="utf-8") as f:
        content = f.read()

    log_audit(db, current_user, "VIEW_CONTENT", document_id, doc.case_id, "SUCCESS", latest_version.version_number)
    return {"content": content}

@router.post("/{document_id}/tamper")
def simulate_cyber_attack_tamper(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DEMO ONLY: Simulates a malicious file alteration to trigger integrity failure."""
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    latest_version = doc.versions[0] if doc.versions else None
    if not latest_version or not os.path.exists(latest_version.file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    # Read the file and inject a malicious string at the end
    with open(latest_version.file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    tampered_content = content + "\n\n[MALICIOUS INJECTION: EVIDENCE TAMPERED]"
    
    # Write back to disk without updating the SHA-256 hash in the database
    with open(latest_version.file_path, "w", encoding="utf-8") as f:
        f.write(tampered_content)
        
    log_audit(db, current_user, "SIMULATE_TAMPER", document_id, doc.case_id, "SUCCESS", latest_version.version_number)
    return {"status": "success", "message": "Document file tampered successfully"}

@router.get("/{document_id}/verify")
def verify_document_integrity(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access
    try:
        require_case_access(doc.case_id, current_user, db)
    except HTTPException:
        log_audit(db, current_user, "VERIFY_INTEGRITY", document_id, doc.case_id, "ACCESS_DENIED")
        raise

    latest_version = doc.versions[0] if doc.versions else None
    if not latest_version:
        return {"status": "NO_VERSIONS"}

    if not os.path.exists(latest_version.file_path):
        log_audit(db, current_user, "VERIFY_INTEGRITY", document_id, doc.case_id, "FILE_NOT_FOUND", latest_version.version_number)
        return {"status": "FILE_NOT_FOUND"}
    
    current_hash = calculate_sha256(latest_version.file_path)
    if current_hash == latest_version.sha256_hash:
        result = "INTEGRITY_VERIFIED"
    else:
        result = "TAMPER_DETECTED"
        
    log_audit(db, current_user, "VERIFY_INTEGRITY", document_id, doc.case_id, result, latest_version.version_number)
    
    return {
        "status": result,
        "expected_hash": latest_version.sha256_hash,
        "actual_hash": current_hash,
        "version_number": latest_version.version_number
    }

@router.post("/{document_id}/versions")
def create_document_version(
    document_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access
    try:
        require_case_access(doc.case_id, current_user, db)
    except HTTPException:
        log_audit(db, current_user, "UPLOAD_DOCUMENT", document_id, doc.case_id, "ACCESS_DENIED")
        raise
        
    content_bytes = file.file.read()
    file_hash = calculate_sha256_bytes(content_bytes)
    
    next_version_num = 1
    if doc.versions:
        next_version_num = doc.versions[0].version_number + 1
        
    version_id = f"V-{document_id}-{next_version_num}"
    
    import os
    STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'storage')
    file_name = f"{document_id}_v{next_version_num}.txt"
    file_path = os.path.join(STORAGE_DIR, doc.case_id, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(content_bytes)
        
    new_v = DocumentVersion(
        version_id=version_id,
        document_id=document_id,
        version_number=next_version_num,
        file_path=file_path,
        sha256_hash=file_hash,
        created_by=current_user.username,
        change_description=f"Uploaded {file.filename}"
    )
    db.add(new_v)
    db.commit()
    
    log_audit(db, current_user, "CREATE_VERSION", document_id, doc.case_id, "SUCCESS", next_version_num)
    
    return {"status": "SUCCESS", "version_id": version_id, "version_number": next_version_num}
