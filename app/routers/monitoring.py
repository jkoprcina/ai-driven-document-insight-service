"""
Monitoring and metrics router.
"""
from fastapi import APIRouter, Request
from prometheus_client import REGISTRY
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get Prometheus metrics in text format."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    metrics = generate_latest(REGISTRY)
    return metrics.decode('utf-8')

@router.get("/health/detailed")
async def health_detailed(request: Request):
    """Get detailed health information."""
    app = request.app
    
    return {
        "status": "healthy",
        "components": {
            "cache": {
                "type": "redis" if app.state.cache.use_redis else "in-memory",
                "connected": True
            },
            "models": {
                "qa": "distilbert-base-cased-distilled-squad",
                "ner": "en_core_web_sm",
                "embedding": "all-MiniLM-L6-v2"
            },
            "gpu": {
                "enabled": app.state.settings.use_gpu,
                "device": app.state.settings.gpu_device if app.state.settings.use_gpu else None
            }
        },
        "version": app.state.settings.api_version
    }

@router.get("/cache/stats")
async def get_cache_stats(request: Request):
    """Get cache statistics."""
    app = request.app
    stats = app.state.cache.get_stats()
    return stats

@router.get("/sessions/count")
async def get_sessions_count(request: Request):
    """Get number of active sessions."""
    app = request.app
    sessions = app.state.session_storage.sessions
    return {
        "active_sessions": len(sessions),
        "sessions": list(sessions.keys())
    }

@router.get("/models/status")
async def get_models_status(request: Request):
    """Get status of loaded models."""
    app = request.app
    
    return {
        "models": {
            "qa": {
                "loaded": app.state.settings.qa_model,
                "type": "DistilBERT (Extractive QA)"
            },
            "ner": {
                "loaded": app.state.settings.ner_model,
                "type": "spaCy NER",
                "labels": app.state.ner.get_entity_labels()
            },
            "embedding": {
                "loaded": app.state.settings.embedding_model,
                "type": "Sentence Transformer"
            },
            "cache": {
                "type": app.state.cache.use_redis and "Redis" or "In-Memory"
            }
        }
    }
