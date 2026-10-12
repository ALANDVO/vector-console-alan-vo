import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db, AuditRecord
from app.core.auth import get_current_user, require_role

router = APIRouter(prefix="/api/audit", tags=["audit"])

class AuditItem(BaseModel):
    id: str
    timestamp: str
    actor: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]

@router.get("", response_model=List[AuditItem])
async def list_audit_logs(
    action: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(require_role("analyst"))
):
    """Retrieves immutable audit trail of mutating events and evaluations."""
    query = db.query(AuditRecord)
    if action:
        query = query.filter(AuditRecord.action == action)
    records = query.order_by(AuditRecord.timestamp.desc()).offset(offset).limit(limit).all()

    return [
        AuditItem(
            id=r.id,
            timestamp=r.timestamp.isoformat(),
            actor=r.actor,
            action=r.action,
            resource_type=r.resource_type,
            resource_id=r.resource_id,
            details=json.loads(r.details_json)
        )
        for r in records
    ]
