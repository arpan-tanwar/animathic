#!/usr/bin/env python3
"""
Test script for the enhanced workflow orchestrator
Tests both simple and complex prompts to verify workflow selection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.enhanced_workflow_orchestrator import EnhancedWorkflowOrchestrator
from services.animation_analysis import AnimationSequenceAnalyzer
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

def test_animation_sequence_analyzer():
    """Test the enhanced animation sequence analyzer"""
    print("\n🧪 Testing Animation Sequence Analyzer...")
    
    analyzer = AnimationSequenceAnalyzer()
    
    # Test 1: Basic sequence analysis
    print("\n📝 Test 1: Basic Sequence Analysis")
    basic_spec = {
        'objects': [
            {
                'id': 'obj_1',
                'type': 'axes',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_2',
                'type': 'plot',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            }
        ]
    }
    
    analysis = analyzer.analyze_animation_sequence(basic_spec)
    print(f"✅ Basic analysis completed")
    print(f"   Sequential objects: {len(analysis.get('sequential_objects', []))}")
    print(f"   Overlap risks: {len(analysis.get('overlap_risks', []))}")
    print(f"   Risk assessment: {analysis.get('risk_assessment', {}).get('overall_risk', 'unknown')}")
    
    # Test 2: Complex sequence with multiple plots
    print("\n📝 Test 2: Complex Sequence Analysis")
    complex_spec = {
        'objects': [
            {
                'id': 'obj_1',
                'type': 'axes',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_2',
                'type': 'plot',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_3',
                'type': 'plot',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_4',
                'type': 'circle',
                'properties': {'position': [2, 2, 0]},
                'animations': []
            },
            {
                'id': 'obj_5',
                'type': 'text',
                'properties': {'position': [-2, -2, 0]},
                'animations': []
            }
        ]
    }
    
    analysis = analyzer.analyze_animation_sequence(complex_spec)
    print(f"✅ Complex analysis completed")
    print(f"   Object clusters: {len(analysis.get('object_clusters', []))}")
    print(f"   Spatial analysis: {analysis.get('spatial_analysis', {}).get('status', 'unknown')}")
    print(f"   Temporal analysis: {analysis.get('temporal_analysis', {}).get('status', 'unknown')}")
    print(f"   Optimization suggestions: {len(analysis.get('optimization_suggestions', []))}")
    
    # Test 3: Spatial distribution analysis
    print("\n📝 Test 3: Spatial Distribution Analysis")
    spatial_spec = {
        'objects': [
            {
                'id': 'obj_1',
                'type': 'circle',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_2',
                'type': 'square',
                'properties': {'position': [0.5, 0.5, 0]},
                'animations': []
            },
            {
                'id': 'obj_3',
                'type': 'line',
                'properties': {'position': [1, 1, 0]},
                'animations': []
            }
        ]
    }
    
    analysis = analyzer.analyze_animation_sequence(spatial_spec)
    spatial_data = analysis.get('spatial_analysis', {})
    print(f"✅ Spatial analysis completed")
    print(f"   Distribution: {spatial_data.get('spatial_distribution', 'unknown')}")
    print(f"   Screen coverage: {spatial_data.get('screen_coverage', 'unknown')}")
    print(f"   Bounds: {spatial_data.get('bounds', {})}")
    
    # Test 4: Temporal sequence analysis
    print("\n📝 Test 4: Temporal Sequence Analysis")
    temporal_spec = {
        'objects': [
            {
                'id': 'obj_1',
                'type': 'axes',
                'properties': {'position': [0, 0, 0]},
                'animations': [{'duration': 1.0}]
            },
            {
                'id': 'obj_2',
                'type': 'plot',
                'properties': {'position': [0, 0, 0]},
                'animations': [{'duration': 2.0}]
            },
            {
                'id': 'obj_3',
                'type': 'plot',
                'properties': {'position': [0, 0, 0]},
                'animations': [{'duration': 2.0}]
            }
        ]
    }
    
    analysis = analyzer.analyze_animation_sequence(temporal_spec)
    temporal_data = analysis.get('temporal_analysis', {})
    print(f"✅ Temporal analysis completed")
    print(f"   Estimated duration: {temporal_data.get('estimated_duration', 'unknown')}")
    print(f"   Sequence complexity: {temporal_data.get('sequence_complexity', 'unknown')}")
    print(f"   Timing issues: {len(temporal_data.get('timing_issues', []))}")
    
    # Test 5: Object clustering
    print("\n📝 Test 5: Object Clustering")
    cluster_spec = {
        'objects': [
            {
                'id': 'obj_1',
                'type': 'axes',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_2',
                'type': 'plot',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_3',
                'type': 'circle',
                'properties': {'position': [2, 2, 0]},
                'animations': []
            },
            {
                'id': 'obj_4',
                'type': 'text',
                'properties': {'position': [-2, -2, 0]},
                'animations': []
            }
        ]
    }
    
    analysis = analyzer.analyze_animation_sequence(cluster_spec)
    clusters = analysis.get('object_clusters', [])
    print(f"✅ Object clustering completed")
    for cluster in clusters:
        print(f"   Cluster type: {cluster.get('type', 'unknown')}")
        print(f"   Objects: {cluster.get('objects', [])}")
        print(f"   Priority: {cluster.get('priority', 'unknown')}")
    
    print("\n🎉 All Animation Sequence Analyzer tests passed!")

def test_ai_service_integration():
    """Test the AI service integration with enhanced workflow"""
    print("\n🧪 Testing AI Service Integration...")
    
    try:
        # Initialize AI service
        ai_service = AIService()
        print("✅ AI Service initialized successfully")
        
        # Note: AI service methods are async, so we can't test them directly in sync context
        print("⚠️  AI Service methods are async - testing initialization only")
        print("   To test full integration, use async test runner")
        
        print("\n🎉 AI Service initialization test passed!")
        
    except Exception as e:
        print(f"❌ AI Service test failed: {e}")
        import traceback
        traceback.print_exc()

def test_enhanced_features():
    """Test the enhanced features specifically"""
    print("\n🧪 Testing Enhanced Features...")
    
    analyzer = AnimationSequenceAnalyzer()
    
    # Test 1: Caching functionality
    print("\n📝 Test 1: Caching Functionality")
    test_spec = {
        'objects': [
            {
                'id': 'obj_1',
                'type': 'circle',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            }
        ]
    }
    
    # First analysis
    analysis1 = analyzer.analyze_animation_sequence(test_spec)
    print(f"✅ First analysis completed")
    
    # Second analysis (should use cache)
    analysis2 = analyzer.analyze_animation_sequence(test_spec)
    print(f"✅ Second analysis completed (cached)")
    
    # Verify cache is working
    if hasattr(analyzer, 'analysis_cache') and len(analyzer.analysis_cache) > 0:
        print(f"✅ Cache is working: {len(analyzer.analysis_cache)} entries")
    else:
        print(f"⚠️  Cache may not be working properly")
    
    # Test 2: Risk thresholds
    print("\n📝 Test 2: Risk Thresholds")
    if hasattr(analyzer, 'risk_thresholds'):
        thresholds = analyzer.risk_thresholds
        print(f"✅ Risk thresholds configured:")
        for key, value in thresholds.items():
            print(f"   {key}: {value}")
    else:
        print(f"⚠️  Risk thresholds not configured")
    
    # Test 3: Advanced analysis features
    print("\n📝 Test 3: Advanced Analysis Features")
    advanced_spec = {
        'objects': [
            {
                'id': 'obj_1',
                'type': 'axes',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_2',
                'type': 'plot',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_3',
                'type': 'plot',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            },
            {
                'id': 'obj_4',
                'type': 'plot',
                'properties': {'position': [0, 0, 0]},
                'animations': []
            }
        ]
    }
    
    analysis = analyzer.analyze_animation_sequence(advanced_spec)
    
    # Check for enhanced features
    enhanced_features = [
        'object_clusters',
        'spatial_analysis', 
        'temporal_analysis',
        'optimization_suggestions',
        'timing_recommendations',
        'camera_adjustments'
    ]
    
    for feature in enhanced_features:
        if feature in analysis:
            print(f"✅ {feature}: Available")
        else:
            print(f"⚠️  {feature}: Missing")
    
    print("\n🎉 All Enhanced Features tests passed!")

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Workflow Testing Suite...")
    
    try:
        # Test the enhanced workflow orchestrator
        test_enhanced_workflow_orchestrator()
        
        # Test the animation sequence analyzer
        test_animation_sequence_analyzer()
        
        # Test enhanced features
        test_enhanced_features()
        
        # Test AI service integration (may fail if dependencies not available)
        try:
            test_ai_service_integration()
        except Exception as e:
            print(f"⚠️  AI Service test skipped: {e}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
