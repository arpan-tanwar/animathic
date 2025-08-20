"""
Production-ready configuration management for Animathic Backend
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Fallback for older versions
        BaseSettings = None

from pydantic import validator

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT.lower() == "production"
IS_DEVELOPMENT = ENVIRONMENT.lower() == "development"

class DatabaseConfig:
    """Database configuration"""
    def __init__(self):
        self.url = os.getenv("DATABASE_URL", "sqlite:///./animathic.db")
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))

class GoogleAIConfig:
    """Google AI configuration"""
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_AI_API_KEY", "")
        self.model = os.getenv("GOOGLE_AI_MODEL", "gemini-2.0-flash-exp")
        self.temperature = float(os.getenv("GOOGLE_AI_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("GOOGLE_AI_MAX_TOKENS", "4096"))
        self.top_p = float(os.getenv("GOOGLE_AI_TOP_P", "0.8"))
        self.top_k = int(os.getenv("GOOGLE_AI_TOP_K", "40"))
        self.confidence_threshold = float(os.getenv("GEMINI_CONFIDENCE_THRESHOLD", "0.7"))
        
        if not self.api_key and IS_PRODUCTION:
            raise ValueError("GOOGLE_AI_API_KEY is required in production")

class LocalLLMConfig:
    """Local LLM configuration"""
    def __init__(self):
        self.enabled = os.getenv("LOCAL_FALLBACK_ENABLED", "true").lower() == "true"
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "30"))

class MediaConfig:
    """Media handling configuration"""
    def __init__(self):
        self.base_dir = Path(os.getenv("MEDIA_BASE_DIR", "./media"))
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB
        self.cleanup_interval = int(os.getenv("CLEANUP_INTERVAL", "3600"))  # 1 hour
        self.retention_hours = int(os.getenv("RETENTION_HOURS", "24"))
        self.supported_formats = ["mp4", "gif", "png", "jpg", "jpeg"]

class SecurityConfig:
    """Security configuration"""
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        
        if self.secret_key == "dev-secret-key-change-in-production" and IS_PRODUCTION:
            raise ValueError("SECRET_KEY must be changed in production")

class RateLimitConfig:
    """Rate limiting configuration"""
    def __init__(self):
        self.enabled = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
        self.max_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
        self.window_minutes = int(os.getenv("RATE_LIMIT_WINDOW", "1"))

class MonitoringConfig:
    """Monitoring and logging configuration"""
    def __init__(self):
        self.log_level = os.getenv("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG")
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.enable_health_checks = os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true"
        self.metrics_port = int(os.getenv("METRICS_PORT", "9090"))

class FeatureFlags:
    """Feature flags configuration"""
    def __init__(self):
        self.enhanced_database = os.getenv("ENABLE_ENHANCED_DATABASE", "true").lower() == "true"
        self.ai_animations = os.getenv("ENABLE_AI_ANIMATIONS", "true").lower() == "true"
        self.user_management = os.getenv("ENABLE_USER_MANAGEMENT", "true").lower() == "true"
        self.file_upload = os.getenv("ENABLE_FILE_UPLOAD", "true").lower() == "true"
        self.hybrid_ai = os.getenv("ENABLE_HYBRID_AI", "true").lower() == "true"
        self.feedback_collection = os.getenv("ENABLE_FEEDBACK_COLLECTION", "true").lower() == "true"

class AppConfig:
    """Main application configuration"""
    def __init__(self):
        self.environment = ENVIRONMENT
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8080"))
        self.workers = int(os.getenv("WORKERS", "1"))
        
        # Sub-configurations
        self.database = DatabaseConfig()
        self.google_ai = GoogleAIConfig()
        self.local_llm = LocalLLMConfig()
        self.media = MediaConfig()
        self.security = SecurityConfig()
        self.rate_limit = RateLimitConfig()
        self.monitoring = MonitoringConfig()
        self.features = FeatureFlags()

# Global configuration instance
_config: Optional[AppConfig] = None

def get_config() -> AppConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config

def get_api_config() -> Dict[str, Any]:
    """Get API-specific configuration"""
    config = get_config()
    return {
        "title": "Animathic API",
        "description": "AI-Powered Mathematical Animation Generation",
        "version": "1.0.0",
        "docs_url": "/docs" if not IS_PRODUCTION else None,
        "redoc_url": "/redoc" if not IS_PRODUCTION else None,
        "openapi_url": "/openapi.json" if not IS_PRODUCTION else None,
    }

def get_feature_flags() -> FeatureFlags:
    """Get feature flags configuration"""
    return get_config().features

def is_production() -> bool:
    """Check if running in production"""
    return IS_PRODUCTION

def get_log_level() -> str:
    """Get logging level"""
    return get_config().monitoring.log_level

def get_cors_origins() -> List[str]:
    """Get CORS origins"""
    return get_config().security.cors_origins

def get_rate_limit_config() -> Dict[str, Any]:
    """Get rate limiting configuration"""
    config = get_config().rate_limit
    return {
        "enabled": config.enabled,
        "max_requests": config.max_requests,
        "window_minutes": config.window_minutes
    }

# Environment-specific configurations
if IS_PRODUCTION:
    # Production-specific overrides
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
else:
    # Development-specific overrides
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
