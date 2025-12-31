"""
Test the Auth0 integration with backend authentication.

This test verifies that the auth.py module correctly handles both Auth0 tokens
and legacy JWT tokens for backward compatibility.
"""

import jwt
import pytest
from fastapi import HTTPException

from app.auth import verify_auth0_token, verify_jwt_token, verify_legacy_jwt_token
from app.config import config


def test_legacy_jwt_token_verification():
    """Test that legacy JWT tokens are still verified correctly."""
    # Create a test JWT token
    test_payload = {"sub": "test_user", "role": "admin"}
    test_token = jwt.encode(test_payload, config.JWT_SECRET, algorithm="HS256")

    # Verify the token
    payload = verify_legacy_jwt_token(test_token)
    assert payload["sub"] == "test_user"
    assert payload["role"] == "admin"


def test_invalid_legacy_jwt_token():
    """Test that invalid legacy JWT tokens are rejected."""
    invalid_token = "invalid.token.here"

    with pytest.raises(HTTPException) as exc_info:
        verify_legacy_jwt_token(invalid_token)

    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


def test_verify_jwt_token_with_legacy_token():
    """Test that verify_jwt_token works with legacy tokens."""
    # Create a test JWT token
    test_payload = {"sub": "test_user"}
    test_token = jwt.encode(test_payload, config.JWT_SECRET, algorithm="HS256")

    # Verify using the main verify_jwt_token function with Bearer header
    authorization_header = f"Bearer {test_token}"
    payload = verify_jwt_token(authorization_header)
    assert payload["sub"] == "test_user"


def test_verify_jwt_token_missing_header():
    """Test that missing authorization header is rejected."""
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(None)

    assert exc_info.value.status_code == 401
    assert "Authorization header missing" in exc_info.value.detail


def test_verify_jwt_token_invalid_format():
    """Test that invalid authorization header format is rejected."""
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token("InvalidFormat token")

    assert exc_info.value.status_code == 401
    assert "Invalid token format" in exc_info.value.detail


def test_verify_jwt_token_no_token():
    """Test that Bearer header without token is rejected."""
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token("Bearer")

    assert exc_info.value.status_code == 401
    assert "Invalid token format" in exc_info.value.detail


def test_auth0_token_verification_without_config():
    """Test that Auth0 verification fails gracefully when not configured."""
    # This test assumes Auth0 is not configured in the test environment
    # If Auth0 is configured, the test would need to be adjusted
    
    # Create a mock Auth0-like token (it will fail verification)
    mock_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRlc3Qta2lkIn0.eyJzdWIiOiJ0ZXN0In0.test"
    
    # If Auth0 is not configured, it should fall back to legacy JWT
    # and fail there as well (since the token is not a valid legacy JWT)
    with pytest.raises(HTTPException):
        verify_jwt_token(f"Bearer {mock_token}")
