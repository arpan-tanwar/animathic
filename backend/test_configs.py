#!/usr/bin/env python3
"""
Test script to demonstrate different configurations
"""

from config_dev import (
    get_llm_config, 
    get_server_config, 
    get_config,
    print_available_configs,
    update_feature_flag
)

def test_llm_configs():
    """Test different LLM configurations"""
    print("🧪 Testing LLM Configurations...")
    print("=" * 50)
    
    # Test each LLM config
    for model_name in ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]:
        config = get_llm_config(model_name)
        if config:
            print(f"📝 {model_name}:")
            print(f"   Temperature: {config['temperature']}")
            print(f"   Max Tokens: {config['max_output_tokens']}")
            print(f"   Description: {config['description']}")
            print()

def test_server_configs():
    """Test different server configurations"""
    print("🧪 Testing Server Configurations...")
    print("=" * 50)
    
    # Test each server config
    for config_name in ["development", "testing", "production"]:
        config = get_server_config(config_name)
        if config:
            print(f"🖥️  {config_name}:")
            print(f"   Host: {config['host']}")
            print(f"   Port: {config['port']}")
            print(f"   Reload: {config['reload']}")
            print(f"   Workers: {config['workers']}")
            print(f"   Description: {config['description']}")
            print()

def test_feature_flags():
    """Test feature flag functionality"""
    print("🧪 Testing Feature Flags...")
    print("=" * 50)
    
    # Show current flags
    print("Current Feature Flags:")
    feature_flags = get_config("features")
    for flag, value in feature_flags.items():
        print(f"   {'✅' if value else '❌'} {flag}: {value}")
    
    print("\n🔧 Testing Feature Flag Updates...")
    
    # Test updating a feature flag
    print("   Updating experimental_prompts to True...")
    update_feature_flag("experimental_prompts", True)
    
    # Show updated flags
    print("\nUpdated Feature Flags:")
    updated_flags = get_config("features")
    for flag, value in updated_flags.items():
        print(f"   {'✅' if value else '❌'} {flag}: {value}")
    
    # Reset to original value
    update_feature_flag("experimental_prompts", False)
    print("   Reset experimental_prompts to False")

def test_config_loading():
    """Test configuration loading functions"""
    print("🧪 Testing Configuration Loading...")
    print("=" * 50)
    
    # Test base config
    base_config = get_config()
    print(f"Base Config Keys: {list(base_config.keys())}")
    
    # Test LLM configs
    llm_configs = get_config("llm")
    print(f"LLM Configs Available: {list(llm_configs.keys())}")
    
    # Test server configs
    server_configs = get_config("server")
    print(f"Server Configs Available: {list(server_configs.keys())}")

def main():
    """Run all tests"""
    print("🚀 Animathic Configuration Testing Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_llm_configs()
    test_server_configs()
    test_feature_flags()
    test_config_loading()
    
    print("\n" + "=" * 60)
    print("✅ All configuration tests completed!")
    print("\nTo start the development server with different configs:")
    print("   python dev_server.py --help")
    print("   python dev_server.py --list-configs")

if __name__ == "__main__":
    main()
