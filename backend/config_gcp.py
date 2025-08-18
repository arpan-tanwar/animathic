"""
Google Cloud Platform Configuration for Animathic Backend

This file contains GCP-specific configurations for deployment.
"""

import os
from typing import Dict, Any

# GCP Project Configuration
GCP_CONFIG = {
    "project_id": "animathic-backend",
    "region": "us-central1",
    "zone": "us-central1-a",
    "service_name": "animathic-backend",
    "image_name": "gcr.io/animathic-backend/animathic-backend",
    "min_instances": 0,
    "max_instances": 10,
    "cpu": 1,
    "memory": "2Gi",
    "timeout": 300,
    "concurrency": 80
}

# GCP Services Configuration
GCP_SERVICES = {
    "cloud_run": {
        "service_name": "animathic-backend",
        "region": "us-central1",
        "port": 8000,
        "cpu": 1,
        "memory": "2Gi",
        "min_instances": 0,
        "max_instances": 10,
        "timeout": 300,
        "concurrency": 80
    },
    
    "cloud_sql": {
        "instance_name": "animathic-db",
        "database_name": "animathic",
        "user": "animathic_user",
        "tier": "db-f1-micro",  # Smallest instance for testing
        "region": "us-central1",
        "backup_enabled": True
    },
    
    "cloud_storage": {
        "bucket_name": "animathic-media",
        "location": "US",
        "storage_class": "STANDARD",
        "public_access": False
    },
    
    "secret_manager": {
        "google_api_key_secret": "GOOGLE_AI_API_KEY",
        "supabase_url_secret": "SUPABASE_URL",
        "supabase_key_secret": "SUPABASE_ANON_KEY"
    }
}

# Environment Variables for GCP
GCP_ENV_VARS = {
    "GOOGLE_CLOUD_PROJECT": "animathic-backend",
    "GOOGLE_CLOUD_REGION": "us-central1",
    "PORT": "8000",
    "HOST": "0.0.0.0",
    "ENVIRONMENT": "production",
    "LOG_LEVEL": "INFO"
}

def get_gcp_config() -> Dict[str, Any]:
    """Get GCP configuration"""
    return GCP_CONFIG

def get_gcp_service_config(service_name: str) -> Dict[str, Any]:
    """Get specific GCP service configuration"""
    return GCP_SERVICES.get(service_name, {})

def get_gcp_env_vars() -> Dict[str, str]:
    """Get GCP environment variables"""
    return GCP_ENV_VARS.copy()

def update_gcp_config(key: str, value: Any) -> None:
    """Update GCP configuration"""
    if key in GCP_CONFIG:
        GCP_CONFIG[key] = value

def print_gcp_config():
    """Print GCP configuration"""
    print("🚀 Google Cloud Platform Configuration")
    print("=" * 50)
    
    print("📊 Project Settings:")
    for key, value in GCP_CONFIG.items():
        print(f"   {key}: {value}")
    
    print("\n🌐 Services Configuration:")
    for service, config in GCP_SERVICES.items():
        print(f"   {service}:")
        for key, value in config.items():
            print(f"     {key}: {value}")
    
    print("\n🔧 Environment Variables:")
    for key, value in GCP_ENV_VARS.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    print_gcp_config()
