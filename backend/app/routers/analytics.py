from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Case, Document, AuditEvent

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)

@router.get("/summary")
def get_analytics_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Analytics access requires admin role")
        
    total_cases = db.query(Case).count()
    total_documents = db.query(Document).count()
    
    # Action breakdown
    action_counts = db.query(AuditEvent.action, func.count(AuditEvent.id)).group_by(AuditEvent.action).all()
    action_data = [{"name": a[0], "value": a[1]} for a in action_counts]
    
    # Tamper events
    tamper_events = db.query(AuditEvent).filter(AuditEvent.result == "TAMPER_DETECTED").count()
    verified_events = db.query(AuditEvent).filter(AuditEvent.result == "INTEGRITY_VERIFIED").count()
    
    integrity_data = [
        {"name": "Verified", "value": verified_events},
        {"name": "Tamper Detected", "value": tamper_events}
    ]
    
    return {
        "summary": {
            "total_cases": total_cases,
            "total_documents": total_documents,
            "tamper_alerts": tamper_events
        },
        "activity_breakdown": action_data,
        "integrity_stats": integrity_data
    }
