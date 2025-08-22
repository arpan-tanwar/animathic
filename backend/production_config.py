"""
Production configuration for Animathic Backend
"""

import os
from typing import List

# Production environment settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEBUG = ENVIRONMENT.lower() != "production"

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
WORKERS = int(os.getenv("WORKERS", "4"))

# CORS configuration for production
ALLOWED_ORIGINS = [
    "https://animathic.com",  # Production domain
    "https://www.animathic.com",  # Production domain with www
    "https://clerk.animathic.com",  # Clerk authentication domain
    "https://img.clerk.com",  # Clerk image domain
    "https://animathic-backend-*.run.app",  # Cloud Run domains
    "http://localhost:3000",  # Local development
    "http://localhost:3001",  # Alternative local port
]

# Security settings
MAX_REQUEST_SIZE = os.getenv("MAX_REQUEST_SIZE", "100MB")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))  # 5 minutes
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

# Database settings
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "20"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))
DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))

# AI Service settings
AI_SERVICE_TIMEOUT = int(os.getenv("AI_SERVICE_TIMEOUT", "120"))
AI_SERVICE_RETRIES = int(os.getenv("AI_SERVICE_RETRIES", "3"))

# Manim settings
MANIM_RENDER_TIMEOUT = int(os.getenv("MANIM_RENDER_TIMEOUT", "600"))  # 10 minutes
MANIM_MAX_FILE_SIZE = os.getenv("MANIM_MAX_FILE_SIZE", "50MB")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", "/var/log/animathic/backend.log")

# Monitoring and health checks
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"

# File storage settings
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/animathic")
MAX_UPLOAD_SIZE = os.getenv("MAX_UPLOAD_SIZE", "100MB")

# Production optimizations
ENABLE_COMPRESSION = True
ENABLE_CACHING = True
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
