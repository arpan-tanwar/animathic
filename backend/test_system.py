#!/usr/bin/env python3
"""
Test script for the complete system validation
"""
import os
import sys
import asyncio
from unittest.mock import MagicMock, patch

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing System Imports")
    print("=" * 50)
    
    try:
        # Test FastAPI imports
        import fastapi
        print("✅ FastAPI imported successfully")
        
        # Test Manim imports
        import manim
        print("✅ Manim imported successfully")
        
        # Test Google AI imports
        import google.generativeai as genai
        print("✅ Google GenerativeAI imported successfully")
        
        # Test our service imports
        from services.manim import ManimService
        print("✅ ManimService imported successfully")
        
        from services.storage import StorageService
        print("✅ StorageService imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_code_validation():
    """Test code validation without requiring API"""
    print("\n🔍 Testing Code Validation Logic")
    print("=" * 50)
    
    try:
        # Mock the service without needing API key
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            from services.manim import ManimService
            service = ManimService()
            
            # Test valid code
            valid_code = """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        self.play(Create(circle))
        self.wait(1)
"""
            
            result = service._validate_scene_code(valid_code)
            if result:
                print("✅ Valid code validation PASSED")
            else:
                print("❌ Valid code validation FAILED")
                return False
            
            # Test invalid code (missing import)
            invalid_code = """class GeneratedScene(Scene):
    def construct(self):
        pass
"""
            
            result = service._validate_scene_code(invalid_code)
            if not result:
                print("✅ Invalid code validation PASSED (correctly rejected)")
            else:
                print("❌ Invalid code validation FAILED (should have been rejected)")
                return False
            
            # Test forbidden elements
            forbidden_code = """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        text = MathTex("E=mc^2")
        self.play(Write(text))
"""
            
            result = service._validate_scene_code(forbidden_code)
            if not result:
                print("✅ Forbidden element validation PASSED (correctly rejected)")
            else:
                print("❌ Forbidden element validation FAILED (should have been rejected)")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ Code validation test failed: {str(e)}")
        return False

def test_code_cleaning():
    """Test code cleaning functionality"""
    print("\n🧹 Testing Code Cleaning Logic")
    print("=" * 50)
    
    try:
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            from services.manim import ManimService
            service = ManimService()
            
            # Test markdown removal
            messy_code = """```python
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        self.play(Create(circle))
        self.wait(1)
```"""
            
            cleaned = service._clean_code_response(messy_code)
            if "```" not in cleaned and "from manim import *" in cleaned:
                print("✅ Markdown cleaning PASSED")
            else:
                print("❌ Markdown cleaning FAILED")
                return False
            
            # Test prefix removal
            prefix_code = """Here's your code:

from manim import *

class GeneratedScene(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        self.play(Create(circle))
        self.wait(1)
"""
            
            cleaned = service._clean_code_response(prefix_code)
            if cleaned.startswith("from manim import *"):
                print("✅ Prefix removal PASSED")
            else:
                print("❌ Prefix removal FAILED")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ Code cleaning test failed: {str(e)}")
        return False

def test_manim_config():
    """Test Manim configuration"""
    print("\n⚙️ Testing Manim Configuration")
    print("=" * 50)
    
    try:
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            from services.manim import ManimService
            service = ManimService()
            
            # Check if media directory exists
            if os.path.exists(service.media_dir):
                print("✅ Media directory exists")
            else:
                print("❌ Media directory missing")
                return False
            
            # Test Manim config
            from manim import config
            if config.media_dir == service.media_dir:
                print("✅ Manim config set correctly")
            else:
                print("❌ Manim config not set correctly")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ Manim config test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 SYSTEM VALIDATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_code_validation, 
        test_code_cleaning,
        test_manim_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready!")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
