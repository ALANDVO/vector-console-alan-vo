from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.models.diagram import AdvisoryRequest, AdvisoryResponse
from app.core.auth import get_current_user
from app.services.llm_client import LLMClient

router = APIRouter(prefix="/api/llm", tags=["llm"])

@router.post("/advisory", response_model=AdvisoryResponse)
async def get_diagram_advisory(req: AdvisoryRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Provides advisory, grounded design and layout critique for diagrams."""
    return await LLMClient.generate_advisory(req)
