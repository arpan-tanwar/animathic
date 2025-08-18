#!/usr/bin/env python3
"""
Development Server for Animathic Backend

This script allows you to easily test different configurations:
- Different LLM models
- Different server settings
- Feature flags
- Experimental configurations
"""

import os
import sys
import argparse
import asyncio
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config_dev import (
    get_llm_config, 
    get_server_config, 
    get_config,
    print_available_configs,
    update_feature_flag
)

def setup_environment(config_type: str = "development"):
    """Setup environment variables for the specified configuration"""
    print(f"🔧 Setting up {config_type} environment...")
    
    # Set server configuration
    server_config = get_server_config(config_type)
    if server_config:
        os.environ['DEV_SERVER_HOST'] = str(server_config['host'])
        os.environ['DEV_SERVER_PORT'] = str(server_config['port'])
        os.environ['DEV_SERVER_RELOAD'] = str(server_config['reload']).lower()
        os.environ['DEV_SERVER_WORKERS'] = str(server_config['workers'])
        print(f"✅ Server config: {server_config['description']}")
    
    # Set feature flags
    feature_flags = get_config("features")
    for flag, value in feature_flags.items():
        os.environ[f'FEATURE_{flag.upper()}'] = str(value).upper()
    
    print("✅ Environment configured")

def start_dev_server():
    """Start the development server with specified configuration"""
    parser = argparse.ArgumentParser(description="Animathic Development Server")
    parser.add_argument(
        "--config", 
        "-c", 
        default="development",
        choices=["development", "testing", "production", "docker"],
        help="Server configuration to use"
    )
    parser.add_argument(
        "--llm", 
        "-l",
        default="gemini-2.5-flash",
        choices=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        help="LLM model to use"
    )
    parser.add_argument(
        "--port", 
        "-p", 
        type=int,
        help="Override port number"
    )
    parser.add_argument(
        "--host", 
        "-H",
        help="Override host address"
    )
    parser.add_argument(
        "--reload", 
        "-r", 
        action="store_true",
        help="Enable auto-reload"
    )
    parser.add_argument(
        "--workers", 
        "-w", 
        type=int,
        help="Number of worker processes"
    )
    parser.add_argument(
        "--list-configs", 
        "-L", 
        action="store_true",
        help="List all available configurations"
    )
    parser.add_argument(
        "--feature", 
        "-f",
        nargs=2,
        metavar=('FLAG', 'VALUE'),
        help="Set a feature flag (e.g., --feature enhanced_logging true)"
    )
    
    args = parser.parse_args()
    
    if args.list_configs:
        print_available_configs()
        return
    
    # Set feature flag if specified
    if args.feature:
        flag_name, flag_value = args.feature
        value = flag_value.lower() == 'true'
        update_feature_flag(flag_name, value)
        print(f"✅ Feature flag '{flag_name}' set to {value}")
    
    # Setup environment
    setup_environment(args.config)
    
    # Get server configuration
    server_config = get_server_config(args.config)
    if not server_config:
        print(f"❌ Unknown server configuration: {args.config}")
        return
    
    # Override with command line arguments
    host = args.host or server_config['host']
    port = args.port or server_config['port']
    reload = args.reload if args.reload is not None else server_config['reload']
    workers = args.workers or server_config['workers']
    
    # Set LLM model
    os.environ['DEV_LLM_MODEL'] = args.llm
    llm_config = get_llm_config(args.llm)
    if llm_config:
        print(f"🤖 Using LLM: {args.llm} - {llm_config['description']}")
    
    print(f"🚀 Starting {args.config} server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"👥 Workers: {workers}")
    print(f"🤖 LLM: {args.llm}")
    
    # Start server
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    start_dev_server()
