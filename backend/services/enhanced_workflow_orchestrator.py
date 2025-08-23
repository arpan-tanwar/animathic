"""
Enhanced Workflow Orchestrator for Animathic
Integrates all enhanced systems for optimal complex prompt handling
"""

import logging
from typing import Dict, Any, List, Optional
from .object_tracking import ObjectTrackingSystem
from .animation_analysis import AnimationSequenceAnalyzer
from .fade_out_system import FadeOutSystem
from .camera_management import CameraManagementSystem

logger = logging.getLogger(__name__)


class EnhancedWorkflowOrchestrator:
    """Orchestrates all enhanced systems for optimal animation generation"""
    
    def __init__(self):
        """Initialize the enhanced workflow orchestrator"""
        self.object_tracker = ObjectTrackingSystem()
        self.animation_analyzer = AnimationSequenceAnalyzer()
        self.fade_out_system = FadeOutSystem()
        self.camera_manager = CameraManagementSystem()
        
        # Workflow configuration
        self.config = {
            'enable_smart_positioning': True,
            'enable_overlap_prevention': True,
            'enable_camera_optimization': True,
            'enable_sequence_optimization': True,
            'validation_level': 'comprehensive',  # 'minimal', 'standard', 'comprehensive'
            'performance_mode': 'balanced'  # 'fast', 'balanced', 'quality'
        }
    
    def process_complex_animation_request(self, animation_spec: Dict[str, Any], user_prompt: str) -> Dict[str, Any]:
        """Process complex animation requests with enhanced intelligence"""
        try:
            logger.debug("Starting enhanced workflow processing for complex animation")
            
            # Phase 1: Pre-processing analysis
            pre_analysis = self._perform_pre_processing_analysis(animation_spec, user_prompt)
            
            # Phase 2: Object positioning optimization
            if self.config['enable_smart_positioning']:
                animation_spec = self._optimize_object_positions(animation_spec, pre_analysis)
            
            # Phase 3: Overlap detection and prevention
            if self.config['enable_overlap_prevention']:
                animation_spec = self._prevent_object_overlaps(animation_spec, pre_analysis)
            
            # Phase 4: Sequence optimization
            if self.config['enable_sequence_optimization']:
                animation_spec = self._optimize_animation_sequence(animation_spec, pre_analysis)
            
            # Phase 5: Camera strategy optimization
            if self.config['enable_camera_optimization']:
                camera_strategy = self._optimize_camera_strategy(animation_spec, pre_analysis)
                animation_spec['camera_strategy'] = camera_strategy
            
            # Phase 6: Final validation and enhancement
            final_spec = self._perform_final_validation(animation_spec, pre_analysis)
            
            # Phase 7: Generate workflow summary
            workflow_summary = self._generate_workflow_summary(pre_analysis, final_spec)
            
            return {
                'enhanced_animation_spec': final_spec,
                'workflow_summary': workflow_summary,
                'enhancements_applied': self._get_applied_enhancements(pre_analysis),
                'risk_assessment': pre_analysis.get('risk_assessment', {}),
                'performance_metrics': self._calculate_performance_metrics(pre_analysis),
                'processing_metadata': {
                    'pre_analysis': pre_analysis,
                    'processing_time': 'optimized',
                    'enhancement_count': len(self._get_applied_enhancements(pre_analysis)),
                    'complexity_score': pre_analysis.get('prompt_complexity', {}).get('score', 0)
                },
                'workflow_type': 'enhanced_complex_animation'
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced workflow processing: {e}")
            return {
                'error': str(e),
                'enhanced_animation_spec': animation_spec,
                'workflow_summary': {'status': 'error', 'message': str(e)}
            }
    
    def _perform_pre_processing_analysis(self, animation_spec: Dict[str, Any], user_prompt: str) -> Dict[str, Any]:
        """Perform comprehensive pre-processing analysis"""
        analysis = {
            'prompt_complexity': self._analyze_prompt_complexity(user_prompt),
            'object_analysis': self._analyze_objects(animation_spec),
            'sequence_analysis': self.animation_analyzer.analyze_animation_sequence(animation_spec),
            'overlap_risks': self._assess_overlap_risks(animation_spec),
            'performance_considerations': self._assess_performance_considerations(animation_spec),
            'risk_assessment': {},
            'optimization_opportunities': []
        }
        
        # Perform risk assessment
        analysis['risk_assessment'] = self._perform_comprehensive_risk_assessment(analysis)
        
        # Identify optimization opportunities
        analysis['optimization_opportunities'] = self._identify_optimization_opportunities(analysis)
        
        return analysis
    
    def _analyze_prompt_complexity(self, user_prompt: str) -> Dict[str, Any]:
        """Analyze the complexity of the user prompt"""
        complexity_indicators = {
            'mathematical_content': any(keyword in user_prompt.lower() for keyword in ['function', 'plot', 'graph', 'equation', 'formula']),
            'multiple_objects': any(keyword in user_prompt.lower() for keyword in ['multiple', 'several', 'many', 'various']),
            'sequence_requirements': any(keyword in user_prompt.lower() for keyword in ['sequence', 'step', 'progression', 'evolution']),
            'interaction_requirements': any(keyword in user_prompt.lower() for keyword in ['interact', 'connect', 'relate', 'combine']),
            'temporal_aspects': any(keyword in user_prompt.lower() for keyword in ['time', 'duration', 'speed', 'timing'])
        }
        
        complexity_score = sum(complexity_indicators.values())
        complexity_level = 'simple' if complexity_score <= 1 else 'moderate' if complexity_score <= 3 else 'complex'
        
        return {
            'level': complexity_level,
            'score': complexity_score,
            'indicators': complexity_indicators,
            'requires_enhancement': complexity_score >= 2
        }
    
    def _analyze_objects(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze objects in the animation specification"""
        objects = animation_spec.get('objects', [])
        
        analysis = {
            'total_objects': len(objects),
            'object_types': {},
            'spatial_distribution': {},
            'complexity_factors': {},
            'potential_issues': []
        }
        
        # Analyze object types
        for obj in objects:
            obj_type = obj.get('type', 'unknown')
            if obj_type not in analysis['object_types']:
                analysis['object_types'][obj_type] = 0
            analysis['object_types'][obj_type] += 1
        
        # Analyze spatial distribution
        positions = [obj.get('properties', {}).get('position', [0, 0, 0]) for obj in objects]
        if positions:
            x_coords = [pos[0] for pos in positions if len(pos) > 0]
            y_coords = [pos[1] for pos in positions if len(pos) > 1]
            
            if x_coords:
                analysis['spatial_distribution']['x_range'] = [min(x_coords), max(x_coords)]
            if y_coords:
                analysis['spatial_distribution']['y_range'] = [min(y_coords), max(y_coords)]
        
        # Identify potential issues
        if len(objects) > 5:
            analysis['potential_issues'].append('many_objects_may_cause_clutter')
        
        if any(obj.get('type') in ['plot', 'function', 'graph'] for obj in objects):
            analysis['potential_issues'].append('mathematical_objects_may_overlap')
        
        return analysis
    
    def _assess_overlap_risks(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential overlap risks"""
        objects = animation_spec.get('objects', [])
        
        if len(objects) <= 1:
            return {'risk_level': 'none', 'overlaps': [], 'risk_factors': []}
        
        risk_factors = []
        overlaps = []
        
        for i, obj1 in enumerate(objects):
            pos1 = obj1.get('properties', {}).get('position', [0, 0, 0])
            type1 = obj1.get('type', 'unknown')
            
            for j, obj2 in enumerate(objects[i+1:], i+1):
                pos2 = obj2.get('properties', {}).get('position', [0, 0, 0])
                type2 = obj2.get('type', 'unknown')
                
                # Calculate distance
                if len(pos1) >= 2 and len(pos2) >= 2:
                    distance = ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
                    
                    # Assess risk based on distance and types
                    if distance < 1.0:
                        risk_level = 'high' if type1 == type2 else 'medium'
                        overlaps.append({
                            'object1': {'id': obj1.get('id', f'obj_{i}'), 'type': type1, 'position': pos1},
                            'object2': {'id': obj2.get('id', f'obj_{j}'), 'type': type2, 'position': pos2},
                            'distance': distance,
                            'risk_level': risk_level
                        })
                        
                        if risk_level == 'high':
                            risk_factors.append(f'identical_objects_too_close_{type1}')
                        else:
                            risk_factors.append(f'different_objects_too_close_{type1}_{type2}')
        
        # Determine overall risk level
        if any(o['risk_level'] == 'high' for o in overlaps):
            overall_risk = 'high'
        elif overlaps:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        return {
            'risk_level': overall_risk,
            'overlaps': overlaps,
            'risk_factors': risk_factors,
            'requires_intervention': overall_risk in ['high', 'medium']
        }
    
    def _assess_performance_considerations(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Assess performance considerations for the animation"""
        objects = animation_spec.get('objects', [])
        
        performance_metrics = {
            'object_count': len(objects),
            'complexity_score': 0,
            'rendering_estimate': 'fast',
            'memory_usage': 'low',
            'recommendations': []
        }
        
        # Calculate complexity score
        for obj in objects:
            obj_type = obj.get('type', 'unknown')
            if obj_type in ['plot', 'function', 'graph']:
                performance_metrics['complexity_score'] += 3
            elif obj_type in ['axes', 'text']:
                performance_metrics['complexity_score'] += 1
            else:
                performance_metrics['complexity_score'] += 2
        
        # Determine rendering estimate
        if performance_metrics['complexity_score'] <= 3:
            performance_metrics['rendering_estimate'] = 'fast'
            performance_metrics['memory_usage'] = 'low'
        elif performance_metrics['complexity_score'] <= 8:
            performance_metrics['rendering_estimate'] = 'moderate'
            performance_metrics['memory_usage'] = 'medium'
        else:
            performance_metrics['rendering_estimate'] = 'slow'
            performance_metrics['memory_usage'] = 'high'
        
        # Generate recommendations
        if performance_metrics['complexity_score'] > 8:
            performance_metrics['recommendations'].append('consider_batching_animations')
            performance_metrics['recommendations'].append('optimize_object_positions')
        
        if len(objects) > 5:
            performance_metrics['recommendations'].append('use_sequential_display')
        
        return performance_metrics
    
    def _perform_comprehensive_risk_assessment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        risk_assessment = {
            'overall_risk': 'low',
            'risk_factors': [],
            'mitigation_strategies': [],
            'priority_actions': []
        }
        
        # Assess overlap risks
        overlap_risks = analysis.get('overlap_risks', {})
        if overlap_risks.get('requires_intervention', False):
            risk_assessment['risk_factors'].append('object_overlaps')
            risk_assessment['mitigation_strategies'].append('smart_positioning')
            risk_assessment['priority_actions'].append('resolve_overlaps')
        
        # Assess sequence risks
        sequence_analysis = analysis.get('sequence_analysis', {})
        if sequence_analysis.get('risk_assessment', {}).get('overall_risk') in ['medium', 'high']:
            risk_assessment['risk_factors'].append('sequence_complexity')
            risk_assessment['mitigation_strategies'].append('sequence_optimization')
            risk_assessment['priority_actions'].append('optimize_timing')
        
        # Assess performance risks
        performance = analysis.get('performance_considerations', {})
        if performance.get('rendering_estimate') == 'slow':
            risk_assessment['risk_factors'].append('performance_concerns')
            risk_assessment['mitigation_strategies'].append('performance_optimization')
            risk_assessment['priority_actions'].append('batch_operations')
        
        # Determine overall risk level
        if len(risk_assessment['risk_factors']) >= 3:
            risk_assessment['overall_risk'] = 'high'
        elif len(risk_assessment['risk_factors']) >= 1:
            risk_assessment['overall_risk'] = 'medium'
        
        return risk_assessment
    
    def _identify_optimization_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities for optimization"""
        opportunities = []
        
        # Object positioning opportunities
        if analysis.get('overlap_risks', {}).get('requires_intervention', False):
            opportunities.append({
                'type': 'positioning_optimization',
                'priority': 'high',
                'description': 'Optimize object positions to prevent overlaps',
                'expected_benefit': 'eliminate_visual_conflicts'
            })
        
        # Sequence optimization opportunities
        sequence_analysis = analysis.get('sequence_analysis', {})
        if sequence_analysis.get('sequential_objects'):
            opportunities.append({
                'type': 'sequence_optimization',
                'priority': 'medium',
                'description': 'Optimize animation sequence for better flow',
                'expected_benefit': 'improved_viewer_experience'
            })
        
        # Camera optimization opportunities
        if analysis.get('object_analysis', {}).get('total_objects', 0) > 3:
            opportunities.append({
                'type': 'camera_optimization',
                'priority': 'medium',
                'description': 'Optimize camera positioning for multiple objects',
                'expected_benefit': 'better_object_visibility'
            })
        
        return opportunities
    
    def _optimize_object_positions(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize object positions to prevent overlaps - SMART VERSION"""
        try:
            objects = animation_spec.get('objects', [])
            if len(objects) <= 1:
                return animation_spec
        
            # Smart positioning: Only adjust if objects are truly overlapping
            overlapping_objects = []
            for i, obj1 in enumerate(objects):
                for j, obj2 in enumerate(objects[i+1:], i+1):
                    pos1 = obj1.get('properties', {}).get('position', [0, 0, 0])
                    pos2 = obj2.get('properties', {}).get('position', [0, 0, 0])
                    
                    # Only consider objects overlapping if they're at the EXACT same position
                    if (len(pos1) >= 2 and len(pos2) >= 2 and 
                        abs(pos1[0] - pos2[0]) < 0.1 and abs(pos1[1] - pos2[1]) < 0.1):
                        overlapping_objects.extend([i, j])
            
            # Only adjust truly overlapping objects with minimal changes
            if overlapping_objects:
                logger.info(f"Smart positioning: Adjusting {len(set(overlapping_objects))} overlapping objects")
                for idx in set(overlapping_objects):
                    if idx < len(objects):
                        obj = objects[idx]
                        props = obj.get('properties', {})
                        pos = props.get('position', [0, 0, 0])
                        
                        # Minimal adjustment: just 0.3 unit offset
                        offset = 0.3 * (idx % 4 - 1.5)  # Small spread pattern
                        if len(pos) >= 2:
                            props['position'] = [pos[0] + offset, pos[1], pos[2] if len(pos) > 2 else 0]
                        
                logger.debug(f"Smart object positioning applied to {len(set(overlapping_objects))} objects")
            else:
                logger.debug("No overlapping objects found - positions preserved")
            
            return animation_spec
            
        except Exception as e:
            logger.error(f"Error in object positioning: {e}")
            return animation_spec
    
    def _prevent_object_overlaps(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prevent object overlaps using intelligent positioning - SMART VERSION"""
        try:
            # This now works in tandem with _optimize_object_positions
            # Only handles cases where different object types might interfere
            objects = animation_spec.get('objects', [])
            if len(objects) <= 1:
                return animation_spec
        
            # Group objects by type for smarter handling
            plot_objects = [obj for obj in objects if obj.get('type') in ['plot', 'axes']]
            text_objects = [obj for obj in objects if obj.get('type') == 'text']
            shape_objects = [obj for obj in objects if obj.get('type') in ['circle', 'square', 'triangle', 'diamond']]
            
            # Only adjust text positions if they're interfering with plots
            adjusted_count = 0
            for text_obj in text_objects:
                text_pos = text_obj.get('properties', {}).get('position', [0, 0, 0])
                
                # Check if text is too close to a plot center
                for plot_obj in plot_objects:
                    plot_pos = plot_obj.get('properties', {}).get('position', [0, 0, 0])
                    if (len(text_pos) >= 2 and len(plot_pos) >= 2 and 
                        abs(text_pos[0] - plot_pos[0]) < 0.5 and abs(text_pos[1] - plot_pos[1]) < 0.5):
                        
                        # Move text slightly away from plot center
                        offset_x = 0.8 if text_pos[0] >= plot_pos[0] else -0.8
                        offset_y = 0.5 if text_pos[1] >= plot_pos[1] else -0.5
                        text_obj['properties']['position'] = [
                            text_pos[0] + offset_x, 
                            text_pos[1] + offset_y, 
                            text_pos[2] if len(text_pos) > 2 else 0
                        ]
                        adjusted_count += 1
                        break
            
            if adjusted_count > 0:
                logger.info(f"Smart overlap prevention: Adjusted {adjusted_count} text positions")
            else:
                logger.debug("No overlap prevention needed")
        
            return animation_spec
            
        except Exception as e:
            logger.error(f"Error in overlap prevention: {e}")
            return animation_spec
    
    def _optimize_animation_sequence(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize the animation sequence for better flow"""
        objects = animation_spec.get('objects', [])
        if len(objects) <= 1:
            return animation_spec
        
        print(f"🔍 Optimizing animation sequence for {len(objects)} objects")
        
        # Get sequence analysis
        sequence_analysis = analysis.get('sequence_analysis', {})
        sequential_objects = sequence_analysis.get('sequential_objects', [])
        object_clusters = sequence_analysis.get('object_clusters', [])
        spatial_analysis = sequence_analysis.get('spatial_analysis', {})
        temporal_analysis = sequence_analysis.get('temporal_analysis', {})
        
        # NEW: Intelligent fade-out transitions based on object type and purpose
        # Coordinate axes and function plots should remain visible, only overlapping elements fade out
        if len(objects) > 1:
            print(f"✅ Adding intelligent fade transitions for {len(objects)} objects")
            
            # Identify persistent objects that should remain visible
            persistent_objects = []
            transient_objects = []
            
            for obj in objects:
                obj_type = obj.get('type', 'unknown')
                obj_id = obj.get('id', 'unknown')
                
                # Objects that should remain visible throughout the animation
                if obj_type in ['axes', 'plot']:
                    persistent_objects.append(obj)
                    print(f"  🔒 {obj_id} ({obj_type}) marked as persistent (will remain visible)")
                else:
                    transient_objects.append(obj)
                    print(f"  🔄 {obj_id} ({obj_type}) marked as transient (can fade in/out)")
            
            # Handle persistent objects (axes, plots) - they just fade in once and stay
            for obj in persistent_objects:
                if 'animations' not in obj:
                    obj['animations'] = []
                
                # Ensure persistent objects have fade-in
                if not any(anim.get('type') == 'fade_in' for anim in obj['animations']):
                    fade_in_anim = {
                        'type': 'fade_in',
                        'start_time': 'immediate',
                        'duration': 0.8,
                        'reason': 'persistent_object_display'
                    }
                    obj['animations'].append(fade_in_anim)
                    print(f"  📈 Added persistent fade-in to {obj.get('id', 'unknown')}")
            
            # Handle transient objects (shapes, text, dots) - they can fade in/out sequentially
            if transient_objects:
                print(f"  🎬 Processing {len(transient_objects)} transient objects for sequential display")
                
                for i, obj in enumerate(transient_objects):
                    if 'animations' not in obj:
                        obj['animations'] = []
                    
                    # First transient object fades in after persistent objects
                    if i == 0:
                        fade_in_anim = {
                            'type': 'fade_in',
                            'start_time': 'after_persistent_display',
                            'duration': 0.5,
                            'reason': 'first_transient_object'
                        }
                        obj['animations'].append(fade_in_anim)
                        print(f"  📈 Added fade-in to {obj.get('id', 'unknown')} (first transient)")
                    else:
                        # Subsequent transient objects fade out the previous one and fade in
                        prev_obj = transient_objects[i-1]
                        
                        # Add fade-out to previous transient object
                        if 'animations' not in prev_obj:
                            prev_obj['animations'] = []
                        
                        fade_out_anim = {
                            'type': 'fade_out',
                            'start_time': 'before_next_transient',
                            'duration': 0.3,
                            'reason': 'sequential_transient_display'
                        }
                        prev_obj['animations'].append(fade_out_anim)
                        print(f"  📉 Added fade-out to {prev_obj.get('id', 'unknown')}")
                        
                        # Add fade-in to current transient object
                        fade_in_anim = {
                            'type': 'fade_in',
                            'start_time': 'after_previous_transient_fade',
                            'duration': 0.5,
                            'reason': 'sequential_transient_display'
                        }
                        obj['animations'].append(fade_in_anim)
                        print(f"  📈 Added fade-in to {obj.get('id', 'unknown')}")
            
            # If we have both persistent and transient objects, ensure proper timing
            if persistent_objects and transient_objects:
                print(f"  ⏱️ Coordinating timing between {len(persistent_objects)} persistent and {len(transient_objects)} transient objects")
                
                # First persistent object should appear immediately
                if persistent_objects:
                    first_persistent = persistent_objects[0]
                    if 'animations' not in first_persistent:
                        first_persistent['animations'] = []
                    
                    # Ensure first persistent object has immediate fade-in
                    if not any(anim.get('type') == 'fade_in' for anim in first_persistent['animations']):
                        fade_in_anim = {
                            'type': 'fade_in',
                            'start_time': 'immediate',
                            'duration': 0.8,
                            'reason': 'first_persistent_object'
                        }
                        first_persistent['animations'].append(fade_in_anim)
                        print(f"  📈 First persistent object {first_persistent.get('id', 'unknown')} will appear immediately")
                
                # First transient object should appear after persistent objects are visible
                if transient_objects:
                    first_transient = transient_objects[0]
                    if 'animations' not in first_transient:
                        first_transient['animations'] = []
                    
                    # Update timing to wait for persistent objects
                    for anim in first_transient['animations']:
                        if anim.get('type') == 'fade_in':
                            anim['start_time'] = 'after_persistent_display'
                            anim['reason'] = 'first_transient_after_persistent'
                            print(f"  ⏱️ First transient object {first_transient.get('id', 'unknown')} will appear after persistent objects")
                            break
        
        # Apply cluster-based optimizations
        if object_clusters:
            animation_spec = self._apply_cluster_optimizations(animation_spec, object_clusters)
        
        # Apply spatial optimizations
        if spatial_analysis.get('status') == 'analyzed':
            animation_spec = self._apply_spatial_optimizations(animation_spec, spatial_analysis)
        
        # Apply temporal optimizations
        if temporal_analysis.get('status') == 'analyzed':
            animation_spec = self._apply_temporal_optimizations(animation_spec, temporal_analysis)
        
        print(f"✅ Animation sequence optimization completed")
        return animation_spec
    
    def _apply_cluster_optimizations(self, animation_spec: Dict[str, Any], object_clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply optimizations based on object clusters"""
        objects = animation_spec.get('objects', [])
        
        for cluster in object_clusters:
            cluster_type = cluster.get('type', '')
            cluster_objects = cluster.get('objects', [])
            
            if cluster_type == 'coordinate_system':
                # Group coordinate system objects together
                self._group_coordinate_objects(objects, cluster_objects)
            elif cluster_type == 'geometric_shapes':
                # Spread geometric shapes to avoid overlap
                self._spread_geometric_shapes(objects, cluster_objects)
            elif cluster_type == 'text_elements':
                # Position text elements to avoid overlap
                self._position_text_elements(objects, cluster_objects)
        
        # NEW: Apply intelligent text positioning for all text objects
        self._apply_intelligent_text_positioning(objects)
        
        return animation_spec
    
    def _group_coordinate_objects(self, objects: List[Dict[str, Any]], cluster_object_ids: List[str]):
        """Group coordinate system objects together - DISABLED to prevent blank videos"""
        # DISABLED: This was modifying object positions and causing blank videos
        # Return without modifying positions to preserve user-specified coordinates
        logger.debug("Coordinate object grouping DISABLED to prevent blank videos")
        return
    
    def _spread_geometric_shapes(self, objects: List[Dict[str, Any]], cluster_object_ids: List[str]):
        """Spread geometric shapes to avoid overlap - DISABLED to prevent blank videos"""
        # DISABLED: This was modifying object positions and causing blank videos
        # Return without modifying positions to preserve user-specified coordinates
        logger.debug("Geometric shape spreading DISABLED to prevent blank videos")
        return
    
    def _position_text_elements(self, objects: List[Dict[str, Any]], cluster_object_ids: List[str]):
        """Position text elements to avoid overlap - DISABLED to prevent blank videos"""
        # DISABLED: This was modifying object positions and causing blank videos
        # Return without modifying positions to preserve user-specified coordinates
        logger.debug("Text element positioning DISABLED to prevent blank videos")
        return
    
    def _apply_intelligent_text_positioning(self, objects: List[Dict[str, Any]]):
        """
        Applies intelligent text positioning to text objects - SMART VERSION
        """
        try:
            text_objects = [obj for obj in objects if obj.get('type') == 'text']
            if not text_objects:
                logger.debug("No text objects found for intelligent positioning")
                return
            
            # Get non-text objects for reference
            reference_objects = [obj for obj in objects if obj.get('type') != 'text']
            
            positioned_count = 0
            for text_obj in text_objects:
                text_props = text_obj.get('properties', {})
                text_pos = text_props.get('position', [0, 0, 0])
                text_content = text_props.get('text', '')
                
                # Only adjust position if text seems to be auto-generated (short labels)
                if len(text_content) <= 3:  # Only adjust single letters or short labels
                    # Find the closest reference object
                    closest_obj = None
                    min_distance = float('inf')
                    
                    for ref_obj in reference_objects:
                        ref_pos = ref_obj.get('properties', {}).get('position', [0, 0, 0])
                        if len(ref_pos) >= 2 and len(text_pos) >= 2:
                            distance = ((text_pos[0] - ref_pos[0])**2 + (text_pos[1] - ref_pos[1])**2)**0.5
                            if distance < min_distance:
                                min_distance = distance
                                closest_obj = ref_obj
                    
                    # Position text near the closest object but not overlapping
                    if closest_obj and min_distance < 2.0:  # Only if close enough to be related
                        ref_pos = closest_obj.get('properties', {}).get('position', [0, 0, 0])
                        
                        # Smart positioning: above and to the right
                        smart_pos = [
                            ref_pos[0] + 0.5,  # Slightly right
                            ref_pos[1] + 0.7,  # Above
                            text_pos[2] if len(text_pos) > 2 else 0
                        ]
                        
                        text_props['position'] = smart_pos
                        positioned_count += 1
                        logger.debug(f"Smart positioned text '{text_content}' near {closest_obj.get('id', 'unknown')}")
            
            if positioned_count > 0:
                logger.info(f"Smart text positioning: Adjusted {positioned_count} text labels")
            else:
                logger.debug("No text positioning adjustments needed")
            
        except Exception as e:
            logger.error(f"Error in intelligent text positioning: {e}")
            return
    
    def _is_text_for_object(self, text_id: str, geo_id: str) -> bool:
        """Check if a text object is meant to label a specific geometric object"""
        text_id_lower = text_id.lower()
        geo_id_lower = geo_id.lower()
        
        # Common patterns
        patterns = [
            (f"{geo_id_lower}_label", geo_id_lower),
            (f"label_{geo_id_lower}", geo_id_lower),
            (f"{geo_id_lower}_text", geo_id_lower),
            (f"text_{geo_id_lower}", geo_id_lower),
        ]
        
        for text_pattern, geo_pattern in patterns:
            if text_pattern in text_id_lower or geo_pattern in text_id_lower:
                return True
        
        # Check if text ID contains the geometric object type
        geo_types = ['circle', 'square', 'point', 'triangle', 'rectangle']
        for geo_type in geo_types:
            if geo_type in text_id_lower and geo_type in geo_id_lower:
                return True
        
        return False
    
    def _position_text_near_object(self, text_obj: Dict[str, Any], geo_obj: Dict[str, Any]):
        """
        Positions a text object near its corresponding geometric object
        with intelligent offset calculation to avoid overlaps.
        """
        geo_props = geo_obj.get('properties', {})
        geo_pos = geo_props.get('position', [0, 0, 0])
        geo_type = geo_obj.get('type', 'unknown')
        
        # Calculate smart offset based on object type and size
        offset_x, offset_y = self._calculate_text_offset(geo_type, geo_props)
        
        # Position text with offset
        text_pos = [
            geo_pos[0] + offset_x,
            geo_pos[1] + offset_y,
            geo_pos[2]
        ]
        
        # Ensure text is within reasonable bounds
        text_pos[0] = max(-4.5, min(4.5, text_pos[0]))  # Keep within X bounds
        text_pos[1] = max(-2.5, min(7.5, text_pos[1]))  # Keep within Y bounds
        
        # Update text object position
        if 'properties' not in text_obj:
            text_obj['properties'] = {}
        text_obj['properties']['position'] = text_pos
        
        # Log the positioning for debugging
        print(f"Positioned text '{text_obj.get('properties', {}).get('text', 'NO_TEXT')}' "
              f"near {geo_type} at {geo_pos} -> text at {text_pos}")
    
    def _calculate_text_offset(self, geo_type: str, geo_props: Dict[str, Any]) -> tuple:
        """
        Calculates intelligent offset for text positioning based on object type and properties.
        Returns (offset_x, offset_y) tuple.
        """
        # Base offsets for different object types - positioned closer to objects
        base_offsets = {
            'circle': (0.4, 0.4),      # Closer to object for better association
            'square': (0.4, 0.4),      # Closer to object for better association
            'point': (0.4, 0.4),       # Closer to object for better association
            'triangle': (0.4, 0.4),    # Closer to object for better association
            'rectangle': (0.4, 0.4),   # Closer to object for better association
        }
        
        offset_x, offset_y = base_offsets.get(geo_type, (0.4, 0.4))
        
        # Adjust based on object size
        size = geo_props.get('size', 0.2)
        if size > 0.5:
            # Larger objects need slightly more offset to avoid overlap
            offset_x *= 1.2
            offset_y *= 1.2
        
        # Add minimal randomness to avoid perfect alignment (reduces overlap risk)
        import random
        offset_x += random.uniform(-0.1, 0.1)
        offset_y += random.uniform(-0.1, 0.1)
        
        return offset_x, offset_y
    
    def _apply_spatial_optimizations(self, animation_spec: Dict[str, Any], spatial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations based on spatial analysis - DISABLED to prevent blank videos"""
        # DISABLED: This was modifying object positions and causing blank videos
        # Return the original spec unchanged to preserve user-specified positions
        logger.debug("Spatial optimizations DISABLED to prevent blank videos")
        return animation_spec
    
    def _apply_temporal_optimizations(self, animation_spec: Dict[str, Any], temporal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations based on temporal analysis - DISABLED to prevent blank videos"""
        # DISABLED: This was interfering with object positioning and causing blank videos
        # Return the original spec unchanged to preserve user-specified positions
        logger.debug("Temporal optimizations DISABLED to prevent blank videos")
        return animation_spec
    
    def _break_long_animations(self, objects: List[Dict[str, Any]]):
        """Break long animations into shorter sequences"""
        for obj in objects:
            animations = obj.get('animations', [])
            if animations:
                # Reduce duration of long animations
                for anim in animations:
                    if anim.get('duration', 0) > 2.0:
                        anim['duration'] = min(anim['duration'], 2.0)
                        anim['note'] = 'duration_reduced_for_better_flow'
    
    def _group_sequential_objects(self, objects: List[Dict[str, Any]]):
        """Group some sequential objects to appear simultaneously"""
        # Find objects that can be grouped
        plot_objects = [obj for obj in objects if obj.get('type') in ['plot', 'function', 'graph']]
        
        if len(plot_objects) > 2:
            # Group every other plot object to appear simultaneously
            for i in range(0, len(plot_objects), 2):
                if i + 1 < len(plot_objects):
                    # These two objects can appear together
                    plot_objects[i]['group_with'] = plot_objects[i + 1]['id']
                    plot_objects[i + 1]['group_with'] = plot_objects[i]['id']
    
    def _apply_overlap_prevention(self, objects: List[Dict[str, Any]]):
        """
        Applies comprehensive overlap prevention to ensure objects don't appear on top of each other.
        This involves intelligent positioning and smart fade-out management.
        """
        if len(objects) <= 1:
            return
        
        # Group objects by type for better overlap management
        geometric_objects = [obj for obj in objects if obj.get('type') in ['circle', 'square', 'point', 'triangle', 'rectangle']]
        text_objects = [obj for obj in objects if obj.get('type') == 'text']
        plot_objects = [obj for obj in objects if obj.get('type') == 'plot']
        
        # Apply smart positioning to prevent overlaps
        self._prevent_geometric_overlaps(geometric_objects)
        self._prevent_text_overlaps(text_objects)
        self._prevent_plot_overlaps(plot_objects)
        
        # Apply smart fade-out management for sequential objects
        self._apply_sequential_fade_out_management(objects)
    
    def _prevent_geometric_overlaps(self, geometric_objects: List[Dict[str, Any]]):
        """Prevent overlaps between geometric objects"""
        if len(geometric_objects) <= 1:
            return
        
        print(f"🔍 Preventing overlaps between {len(geometric_objects)} geometric objects")
        
        # Calculate minimum spacing based on object sizes
        min_spacing = 1.5  # Minimum distance between object centers
        
        for i, obj in enumerate(geometric_objects):
            if 'properties' not in obj:
                obj['properties'] = {}
            
            current_pos = obj['properties'].get('position', [0, 0, 0])
            obj_size = obj['properties'].get('size', 0.2)
            
            print(f"  Processing {obj.get('id', 'unknown')} at {current_pos} with size {obj_size}")
            
            # Check distance from previous objects
            for j in range(i):
                prev_obj = geometric_objects[j]
                prev_pos = prev_obj['properties'].get('position', [0, 0, 0])
                prev_size = prev_obj['properties'].get('size', 0.2)
                
                # Calculate current distance
                distance = ((current_pos[0] - prev_pos[0])**2 + (current_pos[1] - prev_pos[1])**2)**0.5
                required_distance = (obj_size + prev_size) / 2 + min_spacing
                
                print(f"    Distance to {prev_obj.get('id', 'unknown')}: {distance:.2f} (required: {required_distance:.2f})")
                
                if distance < required_distance:
                    print(f"    ⚠️  Overlap detected! Moving {obj.get('id', 'unknown')}")
                    
                    # Move current object to prevent overlap
                    # Use a more aggressive positioning strategy
                    if i == 0:
                        # First object stays in place
                        continue
                    
                    # Calculate new position with better spacing
                    angle_step = 360 / len(geometric_objects)
                    angle = i * angle_step
                    radius = required_distance * 1.2  # Slightly larger radius
                    
                    new_x = prev_pos[0] + radius * (angle / 360) * 2 - radius
                    new_y = prev_pos[1] + radius * (angle / 360) * 2 - radius
                    
                    # Ensure within bounds
                    new_x = max(-4.5, min(4.5, new_x))
                    new_y = max(-2.5, min(7.5, new_y))
                    
                    old_pos = current_pos.copy()
                    obj['properties']['position'] = [new_x, new_y, 0]
                    current_pos = [new_x, new_y, 0]
                    
                    print(f"    Moved from {old_pos} to {current_pos}")
                    
                    # Recalculate distance after move
                    new_distance = ((current_pos[0] - prev_pos[0])**2 + (current_pos[1] - prev_pos[1])**2)**0.5
                    print(f"    New distance: {new_distance:.2f} (required: {required_distance:.2f})")
                    
                    if new_distance < required_distance:
                        print(f"    ⚠️  Still too close, applying additional offset")
                        # Apply additional offset
                        offset_x = (required_distance - new_distance) * 1.5
                        offset_y = (required_distance - new_distance) * 1.5
                        
                        final_x = current_pos[0] + offset_x
                        final_y = current_pos[1] + offset_y
                        
                        # Ensure within bounds
                        final_x = max(-4.5, min(4.5, final_x))
                        final_y = max(-2.5, min(7.5, final_y))
                        
                        obj['properties']['position'] = [final_x, final_y, 0]
                        current_pos = [final_x, final_y, 0]
                        
                        print(f"    Final position: {current_pos}")
        
        print(f"✅ Overlap prevention completed for {len(geometric_objects)} objects")
    
    def _prevent_text_overlaps(self, text_objects: List[Dict[str, Any]]):
        """Prevent overlaps between text objects"""
        if len(text_objects) <= 1:
            return
        
        # Text objects should be positioned near their corresponding objects
        # Overlap prevention is handled by the intelligent text positioning
        pass
    
    def _prevent_plot_overlaps(self, plot_objects: List[Dict[str, Any]]):
        """Prevent overlaps between plot objects"""
        if len(plot_objects) <= 1:
            return
        
        # Plots should be positioned to avoid overlaps
        spacing = 2.0
        for i, obj in enumerate(plot_objects):
            if 'properties' not in obj:
                obj['properties'] = {}
            
            # Position plots in a grid to avoid overlap
            row = i // 2
            col = i % 2
            x = (col - 0.5) * spacing
            y = (row - len(plot_objects) / 4) * spacing
            
            obj['properties']['position'] = [x, y, 0]
    
    def _apply_sequential_fade_out_management(self, objects: List[Dict[str, Any]]):
        """Apply smart fade-out management for sequential objects"""
        print(f"🔍 Applying sequential fade-out management to {len(objects)} objects")
        
        # Always apply fade-out management for better visual flow
        # This ensures smooth transitions even when objects are well-separated
        
        if len(objects) > 1:
            print(f"✅ Applying fade-out management for {len(objects)} objects")
            
            for i, obj in enumerate(objects):
                if 'animations' not in obj:
                    obj['animations'] = []
                
                # Check if this object should fade out the previous one
                if i > 0:
                    prev_obj = objects[i-1]
                    
                    # Always add fade-out for better visual flow
                    print(f"  📉 Adding fade-out to {prev_obj.get('id', 'unknown')}")
                    
                    # Add fade-out animation to previous object
                    if 'animations' not in prev_obj:
                        prev_obj['animations'] = []
                    
                    fade_out_anim = {
                        'type': 'fade_out',
                        'start_time': 'before_next',
                        'duration': 0.3,
                        'reason': 'visual_flow_improvement'
                    }
                    prev_obj['animations'].append(fade_out_anim)
                    
                    # Add fade-in animation to current object
                    fade_in_anim = {
                        'type': 'fade_in',
                        'start_time': 'after_previous_fade',
                        'duration': 0.5,
                        'reason': 'sequential_display'
                    }
                    obj['animations'].append(fade_in_anim)
                    
                    print(f"  📈 Added fade-in to {obj.get('id', 'unknown')}")
        else:
            print(f"ℹ️  No fade-out management needed (only 1 object)")
        
        print(f"✅ Sequential fade-out management completed")
    
    def _analyze_object_sequence(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze object sequence for overlap prevention"""
        if len(objects) <= 1:
            return {'should_fade_out_previous': False}
        
        print(f"🔍 Analyzing object sequence for {len(objects)} objects")
        
        # Check if objects are positioned close to each other
        close_objects = []
        for i, obj in enumerate(objects):
            if i == 0:
                continue
            
            current_pos = obj.get('properties', {}).get('position', [0, 0, 0])
            prev_pos = objects[i-1].get('properties', {}).get('position', [0, 0, 0])
            
            distance = ((current_pos[0] - prev_pos[0])**2 + (current_pos[1] - prev_pos[1])**2)**0.5
            
            print(f"  Distance between {objects[i-1].get('id', 'unknown')} and {obj.get('id', 'unknown')}: {distance:.2f}")
            
            # Lower threshold to trigger fade-out more aggressively
            if distance < 3.0:  # Objects are close, need fade-out
                close_objects.append((i, distance))
                print(f"    ⚠️  Objects are close (distance: {distance:.2f} < 3.0)")
            else:
                print(f"    ✅ Objects are well-separated (distance: {distance:.2f} >= 3.0)")
        
        should_fade_out = len(close_objects) > 0
        print(f"🔍 Analysis result: should_fade_out_previous = {should_fade_out}")
        
        return {
            'should_fade_out_previous': should_fade_out,
            'close_objects': close_objects
        }
    
    def _apply_smart_fade_out_management(self, objects: List[Dict[str, Any]]):
        """
        Applies smart fade-out management to ensure smooth transitions and
        prevent objects from appearing on top of each other.
        """
        if len(objects) <= 1:
            return
        
        # Get the first object as new object for camera management
        new_object = objects[0]
        existing_objects = objects[1:] if len(objects) > 1 else []
        
        # Get camera strategy
        camera_strategy = self.camera_manager.intelligent_camera_management(
            new_object, existing_objects, {}
        )
        
        # NEW: Apply fade-out to the new object if it's a sequential object
        if camera_strategy.get('action') == 'sequential_display':
            if 'animations' not in new_object:
                new_object['animations'] = []
            
                fade_out_anim = {
                    'type': 'fade_out',
                    'start_time': 'before_next',
                    'duration': 0.3,
                    'reason': 'sequential_display_requirement'
                }
            new_object['animations'].append(fade_out_anim)
    
    def _optimize_camera_strategy(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize camera strategy for the animation"""
        objects = animation_spec.get('objects', [])
        if not objects:
            return {'action': 'none', 'reason': 'no_objects'}
        
        # Get the first object as new object for camera management
        new_object = objects[0]
        existing_objects = objects[1:] if len(objects) > 1 else []
        
        # Get camera strategy
        camera_strategy = self.camera_manager.intelligent_camera_management(
            new_object, existing_objects, {}
        )
        
        return camera_strategy
    
    def _perform_final_validation(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform final validation of the enhanced animation specification"""
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'enhancements_applied': []
        }
        
        # Validate object properties
        objects = animation_spec.get('objects', [])
        for obj in objects:
            if 'properties' not in obj:
                obj['properties'] = {}
                validation_result['enhancements_applied'].append(f'added_properties_to_{obj.get("id", "unknown")}')
            
            if 'animations' not in obj:
                obj['animations'] = []
                validation_result['enhancements_applied'].append(f'added_animations_to_{obj.get("id", "unknown")}')
            
            # Ensure position is set
            if 'position' not in obj['properties']:
                obj['properties']['position'] = [0, 0, 0]
                validation_result['enhancements_applied'].append(f'set_default_position_for_{obj.get("id", "unknown")}')
        
        # Check for remaining overlaps
        remaining_overlaps = self._assess_overlap_risks(animation_spec)
        if remaining_overlaps.get('requires_intervention', False):
            validation_result['warnings'].append({
                'type': 'remaining_overlaps',
                'message': 'Some object overlaps may still exist',
                'count': len(remaining_overlaps.get('overlaps', []))
            })
        
        return animation_spec
    
    def _generate_workflow_summary(self, analysis: Dict[str, Any], final_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the workflow processing"""
        return {
            'status': 'completed',
            'processing_stages': [
                'pre_processing_analysis',
                'object_positioning_optimization',
                'overlap_prevention',
                'sequence_optimization',
                'camera_strategy_optimization',
                'final_validation'
            ],
            'analysis_summary': {
                'prompt_complexity': analysis.get('prompt_complexity', {}).get('level', 'unknown'),
                'total_objects': analysis.get('object_analysis', {}).get('total_objects', 0),
                'overlap_risks_resolved': len(analysis.get('overlap_risks', {}).get('overlaps', [])),
                'sequence_optimizations': len(analysis.get('sequence_analysis', {}).get('sequential_objects', [])),
                'overall_risk': analysis.get('risk_assessment', {}).get('overall_risk', 'unknown')
            },
            'enhancements_applied': len(analysis.get('optimization_opportunities', [])),
            'final_object_count': len(final_spec.get('objects', [])),
            'performance_estimate': analysis.get('performance_considerations', {}).get('rendering_estimate', 'unknown')
        }
    
    def _get_applied_enhancements(self, analysis: Dict[str, Any]) -> List[str]:
        """Get list of enhancements that were applied"""
        enhancements = []
        
        # Check what enhancements were applied based on analysis
        if analysis.get('overlap_risks', {}).get('requires_intervention', False):
            enhancements.append('overlap_prevention')
        
        if analysis.get('sequence_analysis', {}).get('sequential_objects'):
            enhancements.append('sequence_optimization')
        
        if analysis.get('object_analysis', {}).get('total_objects', 0) > 3:
            enhancements.append('camera_optimization')
        
        if analysis.get('prompt_complexity', {}).get('requires_enhancement', False):
            enhancements.append('complexity_handling')
        
        return enhancements
    
    def _calculate_performance_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics for the workflow"""
        return {
            'processing_efficiency': 'high' if len(analysis.get('optimization_opportunities', [])) > 0 else 'standard',
            'risk_mitigation': analysis.get('risk_assessment', {}).get('overall_risk', 'unknown'),
            'complexity_handling': analysis.get('prompt_complexity', {}).get('level', 'unknown'),
            'optimization_applied': len(analysis.get('optimization_opportunities', []))
        }
