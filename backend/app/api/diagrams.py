import uuid
import json
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status, Request
from sqlalchemy.orm import Session
from app.models.diagram import DiagramSpec, DiagramResponse, DiagramListSummary
from app.models.database import get_db, DiagramRecord, log_audit
from app.core.auth import get_current_user, require_role, verify_csrf
from app.services.vector_engine import VectorEngine
from app.services.linter import DiagramLinter

router = APIRouter(prefix="/api/diagrams", tags=["diagrams"])

@router.post("/compile")
async def compile_diagram_spec(spec: DiagramSpec, user: Dict[str, Any] = Depends(get_current_user)):
    """Stateless compilation of DiagramSpec into editorial SVG and HTML document."""
    svg, html_doc = VectorEngine.compile(spec)
    report = DiagramLinter.lint_svg(svg)
    return {
        "svg": svg,
        "html": html_doc,
        "lint_report": report
    }

@router.get("", response_model=List[DiagramListSummary])
async def list_diagrams(
    diagram_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    query = db.query(DiagramRecord)
    if diagram_type:
        query = query.filter(DiagramRecord.diagram_type == diagram_type)
    if search:
        query = query.filter(DiagramRecord.title.ilike(f"%{search}%"))

    records = query.order_by(DiagramRecord.updated_at.desc()).offset(offset).limit(limit).all()
    return [
        DiagramListSummary(
            id=r.id,
            title=r.title,
            diagram_type=r.diagram_type,
            created_at=r.created_at.isoformat(),
            created_by=r.created_by
        )
        for r in records
    ]

@router.post("", response_model=DiagramResponse)
async def create_diagram(
    request: Request,
    spec: DiagramSpec,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(require_role("analyst"))
):
    verify_csrf(request, user)
    diag_id = str(uuid.uuid4())
    svg, html_doc = VectorEngine.compile(spec)
    now = datetime.datetime.now(datetime.timezone.utc)

    record = DiagramRecord(
        id=diag_id,
        title=spec.title,
        diagram_type=spec.diagram_type.value,
        spec_json=json.dumps(spec.model_dump()),
        svg_content=svg,
        html_content=html_doc,
        created_by=user.get("email", "unknown"),
        created_at=now,
        updated_at=now
    )
    db.add(record)
    db.commit()

    log_audit(db, user.get("email", "unknown"), "CREATE", "diagram", diag_id, {"title": spec.title})

    return DiagramResponse(
        id=record.id,
        title=record.title,
        diagram_type=record.diagram_type,
        spec=spec,
        svg_content=record.svg_content,
        html_content=record.html_content,
        created_at=record.created_at.isoformat(),
        updated_at=record.updated_at.isoformat(),
        created_by=record.created_by
    )

@router.get("/{diag_id}", response_model=DiagramResponse)
async def get_diagram(
    diag_id: str,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    record = db.query(DiagramRecord).filter(DiagramRecord.id == diag_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagram not found")

    spec_dict = json.loads(record.spec_json)
    spec = DiagramSpec(**spec_dict)

    return DiagramResponse(
        id=record.id,
        title=record.title,
        diagram_type=record.diagram_type,
        spec=spec,
        svg_content=record.svg_content,
        html_content=record.html_content,
        created_at=record.created_at.isoformat(),
        updated_at=record.updated_at.isoformat(),
        created_by=record.created_by
    )

@router.put("/{diag_id}", response_model=DiagramResponse)
async def update_diagram(
    request: Request,
    diag_id: str,
    spec: DiagramSpec,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(require_role("analyst"))
):
    verify_csrf(request, user)
    record = db.query(DiagramRecord).filter(DiagramRecord.id == diag_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagram not found")

    svg, html_doc = VectorEngine.compile(spec)
    now = datetime.datetime.now(datetime.timezone.utc)

    record.title = spec.title
    record.diagram_type = spec.diagram_type.value
    record.spec_json = json.dumps(spec.model_dump())
    record.svg_content = svg
    record.html_content = html_doc
    record.updated_at = now
    db.commit()

    log_audit(db, user.get("email", "unknown"), "UPDATE", "diagram", diag_id, {"title": spec.title})

    return DiagramResponse(
        id=record.id,
        title=record.title,
        diagram_type=record.diagram_type,
        spec=spec,
        svg_content=record.svg_content,
        html_content=record.html_content,
        created_at=record.created_at.isoformat(),
        updated_at=record.updated_at.isoformat(),
        created_by=record.created_by
    )

@router.delete("/{diag_id}")
async def delete_diagram(
    request: Request,
    diag_id: str,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(require_role("admin"))
):
    verify_csrf(request, user)
    record = db.query(DiagramRecord).filter(DiagramRecord.id == diag_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagram not found")

    db.delete(record)
    db.commit()
    log_audit(db, user.get("email", "unknown"), "DELETE", "diagram", diag_id, {})
    return {"success": True, "message": "Diagram deleted"}

@router.get("/{diag_id}/export/{export_format}")
async def export_diagram(
    diag_id: str,
    export_format: str,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    record = db.query(DiagramRecord).filter(DiagramRecord.id == diag_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagram not found")

    if export_format.lower() == "svg":
        return Response(
            content=record.svg_content,
            media_type="image/svg+xml",
            headers={"Content-Disposition": f'attachment; filename="{record.title}.svg"'}
        )
    elif export_format.lower() == "html":
        return Response(
            content=record.html_content,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{record.title}.html"'}
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported export format (use svg or html)")
