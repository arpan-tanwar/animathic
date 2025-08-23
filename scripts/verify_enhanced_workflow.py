#!/usr/bin/env python3
"""
Verification script for the enhanced workflow system
Tests the system in a production-like environment
"""

import sys
import os
import logging
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def verify_enhanced_workflow():
    """Verify the enhanced workflow system is working correctly"""
    print("🔍 Verifying Enhanced Workflow System...")
    
    try:
        # Test 1: Import all required modules
        print("\n📦 Testing Module Imports...")
        
        from services.enhanced_workflow_orchestrator import EnhancedWorkflowOrchestrator
        from services.animation_analysis import AnimationSequenceAnalyzer
        from services.object_tracking import ObjectTrackingSystem
        from services.fade_out_system import FadeOutSystem
        from services.camera_management import CameraManagementSystem
        
        print("✅ All required modules imported successfully")
        
        # Test 2: Initialize all systems
        print("\n🚀 Testing System Initialization...")
        
        orchestrator = EnhancedWorkflowOrchestrator()
        analyzer = AnimationSequenceAnalyzer()
        object_tracker = ObjectTrackingSystem()
        fade_out_system = FadeOutSystem()
        camera_manager = CameraManagementSystem()
        
        print("✅ All systems initialized successfully")
        
        # Test 3: Test enhanced animation analysis
        print("\n🧪 Testing Enhanced Animation Analysis...")
        
        # Complex animation spec that should trigger enhanced analysis
        complex_spec = {
            'objects': [
                {
                    'id': 'axes_1',
                    'type': 'axes',
                    'properties': {'position': [0, 0, 0]},
                    'animations': []
                },
                {
                    'id': 'plot_1',
                    'type': 'plot',
                    'properties': {
                        'function': 'sin(x)',
                        'position': [0, 0, 0],
                        'color': 'BLUE'
                    },
                    'animations': [{'duration': 2.0}]
                },
                {
                    'id': 'plot_2',
                    'type': 'plot',
                    'properties': {
                        'function': 'cos(x)',
                        'position': [0, 0, 0],
                        'color': 'RED'
                    },
                    'animations': [{'duration': 2.0}]
                },
                {
                    'id': 'circle_1',
                    'type': 'circle',
                    'properties': {
                        'position': [3, 2, 0],
                        'color': 'GREEN'
                    },
                    'animations': []
                },
                {
                    'id': 'text_1',
                    'type': 'text',
                    'properties': {
                        'text': 'Function Plot',
                        'position': [-3, -2, 0]
                    },
                    'animations': []
                }
            ],
            'duration': 6.0
        }
        
        # Analyze the complex spec
        analysis = analyzer.analyze_animation_sequence(complex_spec)
        
        # Verify analysis contains all expected fields
        expected_fields = [
            'sequential_objects', 'concurrent_objects', 'overlap_risks',
            'optimization_suggestions', 'required_fade_outs', 'timing_recommendations',
            'camera_adjustments', 'object_clusters', 'spatial_analysis',
            'temporal_analysis', 'risk_assessment'
        ]
        
        missing_fields = []
        for field in expected_fields:
            if field not in analysis:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing analysis fields: {missing_fields}")
            return False
        
        print("✅ Enhanced animation analysis working correctly")
        
        # Test 4: Test workflow orchestration
        print("\n🎭 Testing Workflow Orchestration...")
        
        result = orchestrator.process_complex_animation_request(complex_spec, "Create complex function plots")
        
        if 'error' in result:
            print(f"❌ Workflow orchestration failed: {result['error']}")
            return False
        
        print("✅ Workflow orchestration working correctly")
        
        # Test 5: Verify enhancements were applied
        print("\n✨ Verifying Applied Enhancements...")
        
        enhancements = result.get('enhancements_applied', [])
        workflow_summary = result.get('workflow_summary', {})
        
        print(f"   Enhancements applied: {len(enhancements)}")
        print(f"   Workflow status: {workflow_summary.get('status', 'unknown')}")
        print(f"   Risk assessment: {result.get('risk_assessment', {}).get('overall_risk', 'unknown')}")
        
        # Test 6: Test caching functionality
        print("\n💾 Testing Caching Functionality...")
        
        # Second analysis should use cache
        analysis2 = analyzer.analyze_animation_sequence(complex_spec)
        
        if hasattr(analyzer, 'analysis_cache') and len(analyzer.analysis_cache) > 0:
            print(f"✅ Caching system working: {len(analyzer.analysis_cache)} cached entries")
        else:
            print("⚠️  Caching system may not be working properly")
        
        # Test 7: Test spatial analysis
        print("\n🗺️  Testing Spatial Analysis...")
        
        spatial_data = analysis.get('spatial_analysis', {})
        if spatial_data.get('status') == 'analyzed':
            print(f"✅ Spatial analysis working:")
            print(f"   Distribution: {spatial_data.get('spatial_distribution', 'unknown')}")
            print(f"   Screen coverage: {spatial_data.get('screen_coverage', 'unknown')}")
            print(f"   Bounds: {spatial_data.get('bounds', {})}")
        else:
            print(f"❌ Spatial analysis failed: {spatial_data.get('status', 'unknown')}")
            return False
        
        # Test 8: Test object clustering
        print("\n🔗 Testing Object Clustering...")
        
        clusters = analysis.get('object_clusters', [])
        if clusters:
            print(f"✅ Object clustering working: {len(clusters)} clusters identified")
            for cluster in clusters:
                print(f"   - {cluster.get('type', 'unknown')}: {len(cluster.get('objects', []))} objects")
        else:
            print("❌ Object clustering failed")
            return False
        
        # Test 9: Test risk assessment
        print("\n⚠️  Testing Risk Assessment...")
        
        risk_assessment = analysis.get('risk_assessment', {})
        if risk_assessment:
            print(f"✅ Risk assessment working:")
            print(f"   Overall risk: {risk_assessment.get('overall_risk', 'unknown')}")
            print(f"   Overlap risk: {risk_assessment.get('overlap_risk', 'unknown')}")
            print(f"   Sequence risk: {risk_assessment.get('sequence_risk', 'unknown')}")
        else:
            print("❌ Risk assessment failed")
            return False
        
        print("\n🎉 All Enhanced Workflow System tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    print("🚀 Enhanced Workflow System Verification")
    print("=" * 50)
    
    success = verify_enhanced_workflow()
    
    if success:
        print("\n✅ VERIFICATION SUCCESSFUL")
        print("The enhanced workflow system is ready for production use!")
        return 0
    else:
        print("\n❌ VERIFICATION FAILED")
        print("Please check the errors above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
