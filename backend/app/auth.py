# app/core/security.py
import jwt
from fastapi import Header, HTTPException, status
from app.config import config

def verify_jwt_token(authorization: str = Header(None)):
    """
    This function checks for an Authorization header of the form:
      Authorization: Bearer <JWT>

    1. If the header is missing or doesn't start with "Bearer", raise 401.
    2. If the token fails to decode with our secret, raise 401.
    3. Otherwise, return the decoded payload (or True).
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

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        # Optionally check payload claims here if desired
        # e.g. check if "sub" in payload or "role" in payload

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return True  # or return payload if you need user info
