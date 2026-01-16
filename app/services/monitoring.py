"""
Structured logging and monitoring service with Prometheus metrics.
"""
import logging
import structlog
import sys
from logging.handlers import RotatingFileHandler
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any
import time

# Prometheus metrics
request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_latency = Histogram(
    'api_request_latency_seconds',
    'API request latency',
    ['method', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

model_inference_time = Histogram(
    'model_inference_seconds',
    'Model inference time',
    ['model_type'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active sessions'
)

cached_items = Gauge(
    'cached_items_total',
    'Total cached items'
)

class LoggingManager:
    """Manage structured logging across the application."""
    
    @staticmethod
    def configure_logging(
        log_level: str = "INFO",
        log_file: str = "logs/app.log"
    ):
        """
        Configure structured logging.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Path to log file
        """
        # Create logs directory if needed
        import os
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure standard logging
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        root_logger.addHandler(file_handler)
    
    @staticmethod
    def get_logger(name: str):
        """Get logger instance."""
        return structlog.get_logger(name)

class MonitoringContext:
    """Context manager for monitoring API requests."""
    
    def __init__(self, method: str, endpoint: str):
        """
        Initialize monitoring context.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
        """
        self.method = method
        self.endpoint = endpoint
        self.start_time = None
        self.logger = LoggingManager.get_logger(__name__)
    
    def __enter__(self):
        """Enter context."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and record metrics."""
        duration = time.time() - self.start_time
        
        status = "error" if exc_type else "success"
        request_count.labels(
            method=self.method,
            endpoint=self.endpoint,
            status=status
        ).inc()
        
        request_latency.labels(
            method=self.method,
            endpoint=self.endpoint
        ).observe(duration)
        
        self.logger.info(
            "api_request",
            method=self.method,
            endpoint=self.endpoint,
            duration=duration,
            status=status
        )
        
        return False

class ModelProfiler:
    """Profile model inference latency."""
    
    def __init__(self, model_type: str):
        """
        Initialize profiler.
        
        Args:
            model_type: Type of model (qa, ner, embedding, etc.)
        """
        self.model_type = model_type
        self.start_time = None
        self.logger = LoggingManager.get_logger(__name__)
    
    def __enter__(self):
        """Enter context."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and record metrics."""
        duration = time.time() - self.start_time
        
        model_inference_time.labels(
            model_type=self.model_type
        ).observe(duration)
        
        self.logger.info(
            "model_inference",
            model_type=self.model_type,
            duration=duration
        )
        
        return False

class PerformanceProfiler:
    """Profile overall API performance."""
    
    def __init__(self):
        """Initialize performance profiler."""
        self.profiles = {}
    
    def start(self, operation: str):
        """Start profiling an operation."""
        self.profiles[operation] = time.time()
    
    def end(self, operation: str) -> float:
        """
        End profiling and return duration.
        
        Args:
            operation: Operation name
            
        Returns:
            Duration in seconds
        """
        if operation not in self.profiles:
            return 0.0
        
        duration = time.time() - self.profiles[operation]
        del self.profiles[operation]
        return duration
    
    def get_report(self) -> Dict[str, Any]:
        """Get profiling report."""
        return {
            "active_operations": list(self.profiles.keys()),
            "active_count": len(self.profiles)
        }
