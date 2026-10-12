import os
from pydantic import BaseModel

class Settings(BaseModel):
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vector_console.db")
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "dev-session-insecure-key-change-in-prod")
    
    # OIDC Configuration (Keycloak)
    OIDC_ISSUER: str = os.getenv("OIDC_ISSUER", "http://127.0.0.1:8080/realms/vector-console")
    OIDC_CLIENT_ID: str = os.getenv("OIDC_CLIENT_ID", "vector-console-client")
    OIDC_CLIENT_SECRET: str = os.getenv("OIDC_CLIENT_SECRET", "")
    OIDC_REDIRECT_URI: str = os.getenv("OIDC_REDIRECT_URI", "http://127.0.0.1:8000/api/auth/callback")
    
    # Advisory LLM Configuration (opt-in; keys server-side only)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai-compatible")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

settings = Settings()
