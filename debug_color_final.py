#!/usr/bin/env python3
"""
Comprehensive debug script to find the exact color issue
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.manim_code_generator import ManimCodeGenerator

def test_color_generation():
    """Test the exact color generation process"""
    print("🔍 Comprehensive Color Debug Test...")
    
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
        "background_color": "#000000",  # Pure black for maximum contrast
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
        print(f"\n🔍 Critical Color Lines in Generated Code:")
        
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in ['color_name', 'color_mapping', 'fill_color', 'stroke_color', 'Circle(']):
                print(f"Line {i+1}: {line.strip()}")
        
        # Check if the color mapping is correct
        print(f"\n🎨 Color Mapping Verification:")
        if 'fill_color=color' in manim_code:
            print("✅ fill_color=color found in Circle creation")
        else:
            print("❌ fill_color=color NOT found in Circle creation")
            
        if 'stroke_color=color' in manim_code:
            print("✅ stroke_color=color found in Circle creation")
        else:
            print("❌ stroke_color=color NOT found in Circle creation")
        
        # Check if RED is properly mapped
        print(f"\n🔴 RED Color Check:")
        if 'RED' in manim_code:
            print("✅ RED color found in generated code")
        else:
            print("❌ RED color missing from generated code")
            
        if 'color_mapping' in manim_code:
            print("✅ color_mapping found in generated code")
        else:
            print("❌ color_mapping missing from generated code")
        
        # Show the exact Circle creation code
        print(f"\n🎯 Exact Circle Creation Code:")
        for i, line in enumerate(lines):
            if 'Circle(' in line:
                print(f"Line {i+1}: {line.strip()}")
                # Show next few lines for context
                for j in range(i+1, min(i+6, len(lines))):
                    if lines[j].strip():
                        print(f"Line {j+1}: {lines[j].strip()}")
                break
        
        # Check the color variable assignment
        print(f"\n🎨 Color Variable Assignment:")
        for i, line in enumerate(lines):
            if 'color = color_mapping.get' in line:
                print(f"Line {i+1}: {line.strip()}")
                # Show the debug print line
                if i+1 < len(lines) and 'print(f"Color mapping' in lines[i+1]:
                    print(f"Line {i+2}: {lines[i+1].strip()}")
                break
        
        # Show the full generated code for manual inspection
        print(f"\n📄 Full Generated Code:")
        print(manim_code)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_color_generation()
