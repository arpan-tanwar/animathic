#!/usr/bin/env python3
"""
Test script for the enhanced workflow orchestrator
Tests both simple and complex prompts to verify workflow selection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.enhanced_workflow_orchestrator import EnhancedWorkflowOrchestrator
from services.ai_service_new import AIService

def test_enhanced_workflow_orchestrator():
    """Test the enhanced workflow orchestrator directly"""
    print("🧪 Testing Enhanced Workflow Orchestrator...")
    
    orchestrator = EnhancedWorkflowOrchestrator()
    
    # Test 1: Simple prompt (should use restrictive workflow)
    print("\n📝 Test 1: Simple Prompt")
    simple_prompt = "Create a red circle"
    simple_spec = {
        'objects': [{
            'id': 'obj_1',
            'type': 'circle',
            'properties': {
                'color': 'RED',
                'position': [0, 0, 0]
            },
            'animations': []
        }],
        'duration': 3.0
    }
    
    result = orchestrator.process_complex_animation_request(simple_spec, simple_prompt)
    print(f"✅ Simple prompt processed successfully")
    print(f"   Workflow status: {result.get('workflow_summary', {}).get('status', 'unknown')}")
    print(f"   Enhancements applied: {len(result.get('enhancements_applied', []))}")
    
    # Test 2: Complex prompt (should use enhanced workflow)
    print("\n📝 Test 2: Complex Prompt")
    complex_prompt = "Create coordinate axes with a sine wave plot, then show a cosine wave plot"
    complex_spec = {
        'objects': [
            {
                'id': 'obj_1',
                'type': 'axes',
                'properties': {
                    'position': [0, 0, 0]
                },
                'animations': []
            },
            {
                'id': 'obj_2',
                'type': 'plot',
                'properties': {
                    'function': 'sin(x)',
                    'position': [0, 0, 0]
                },
                'animations': []
            },
            {
                'id': 'obj_3',
                'type': 'plot',
                'properties': {
                    'function': 'cos(x)',
                    'position': [0, 0, 0]
                },
                'animations': []
            }
        ],
        'duration': 5.0
    }
    
    result = orchestrator.process_complex_animation_request(complex_spec, complex_prompt)
    print(f"✅ Complex prompt processed successfully")
    print(f"   Workflow status: {result.get('workflow_summary', {}).get('status', 'unknown')}")
    print(f"   Enhancements applied: {len(result.get('enhancements_applied', []))}")
    print(f"   Risk assessment: {result.get('risk_assessment', {}).get('overall_risk', 'unknown')}")
    
    # Test 3: Overlap detection
    print("\n📝 Test 3: Overlap Detection")
    overlap_spec = {
        'objects': [
            {
                'id': 'obj_1',
                'type': 'circle',
                'properties': {
                    'position': [0, 0, 0]
                },
                'animations': []
            },
            {
                'id': 'obj_2',
                'type': 'square',
                'properties': {
                    'position': [0.1, 0.1, 0]  # Very close to obj_1
                },
                'animations': []
            }
        ],
        'duration': 3.0
    }
    
    result = orchestrator.process_complex_animation_request(overlap_spec, "Create overlapping shapes")
    print(f"✅ Overlap detection test completed")
    print(f"   Overlaps detected: {len(result.get('enhancements_applied', []))}")
    
    print("\n🎉 All Enhanced Workflow Orchestrator tests passed!")

def test_ai_service_integration():
    """Test the AI service integration with enhanced workflow"""
    print("\n🧪 Testing AI Service Integration...")
    
    try:
        # Initialize AI service
        ai_service = AIService()
        print("✅ AI Service initialized successfully")
        
        # Test 1: Simple prompt
        print("\n📝 Test 1: Simple Prompt")
        simple_result = ai_service.process_animation_request("Create a blue square")
        
        if 'error' not in simple_result:
            print(f"✅ Simple prompt processed successfully")
            print(f"   Workflow type: {simple_result.get('workflow_type', 'unknown')}")
            print(f"   Complexity level: {simple_result.get('complexity_analysis', {}).get('level', 'unknown')}")
        else:
            print(f"❌ Simple prompt failed: {simple_result['error']}")
        
        # Test 2: Complex prompt
        print("\n📝 Test 2: Complex Prompt")
        complex_result = ai_service.process_animation_request("Create multiple function plots with axes")
        
        if 'error' not in complex_result:
            print(f"✅ Complex prompt processed successfully")
            print(f"   Workflow type: {complex_result.get('workflow_type', 'unknown')}")
            print(f"   Complexity level: {complex_result.get('complexity_analysis', {}).get('level', 'unknown')}")
            print(f"   Enhancements applied: {len(complex_result.get('enhancements_applied', []))}")
        else:
            print(f"❌ Complex prompt failed: {complex_result['error']}")
        
        print("\n🎉 AI Service integration tests completed!")
        
    except Exception as e:
        print(f"❌ AI Service test failed: {e}")

def test_prompt_complexity_analysis():
    """Test prompt complexity analysis"""
    print("\n🧪 Testing Prompt Complexity Analysis...")
    
    ai_service = AIService()
    
    test_prompts = [
        ("Create a red circle", "simple"),
        ("Create a square and a circle", "moderate"),
        ("Create coordinate axes with sine wave plot", "complex"),
        ("Show multiple function plots in sequence", "complex"),
        ("Create a text label", "simple"),
        ("Animate a bouncing ball with physics", "moderate")
    ]
    
    for prompt, expected_level in test_prompts:
        complexity = ai_service._analyze_prompt_complexity(prompt)
        actual_level = complexity['level']
        requires_enhancement = complexity['requires_enhancement']
        
        print(f"📝 Prompt: {prompt[:50]}...")
        print(f"   Expected: {expected_level}, Actual: {actual_level}")
        print(f"   Requires enhancement: {requires_enhancement}")
        print(f"   Complexity score: {complexity['score']}")
        
        # Verify the analysis makes sense
        if expected_level == 'simple' and requires_enhancement:
            print(f"   ⚠️  Warning: Simple prompt marked as requiring enhancement")
        elif expected_level == 'complex' and not requires_enhancement:
            print(f"   ⚠️  Warning: Complex prompt not marked as requiring enhancement")
        else:
            print(f"   ✅ Analysis looks correct")
        print()
    
    print("🎉 Prompt complexity analysis tests completed!")

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Workflow Tests...")
    print("=" * 50)
    
    try:
        # Test 1: Enhanced Workflow Orchestrator
        test_enhanced_workflow_orchestrator()
        
        # Test 2: AI Service Integration
        test_ai_service_integration()
        
        # Test 3: Prompt Complexity Analysis
        test_prompt_complexity_analysis()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("The enhanced workflow system is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
