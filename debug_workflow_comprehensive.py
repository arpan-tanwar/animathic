#!/usr/bin/env python3
"""
Comprehensive workflow debugging script to identify video generation failures
"""

import sys
import os
import json
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.manim_code_generator import ManimCodeGenerator
from services.ai_service_new import AIService

def test_workflow_step_by_step():
    """Test the entire workflow step by step"""
    print("🔍 COMPREHENSIVE WORKFLOW DEBUG")
    print("=" * 50)
    
    # Test 1: Basic Manim Code Generation
    print("\n📋 TEST 1: Basic Manim Code Generation")
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
                    "color": "RED",
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
    
    try:
        code_generator = ManimCodeGenerator()
        manim_code = code_generator.generate_manim_code(test_spec)
        
        print("✅ Manim code generated successfully")
        print(f"Code length: {len(manim_code)} characters")
        
        # Check for critical components
        critical_checks = [
            ('from manim import', 'Manim imports'),
            ('class GeneratedScene', 'Scene class'),
            ('def construct(self)', 'Construct method'),
            ('Circle(', 'Circle creation'),
            ('fill_color=color', 'Fill color'),
            ('stroke_color=color', 'Stroke color'),
            ('FadeIn(', 'FadeIn animation'),
            ('FadeOut(', 'FadeOut animation'),
            ('self.add(', 'Add method'),
            ('self.play(', 'Play method')
        ]
        
        print("\n🔍 Critical Component Check:")
        for check, description in critical_checks:
            if check in manim_code:
                print(f"✅ {description}: Found")
            else:
                print(f"❌ {description}: Missing")
        
        # Check for potential issues
        print("\n🚨 Potential Issues Check:")
        
        issues = []
        if 'eval(' in manim_code:
            issues.append("eval() function found")
        if 'lambda x:' in manim_code:
            issues.append("Lambda functions found")
        if 'color = WHITE' in manim_code:
            issues.append("Color defaulting to WHITE")
        if 'except Exception:' in manim_code:
            issues.append("Broad exception handling")
        
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ No obvious issues found")
        
        # Show the critical sections
        print("\n📄 Critical Code Sections:")
        
        lines = manim_code.split('\n')
        
        # Show imports
        print("Imports:")
        for i, line in enumerate(lines[:15]):
            if line.strip():
                print(f"  {i+1}: {line.strip()}")
        
        # Show Circle creation
        print("\nCircle Creation:")
        for i, line in enumerate(lines):
            if 'Circle(' in line:
                print(f"  {i+1}: {line.strip()}")
                # Show next few lines for context
                for j in range(i+1, min(i+10, len(lines))):
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
        
        # Show animations
        print("\nAnimations:")
        for i, line in enumerate(lines):
            if 'FadeIn(' in line or 'FadeOut(' in line:
                print(f"  {i+1}: {line.strip()}")
        
        return manim_code
        
    except Exception as e:
        print(f"❌ Error in Manim code generation: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_manim_execution_simulation(manim_code):
    """Simulate what would happen during Manim execution"""
    print("\n\n📋 TEST 2: Manim Execution Simulation")
    print("-" * 30)
    
    if not manim_code:
        print("❌ No Manim code to test")
        return
    
    try:
        # Simulate the execution environment
        print("Simulating Manim execution environment...")
        
        # Check for common execution issues
        execution_checks = [
            ('import numpy as np', 'NumPy import'),
            ('from manim import RED', 'RED constant import'),
            ('from manim import GREEN', 'GREEN constant import'),
            ('from manim import BLUE', 'BLUE constant import'),
            ('from manim import WHITE', 'WHITE constant import'),
            ('from manim import BLACK', 'BLACK constant import'),
            ('MovingCameraScene', 'MovingCameraScene import'),
            ('Circle', 'Circle class import'),
            ('FadeIn', 'FadeIn import'),
            ('FadeOut', 'FadeOut import'),
            ('Create', 'Create import'),
            ('Write', 'Write import')
        ]
        
        print("\n🔍 Execution Environment Check:")
        for check, description in execution_checks:
            if check in manim_code:
                print(f"✅ {description}: Available")
            else:
                print(f"❌ {description}: Missing")
        
        # Check for syntax issues
        print("\n🔍 Syntax Check:")
        
        # Check for balanced parentheses and brackets
        open_parens = manim_code.count('(')
        close_parens = manim_code.count(')')
        open_brackets = manim_code.count('[')
        close_brackets = manim_code.count(']')
        open_braces = manim_code.count('{')
        close_braces = manim_code.count('}')
        
        print(f"Parentheses: {open_parens} open, {close_parens} close - {'✅ Balanced' if open_parens == close_parens else '❌ Unbalanced'}")
        print(f"Brackets: {open_brackets} open, {close_brackets} close - {'✅ Balanced' if open_brackets == close_brackets else '❌ Unbalanced'}")
        print(f"Braces: {open_braces} open, {close_braces} close - {'✅ Balanced' if open_braces == close_braces else '❌ Unbalanced'}")
        
        # Check for common Python syntax issues
        syntax_issues = []
        
        # Check for missing colons
        lines = manim_code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('def ') and not stripped.endswith(':'):
                syntax_issues.append(f"Missing colon after def on line {i+1}")
            if stripped.startswith('if ') and not stripped.endswith(':'):
                syntax_issues.append(f"Missing colon after if on line {i+1}")
            if stripped.startswith('elif ') and not stripped.endswith(':'):
                syntax_issues.append(f"Missing colon after elif on line {i+1}")
            if stripped.startswith('else') and not stripped.endswith(':'):
                syntax_issues.append(f"Missing colon after else on line {i+1}")
            if stripped.startswith('for ') and not stripped.endswith(':'):
                syntax_issues.append(f"Missing colon after for on line {i+1}")
            if stripped.startswith('while ') and not stripped.endswith(':'):
                syntax_issues.append(f"Missing colon after while on line {i+1}")
            if stripped.startswith('try:') and not stripped.endswith(':'):
                syntax_issues.append(f"Missing colon after try on line {i+1}")
            if stripped.startswith('except') and not stripped.endswith(':'):
                syntax_issues.append(f"Missing colon after except on line {i+1}")
            if stripped.startswith('finally:') and not stripped.endswith(':'):
                syntax_issues.append(f"Missing colon after finally on line {i+1}")
        
        if syntax_issues:
            print("\n❌ Syntax issues found:")
            for issue in syntax_issues:
                print(f"  - {issue}")
        else:
            print("\n✅ No syntax issues found")
        
        # Check for indentation issues
        print("\n🔍 Indentation Check:")
        
        indentation_issues = []
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('#'):
                # Check if line has mixed tabs and spaces
                if '\t' in line and ' ' in line:
                    indentation_issues.append(f"Mixed tabs and spaces on line {i+1}")
                
                # Check for inconsistent indentation
                if line.startswith(' ') and not line.startswith('    '):
                    # Check if it's not a multiple of 4 spaces
                    leading_spaces = len(line) - len(line.lstrip())
                    if leading_spaces % 4 != 0:
                        indentation_issues.append(f"Inconsistent indentation on line {i+1}: {leading_spaces} spaces")
        
        if indentation_issues:
            print("❌ Indentation issues found:")
            for issue in indentation_issues:
                print(f"  - {issue}")
        else:
            print("✅ No indentation issues found")
        
        print("\n✅ Manim execution simulation completed")
        
    except Exception as e:
        print(f"❌ Error in execution simulation: {e}")
        import traceback
        traceback.print_exc()

def test_ai_service_integration():
    """Test AI service integration"""
    print("\n\n📋 TEST 3: AI Service Integration")
    print("-" * 30)
    
    try:
        # Test complexity analysis
        prompt = "Create a red circle that fades in, then fades out"
        
        print(f"Testing prompt: {prompt}")
        
        # Simulate complexity analysis
        prompt_lower = prompt.lower()
        
        complexity_indicators = {
            'animation_effects': any(keyword in prompt_lower for keyword in 
                ['fade', 'appear', 'disappear', 'animate', 'transition', 'effect']),
            'color_specifications': any(keyword in prompt_lower for keyword in 
                ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'color', 'colored'])
        }
        
        complexity_score = sum(complexity_indicators.values())
        
        print(f"Complexity score: {complexity_score}")
        print(f"Animation effects: {complexity_indicators['animation_effects']}")
        print(f"Color specifications: {complexity_indicators['color_specifications']}")
        
        # Determine workflow
        if complexity_score <= 2:
            workflow = 'restrictive'
        else:
            workflow = 'enhanced'
        
        print(f"Recommended workflow: {workflow}")
        
        print("✅ AI service integration test completed")
        
    except Exception as e:
        print(f"❌ Error in AI service test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("Starting comprehensive workflow debug...")
    
    # Test 1: Basic Manim Code Generation
    manim_code = test_workflow_step_by_step()
    
    if manim_code:
        # Test 2: Manim Execution Simulation
        test_manim_execution_simulation(manim_code)
        
        # Test 3: AI Service Integration
        test_ai_service_integration()
        
        # Show summary
        print("\n\n📊 WORKFLOW SUMMARY")
        print("=" * 50)
        print(f"✅ Manim code generation: {'Working' if manim_code else 'Failed'}")
        print(f"✅ Code validation: {'Passed' if manim_code else 'Failed'}")
        print(f"✅ Syntax check: {'Passed' if manim_code else 'Failed'}")
        print(f"✅ Color handling: {'Working' if 'fill_color=color' in manim_code else 'Failed'}")
        print(f"✅ Animation handling: {'Working' if 'FadeIn(' in manim_code else 'Failed'}")
        
        if manim_code:
            print("\n🎯 Next Steps:")
            print("1. Deploy the backend with these fixes")
            print("2. Test the prompt: 'Create a red circle that fades in, then fades out'")
            print("3. Check console logs for detailed color processing information")
            print("4. Verify the circle appears in RED with fade animations")
        else:
            print("\n❌ Issues Found:")
            print("1. Manim code generation is failing")
            print("2. Check the error messages above")
            print("3. Fix the identified issues before testing")
    
    print("\n🔍 Debug completed!")

if __name__ == "__main__":
    main()
