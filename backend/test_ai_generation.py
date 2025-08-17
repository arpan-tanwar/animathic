#!/usr/bin/env python3
"""
Test script for AI code generation
"""
import asyncio
import os
from services.manim import ManimService

async def test_ai_generation():
    """Test the AI code generation process"""
    print("🧪 Testing AI Code Generation System")
    print("=" * 50)
    
    # Check environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable not set")
        return False
    
    print(f"✅ GOOGLE_API_KEY found: {api_key[:10]}...")
    
    try:
        # Initialize service
        print("\n📚 Initializing ManimService...")
        service = ManimService()
        print("✅ ManimService initialized successfully")
        
        # Test prompt
        test_prompt = "Create a simple animation of a blue circle that grows and then turns into a red square"
        print(f"\n🎯 Testing with prompt: '{test_prompt}'")
        
        # Generate code only (not full video)
        print("\n🤖 Generating AI code...")
        scene_code = await service._generate_animation_code(test_prompt, 0)
        
        print(f"\n📝 Generated code ({len(scene_code)} chars):")
        print("-" * 40)
        print(scene_code)
        print("-" * 40)
        
        # Validate code
        print("\n🔍 Validating generated code...")
        is_valid = service._validate_scene_code(scene_code)
        
        if is_valid:
            print("✅ Code validation PASSED!")
            print("\n🎉 AI Code Generation System is working correctly!")
            return True
        else:
            print("❌ Code validation FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_generation())
    exit(0 if success else 1)
