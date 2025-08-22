#!/usr/bin/env python3
"""
Debug script to test Manim code generation and identify video generation failures
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.manim_code_generator import ManimCodeGenerator

def test_manim_generation():
    """Test the Manim code generation process"""
    print("🔍 Testing Manim Code Generation...")
    
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
        
        # Check for potential syntax errors
        print(f"\n🔍 Syntax Check:")
        
        # Check for common issues
        issues = []
        
        if 'from manim import RED' not in manim_code:
            issues.append("Missing explicit RED import")
        
        if 'fill_color=color' not in manim_code:
            issues.append("Missing fill_color parameter")
            
        if 'stroke_color=color' not in manim_code:
            issues.append("Missing stroke_color parameter")
            
        if 'set_fill(' not in manim_code:
            issues.append("Missing set_fill call")
            
        if 'set_stroke(' not in manim_code:
            issues.append("Missing set_stroke call")
        
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ No obvious syntax issues found")
        
        # Check for specific error patterns
        print(f"\n🎯 Error Pattern Check:")
        
        if 'except Exception:' in manim_code:
            print("⚠️  Broad exception handling found (might be masking errors)")
        
        if 'color = WHITE' in manim_code:
            print("⚠️  Color defaulting to WHITE found")
            
        if 'print(' in manim_code:
            print("✅ Debug logging found")
        
        # Show the critical parts of the generated code
        print(f"\n📄 Critical Code Sections:")
        
        lines = manim_code.split('\n')
        
        # Show imports
        print("Imports:")
        for i, line in enumerate(lines[:10]):
            if line.strip():
                print(f"  {i+1}: {line.strip()}")
        
        # Show Circle creation
        print("\nCircle Creation:")
        for i, line in enumerate(lines):
            if 'Circle(' in line:
                print(f"  {i+1}: {line.strip()}")
                # Show next few lines for context
                for j in range(i+1, min(i+6, len(lines))):
                    if lines[j].strip():
                        print(f"  {j+1}: {lines[j].strip()}")
                break
        
        # Show color assignment
        print("\nColor Assignment:")
        for i, line in enumerate(lines):
            if 'color = color_mapping.get' in line:
                print(f"  {i+1}: {line.strip()}")
                # Show the debug print line
                if i+1 < len(lines) and 'print(f"Color mapping' in lines[i+1]:
                    print(f"  {i+2}: {lines[i+1].strip()}")
                break
        
        # Try to identify potential runtime issues
        print(f"\n🚨 Potential Runtime Issues:")
        
        if 'eval(' in manim_code:
            print("⚠️  eval() function found (security risk)")
            
        if 'lambda x:' in manim_code:
            print("⚠️  Lambda functions found (might cause issues)")
            
        if 'Color(' in manim_code:
            print("✅ Color() function calls found")
            
        # Check if the code looks valid
        print(f"\n📊 Code Validation:")
        print(f"Total lines: {len(lines)}")
        print(f"Contains 'class GeneratedScene': {'class GeneratedScene' in manim_code}")
        print(f"Contains 'def construct': {'def construct' in manim_code}")
        print(f"Contains 'self.add': {'self.add' in manim_code}")
        print(f"Contains 'self.play': {'self.play' in manim_code}")
        
        # Show the full generated code for manual inspection
        print(f"\n📄 Full Generated Code:")
        print(manim_code)
        
    except Exception as e:
        print(f"❌ Error during Manim code generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manim_generation()
