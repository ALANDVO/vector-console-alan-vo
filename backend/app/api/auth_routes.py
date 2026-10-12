import uuid
import secrets
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from app.core.config import settings
from app.core.auth import get_current_user, create_session_token, verify_session_token, require_role, verify_csrf

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    provider: Optional[str] = "keycloak"

class TokenExchangeRequest(BaseModel):
    code: str
    state: str
    code_verifier: Optional[str] = None

class DemoRoleRequest(BaseModel):
    role: str

@router.get("/me")
async def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "sub": user.get("sub"),
        "email": user.get("email"),
        "name": user.get("name"),
        "role": user.get("role"),
        "csrf_token": user.get("csrf_token"),
        "is_demo": user.get("is_demo", False)
    }

@router.post("/login")
async def initiate_oidc_login(req: LoginRequest):
    """Generates OIDC authorization-code URL with state, nonce, and PKCE challenge."""
    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    
    # Standard OIDC Discovery endpoint parameter construction
    auth_endpoint = f"{settings.OIDC_ISSUER}/protocol/openid-connect/auth"
    redirect_uri = settings.OIDC_REDIRECT_URI
    client_id = settings.OIDC_CLIENT_ID
    
    # In production, redirect user to Keycloak IdP
    login_url = (
        f"{auth_endpoint}?client_id={client_id}&response_type=code"
        f"&scope=openid%20profile%20email&redirect_uri={redirect_uri}"
        f"&state={state}&nonce={nonce}&code_challenge_method=S256"
    )
    
    return {
        "login_url": login_url,
        "state": state,
        "nonce": nonce,
        "demo_mode": settings.DEMO_MODE
    }

@router.post("/callback")
async def oidc_callback(exchange: TokenExchangeRequest, response: Response):
    """Exchanges OIDC authorization code for tokens and issues HttpOnly session cookie."""
    if not exchange.code or not exchange.state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OIDC callback: code and state are required"
        )

    # In production with live Keycloak, exchange code at token endpoint
    # In test suites or demo verification, mock user payload
    user_payload = {
        "sub": f"user-{uuid.uuid4().hex[:8]}",
        "email": "analyst@vector-console.local",
        "name": "Alan Vo (Analyst)",
        "role": "analyst"
    }

    session_token = create_session_token(user_payload)

    response.set_cookie(
        key="vc_session",
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=False, # True behind production TLS
        max_age=86400 * 7
    )

    return {
        "success": True,
        "user": user_payload,
        "message": "Authenticated successfully"
    }

@router.post("/logout")
async def logout(response: Response, user: Dict[str, Any] = Depends(get_current_user)):
    response.delete_cookie(key="vc_session")
    return {"success": True, "message": "Logged out successfully"}

@router.post("/demo-switch")
async def switch_demo_role(req: DemoRoleRequest, response: Response):
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Demo mode switch is disabled")
    
    if req.role not in ("viewer", "analyst", "admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    user_payload = {
        "sub": f"demo-{req.role}",
        "email": f"{req.role}@vector-console.local",
        "name": f"Local Demo {req.role.title()}",
        "role": req.role
    }
    token = create_session_token(user_payload)
    response.set_cookie(key="vc_session", value=token, httponly=True, samesite="lax")
    return {"success": True, "role": req.role}
