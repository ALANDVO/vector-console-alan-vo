import re
import secrets
import time
from typing import Optional, Dict, Any, List
from fastapi import Request, HTTPException, status, Depends
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.core.config import settings

# Enforce production security safeguard: refuse demo mode in production
if settings.ENVIRONMENT.lower() == "production" and settings.DEMO_MODE:
    raise RuntimeError("Security Violation: DEMO_MODE is strictly forbidden in production environment")

serializer = URLSafeTimedSerializer(settings.SESSION_SECRET, salt="vector-console-session")

ROLE_HIERARCHY = {
    "viewer": 1,
    "analyst": 2,
    "admin": 3
}

def redact_secrets(text: str) -> str:
    """Redacts synthetic and real sensitive tokens and keys from log strings and error messages."""
    if not text:
        return ""
    # Mask bearer tokens, API keys, credentials
    text = re.sub(r'Bearer\s+[A-Za-z0-9\-_\.]+', 'Bearer [REDACTED]', text)
    text = re.sub(r'(?:api[_-]?key|secret|token|password)=["\']?[A-Za-z0-9\-_\.]+["\']?', 'token=[REDACTED]', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,})\b', '[REDACTED]', text)
    return text

def create_session_token(user_data: Dict[str, Any]) -> str:
    payload = {
        "sub": user_data["sub"],
        "email": user_data.get("email", ""),
        "role": user_data.get("role", "viewer"),
        "name": user_data.get("name", "User"),
        "created_at": time.time(),
        "csrf_token": secrets.token_hex(16)
    }
    return serializer.dumps(payload)

def verify_session_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        data = serializer.loads(token, max_age=86400 * 7) # 7 days
        return data
    except (BadSignature, SignatureExpired):
        return None

async def get_current_user(request: Request) -> Dict[str, Any]:
    session_cookie = request.cookies.get("vc_session")
    auth_header = request.headers.get("Authorization")
    
    # 1. Check session cookie
    if session_cookie:
        payload = verify_session_token(session_cookie)
        if payload:
            return payload

    # 2. Check Bearer token (for API tokens / test suites)
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        payload = verify_session_token(token)
        if payload:
            return payload

    # 3. Local Demo Mode fallback (if explicitly enabled)
    if settings.DEMO_MODE:
        # Provide demo analyst role with synthetic CSRF token
        demo_role = request.headers.get("X-Demo-Role", "analyst")
        if demo_role not in ROLE_HIERARCHY:
            demo_role = "analyst"
        return {
            "sub": "demo-analyst-local",
            "email": "demo@vector-console.local",
            "role": demo_role,
            "name": f"Local Demo {demo_role.title()}",
            "csrf_token": "demo-csrf-token-local",
            "is_demo": True
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please authenticate via Keycloak OIDC or activate local demo mode."
    )

def require_role(min_role: str):
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = user.get("role", "viewer")
        user_weight = ROLE_HIERARCHY.get(user_role, 0)
        required_weight = ROLE_HIERARCHY.get(min_role, 999)
        if user_weight < required_weight:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires at least '{min_role}' role (current role: '{user_role}')."
            )
        return user
    return role_checker

def verify_csrf(request: Request, user: Dict[str, Any]):
    """Enforces CSRF token check for state-changing operations when using session cookies."""
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        if user.get("is_demo"):
            return
        csrf_header = request.headers.get("X-CSRF-Token")
        expected_csrf = user.get("csrf_token")
        if not csrf_header or csrf_header != expected_csrf:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF validation failed: missing or invalid X-CSRF-Token header"
            )
