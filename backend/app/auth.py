# app/core/security.py
import jwt
import requests
from fastapi import Header, HTTPException, status
from jose import jwt as jose_jwt
from jose.exceptions import JWTError

from app.config import config

# Cache for JWKS to avoid fetching on every request
_jwks_cache = {"data": None, "timestamp": 0}
JWKS_CACHE_DURATION = 3600  # Cache for 1 hour


def get_jwks(domain: str):
    """
    Fetch JWKS from Auth0, with caching to avoid rate limiting.
    Cache is valid for 1 hour.
    """
    import time
    
    current_time = time.time()
    
    # Return cached data if still valid
    if _jwks_cache["data"] and (current_time - _jwks_cache["timestamp"]) < JWKS_CACHE_DURATION:
        return _jwks_cache["data"]
    
    # Fetch new JWKS
    jwks_url = f"https://{domain}/.well-known/jwks.json"
    try:
        jwks_response = requests.get(jwks_url, timeout=10)
        jwks_response.raise_for_status()  # Raise exception for bad status codes
        jwks = jwks_response.json()
        
        # Update cache
        _jwks_cache["data"] = jwks
        _jwks_cache["timestamp"] = current_time
        
        return jwks
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to fetch JWKS from Auth0: {str(e)}",
        ) from e


def verify_auth0_token(token: str):
    """
    Verify an Auth0 JWT token.
    
    This function:
    1. Fetches the JWKS from Auth0 (with caching)
    2. Verifies the token signature
    3. Validates the token claims (audience, issuer)
    
    Returns the decoded payload if valid, raises HTTPException otherwise.
    """
    if not config.AUTH0_DOMAIN or not config.AUTH0_AUDIENCE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth0 configuration missing",
        )
    
    issuer = f"https://{config.AUTH0_DOMAIN}/"
    
    try:
        # Decode without verification to get the key ID
        unverified_header = jose_jwt.get_unverified_header(token)
        
        # Get JWKS from Auth0 (with caching)
        jwks = get_jwks(config.AUTH0_DOMAIN)
        
        # Find the key that matches the token's kid
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break
        
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key",
            )
        
        # Verify and decode the token
        payload = jose_jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=config.AUTH0_AUDIENCE,
            issuer=issuer,
        )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 token",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
        ) from e


def verify_legacy_jwt_token(token: str):
    """
    Verify a legacy JWT token using the JWT_SECRET.
    
    This is the original verification method for backward compatibility.
    """
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


def verify_jwt_token(authorization: str = Header(None)):
    """
    This function checks for an Authorization header of the form:
      Authorization: Bearer <JWT>

    1. If the header is missing or doesn't start with "Bearer", raise 401.
    2. Try to verify the token as an Auth0 token first (if Auth0 is configured).
    3. If Auth0 verification fails or is not configured, fall back to legacy JWT verification.
    4. If both fail, raise 401.
    
    Returns the decoded payload.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    # Typically "Bearer <token>"
    parts = authorization.split()
    if parts[0].lower() != "bearer" or len(parts) == 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format. Use 'Bearer <token>'.",
        )

    token = parts[1]
    
    # Try Auth0 verification first if configured
    if config.AUTH0_DOMAIN and config.AUTH0_AUDIENCE:
        try:
            payload = verify_auth0_token(token)
            return payload
        except HTTPException:
            # If Auth0 verification fails, try legacy JWT
            pass
    
    # Fall back to legacy JWT verification
    return verify_legacy_jwt_token(token)
