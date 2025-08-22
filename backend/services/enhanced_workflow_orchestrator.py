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
            logger.info("Starting enhanced workflow processing for complex animation")
            
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
                'performance_metrics': self._calculate_performance_metrics(pre_analysis)
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
        """Optimize object positions to prevent overlaps"""
        objects = animation_spec.get('objects', [])
        if len(objects) <= 1:
            return animation_spec
        
        # Get screen bounds
        screen_bounds = self.camera_manager.get_screen_bounds()
        
        # Apply smart positioning for each object
        for i, obj in enumerate(objects):
            existing_objects = objects[:i]
            
            # Get positioning strategy
            positioning_strategy = self.camera_manager.advanced_object_positioning(
                obj, existing_objects, screen_bounds, {}
            )
            
            # Apply the strategy if it provides a position
            if positioning_strategy.get('position'):
                if 'properties' not in obj:
                    obj['properties'] = {}
                obj['properties']['position'] = positioning_strategy['position']
        
        return animation_spec
    
    def _prevent_object_overlaps(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prevent object overlaps using intelligent positioning"""
        objects = animation_spec.get('objects', [])
        if len(objects) <= 1:
            return animation_spec
        
        # Check for overlaps and resolve them
        overlaps = analysis.get('overlap_risks', {}).get('overlaps', [])
        
        if overlaps:
            # Apply overlap resolution strategies
            for overlap in overlaps:
                obj1_id = overlap['object1']['id']
                obj2_id = overlap['object2']['id']
                
                # Find the objects in the spec
                obj1 = next((obj for obj in objects if obj.get('id') == obj1_id), None)
                obj2 = next((obj for obj in objects if obj.get('id') == obj2_id), None)
                
                if obj1 and obj2:
                    # Calculate new positions to avoid overlap
                    pos1 = obj1.get('properties', {}).get('position', [0, 0, 0])
                    pos2 = obj2.get('properties', {}).get('position', [0, 0, 0])
                    
                    # Simple separation strategy
                    separation = 2.0
                    if len(pos1) >= 2 and len(pos2) >= 2:
                        # Move objects apart
                        new_pos1 = [pos1[0] - separation/2, pos1[1], pos1[2] if len(pos1) > 2 else 0]
                        new_pos2 = [pos2[0] + separation/2, pos2[1], pos2[2] if len(pos2) > 2 else 0]
                        
                        if 'properties' not in obj1:
                            obj1['properties'] = {}
                        if 'properties' not in obj2:
                            obj2['properties'] = {}
                        
                        obj1['properties']['position'] = new_pos1
                        obj2['properties']['position'] = new_pos2
        
        return animation_spec
    
    def _optimize_animation_sequence(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize the animation sequence for better flow"""
        objects = animation_spec.get('objects', [])
        if len(objects) <= 1:
            return animation_spec
        
        # Get sequence analysis
        sequence_analysis = analysis.get('sequence_analysis', {})
        sequential_objects = sequence_analysis.get('sequential_objects', [])
        
        # Add fade-out transitions for sequential objects
        for seq_obj in sequential_objects:
            current_id = seq_obj['current']['id']
            previous_id = seq_obj['previous']['id']
            
            # Find the current object and add fade-out animation for previous
            current_obj = next((obj for obj in objects if obj.get('id') == current_id), None)
            previous_obj = next((obj for obj in objects if obj.get('id') == previous_id), None)
            
            if current_obj and previous_obj:
                # Add fade-out animation to previous object
                if 'animations' not in previous_obj:
                    previous_obj['animations'] = []
                
                # Add fade-out before current object appears
                fade_out_anim = {
                    'type': 'fade_out',
                    'start_time': 'before_next',
                    'duration': 0.3,
                    'reason': 'sequential_display_requirement'
                }
                previous_obj['animations'].append(fade_out_anim)
        
        return animation_spec
    
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
