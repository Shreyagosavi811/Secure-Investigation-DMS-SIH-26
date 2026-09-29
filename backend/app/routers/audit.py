from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models import User, AuditEvent

router = APIRouter(
    prefix="/api/audit",
    tags=["Audit"],
)

@router.get("/")
def get_audit_trail(
    current_user: User = Depends(require_role(["Admin", "Senior Officer"])),
    db: Session = Depends(get_db),
    action: str = Query(None),
    username: str = Query(None),
    case_id: str = Query(None),
    limit: int = Query(50, le=200),
    offset: int = 0
):
    query = db.query(AuditEvent)
    if action:
        query = query.filter(AuditEvent.action == action)
    if username:
        query = query.filter(AuditEvent.username == username)
    if case_id:
        query = query.filter(AuditEvent.case_id == case_id)
        
    total = query.count()
    events = query.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "events": [
            {
                "id": e.id,
                "timestamp": e.timestamp,
                "username": e.username,
                "role": e.role,
                "action": e.action,
                "document_id": e.document_id,
                "case_id": e.case_id,
                "version": e.version,
                "result": e.result
            } for e in events
        ]
    }
