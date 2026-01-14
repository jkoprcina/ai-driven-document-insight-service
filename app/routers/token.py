"""
Token generation router for development/demo purposes.
Provides simple token generation without authentication.
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


@router.post("/token", response_model=TokenResponse)
async def get_token(request: Request):
    """
    Get a JWT token for API access (development/demo only).
    
    This endpoint is for development and demo purposes.
    In production, implement proper user authentication.
    
    Returns:
        Token response with access_token and token_type
    """
    security_manager = request.app.state.security_manager
    
    # Create a token with a generic "demo" user
    token = security_manager.create_access_token(
        data={"sub": "demo_user"},
        expires_delta=None  # Default expiry from config
    )
    
    logger.info("Demo token generated")
    
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )
