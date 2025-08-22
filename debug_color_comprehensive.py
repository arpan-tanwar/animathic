#!/usr/bin/env python3
"""
Comprehensive color debugging script to identify where color is being lost
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.manim_code_generator import ManimCodeGenerator
from services.ai_service_new import AIService

def test_entire_color_pipeline():
    """Test the entire color pipeline from AI to Manim"""
    print("🔍 COMPREHENSIVE COLOR PIPELINE DEBUG")
    print("=" * 50)
    
    # Test 1: Direct Manim Code Generation
    print("\n📋 TEST 1: Direct Manim Code Generation")
    print("-" * 30)
    
    test_spec = {
        "animation_type": "geometric",
        "scene_description": "A red circle that fades in and then fades out.",
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
        "background_color": "#000000",
        "style": "modern"
    }
    
    print(f"Input spec color: {test_spec['objects'][0]['properties']['color']}")
    
    try:
        code_generator = ManimCodeGenerator()
        manim_code = code_generator.generate_manim_code(test_spec)
        
        print("✅ Manim code generated successfully")
        
        # Check for color-related code
        print("\n🔍 Color-related code analysis:")
        
        # Check imports
        if 'from manim import RED' in manim_code:
            print("✅ RED import found")
        else:
            print("❌ RED import missing")
        
        # Check color assignment
        if 'color = color_mapping.get' in manim_code:
            print("✅ Color mapping logic found")
        else:
            print("❌ Color mapping logic missing")
        
        # Check Circle creation
        if 'fill_color=color' in manim_code:
            print("✅ fill_color=color found")
        else:
            print("❌ fill_color=color missing")
        
        if 'stroke_color=color' in manim_code:
            print("✅ stroke_color=color found")
        else:
            print("❌ stroke_color=color missing")
        
        # Check set_fill and set_stroke calls
        if 'set_fill(' in manim_code:
            print("✅ set_fill call found")
        else:
            print("❌ set_fill call missing")
        
        if 'set_stroke(' in manim_code:
            print("✅ set_stroke call found")
        else:
            print("❌ set_stroke call missing")
        
        # Check debug prints
        if 'print(f"Color mapping' in manim_code:
            print("✅ Color debug prints found")
        else:
            print("❌ Color debug prints missing")
        
        # Show the critical color-related sections
        print("\n📄 Critical Color Code Sections:")
        lines = manim_code.split('\n')
        
        # Find color mapping section
        for i, line in enumerate(lines):
            if 'color_mapping = {' in line:
                print(f"\nColor mapping definition (line {i+1}):")
                for j in range(i, min(i+10, len(lines))):
                    if lines[j].strip():
                        print(f"  {j+1}: {lines[j].strip()}")
                break
        
        # Find Circle creation section
        for i, line in enumerate(lines):
            if 'Circle(' in line:
                print(f"\nCircle creation (line {i+1}):")
                for j in range(i, min(i+15, len(lines))):
                    if lines[j].strip():
                        print(f"  {j+1}: {lines[j].strip()}")
                break
        
        # Find color assignment section
        for i, line in enumerate(lines):
            if 'color = color_mapping.get' in line:
                print(f"\nColor assignment (line {i+1}):")
                for j in range(i, min(i+5, len(lines))):
                    if lines[j].strip():
                        print(f"  {j+1}: {lines[j].strip()}")
                break
        
        # Test 2: AI Service Integration
        print("\n\n📋 TEST 2: AI Service Integration")
        print("-" * 30)
        
        try:
            # Mock AI service without requiring API key
            print("Testing AI service workflow...")
            
            # Simulate the workflow manually
            prompt = "Create a red circle that fades in, then fades out"
            
            # This is what the AI would generate
            ai_generated_spec = {
                "animation_type": "geometric",
                "scene_description": "A red circle that fades in and then fades out.",
                "objects": [
                    {
                        "id": "red_circle",
                        "type": "circle",
                        "properties": {
                            "position": [0.0, 0.0, 0.0],
                            "color": "RED",  # AI generates uppercase
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
                "background_color": "#000000",
                "style": "modern"
            }
            
            print(f"AI generated spec color: {ai_generated_spec['objects'][0]['properties']['color']}")
            
            # Test complexity analysis
            print("\n🔍 Complexity Analysis:")
            complexity_indicators = {
                'animation_effects': any(keyword in prompt.lower() for keyword in 
                    ['fade', 'appear', 'disappear', 'animate', 'transition', 'effect']),
                'color_specifications': any(keyword in prompt.lower() for keyword in 
                    ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'color', 'colored'])
            }
            
            complexity_score = sum(complexity_indicators.values())
            print(f"Complexity score: {complexity_score}")
            print(f"Animation effects: {complexity_indicators['animation_effects']}")
            print(f"Color specifications: {complexity_indicators['color_specifications']}")
            
            # Test 3: Manim Code Execution Simulation
            print("\n\n📋 TEST 3: Manim Code Execution Simulation")
            print("-" * 30)
            
            # Extract the critical color logic from generated code
            print("Simulating color assignment logic...")
            
            # This is what should happen during execution
            color_name = "RED"  # From AI spec
            print(f"Color name from spec: {color_name}")
            
            # Color mapping lookup
            color_mapping = {
                'WHITE': 'WHITE_CONSTANT', 'BLACK': 'BLACK_CONSTANT', 'RED': 'RED_CONSTANT', 
                'GREEN': 'GREEN_CONSTANT', 'BLUE': 'BLUE_CONSTANT', 'YELLOW': 'YELLOW_CONSTANT'
            }
            
            print(f"Color mapping keys: {list(color_mapping.keys())}")
            print(f"Looking up: '{color_name}'")
            
            color = color_mapping.get(str(color_name), 'WHITE_CONSTANT')
            print(f"Color mapping result: '{color_name}' -> {color}")
            
            if color == 'RED_CONSTANT':
                print("✅ Color mapping successful - RED found")
            else:
                print(f"❌ Color mapping failed - got {color} instead of RED")
            
            # Test 4: Generated Code Analysis
            print("\n\n📋 TEST 4: Generated Code Analysis")
            print("-" * 30)
            
            # Check if the generated code has the right structure
            print("Analyzing generated code structure...")
            
            # Count color-related lines
            color_lines = [line for line in lines if 'color' in line.lower()]
            print(f"Total color-related lines: {len(color_lines)}")
            
            # Show all color-related lines
            print("\nAll color-related lines:")
            for i, line in enumerate(lines):
                if 'color' in line.lower():
                    print(f"  {i+1}: {line.strip()}")
            
            # Test 5: Potential Issues
            print("\n\n📋 TEST 5: Potential Issues Analysis")
            print("-" * 30)
            
            issues = []
            
            # Check for case sensitivity issues
            if 'RED' in manim_code and 'red' in manim_code:
                issues.append("Mixed case color references found")
            
            # Check for missing color constants
            if 'from manim import RED' not in manim_code:
                issues.append("RED constant not imported")
            
            # Check for color override
            if 'color = WHITE' in manim_code:
                issues.append("Color being set to WHITE somewhere")
            
            # Check for exception handling that defaults to WHITE
            if 'except Exception:' in manim_code and 'WHITE' in manim_code:
                issues.append("Broad exception handling that might default to WHITE")
            
            if issues:
                print("❌ Issues found:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("✅ No obvious issues found")
            
            # Show the full generated code for manual inspection
            print("\n\n📄 FULL GENERATED CODE:")
            print("=" * 50)
            print(manim_code)
            
        except Exception as e:
            print(f"❌ Error in AI service test: {e}")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"❌ Error in Manim code generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_entire_color_pipeline()
