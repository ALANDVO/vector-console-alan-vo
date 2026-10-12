from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.models.diagram import DiagramSpec, LintReport
from app.core.auth import get_current_user
from app.services.linter import DiagramLinter

router = APIRouter(prefix="/api/lint", tags=["lint"])

class LintSvgRequest(BaseModel):
    svg_content: str

@router.post("/svg", response_model=LintReport)
async def lint_svg_endpoint(req: LintSvgRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Lints raw SVG markup against editorial design rules, shadow prohibitions, and palettes."""
    return DiagramLinter.lint_svg(req.svg_content)

@router.post("/spec", response_model=LintReport)
async def lint_spec_endpoint(spec: DiagramSpec, user: Dict[str, Any] = Depends(get_current_user)):
    """Lints structural DiagramSpec for semantic containment and honest-data invariants."""
    return DiagramLinter.lint_spec(spec)
