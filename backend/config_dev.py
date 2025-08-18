"""
Development Configuration for Animathic Backend

This file contains different configurations for testing various LLMs, 
server settings, and experimental features.
"""

import os
from typing import Dict, Any, Optional

# Base configuration
BASE_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "workers": 1,
        "access_log": True
    },
    "logging": {
        "level": "DEBUG",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "media": {
        "cleanup_interval": 3600,  # 1 hour
        "max_age_hours": 24
    }
}

# LLM Configuration Options
LLM_CONFIGS = {
    "gemini-2.5-flash": {
        "model_name": "gemini-2.5-flash",
        "temperature": 0.1,
        "top_p": 0.8,
        "top_k": 20,
        "max_output_tokens": 4096,
        "candidate_count": 1,
        "description": "Fast, efficient model for simple animations"
    },
    
    "gemini-2.0-flash": {
        "model_name": "gemini-2.0-flash",
        "temperature": 0.05,
        "top_p": 0.8,
        "top_k": 20,
        "max_output_tokens": 4096,
        "candidate_count": 1,
        "description": "Reliable fallback model"
    },
    
    "gemini-1.5-pro": {
        "model_name": "gemini-1.5-pro",
        "temperature": 0.2,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 8192,
        "candidate_count": 1,
        "description": "High-capacity model for complex animations"
    },
    
    "gemini-1.5-flash": {
        "model_name": "gemini-1.5-flash",
        "temperature": 0.1,
        "top_p": 0.8,
        "top_k": 20,
        "max_output_tokens": 4096,
        "candidate_count": 1,
        "description": "Balanced model for general use"
    }
}

# Server Configuration Options
SERVER_CONFIGS = {
    "development": {
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True,
        "workers": 1,
        "access_log": True,
        "description": "Local development server"
    },
    
    "testing": {
        "host": "0.0.0.0",
        "port": 8001,
        "reload": False,
        "workers": 2,
        "access_log": False,
        "description": "Testing server configuration"
    },
    
    "production": {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": False,
        "workers": 4,
        "access_log": True,
        "description": "Production server configuration"
    },
    
    "docker": {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": False,
        "workers": 1,
        "access_log": True,
        "description": "Docker container configuration"
    }
}

# Feature Flags for Testing
FEATURE_FLAGS = {
    "enhanced_logging": True,
    "syntax_error_fixing": True,
    "content_validation": True,
    "response_extraction_debug": True,
    "manim_error_details": True,
    "experimental_prompts": False,
    "custom_llm_integration": False
}

def get_config(config_type: str = "development") -> Dict[str, Any]:
    """Get configuration for specified type"""
    if config_type == "llm":
        return LLM_CONFIGS
    elif config_type == "server":
        return SERVER_CONFIGS
    elif config_type == "features":
        return FEATURE_FLAGS
    else:
        return BASE_CONFIG

def get_llm_config(model_name: str) -> Optional[Dict[str, Any]]:
    """Get specific LLM configuration"""
    return LLM_CONFIGS.get(model_name)

def get_server_config(server_type: str) -> Optional[Dict[str, Any]]:
    """Get specific server configuration"""
    return SERVER_CONFIGS.get(server_type)

def update_feature_flag(flag_name: str, value: bool) -> None:
    """Update a feature flag"""
    if flag_name in FEATURE_FLAGS:
        FEATURE_FLAGS[flag_name] = value

def print_available_configs():
    """Print all available configurations"""
    print("🚀 Available LLM Configurations:")
    for name, config in LLM_CONFIGS.items():
        print(f"  📝 {name}: {config['description']}")
    
    print("\n🌐 Available Server Configurations:")
    for name, config in SERVER_CONFIGS.items():
        print(f"  🖥️  {name}: {config['description']}")
    
    print("\n⚙️  Feature Flags:")
    for name, value in FEATURE_FLAGS.items():
        print(f"  {'✅' if value else '❌'} {name}: {value}")

if __name__ == "__main__":
    print_available_configs()
