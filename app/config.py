"""
Configuration management for the application.
Handles environment variables and settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_title: str = "Document QA API"
    api_version: str = "1.0.0"
    api_description: str = "Advanced Document QA with RAG, NER, and Security"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="TOKEN_EXPIRE_MINUTES")
    
    # Rate Limiting
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    redis_ttl: int = Field(default=3600, env="REDIS_TTL")  # seconds
    
    # Model Configuration
    qa_model: str = Field(
        default="distilbert-base-cased-distilled-squad",
        env="QA_MODEL"
    )
    ner_model: str = Field(default="en_core_web_sm", env="NER_MODEL")
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL"
    )
    
    # GPU Configuration
    use_gpu: bool = Field(default=False, env="USE_GPU")
    gpu_device: int = Field(default=0, env="GPU_DEVICE")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    
    # RAG Configuration
    chunk_size: int = Field(default=500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    top_k_retrieval: int = Field(default=3, env="TOP_K_RETRIEVAL")
    
    # Context Configuration
    max_context_length: int = Field(default=2000, env="MAX_CONTEXT_LENGTH")
    min_chunk_length: int = Field(default=50, env="MIN_CHUNK_LENGTH")
    
    # Input Validation
    max_question_length: int = Field(default=1000, env="MAX_QUESTION_LENGTH")
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=8001, env="METRICS_PORT")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Environment presets
def get_dev_settings() -> Settings:
    """Get development settings."""
    settings = Settings()
    settings.debug = True
    settings.log_level = "DEBUG"
    settings.reload = True
    return settings

def get_prod_settings() -> Settings:
    """Get production settings."""
    settings = Settings()
    settings.debug = False
    settings.log_level = "WARNING"
    settings.reload = False
    settings.enable_rate_limiting = True
    return settings
