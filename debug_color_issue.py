#!/usr/bin/env python3
"""
Debug script to test exact color generation process
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.manim_code_generator import ManimCodeGenerator

def test_color_generation():
    """Test the exact color generation process"""
    print("🔍 Testing Color Generation Process...")
    
    # Create a test animation spec (exactly what the AI would generate)
    test_spec = {
        "animation_type": "geometric",
        "scene_description": "A red circle fades in and then fades out.",
        "objects": [
            {
                "id": "red_circle",
                "type": "circle",
                "properties": {
                    "position": [0.0, 0.0, 0.0],
                    "color": "RED",  # This is what the AI generates
                    "size": 1.0
                },
                "animations": [
                    {"type": "fade_in", "duration": 1.0, "parameters": {}},
                    {"type": "fade_out", "duration": 1.0, "parameters": {}}
                ]
            }
        ],
        "camera_settings": {"position": [0, 0, 0], "zoom": 8},
        "duration": 5,
        "background_color": "#000000",  # Changed to pure black for better contrast
        "style": "modern"
    }
    
    print(f"📋 Test Animation Spec:")
    print(f"  Object color: {test_spec['objects'][0]['properties']['color']}")
    print(f"  Object type: {test_spec['objects'][0]['type']}")
    
    try:
        # Generate Manim code
        code_generator = ManimCodeGenerator()
        manim_code = code_generator.generate_manim_code(test_spec)
        
        print(f"\n✅ Manim Code Generated Successfully!")
        
        # Look for the specific color assignment lines
        lines = manim_code.split('\n')
        print(f"\n🔍 Color Assignment in Generated Code:")
        
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in ['color_name', 'color_mapping', 'color=', 'Color(']):
                print(f"Line {i+1}: {line.strip()}")
        
        # Look for the Circle creation specifically
        print(f"\n🎯 Circle Creation Code:")
        for i, line in enumerate(lines):
            if 'Circle(' in line or 'circle_obj' in line:
                print(f"Line {i+1}: {line.strip()}")
        
        # Check if RED is properly mapped
        print(f"\n🎨 Color Mapping Check:")
        if 'RED' in manim_code and 'color_mapping' in manim_code:
            print("✅ RED color and color_mapping found in generated code")
        else:
            print("❌ RED color or color_mapping missing from generated code")
            
        # Show the full generated code for manual inspection
        print(f"\n📄 Full Generated Code:")
        print(manim_code)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_color_generation()
