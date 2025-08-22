#!/usr/bin/env python3
"""
Debug script to test color handling in the AI service
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.ai_service_new import AIService

async def test_color_generation():
    """Test color generation for red circle prompt"""
    print("🔍 Testing AI Color Generation...")
    
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Test prompt
        prompt = "Create a red circle that fades in, then fades out"
        print(f"📝 Prompt: {prompt}")
        
        # Generate animation spec
        print("\n🔄 Generating animation specification...")
        result = await ai_service.process_animation_request(prompt)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print("\n✅ Success! Generated result:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Workflow Type: {result.get('workflow_type', 'unknown')}")
        
        # Show animation spec
        animation_spec = result.get('animation_spec', {})
        print(f"\n📋 Animation Specification:")
        print(f"Scene Description: {animation_spec.get('scene_description', 'N/A')}")
        print(f"Background Color: {animation_spec.get('background_color', 'N/A')}")
        
        # Show objects
        objects = animation_spec.get('objects', [])
        print(f"\n🎯 Objects ({len(objects)}):")
        for i, obj in enumerate(objects):
            print(f"  Object {i+1}:")
            print(f"    Type: {obj.get('type', 'N/A')}")
            print(f"    ID: {obj.get('id', 'N/A')}")
            
            props = obj.get('properties', {})
            print(f"    Position: {props.get('position', 'N/A')}")
            print(f"    Color: {props.get('color', 'N/A')}")
            print(f"    Size: {props.get('size', 'N/A')}")
            
            animations = obj.get('animations', [])
            print(f"    Animations ({len(animations)}):")
            for j, anim in enumerate(animations):
                print(f"      Animation {j+1}: {anim.get('type', 'N/A')} (duration: {anim.get('duration', 'N/A')})")
        
        # Show generated Manim code
        manim_code = result.get('manim_code', '')
        if manim_code:
            print(f"\n🐍 Generated Manim Code Preview (first 500 chars):")
            print(manim_code[:500] + "..." if len(manim_code) > 500 else manim_code)
            
            # Show the circle creation part specifically
            print(f"\n🔍 Circle Creation Code:")
            lines = manim_code.split('\n')
            for i, line in enumerate(lines):
                if 'circle' in line.lower() or 'Circle(' in line or 'color=' in line:
                    print(f"Line {i+1}: {line}")
                elif 'color_mapping' in line or 'color_name' in line:
                    print(f"Line {i+1}: {line}")
                elif 'FadeIn' in line or 'FadeOut' in line:
                    print(f"Line {i+1}: {line}")
        
        # Test color mapping
        print(f"\n🎨 Testing Color Mapping:")
        test_colors = ['red', 'RED', 'Red', 'blue', 'BLUE', 'green', 'GREEN']
        for test_color in test_colors:
            print(f"  '{test_color}' -> Testing...")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_color_generation())
