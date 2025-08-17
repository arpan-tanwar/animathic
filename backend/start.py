#!/usr/bin/env python3
"""
Simple startup script for Animathic backend

This script checks environment and starts the consolidated main.py
"""

import os
import sys

def check_environment():
    """Check if environment is properly set up"""
    required_vars = ['GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Set them with:")
        for var in missing_vars:
            print(f"   export {var}=your_value")
        print("\n📚 Get GOOGLE_API_KEY from: https://makersuite.google.com/app/apikey")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🚀 Animathic Backend Startup")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        return 1
    
    print("✅ Environment check passed")
    print("🌐 Starting server on http://localhost:8000")
    print("📊 Health check: http://localhost:8000/api/health")
    print("📖 API docs: http://localhost:8000/docs")
    print("\nStarting...\n")
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        return 0
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
