"""
Centralized Configuration Management for Optimized Backend

This module provides:
- Environment-based configuration
- Security settings
- Performance tuning
- Resource limits
"""

import os
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    max_prompt_length: int = 500
    max_code_length: int = 8192
    rate_limit_requests: int = 5
    rate_limit_window_minutes: int = 1
    allowed_origins: List[str] = None
    enable_cors: bool = True
    enable_security_headers: bool = True
    
    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = [
                "http://localhost:5173",
                "http://localhost:3000",
                "http://localhost:8080",
                "https://animathic.com",
            ]

@dataclass
class PerformanceConfig:
    """Performance and resource configuration"""
    max_memory_mb: int = 1024
    max_execution_time_seconds: int = 300
    max_workers: int = 2
    enable_caching: bool = True
    cleanup_interval_hours: int = 24
    video_quality: str = "medium_quality"
    video_resolution: tuple = (1280, 720)
    video_frame_rate: int = 30

@dataclass
class AIConfig:
    """AI model configuration"""
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.05
    top_p: float = 0.7
    top_k: int = 15
    max_output_tokens: int = 4096
    max_retries: int = 3

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: Optional[str] = None
    max_connections: int = 10
    connection_timeout: int = 30
    enable_ssl: bool = True
    
    def __post_init__(self):
        if self.url is None:
            self.url = os.getenv("DATABASE_URL")

@dataclass
class StorageConfig:
    """Storage configuration"""
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    bucket_name: str = "animathic-videos"
    max_file_size_mb: int = 100
    signed_url_expiry_hours: int = 1
    
    def __post_init__(self):
        if self.supabase_url is None:
            self.supabase_url = os.getenv("SUPABASE_URL")
        if self.supabase_key is None:
            self.supabase_key = os.getenv("SUPABASE_ANON_KEY")

class Config:
    """Main configuration class"""
    
    def __init__(self, environment: Optional[str] = None):
        self.environment = Environment(environment or os.getenv("ENVIRONMENT", "development"))
        
        # API Keys
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Media directory
        self.media_dir = os.path.abspath(os.getenv("MEDIA_DIR", "media"))
        
        # Load environment-specific configurations
        self.security = self._load_security_config()
        self.performance = self._load_performance_config()
        self.ai = self._load_ai_config()
        self.database = DatabaseConfig()
        self.storage = StorageConfig()
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.enable_file_logging = self.environment == Environment.PRODUCTION
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration based on environment"""
        if self.environment == Environment.PRODUCTION:
            return SecurityConfig(
                rate_limit_requests=3,  # Stricter in production
                rate_limit_window_minutes=1,
                enable_security_headers=True,
            )
        elif self.environment == Environment.STAGING:
            return SecurityConfig(
                rate_limit_requests=5,
                rate_limit_window_minutes=1,
                enable_security_headers=True,
            )
        else:  # Development
            return SecurityConfig(
                rate_limit_requests=10,  # More lenient for development
                rate_limit_window_minutes=1,
                enable_security_headers=False,
            )
    
    def _load_performance_config(self) -> PerformanceConfig:
        """Load performance configuration based on environment"""
        if self.environment == Environment.PRODUCTION:
            return PerformanceConfig(
                max_memory_mb=2048,  # More memory in production
                max_execution_time_seconds=300,
                max_workers=4,
                enable_caching=True,
                cleanup_interval_hours=12,  # More frequent cleanup
            )
        elif self.environment == Environment.STAGING:
            return PerformanceConfig(
                max_memory_mb=1536,
                max_execution_time_seconds=300,
                max_workers=2,
                enable_caching=True,
                cleanup_interval_hours=24,
            )
        else:  # Development
            return PerformanceConfig(
                max_memory_mb=1024,
                max_execution_time_seconds=600,  # Longer timeout for debugging
                max_workers=1,
                enable_caching=False,  # Disable caching for development
                cleanup_interval_hours=24,
            )
    
    def _load_ai_config(self) -> AIConfig:
        """Load AI configuration based on environment"""
        if self.environment == Environment.PRODUCTION:
            return AIConfig(
                temperature=0.02,  # More deterministic in production
                top_p=0.6,
                top_k=10,
                max_retries=2,  # Fewer retries to avoid costs
            )
        else:
            return AIConfig()  # Use defaults for non-production
    
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    def is_staging(self) -> bool:
        return self.environment == Environment.STAGING

# Global configuration instance
config = Config()

# Export commonly used configurations
__all__ = [
    "config",
    "Config",
    "Environment",
    "SecurityConfig",
    "PerformanceConfig",
    "AIConfig",
    "DatabaseConfig",
    "StorageConfig",
]
