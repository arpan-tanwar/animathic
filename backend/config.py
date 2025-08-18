"""
Animathic Backend Configuration
Optimized for Google Cloud Platform deployment
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base configuration
BASE_CONFIG = {
    "app_name": "Animathic Backend",
    "version": "3.0.0",
    "environment": os.getenv("ENVIRONMENT", "production"),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
}

# Google Cloud Platform Configuration
GCP_CONFIG = {
    "project_id": os.getenv("GCP_PROJECT_ID", "animathic-backend"),
    "region": os.getenv("GCP_REGION", "us-central1"),
    "service_name": os.getenv("GCP_SERVICE_NAME", "animathic-backend"),
    "image_name": f"gcr.io/{os.getenv('GCP_PROJECT_ID', 'animathic-backend')}/animathic-backend",
    "memory": os.getenv("GCP_MEMORY", "2Gi"),
    "cpu": int(os.getenv("GCP_CPU", "1")),
    "timeout": int(os.getenv("GCP_TIMEOUT", "300")),
    "max_instances": int(os.getenv("GCP_MAX_INSTANCES", "10")),
    "min_instances": int(os.getenv("GCP_MIN_INSTANCES", "0")),
    "concurrency": int(os.getenv("GCP_CONCURRENCY", "80")),
}

# API Configuration
API_CONFIG = {
    "host": os.getenv("HOST", "0.0.0.0"),
    "port": int(os.getenv("PORT", "8080")),
    "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
    "rate_limit_requests": int(os.getenv("RATE_LIMIT_REQUESTS", "10")),
    "rate_limit_window": int(os.getenv("RATE_LIMIT_WINDOW", "60")),
}

# Google AI Configuration
GOOGLE_AI_CONFIG = {
    "api_key": os.getenv("GOOGLE_AI_API_KEY"),
    "model_name": os.getenv("GOOGLE_AI_MODEL", "gemini-2.0-flash-exp"),
    "temperature": float(os.getenv("GOOGLE_AI_TEMPERATURE", "0.1")),
    "max_output_tokens": int(os.getenv("GOOGLE_AI_MAX_TOKENS", "4096")),
    "top_p": float(os.getenv("GOOGLE_AI_TOP_P", "0.8")),
    "top_k": int(os.getenv("GOOGLE_AI_TOP_K", "40")),
}

# Supabase Configuration
SUPABASE_CONFIG = {
    "url": os.getenv("SUPABASE_URL"),
    "anon_key": os.getenv("SUPABASE_ANON_KEY"),
    "service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    "bucket_name": os.getenv("SUPABASE_BUCKET_NAME", "animathic-media"),
}

# Database Configuration
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL"),
    "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
}

# Media Configuration
MEDIA_CONFIG = {
    "base_dir": os.getenv("MEDIA_BASE_DIR", "./media"),
    "max_file_size": int(os.getenv("MAX_FILE_SIZE", "104857600")),  # 100MB
    "allowed_extensions": [".mp4", ".gif", ".png", ".jpg", ".jpeg"],
    "cleanup_interval": int(os.getenv("CLEANUP_INTERVAL", "3600")),  # 1 hour
    "retention_hours": int(os.getenv("RETENTION_HOURS", "24")),
}

# Security Configuration
SECURITY_CONFIG = {
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
    "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
    "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    "refresh_token_expire_days": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
    "enable_health_checks": os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true",
    "enable_logging": os.getenv("ENABLE_LOGGING", "true").lower() == "true",
    "log_retention_days": int(os.getenv("LOG_RETENTION_DAYS", "30")),
}

# Feature Flags
FEATURE_FLAGS = {
    "enhanced_database": os.getenv("ENABLE_ENHANCED_DATABASE", "true").lower() == "true",
    "ai_animations": os.getenv("ENABLE_AI_ANIMATIONS", "true").lower() == "true",
    "user_management": os.getenv("ENABLE_USER_MANAGEMENT", "true").lower() == "true",
    "file_upload": os.getenv("ENABLE_FILE_UPLOAD", "true").lower() == "true",
    "rate_limiting": os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true",
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration"""
    return {
        "base": BASE_CONFIG,
        "gcp": GCP_CONFIG,
        "api": API_CONFIG,
        "google_ai": GOOGLE_AI_CONFIG,
        "supabase": SUPABASE_CONFIG,
        "database": DATABASE_CONFIG,
        "media": MEDIA_CONFIG,
        "security": SECURITY_CONFIG,
        "monitoring": MONITORING_CONFIG,
        "features": FEATURE_FLAGS,
    }

def get_gcp_config() -> Dict[str, Any]:
    """Get Google Cloud specific configuration"""
    return GCP_CONFIG

def get_api_config() -> Dict[str, Any]:
    """Get API configuration"""
    return API_CONFIG

def get_feature_flags() -> Dict[str, bool]:
    """Get feature flags"""
    return FEATURE_FLAGS

def is_production() -> bool:
    """Check if running in production"""
    return BASE_CONFIG["environment"] == "production"

def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return BASE_CONFIG["debug"]

def get_log_level() -> str:
    """Get log level"""
    return BASE_CONFIG["log_level"]
