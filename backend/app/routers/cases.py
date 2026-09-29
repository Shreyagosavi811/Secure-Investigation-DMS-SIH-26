from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, get_authorized_cases, require_case_access
from app.models import User, Case

router = APIRouter(
    prefix="/api/cases",
    tags=["Cases"],
)

@router.get("/")
def list_cases(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    authorized_case_ids = get_authorized_cases(current_user, db)
    cases = db.query(Case).filter(Case.case_id.in_(authorized_case_ids)).all()
    return {"cases": [{"case_id": c.case_id, "title": c.title, "description": c.description, "classification": c.classification, "status": c.status} for c in cases]}

@router.get("/{case_id}")
def get_case(case_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_case_access(case_id, current_user, db)
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        "case_id": case.case_id,
        "title": case.title,
        "description": case.description,
        "classification": case.classification,
        "status": case.status,
        "created_at": case.created_at,
        "documents": [{"document_id": d.document_id, "title": d.title, "type": d.document_type} for d in case.documents]
    }
