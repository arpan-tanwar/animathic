#!/usr/bin/env python3
"""
Test Manim Imports - Check what's actually available
"""

try:
    print("🔍 Testing Manim imports...")
    
    # Test basic import
    import manim
    print(f"✅ Manim version: {manim.__version__}")
    
    # Test specific imports
    try:
        from manim import RED
        print("✅ RED constant available")
    except ImportError as e:
        print(f"❌ RED constant not available: {e}")
    
    try:
        from manim import Circle
        print("✅ Circle class available")
    except ImportError as e:
        print(f"❌ Circle class not available: {e}")
    
    try:
        from manim import FadeIn
        print("✅ FadeIn available")
    except ImportError as e:
        print(f"❌ FadeIn not available: {e}")
    
    try:
        from manim import FadeOut
        print("✅ FadeOut available")
    except ImportError as e:
        print(f"❌ FadeOut not available: {e}")
    
    try:
        from manim import Create
        print("✅ Create available")
    except ImportError as e:
        print(f"❌ Create not available: {e}")
    
    try:
        from manim import MovingCameraScene
        print("✅ MovingCameraScene available")
    except ImportError as e:
        print(f"❌ MovingCameraScene not available: {e}")
    
    try:
        from manim import Color
        print("✅ Color class available")
    except ImportError as e:
        print(f"❌ Color class not available: {e}")
    
    # List available modules
    print("\n📋 Available modules in manim:")
    for item in dir(manim):
        if not item.startswith('_'):
            print(f"   - {item}")
            
except ImportError as e:
    print(f"❌ Failed to import manim: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
