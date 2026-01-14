"""
FastAPI dependencies for authentication, validation, and services.
"""
from fastapi import Depends, HTTPException, status, Header, Request
from typing import Optional
from app.services.monitoring import LoggingManager

logger = LoggingManager.get_logger(__name__)

async def verify_token(
    authorization: Optional[str] = Header(None),
    request: Request = None
) -> dict:
    """
    Verify JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    security_manager = request.app.state.security_manager
    payload = security_manager.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

async def get_current_user(
    token_data: dict = Depends(verify_token)
) -> str:
    """
    Get current user from token.
    
    Args:
        token_data: Token payload
        
    Returns:
        User ID
    """
    username: str = token_data.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return username

async def optional_auth(
    authorization: Optional[str] = Header(None),
    request: Request = None
) -> Optional[dict]:
    """
    Optional authentication (for public endpoints with auth support).
    
    Args:
        authorization: Authorization header value
        request: FastAPI request
        
    Returns:
        Token payload or None
    """
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        security_manager = request.app.state.security_manager
        return security_manager.verify_token(token)
    except Exception:
        return None

def rate_limit_key(request) -> str:
    """Generate rate limit key from request."""
    return request.client.host if request.client else "unknown"
