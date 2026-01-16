"""
Document QA REST API with RAG, NER, and Advanced Security - Main Application
Allows users to upload documents, extract entities, and ask questions with semantic search.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import logging.config

from app.routers import documents, qa, token, monitoring
from app.services.storage import SessionStorage
from app.services.security import SecurityManager
from app.services.monitoring import LoggingManager
from app.services.ner import EntityRecognizer
from app.services.rag import RAGEngine
from app.services.cache import CacheManager
from app.config import get_settings
from app.middleware import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    InputValidationMiddleware,
    limiter
)

# Get settings
settings = get_settings()

# Validate SECRET_KEY is set and not default
if not settings.secret_key:
    raise ValueError("CRITICAL: SECRET_KEY environment variable must be set")

# Configure logging
LoggingManager.configure_logging(
    log_level=settings.log_level,
    log_file=settings.log_file
)
logger = LoggingManager.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add state
app.state.session_storage = SessionStorage()
app.state.security_manager = SecurityManager(secret_key=settings.secret_key)

# NER is optional - skip if model not available
try:
    app.state.ner = EntityRecognizer(model=settings.ner_model)
except Exception as e:
    logger.warning(f"NER service unavailable: {e}. Continuing without NER.")
    app.state.ner = None

# RAG is optional - skip if model not available
try:
    app.state.rag = RAGEngine(model_name=settings.embedding_model)
except Exception as e:
    logger.warning(f"RAG service unavailable: {e}. Continuing without RAG.")
    app.state.rag = None

# Cache manager - can run without Redis
try:
    app.state.cache = CacheManager(redis_url=settings.redis_url, ttl=settings.redis_ttl)
    # Pass cache manager to RAG engine if RAG is available
    if app.state.rag:
        app.state.rag.cache_manager = app.state.cache
except Exception as e:
    logger.warning(f"Cache service unavailable: {e}. Continuing without caching.")
    app.state.cache = None
app.state.settings = settings

# Add middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(InputValidationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(429, lambda r, e: JSONResponse(
    status_code=429,
    content={"detail": "Rate limit exceeded"}
))

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(token.router, prefix="/api/v1", tags=["Token"])
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])
app.include_router(qa.router, prefix="/api/v1", tags=["QA"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["Monitoring"]) 

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.api_version}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "endpoints": {
            "docs": "/api/docs",
            "redoc": "/api/redoc",
            "metrics": "/metrics",
            "health": "/health",
            "upload": "POST /api/v1/upload",
            "ask": "POST /api/v1/ask",
            "ask_detailed": "POST /api/v1/ask-detailed"
        }
    }

@app.on_event("startup")
async def startup():
    """Startup event."""
    logger.info("Application startup", extra={
        "version": settings.api_version,
        "debug": settings.debug,
        "gpu_enabled": settings.use_gpu
    })

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event."""
    logger.info("Application shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
