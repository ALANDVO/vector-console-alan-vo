import pytest
from app.core.auth import redact_secrets, create_session_token, verify_session_token, require_role, ROLE_HIERARCHY

def test_secret_redaction_with_synthetic_tokens():
    # Generate synthetic values strictly at runtime (zero characters)
    synthetic_gh = "ghp_" + ("0" * 32)
    synthetic_sk = "sk-" + ("0" * 32)

    sample_log = f"Error communicating with provider using Bearer {synthetic_gh} and key {synthetic_sk}"
    redacted = redact_secrets(sample_log)
    assert synthetic_gh not in redacted
    assert synthetic_sk not in redacted
    assert "[REDACTED]" in redacted

def test_session_token_roundtrip():
    user_data = {
        "sub": "user-42",
        "email": "test@vector-console.local",
        "role": "analyst",
        "name": "Test Analyst"
    }
    token = create_session_token(user_data)
    assert isinstance(token, str)
    payload = verify_session_token(token)
    assert payload is not None
    assert payload["sub"] == "user-42"
    assert payload["role"] == "analyst"
    assert "csrf_token" in payload

def test_role_hierarchy_weights():
    assert ROLE_HIERARCHY["admin"] > ROLE_HIERARCHY["analyst"]
    assert ROLE_HIERARCHY["analyst"] > ROLE_HIERARCHY["viewer"]
