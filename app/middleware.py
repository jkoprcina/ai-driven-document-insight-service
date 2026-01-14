"""
Middleware for security, rate limiting, and monitoring.
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import time
from typing import Callable

logger = logging.getLogger(__name__)

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Add security headers."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Log request/response."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} ({duration:.3f}s)",
                extra={
                    "status_code": response.status_code,
                    "duration": duration,
                    "path": request.url.path
                }
            )
            
            # Add custom header
            response.headers["X-Process-Time"] = str(duration)
            
            return response
        
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize inputs."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Validate inputs."""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 100 * 1024 * 1024:  # 100MB limit
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request body too large"}
            )
        
        return await call_next(request)

class RateLimitExceptionHandler:
    """Handle rate limit exceptions."""
    
    @staticmethod
    def handle(request: Request, exc: RateLimitExceeded):
        """Handle rate limit exception."""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )
