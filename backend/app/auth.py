import logging

import jwt
from fastapi import Header, HTTPException, status
from jwt import PyJWKClient

from app.config import config

logger = logging.getLogger(__name__)

# PyJWKClient handles JWKS fetching, caching, and key lookup automatically
_jwks_client: PyJWKClient | None = None


def get_jwks_client() -> PyJWKClient:
    """Get or create PyJWKClient instance with caching."""
    global _jwks_client
    if _jwks_client is None:
        if not config.AUTH0_DOMAIN:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Auth0 not configured",
            )
        jwks_url = f"https://{config.AUTH0_DOMAIN}/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True)
    return _jwks_client


def verify_auth0_token(token: str) -> dict:
    """
    Verify an Auth0 JWT token.

    Uses PyJWKClient to automatically:
    - Fetch JWKS from Auth0 (with caching)
    - Find the correct signing key
    - Verify token signature and claims

    Returns the decoded payload if valid, raises HTTPException otherwise.
    """
    if not config.AUTH0_DOMAIN or not config.AUTH0_AUDIENCE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth0 configuration missing",
        )

    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=config.AUTH0_AUDIENCE,
            issuer=f"https://{config.AUTH0_DOMAIN}/",
        )

        return payload

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
        ) from e


def verify_frontend_request(x_api_key: str = Header(None, alias="X-API-Key")):
    """
    Verify that the request comes from the authorized frontend.

    Checks for X-API-Key header matching the configured API_KEY.
    This is a simple shared secret between frontend and backend to prevent
    direct API access from unauthorized clients.

    Required for all API requests.
    """
    if not config.API_KEY:
        # If not configured, allow all requests (development mode)
        logger.warning("API_KEY not configured - allowing all requests")
        return True

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key required",
        )

    if x_api_key != config.API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return True


def require_user(authorization: str = Header(None)) -> dict:
    """
    Required user authentication via Auth0.

    Returns user payload if valid Auth0 token is provided.
    Raises 401 if token is missing or invalid.

    Use this for endpoints that require user authentication
    (e.g., user profile, saved searches, admin functions).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    parts = authorization.split()
    if parts[0].lower() != "bearer" or len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format. Use 'Bearer <token>'",
        )

    token = parts[1]

    if not config.AUTH0_DOMAIN or not config.AUTH0_AUDIENCE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication not configured",
        )

    return verify_auth0_token(token)
