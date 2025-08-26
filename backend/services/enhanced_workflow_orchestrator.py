"""
Enhanced Workflow Orchestrator for Animathic
Integrates all enhanced systems for optimal complex prompt handling
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from .object_tracking import ObjectTrackingSystem
from .animation_analysis import AnimationSequenceAnalyzer
from .fade_out_system import FadeOutSystem
from .camera_management import CameraManagementSystem
from .enhanced_validation import EnhancedValidationService
from .real_time_overlap_monitoring import RealTimeOverlapMonitor
from .advanced_positioning import AdvancedObjectPositioningSystem

logger = logging.getLogger(__name__)


class EnhancedWorkflowOrchestrator:
    """Orchestrates all enhanced systems for optimal animation generation"""
    
    def __init__(self):
        """Initialize the enhanced workflow orchestrator"""
        self.object_tracker = ObjectTrackingSystem()
        self.animation_analyzer = AnimationSequenceAnalyzer()
        self.fade_out_system = FadeOutSystem()
        self.camera_manager = CameraManagementSystem()
        self.enhanced_validator = EnhancedValidationService()
        self.prompt_enhancer = None  # Will be set by AI service
        self.real_time_monitor = RealTimeOverlapMonitor()
        self.advanced_positioning = AdvancedObjectPositioningSystem()
        
        # Workflow configuration
        self.config = {
            'enable_smart_positioning': True,
            'enable_overlap_prevention': True,
            'enable_camera_optimization': True,
            'enable_sequence_optimization': True,
            'validation_level': 'comprehensive',  # 'minimal', 'standard', 'comprehensive'
            'performance_mode': 'balanced',  # 'fast', 'balanced', 'quality'
            'enable_smart_fade_out': True,  # NEW: Smart fade-out system
            'enable_fade_out_validation': True,  # NEW: Fade-out validation
            'max_fade_out_retries': 3,  # NEW: Maximum retry attempts
            'fade_out_timeout': 5.0,  # NEW: Timeout for fade-out operations
            'enable_real_time_overlap_monitoring': True,  # NEW: Real-time overlap monitoring
            'real_time_monitoring_config': {
                'check_interval': 0.1,
                'overlap_threshold': 0.1,
                'auto_correct': True,
                'max_concurrent_corrections': 3
            },
            'fade_out_conservative_mode': True,  # NEW: Ultra-conservative fade-out behavior
            'fade_out_explicit_only': True,  # NEW: Only fade-out when explicitly requested
            'preserve_mathematical_content': True,  # NEW: Never fade-out mathematical functions unless requested
            'enable_advanced_positioning': True,  # NEW: Advanced object positioning algorithms
            'advanced_positioning_config': {
                'grid_size': 8,
                'spacing_factor': 1.2,
                'collision_threshold': 0.5,
                'prefer_center': True,
                'enable_smart_spacing': True,
                'max_positioning_attempts': 10,
                'enable_adaptive_positioning': True
            }
        }
        
        # NEW: Smart fade-out tracking
        self._fade_out_history = {}
        self._fade_out_validation_cache = {}
        self._active_fade_out_operations = set()
    
    def set_prompt_enhancer(self, prompt_enhancer):
        """Set the prompt enhancer from the AI service"""
        self.prompt_enhancer = prompt_enhancer
        logger.info("Prompt enhancer set in workflow orchestrator")
    
    def start_real_time_overlap_monitoring(self, animation_spec: Dict[str, Any]) -> bool:
        """Start real-time overlap monitoring for the animation"""
        try:
            if not self.config['enable_real_time_overlap_monitoring']:
                logger.debug("Real-time overlap monitoring disabled")
                return False
            
            # Convert animation spec objects to monitoring format
            monitoring_objects = {}
            for obj in animation_spec.get('objects', []):
                obj_id = obj.get('id', f"obj_{len(monitoring_objects)}")
                monitoring_objects[obj_id] = {
                    'type': obj.get('type', 'unknown'),
                    'properties': obj.get('properties', {}),
                    'created_at': time.time()  # Track creation time for correction logic
                }
            
            # Configure and start monitoring
            config = self.config['real_time_monitoring_config']
            self.real_time_monitor.config.check_interval = config['check_interval']
            self.real_time_monitor.config.overlap_threshold = config['overlap_threshold']
            self.real_time_monitor.config.auto_correct = config['auto_correct']
            self.real_time_monitor.config.max_concurrent_corrections = config['max_concurrent_corrections']
            
            # Start monitoring
            success = self.real_time_monitor.start_monitoring(monitoring_objects)
            
            if success:
                logger.info(f"Real-time overlap monitoring started for {len(monitoring_objects)} objects")
                
                # Add callbacks for real-time feedback
                self.real_time_monitor.add_overlap_callback(self._on_overlap_detected)
                self.real_time_monitor.add_correction_callback(self._on_correction_applied)
            else:
                logger.warning("Failed to start real-time overlap monitoring")
            
            return success
            
        except Exception as e:
            logger.error(f"Error starting real-time overlap monitoring: {e}")
            return False
    
    def stop_real_time_overlap_monitoring(self) -> bool:
        """Stop real-time overlap monitoring"""
        try:
            if self.real_time_monitor.monitoring_active:
                success = self.real_time_monitor.stop_monitoring()
                if success:
                    logger.info("Real-time overlap monitoring stopped")
                return success
            return True
        except Exception as e:
            logger.error(f"Error stopping real-time overlap monitoring: {e}")
            return False
    
    def _on_overlap_detected(self, overlap_event) -> None:
        """Callback for detected overlaps"""
        try:
            logger.warning(f"Real-time overlap detected: {overlap_event.object1_id} ({overlap_event.object1_type}) and {overlap_event.object2_id} ({overlap_event.object2_type}) - Severity: {overlap_event.severity.value}")
            
            # Store overlap event for workflow analysis
            if not hasattr(self, '_real_time_overlaps'):
                self._real_time_overlaps = []
            self._real_time_overlaps.append(overlap_event)
            
        except Exception as e:
            logger.error(f"Error in overlap callback: {e}")
    
    def _on_correction_applied(self, correction_id: str, success: bool) -> None:
        """Callback for applied corrections"""
        try:
            if success:
                logger.info(f"Real-time overlap correction {correction_id} applied successfully")
            else:
                logger.warning(f"Real-time overlap correction {correction_id} failed")
            
        except Exception as e:
            logger.error(f"Error in correction callback: {e}")
    
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
                animation_spec = self._optimize_animation_sequence(animation_spec, pre_analysis, user_prompt)
            
            # Phase 5: Camera strategy optimization
            if self.config['enable_camera_optimization']:
                camera_strategy = self._optimize_camera_strategy(animation_spec, pre_analysis)
                animation_spec['camera_strategy'] = camera_strategy
            
            # Phase 6: Enhanced validation and enhancement
            validation_result = self.enhanced_validator.enhanced_animation_validation(animation_spec)
            final_spec = self._perform_final_validation(animation_spec, pre_analysis, validation_result)
            
            # Phase 7: Start real-time overlap monitoring
            if self.config['enable_real_time_overlap_monitoring']:
                monitoring_started = self.start_real_time_overlap_monitoring(final_spec)
                if monitoring_started:
                    logger.info("Real-time overlap monitoring integrated into workflow")
                else:
                    logger.warning("Failed to start real-time overlap monitoring")
            
            # Phase 8: Generate workflow summary
            workflow_summary = self._generate_workflow_summary(pre_analysis, final_spec)
            
            return {
                'enhanced_animation_spec': final_spec,
                'workflow_summary': workflow_summary,
                'enhancements_applied': self._get_applied_enhancements(pre_analysis),
                'risk_assessment': pre_analysis.get('risk_assessment', {}),
                'performance_metrics': self._calculate_performance_metrics(pre_analysis),
                'real_time_monitoring': {
                    'active': self.config['enable_real_time_overlap_monitoring'],
                    'status': self.real_time_monitor.get_monitoring_status() if self.config['enable_real_time_overlap_monitoring'] else None,
                    'overlap_summary': self.real_time_monitor.get_overlap_summary() if self.config['enable_real_time_overlap_monitoring'] else None
                },
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
        """Perform comprehensive pre-processing analysis with prompt enhancement insights"""
        # Analyze prompt enhancement if available
        prompt_enhancement_analysis = {}
        if self.prompt_enhancer:
            try:
                # Get enhancement context for the user prompt
                enhancement_context = self.prompt_enhancer._analyze_prompt_context(user_prompt)
                prompt_enhancement_analysis = {
                    'enhancement_context': enhancement_context,
                    'overlap_risk_level': enhancement_context.overlap_risk_level,
                    'performance_considerations': enhancement_context.performance_considerations,
                    'applied_enhancements': self._get_applicable_enhancements(enhancement_context)
                }
                logger.info(f"Prompt enhancement analysis completed: {enhancement_context.prompt_complexity} complexity, {enhancement_context.overlap_risk_level} overlap risk")
            except Exception as e:
                logger.warning(f"Prompt enhancement analysis failed: {e}")
                prompt_enhancement_analysis = {}
        
        analysis = {
            'prompt_complexity': self._analyze_prompt_complexity(user_prompt),
            'object_analysis': self._analyze_objects(animation_spec),
            'sequence_analysis': self.animation_analyzer.analyze_animation_sequence(animation_spec),
            'overlap_risks': self._assess_overlap_risks(animation_spec),
            'performance_considerations': self._assess_performance_considerations(animation_spec),
            'prompt_enhancement_analysis': prompt_enhancement_analysis,
            'risk_assessment': {},
            'optimization_opportunities': []
        }
        
        # Perform risk assessment
        analysis['risk_assessment'] = self._perform_comprehensive_risk_assessment(analysis)
        
        # Identify optimization opportunities
        analysis['optimization_opportunities'] = self._identify_optimization_opportunities(analysis)
        
        return analysis
    
    def _get_applicable_enhancements(self, enhancement_context) -> List[str]:
        """Get list of applicable enhancements based on context"""
        applicable_enhancements = []
        
        if enhancement_context.has_mathematical_content:
            applicable_enhancements.append('mathematical_optimization')
        if enhancement_context.has_geometric_shapes:
            applicable_enhancements.append('geometric_optimization')
        if enhancement_context.has_text_annotations:
            applicable_enhancements.append('text_optimization')
        if enhancement_context.has_animation_effects:
            applicable_enhancements.append('animation_optimization')
        if enhancement_context.overlap_risk_level in ['medium', 'high']:
            applicable_enhancements.append('overlap_prevention')
        if enhancement_context.has_sequence_requirements:
            applicable_enhancements.append('sequence_optimization')
        
        return applicable_enhancements
    
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
        """Optimize object positions using advanced positioning algorithms"""
        try:
            objects = animation_spec.get('objects', [])
            if len(objects) <= 1:
                return animation_spec
            
            # Check if advanced positioning is enabled
            if self.config.get('enable_advanced_positioning', False):
                logger.info("Applying advanced object positioning algorithms...")
                
                # Apply advanced positioning system
                enhanced_spec = self.apply_advanced_positioning(animation_spec)
                
                # Log positioning results
                positioning_metadata = enhanced_spec.get('positioning_metadata', {})
                if positioning_metadata:
                    results = positioning_metadata.get('results', {})
                    logger.info(f"Advanced positioning completed: {results.get('objects_positioned', 0)} objects positioned, "
                               f"{len(results.get('camera_adjustments', []))} camera adjustments, "
                               f"{results.get('collision_resolutions', 0)} collisions resolved")
                    
                    # Log strategy usage
                    strategies = results.get('positioning_strategies_used', {})
                    if strategies:
                        strategy_log = ", ".join([f"{strategy}: {count}" for strategy, count in strategies.items()])
                        logger.debug(f"Positioning strategies used: {strategy_log}")
                
                return enhanced_spec
            else:
                # Fallback to smart positioning for backward compatibility
                logger.debug("Advanced positioning disabled, using smart positioning fallback")
                return self._apply_smart_positioning_fallback(animation_spec, analysis)
            
        except Exception as e:
            logger.error(f"Error in advanced object positioning: {e}")
            # Fallback to basic positioning
            return self._apply_smart_positioning_fallback(animation_spec, analysis)
    
    def _apply_smart_positioning_fallback(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback smart positioning method for backward compatibility"""
        try:
            objects = animation_spec.get('objects', [])
            if len(objects) <= 1:
                return animation_spec
        
            # Smart positioning: Only adjust if objects are truly overlapping
            # For coordinate systems, be very conservative with position changes
            # Allow function plots to overlap when appropriate (user intent)
            overlapping_objects = []
            for i, obj1 in enumerate(objects):
                for j, obj2 in enumerate(objects[i+1:], i+1):
                    pos1 = obj1.get('properties', {}).get('position', [0, 0, 0])
                    pos2 = obj2.get('properties', {}).get('position', [0, 0, 0])
                    type1 = obj1.get('type', 'unknown')
                    type2 = obj2.get('type', 'unknown')
                    
                    # Function plots can overlap at origin - this is expected and desired
                    if type1 == 'plot' and type2 == 'plot':
                        # Allow function plots to overlap at origin for good visual layout
                        continue
                    
                    # Only consider objects overlapping if they're at the EXACT same position
                    # Use an extremely small threshold to avoid unnecessary adjustments
                    if (len(pos1) >= 2 and len(pos2) >= 2 and 
                        abs(pos1[0] - pos2[0]) < 0.01 and abs(pos1[1] - pos2[1]) < 0.01):
                        overlapping_objects.extend([i, j])
            
            # Only adjust truly overlapping objects with minimal changes
            if overlapping_objects:
                logger.info(f"Smart positioning fallback: Adjusting {len(set(overlapping_objects))} overlapping objects")
                for idx in set(overlapping_objects):
                    if idx < len(objects):
                        obj = objects[idx]
                        props = obj.get('properties', {})
                        pos = props.get('position', [0, 0, 0])
                        
                        # Extremely minimal adjustment: just 0.05 unit offset to preserve user intent
                        offset = 0.05 * (idx % 4 - 1.5)  # Minimal spread pattern
                        if len(pos) >= 2:
                            props['position'] = [pos[0] + offset, pos[1], pos[2] if len(pos) > 2 else 0]
                        
                logger.debug(f"Smart object positioning fallback applied to {len(set(overlapping_objects))} objects")
            else:
                logger.debug("No overlapping objects found - positions preserved")
        
            return animation_spec
            
        except Exception as e:
            logger.error(f"Error in smart positioning fallback: {e}")
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
            # For coordinate systems, be very conservative with text positioning
            adjusted_count = 0
            for text_obj in text_objects:
                text_pos = text_obj.get('properties', {}).get('position', [0, 0, 0])
                
                # Check if text is too close to a plot center
                # Use a smaller threshold to avoid unnecessary adjustments
                for plot_obj in plot_objects:
                    plot_pos = plot_obj.get('properties', {}).get('position', [0, 0, 0])
                    if (len(text_pos) >= 2 and len(plot_pos) >= 2 and 
                        abs(text_pos[0] - plot_pos[0]) < 0.3 and abs(text_pos[1] - plot_pos[1]) < 0.3):
                        
                        # Move text very slightly away from plot center
                        # Use smaller offsets to preserve user intent
                        offset_x = 0.3 if text_pos[0] >= plot_pos[0] else -0.3
                        offset_y = 0.2 if text_pos[1] >= plot_pos[1] else -0.2
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
    
    def _optimize_animation_sequence(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any], user_prompt: str = "") -> Dict[str, Any]:
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
            
            # Handle transient objects (shapes, text, dots) - SMART STRATEGY for coordinate systems
            if transient_objects:
                print(f"  🎬 Processing {len(transient_objects)} transient objects with smart display strategy")
                
                # ULTRA CONSERVATIVE: Only use fade-out if EXPLICITLY requested
                # Mathematical functions, coordinate systems, and most objects should remain visible
                # NEVER use fade-out for mathematical content unless explicitly requested
                should_use_fade_out = self._should_use_fade_out_conservative(user_prompt, transient_objects)
                
                if should_use_fade_out:
                    # Check if this is an "appear then fade out" sequence
                    is_appear_then_fade_out = (
                        'then fade out' in user_prompt.lower() or
                        'appear one by one, then fade out' in user_prompt.lower() or
                        'appear one by one, then disappear' in user_prompt.lower()
                    )
                    
                    if is_appear_then_fade_out:
                        print(f"  🎭 Using 'appear then fade out' sequence strategy")
                        # Use Manim's built-in sequential animation approach
                        # This is much simpler and more reliable
                        
                        # Clear any existing animations
                        for obj in transient_objects:
                            obj['animations'] = []
                        
                        # Add simple sequential animations using Manim's natural timing
                        for i, obj in enumerate(transient_objects):
                            # Each object gets a simple fade_in animation
                            # The timing will be handled by Manim's sequential execution
                            fade_in_anim = {
                                'type': 'fade_in',
                                'start_time': 'sequential',
                                'duration': 0.5,
                                'reason': f'sequential_appearance_{i+1}'
                            }
                            obj['animations'].append(fade_in_anim)
                            print(f"  📈 Added sequential fade-in to {obj.get('id', 'unknown')}")
                        
                        # Add fade-out animations that will execute after all fade-ins
                        # ONLY if user explicitly requested fade-out behavior
                        if 'fade out' in user_prompt.lower() or 'disappear' in user_prompt.lower():
                            for i, obj in enumerate(transient_objects):
                                fade_out_anim = {
                                    'type': 'fade_out',
                                    'start_time': 'after_sequence',
                                    'duration': 0.3,
                                    'reason': f'explicit_user_request_{i+1}'
                                }
                                obj['animations'].append(fade_out_anim)
                                print(f"  📉 Added fade-out to {obj.get('id', 'unknown')} (user requested)")
                        else:
                            print(f"  ✅ No fade-out animations added - objects will remain visible")
                    else:
                        print(f"  ⚠️  Many objects detected - using sequential fade-out to prevent clutter")
                        # ULTRA CONSERVATIVE: Only use fade-out if explicitly requested
                        # For complex scenes, prefer keeping objects visible
                        if 'fade out' in user_prompt.lower() or 'disappear' in user_prompt.lower():
                            print(f"  📉 User requested fade-out - applying sequential fade-out")
                            for i, obj in enumerate(transient_objects):
                                if 'animations' not in obj:
                                    obj['animations'] = []
                                
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
                                    prev_obj = transient_objects[i-1]
                                    if 'animations' not in prev_obj:
                                        prev_obj['animations'] = []
                                    
                                    fade_out_anim = {
                                        'type': 'fade_out',
                                        'start_time': 'before_next_transient',
                                        'duration': 0.3,
                                        'reason': 'explicit_user_request'
                                    }
                                    prev_obj['animations'].append(fade_out_anim)
                                    print(f"  📉 Added fade-out to {prev_obj.get('id', 'unknown')} (user requested)")
                                            
                                    fade_in_anim = {
                                        'type': 'fade_in',
                                        'start_time': 'after_previous_transient_fade',
                                        'duration': 0.5,
                                        'reason': 'sequential_display'
                                    }
                                    obj['animations'].append(fade_in_anim)
                                    print(f"  📈 Added fade-in to {obj.get('id', 'unknown')}")
                        else:
                            print(f"  ✅ No fade-out requested - all objects will remain visible")
                            # Simple sequential fade-in without fade-out
                            for i, obj in enumerate(transient_objects):
                                if 'animations' not in obj:
                                    obj['animations'] = []
                                
                                fade_in_anim = {
                                    'type': 'fade_in',
                                    'start_time': 'sequential',
                                    'duration': 0.5,
                                    'reason': 'sequential_appearance'
                                }
                                obj['animations'].append(fade_in_anim)
                                print(f"  📈 Added sequential fade-in to {obj.get('id', 'unknown')} (no fade-out)")
                else:
                    print(f"  ✅ Using smart display - objects will remain visible (no unnecessary fade-out)")
                    # All transient objects fade in sequentially but stay visible
                    for i, obj in enumerate(transient_objects):
                        if 'animations' not in obj:
                            obj['animations'] = []
                        
                        # Calculate delay based on position in sequence
                        # Text should appear with its corresponding object
                        delay = i * 0.3  # 0.3 second delay between each object
                    
                    # Check if this is text that should sync with a plot
                    if obj.get('type') == 'text':
                        # Find corresponding plot and sync timing
                        sync_delay = self._calculate_text_sync_delay(obj, persistent_objects, i)
                        if sync_delay is not None:
                            delay = sync_delay
                    
                    fade_in_anim = {
                        'type': 'fade_in',
                        'start_time': f'after_persistent_display + {delay}s',
                        'duration': 0.5,
                        'reason': 'sequential_display_no_fade_out'
                    }
                    obj['animations'].append(fade_in_anim)
                    print(f"  📈 Added sequential fade-in to {obj.get('id', 'unknown')} (delay: {delay}s)")
            
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
    
    def _calculate_text_sync_delay(self, text_obj: Dict[str, Any], persistent_objects: List[Dict[str, Any]], base_delay: float) -> float:
        """Calculate optimal delay for text to sync with its corresponding plot"""
        try:
            text_pos = text_obj.get('properties', {}).get('position', [0, 0, 0])
            text_content = text_obj.get('properties', {}).get('text', '')
            
            # Find the closest plot object
            closest_plot = None
            min_distance = float('inf')
            
            for plot_obj in persistent_objects:
                if plot_obj.get('type') == 'plot':
                    plot_pos = plot_obj.get('properties', {}).get('position', [0, 0, 0])
                    if len(text_pos) >= 2 and len(plot_pos) >= 2:
                        distance = ((text_pos[0] - plot_pos[0])**2 + (text_pos[1] - plot_pos[1])**2)**0.5
                        if distance < min_distance:
                            min_distance = distance
                            closest_plot = plot_obj
            
            # If text is close to a plot, sync the timing
            if closest_plot and min_distance < 3.0:  # Within 3 units
                # Text should appear shortly after the plot
                return 0.1  # Very short delay after plot
            else:
                # Use base delay for text not associated with plots
                return base_delay
                
        except Exception as e:
            logger.error(f"Error calculating text sync delay: {e}")
            return base_delay
    
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
                # For coordinate systems, be very conservative - only adjust if text is at exact same position as object
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
                    
                    # Only adjust if text is very close to an object (likely overlapping)
                    # Use a very small threshold to preserve user intent
                    if closest_obj and min_distance < 0.2:  # Only if almost overlapping
                        ref_pos = closest_obj.get('properties', {}).get('position', [0, 0, 0])
                        
                        # Very minimal adjustment: just slightly above and to the right
                        smart_pos = [
                            ref_pos[0] + 0.2,  # Very slightly right
                            ref_pos[1] + 0.3,  # Very slightly above
                            text_pos[2] if len(text_pos) > 2 else 0
                        ]
                        
                        text_props['position'] = smart_pos
                        positioned_count += 1
                        logger.debug(f"Minimal text adjustment for '{text_content}' near {closest_obj.get('id', 'unknown')}")
            
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
        DISABLED for coordinate systems to preserve user-specified positions.
        """
        # DISABLED: This was interfering with coordinate system positioning
        # Return without modifying positions to preserve user intent
        logger.debug("Comprehensive overlap prevention DISABLED to preserve coordinate system")
        return
    
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
        """Prevent overlaps between plot objects - DISABLED for coordinate systems"""
        # DISABLED: This was modifying plot positions and interfering with coordinate systems
        # Return without modifying positions to preserve user-specified coordinates
        logger.debug("Plot overlap prevention DISABLED to preserve coordinate system")
        return
    
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
        """Optimize camera strategy for the animation with enhanced smart camera management"""
        objects = animation_spec.get('objects', [])
        if not objects:
            return {'action': 'none', 'reason': 'no_objects'}
        
        # Get the first object as new object for camera management
        new_object = objects[0]
        existing_objects = objects[1:] if len(objects) > 1 else []
        
        # Get enhanced camera strategy with object awareness
        camera_strategy = self.camera_manager.intelligent_camera_management(
            new_object, existing_objects, {}
        )
        
        # ENHANCED: Apply additional camera optimizations based on analysis
        camera_strategy = self._enhance_camera_strategy_with_analysis(camera_strategy, analysis, objects)
        
        # ENHANCED: Add camera strategy metadata for better tracking
        camera_strategy['metadata'] = {
            'total_objects': len(objects),
            'object_types': list(set(obj.get('type', 'unknown') for obj in objects)),
            'has_mathematical_content': any(obj.get('type') in ['plot', 'function', 'graph', 'axes'] for obj in objects),
            'has_text_annotations': any(obj.get('type') == 'text' for obj in objects),
            'has_geometric_shapes': any(obj.get('type') in ['circle', 'square', 'triangle', 'diamond'] for obj in objects),
            'optimization_timestamp': time.time()
        }
        
        return camera_strategy
    
    def _enhance_camera_strategy_with_analysis(self, camera_strategy: Dict[str, Any], analysis: Dict[str, Any], objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance camera strategy based on animation analysis"""
        try:
            # Check if we need to override camera strategy based on analysis
            prompt_complexity = analysis.get('prompt_complexity', {}).get('level', 'unknown')
            overlap_risks = analysis.get('overlap_risks', {}).get('requires_intervention', False)
            
            # For complex prompts, ensure optimal camera positioning
            if prompt_complexity == 'complex':
                if camera_strategy['action'] == 'none':
                    camera_strategy.update({
                        'action': 'complex_prompt_optimization',
                        'reason': 'complex_prompt_requires_enhanced_camera_management',
                        'parameters': {
                            'margin': 0.1,
                            'duration': 0.5,
                            'preserve_mathematical_precision': True,
                            'ensure_text_readability': True
                        },
                        'priority': 'high'
                    })
            
            # For overlap risks, adjust camera to provide more space
            if overlap_risks:
                if camera_strategy['action'] == 'none':
                    camera_strategy.update({
                        'action': 'overlap_prevention_camera_adjustment',
                        'reason': 'overlap_risks_detected_need_more_space',
                        'parameters': {
                            'margin': 0.3,
                            'duration': 0.4,
                            'zoom_factor': 0.9,
                            'prevent_overlaps': True
                        },
                        'priority': 'high'
                    })
            
            return camera_strategy
            
        except Exception as e:
            logger.error(f"Error enhancing camera strategy with analysis: {e}")
            return camera_strategy
    
    def _perform_final_validation(self, animation_spec: Dict[str, Any], analysis: Dict[str, Any], enhanced_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Perform final validation using enhanced validation results"""
        validation_result = {
            'is_valid': enhanced_validation.get('is_valid', True),
            'warnings': enhanced_validation.get('warnings', []),
            'errors': enhanced_validation.get('errors', []),
            'suggestions': enhanced_validation.get('suggestions', []),
            'enhancements_applied': []
        }
        
        # Apply enhanced validation suggestions automatically
        objects = animation_spec.get('objects', [])
        
        # Apply overlap prevention suggestions
        for suggestion in enhanced_validation.get('suggestions', []):
            if suggestion.get('suggested_action') == 'adjust_text_position':
                # Apply text positioning optimization
                self._apply_text_positioning_optimization(animation_spec, suggestion)
                validation_result['enhancements_applied'].append('text_positioning_optimized')
            
            elif suggestion.get('suggested_action') == 'enable_sequential_display':
                # Apply sequential display optimization
                self._apply_sequential_display_optimization(animation_spec)
                validation_result['enhancements_applied'].append('sequential_display_enabled')
            
            elif suggestion.get('suggested_action') == 'add_animation_delay':
                # Apply animation delay optimization
                self._apply_animation_delay_optimization(animation_spec, suggestion)
                validation_result['enhancements_applied'].append('animation_delays_optimized')
        
        # Ensure basic properties are set (fallback to original logic)
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
        
        # Add enhanced validation metadata
        animation_spec['enhanced_validation'] = {
            'validation_result': enhanced_validation,
            'summary': self.enhanced_validator.get_validation_summary(enhanced_validation),
            'applied_enhancements': validation_result['enhancements_applied']
        }
        
        return animation_spec
    
    def _apply_text_positioning_optimization(self, animation_spec: Dict[str, Any], suggestion: Dict[str, Any]):
        """Apply text positioning optimization based on validation suggestion"""
        try:
            objects = animation_spec.get('objects', [])
            for obj in objects:
                if obj.get('type') == 'text':
                    # Adjust text position to avoid overlaps
                    current_pos = obj.get('properties', {}).get('position', [0, 0, 0])
                    if len(current_pos) >= 2:
                        # Move text slightly up and to the right to avoid overlaps
                        new_pos = [current_pos[0] + 0.5, current_pos[1] + 0.5, current_pos[2]]
                        obj['properties']['position'] = new_pos
                        logger.info(f"Optimized text position for {obj.get('id', 'unknown')}: {current_pos} -> {new_pos}")
            
        except Exception as e:
            logger.error(f"Error applying text positioning optimization: {e}")
    
    def _apply_sequential_display_optimization(self, animation_spec: Dict[str, Any]):
        """Apply sequential display optimization based on validation suggestion"""
        try:
            objects = animation_spec.get('objects', [])
            for i, obj in enumerate(objects):
                if 'animations' not in obj:
                    obj['animations'] = []
                
                # Add sequential timing to animations
                for anim in obj['animations']:
                    if anim.get('type') == 'fade_in':
                        anim['start_time'] = f'after_persistent_display + {i * 0.3}s'
                    elif anim.get('type') == 'fade_out':
                        anim['start_time'] = f'after_persistent_display + {(i + 1) * 0.3}s'
                
                logger.info(f"Applied sequential display optimization to {obj.get('id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error applying sequential display optimization: {e}")
    
    def _apply_animation_delay_optimization(self, animation_spec: Dict[str, Any], suggestion: Dict[str, Any]):
        """Apply animation delay optimization based on validation suggestion"""
        try:
            target_object_id = suggestion.get('parameters', {}).get('target_object')
            delay_duration = suggestion.get('parameters', {}).get('delay_duration', 0.5)
            
            objects = animation_spec.get('objects', [])
            for obj in objects:
                if obj.get('id') == target_object_id:
                    if 'animations' not in obj:
                        obj['animations'] = []
                    
                    # Add delay animation before conflicting animations
                    delay_anim = {
                        'type': 'wait',
                        'duration': delay_duration,
                        'start_time': 'immediate'
                    }
                    obj['animations'].insert(0, delay_anim)
                    
                    logger.info(f"Added animation delay to {target_object_id}: {delay_duration}s")
                    break
            
        except Exception as e:
            logger.error(f"Error applying animation delay optimization: {e}")
    
    def _generate_workflow_summary(self, analysis: Dict[str, Any], final_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the workflow processing"""
        # Get advanced positioning information
        positioning_metadata = final_spec.get('positioning_metadata', {})
        positioning_results = positioning_metadata.get('results', {}) if positioning_metadata else {}
        
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
            'performance_estimate': analysis.get('performance_considerations', {}).get('rendering_estimate', 'unknown'),
            'enhanced_validation': final_spec.get('enhanced_validation', {}).get('summary', {}),
            'advanced_positioning': {
                'enabled': self.config.get('enable_advanced_positioning', False),
                'objects_positioned': positioning_results.get('objects_positioned', 0),
                'strategies_used': positioning_results.get('positioning_strategies_used', {}),
                'camera_adjustments': len(positioning_results.get('camera_adjustments', [])),
                'collision_resolutions': positioning_results.get('collision_resolutions', 0),
                'positioning_errors': len(positioning_results.get('errors', []))
            } if positioning_metadata else {
                'enabled': False,
                'message': 'Advanced positioning not applied'
            }
        }
    
    def _should_use_fade_out_conservative(self, user_prompt: str, transient_objects: List[Dict[str, Any]]) -> bool:
        """Ultra-conservative decision making for fade-out usage"""
        try:
            # Check configuration first
            if not self.config.get('fade_out_conservative_mode', True):
                return False
            
            # FIRST: Check if user explicitly requested fade-out (this overrides everything)
            # Use more flexible keyword detection
            explicit_fade_out_keywords = [
                'fade out', 'disappear', 'sequential fade', 'then fade', 'fade them',
                'appear one by one, then fade', 'appear one by one, then disappear',
                'temporary', 'brief', 'momentary', 'remove', 'hide'
            ]
            
            # More flexible detection: check if any keyword is contained in the prompt
            has_explicit_request = any(keyword in user_prompt.lower() for keyword in explicit_fade_out_keywords)
            
            if has_explicit_request:
                print(f"  ✅ Explicit fade-out request detected - allowing fade-out")
                return True
            
            # SECOND: If no explicit request, check if fade-out is required
            if self.config.get('fade_out_explicit_only', True):
                print(f"  🚫 No explicit fade-out request - keeping objects visible")
                return False
            
            # THIRD: Check mathematical content (only if no explicit request)
            if self.config.get('preserve_mathematical_content', True):
                mathematical_keywords = ['function', 'plot', 'graph', 'sine', 'cosine', 'tangent', 'exponential', 'logarithmic']
                has_mathematical_content = any(keyword in user_prompt.lower() for keyword in mathematical_keywords)
                
                if has_mathematical_content:
                    print(f"  🧮 Mathematical content detected - NO fade-out for functions/plots")
                    return False
            
            # FOURTH: Check object types - avoid fade-out for important objects
            for obj in transient_objects:
                obj_type = obj.get('type', '').lower()
                if obj_type in ['axes', 'plot', 'function', 'coordinate']:
                    print(f"  📊 Important object type '{obj_type}' detected - avoiding fade-out")
                    return False
            
            # If we get here, fade-out might be acceptable
            print(f"  ✅ Fade-out conditions met - proceeding with fade-out")
            return True
            
        except Exception as e:
            logger.error(f"Error in conservative fade-out decision: {e}")
            # Default to conservative (no fade-out)
            return False
    
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
        
        # Check if advanced positioning was applied
        if self.config.get('enable_advanced_positioning', False):
            enhancements.append('advanced_positioning')
        
        return enhancements
    
    def _calculate_performance_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics for the workflow"""
        return {
            'processing_efficiency': 'high' if len(analysis.get('optimization_opportunities', [])) > 0 else 'standard',
            'risk_mitigation': analysis.get('risk_assessment', {}).get('overall_risk', 'unknown'),
            'complexity_handling': analysis.get('prompt_complexity', {}).get('level', 'unknown'),
            'optimization_applied': len(analysis.get('optimization_opportunities', []))
        }
    
    # ===== SMART FADE-OUT SYSTEM WITH VALIDATION =====
    
    def robust_fade_out_system(self, object_ids: List[str], validation: bool = True) -> Dict[str, Any]:
        """
        Enhanced fade-out system with validation and fallbacks
        
        Args:
            object_ids: List of object IDs to fade out
            validation: Whether to validate fade-out completion
            
        Returns:
            Dictionary with fade-out results and validation status
        """
        results = {
            'successfully_faded': [],
            'failed_fades': [],
            'validation_passed': False,
            'retry_attempts': 0,
            'total_objects': len(object_ids),
            'operation_id': self._generate_operation_id()
        }
        
        # Track this operation
        self._active_fade_out_operations.add(results['operation_id'])
        
        try:
            logger.info(f"Starting robust fade-out system for {len(object_ids)} objects")
            
            # Phase 1: Primary fade-out attempt
            results.update(self._execute_primary_fade_out(object_ids))
            
            # Phase 2: Validation (if enabled)
            if validation and self.config['enable_fade_out_validation']:
                results['validation_passed'] = self._validate_fade_out_completion(
                    results['successfully_faded']
                )
                
                # Phase 3: Fallback methods if validation failed
                if not results['validation_passed']:
                    results.update(self._execute_fallback_fade_out_methods(object_ids))
                    
                    # Re-validate after fallback
                    if results['successfully_faded']:
                        results['validation_passed'] = self._validate_fade_out_completion(
                            results['successfully_faded']
                        )
            
            # Update tracking
            self._update_fade_out_tracking(results)
            
        except Exception as e:
            logger.error(f"Error in robust fade-out system: {e}")
            results['error'] = str(e)
        finally:
            # Clean up operation tracking
            self._active_fade_out_operations.discard(results['operation_id'])
        
        return results
    
    def _execute_primary_fade_out(self, object_ids: List[str]) -> Dict[str, Any]:
        """Execute primary fade-out strategy"""
        results = {
            'successfully_faded': [],
            'failed_fades': [],
            'primary_method': 'standard_fade_out'
        }
        
        for obj_id in object_ids:
            try:
                # Get object from tracking system
                obj_info = self.object_tracker.get_object_by_id(obj_id)
                if obj_info is None:
                    results['failed_fades'].append({
                        'id': obj_id, 
                        'error': 'Object not found in tracking system'
                    })
                    continue
                
                # Execute fade-out with multiple strategies
                fade_out_success = self._execute_fade_out_strategy(obj_id, obj_info)
                
                if fade_out_success:
                    results['successfully_faded'].append(obj_id)
                    # Mark object as faded out in tracking system
                    try:
                        self.object_tracker.update_visibility_state(obj_id, False, 0.0)
                    except Exception as e:
                        logger.debug(f"Could not update visibility state for {obj_id}: {e}")
                else:
                    results['failed_fades'].append({
                        'id': obj_id, 
                        'error': 'Primary fade-out strategy failed'
                    })
                    
            except Exception as e:
                results['failed_fades'].append({
                    'id': obj_id, 
                    'error': str(e)
                })
        
        return results
    
    def _execute_fade_out_strategy(self, obj_id: str, obj_info: Dict[str, Any]) -> bool:
        """Execute fade-out with multiple fallback strategies"""
        strategies = [
            self._standard_fade_out,
            self._gradual_fade_out,
            self._instant_fade_out,
            self._scale_fade_out
        ]
        
        for strategy in strategies:
            try:
                if strategy(obj_id, obj_info):
                    logger.debug(f"Fade-out strategy {strategy.__name__} succeeded for {obj_id}")
                    return True
            except Exception as e:
                logger.debug(f"Fade-out strategy {strategy.__name__} failed for {obj_id}: {e}")
                continue
        
        return False
    
    def _standard_fade_out(self, obj_id: str, obj_info: Dict[str, Any]) -> bool:
        """Standard fade-out animation"""
        try:
            # This would integrate with Manim's FadeOut
            # For now, we simulate success
            logger.debug(f"Standard fade-out executed for {obj_id}")
            return True
        except Exception as e:
            logger.error(f"Standard fade-out failed for {obj_id}: {e}")
            return False
    
    def _gradual_fade_out(self, obj_id: str, obj_info: Dict[str, Any]) -> bool:
        """Gradual fade-out with opacity reduction"""
        try:
            # Simulate gradual opacity reduction
            logger.debug(f"Gradual fade-out executed for {obj_id}")
            return True
        except Exception as e:
            logger.error(f"Gradual fade-out failed for {obj_id}: {e}")
            return False
    
    def _instant_fade_out(self, obj_id: str, obj_info: Dict[str, Any]) -> bool:
        """Instant fade-out (fallback method)"""
        try:
            # Simulate instant removal
            logger.debug(f"Instant fade-out executed for {obj_id}")
            return True
        except Exception as e:
            logger.error(f"Instant fade-out failed for {obj_id}: {e}")
            return False
    
    def _scale_fade_out(self, obj_id: str, obj_info: Dict[str, Any]) -> bool:
        """Scale-based fade-out (alternative method)"""
        try:
            # Simulate scale-based fade-out
            logger.debug(f"Scale fade-out executed for {obj_id}")
            return True
        except Exception as e:
            logger.error(f"Scale fade-out failed for {obj_id}: {e}")
            return False
    
    def _validate_fade_out_completion(self, faded_object_ids: List[str]) -> bool:
        """
        Validate that fade-out actually completed successfully
        
        Args:
            faded_object_ids: List of object IDs that were faded out
            
        Returns:
            True if all objects are properly faded out, False otherwise
        """
        if not faded_object_ids:
            return True
        
        validation_results = []
        
        for obj_id in faded_object_ids:
            try:
                # Check if object is still in tracking system
                obj_info = self.object_tracker.get_object_by_id(obj_id)
                
                if obj_info is None:
                    # Object successfully removed from tracking
                    validation_results.append(True)
                else:
                    # Check object state
                    obj_state = obj_info.get('state', {})
                    opacity = obj_state.get('opacity', 1.0)
                    visibility = obj_state.get('is_visible', True)
                    
                    # Object should be invisible or have very low opacity
                    if opacity <= 0.1 or not visibility:
                        validation_results.append(True)
                    else:
                        validation_results.append(False)
                        logger.warning(f"Object {obj_id} still visible after fade-out (opacity: {opacity})")
                        
            except Exception as e:
                logger.error(f"Error validating fade-out for {obj_id}: {e}")
                validation_results.append(False)
        
        # All objects must pass validation
        return all(validation_results)
    
    def _execute_fallback_fade_out_methods(self, object_ids: List[str]) -> Dict[str, Any]:
        """Execute alternative fade-out methods when primary method fails"""
        results = {
            'fallback_methods_used': [],
            'additional_faded': [],
            'fallback_errors': []
        }
        
        # Try alternative methods for failed objects
        failed_objects = [obj for obj in object_ids if obj not in results.get('successfully_faded', [])]
        
        for obj_id in failed_objects:
            try:
                # Try aggressive fade-out
                if self._aggressive_fade_out(obj_id):
                    results['additional_faded'].append(obj_id)
                    results['fallback_methods_used'].append('aggressive_fade_out')
                else:
                    # Try object removal
                    if self._force_object_removal(obj_id):
                        results['additional_faded'].append(obj_id)
                        results['fallback_methods_used'].append('force_removal')
                    else:
                        results['fallback_errors'].append({
                            'id': obj_id,
                            'error': 'All fallback methods failed'
                        })
                        
            except Exception as e:
                results['fallback_errors'].append({
                    'id': obj_id,
                    'error': str(e)
                })
        
        return results
    
    def _aggressive_fade_out(self, obj_id: str) -> bool:
        """Aggressive fade-out with multiple techniques"""
        try:
            # Simulate aggressive fade-out
            logger.debug(f"Aggressive fade-out executed for {obj_id}")
            return True
        except Exception as e:
            logger.error(f"Aggressive fade-out failed for {obj_id}: {e}")
            return False
    
    def _force_object_removal(self, obj_id: str) -> bool:
        """Force object removal from scene"""
        try:
            # Simulate force removal
            logger.debug(f"Force removal executed for {obj_id}")
            return True
        except Exception as e:
            logger.error(f"Force removal failed for {obj_id}: {e}")
            return False
    
    def _update_fade_out_tracking(self, results: Dict[str, Any]) -> None:
        """Update fade-out tracking and history"""
        operation_id = results.get('operation_id')
        if operation_id:
            self._fade_out_history[operation_id] = {
                'timestamp': self._get_current_timestamp(),
                'results': results,
                'success_rate': len(results['successfully_faded']) / results['total_objects'] if results['total_objects'] > 0 else 0
            }
            
            # Cache validation results for performance
            for obj_id in results['successfully_faded']:
                self._fade_out_validation_cache[obj_id] = {
                    'validated': results['validation_passed'],
                    'timestamp': self._get_current_timestamp(),
                    'operation_id': operation_id
                }
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID for tracking"""
        import uuid
        return str(uuid.uuid4())
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp for tracking"""
        import time
        return time.time()
    
    def apply_advanced_positioning(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply advanced object positioning algorithms to the animation specification
        
        Args:
            animation_spec: The animation specification to enhance
            
        Returns:
            Enhanced animation specification with optimal object positions
        """
        try:
            if not self.config['enable_advanced_positioning']:
                logger.debug("Advanced positioning disabled")
                return animation_spec
            
            logger.info("Applying advanced object positioning algorithms...")
            
            # Get screen bounds
            screen_bounds = self._get_screen_bounds()
            
            # Track positioning results
            positioning_results = {
                'objects_positioned': 0,
                'positioning_strategies_used': {},
                'camera_adjustments': [],
                'collision_resolutions': 0,
                'errors': []
            }
            
            objects = animation_spec.get('objects', [])
            existing_objects = []
            
            # Process objects in sequence to build up existing objects list
            for i, obj in enumerate(objects):
                try:
                    # Get object properties
                    properties = obj.get('properties', {})
                    obj_type = obj.get('type', 'unknown')
                    
                    # Apply advanced positioning
                    positioning_strategy = self.advanced_positioning.find_optimal_position(
                        obj, existing_objects, screen_bounds
                    )
                    
                    if positioning_strategy and positioning_strategy['position']:
                        # Update object position
                        properties['position'] = positioning_strategy['position']
                        obj['properties'] = properties
                        
                        # Track strategy usage
                        strategy = positioning_strategy['method']
                        positioning_results['positioning_strategies_used'][strategy] = \
                            positioning_results['positioning_strategies_used'].get(strategy, 0) + 1
                        
                        # Check for camera adjustments
                        if positioning_strategy['camera_adjustment']:
                            positioning_results['camera_adjustments'].append({
                                'object_id': obj.get('id', f'obj_{i}'),
                                'adjustment': positioning_strategy['camera_adjustment']
                            })
                        
                        positioning_results['objects_positioned'] += 1
                        
                        # Log positioning details
                        logger.debug(f"Object {obj.get('id', f'obj_{i}')} ({obj_type}) positioned using "
                                   f"{strategy} at {positioning_strategy['position']} "
                                   f"(confidence: {positioning_strategy['confidence']:.2f})")
                        
                        # Add to existing objects for next iteration
                        existing_objects.append(obj)
                        
                        # Resolve collisions if needed
                        if positioning_strategy['collision_risk'] > 0.5:
                            self._resolve_positioning_collision(obj, existing_objects, screen_bounds)
                            positioning_results['collision_resolutions'] += 1
                    else:
                        # Fallback positioning
                        properties['position'] = [0, 0, 0]
                        obj['properties'] = properties
                        existing_objects.append(obj)
                        positioning_results['errors'].append({
                            'object_id': obj.get('id', f'obj_{i}'),
                            'error': 'Positioning strategy failed, using fallback'
                        })
                        
                except Exception as e:
                    logger.error(f"Error positioning object {i}: {e}")
                    positioning_results['errors'].append({
                        'object_id': obj.get('id', f'obj_{i}'),
                        'error': str(e)
                    })
                    # Use fallback position
                    properties = obj.get('properties', {})
                    properties['position'] = [0, 0, 0]
                    obj['properties'] = properties
                    existing_objects.append(obj)
            
            # Apply camera adjustments if needed
            if positioning_results['camera_adjustments']:
                self._apply_camera_adjustments(positioning_results['camera_adjustments'])
            
            # Update animation spec with positioning metadata
            animation_spec['positioning_metadata'] = {
                'advanced_positioning_applied': True,
                'timestamp': time.time(),
                'results': positioning_results
            }
            
            logger.info(f"Advanced positioning completed: {positioning_results['objects_positioned']} objects positioned, "
                       f"{len(positioning_results['camera_adjustments'])} camera adjustments, "
                       f"{positioning_results['collision_resolutions']} collisions resolved")
            
            return animation_spec
            
        except Exception as e:
            logger.error(f"Error in advanced positioning: {e}")
            return animation_spec
    
    def _get_screen_bounds(self) -> Dict[str, float]:
        """Get screen bounds for positioning calculations"""
        try:
            # Use camera management system to get screen bounds
            return self.camera_manager.get_screen_bounds()
        except Exception as e:
            logger.error(f"Error getting screen bounds: {e}")
            # Fallback to default bounds
            return {
                'min_x': -8,
                'min_y': -4.5,
                'max_x': 8,
                'max_y': 4.5,
                'width': 16,
                'height': 9
            }
    
    def _resolve_positioning_collision(self, obj: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                                     screen_bounds: Dict[str, float]) -> None:
        """Resolve positioning collisions using advanced algorithms"""
        try:
            # Get alternative positions
            positioning_strategy = self.advanced_positioning.find_optimal_position(
                obj, existing_objects, screen_bounds
            )
            
            if positioning_strategy and positioning_strategy['alternatives']:
                # Try alternative positions
                for alt_pos in positioning_strategy['alternatives']:
                    collision_risk = self._calculate_collision_risk(alt_pos, existing_objects)
                    if collision_risk < 0.3:  # Acceptable collision risk
                        properties = obj.get('properties', {})
                        properties['position'] = alt_pos
                        obj['properties'] = properties
                        logger.debug(f"Resolved collision for {obj.get('id', 'unknown')} using alternative position {alt_pos}")
                        break
                        
        except Exception as e:
            logger.error(f"Error resolving positioning collision: {e}")
    
    def _calculate_collision_risk(self, position: List[float], existing_objects: List[Dict[str, Any]]) -> float:
        """Calculate collision risk for a position"""
        try:
            if not existing_objects:
                return 0.0
            
            min_distance = float('inf')
            for obj in existing_objects:
                properties = obj.get('properties', {})
                obj_pos = properties.get('position', [0, 0, 0])
                
                distance = ((position[0] - obj_pos[0])**2 + (position[1] - obj_pos[1])**2)**0.5
                min_distance = min(min_distance, distance)
            
            # Convert distance to collision risk (closer = higher risk)
            collision_threshold = self.config['advanced_positioning_config']['collision_threshold']
            if min_distance < collision_threshold:
                return 1.0 - (min_distance / collision_threshold)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating collision risk: {e}")
            return 0.5
    
    def _apply_camera_adjustments(self, camera_adjustments: List[Dict[str, Any]]) -> None:
        """Apply camera adjustments from positioning system"""
        try:
            for adjustment in camera_adjustments:
                camera_strategy = adjustment['adjustment']
                if camera_strategy['action'] == 'zoom_out':
                    # Apply zoom out using camera management system
                    self.camera_manager.apply_camera_strategy(camera_strategy, None)  # Scene will be passed later
                    logger.debug(f"Applied camera adjustment: {camera_strategy['action']} for {adjustment['object_id']}")
                    
        except Exception as e:
            logger.error(f"Error applying camera adjustments: {e}")
    
    def get_fade_out_statistics(self) -> Dict[str, Any]:
        """Get statistics about fade-out operations"""
        if not self._fade_out_history:
            return {'message': 'No fade-out operations recorded'}
        
        total_operations = len(self._fade_out_history)
        successful_operations = sum(
            1 for op in self._fade_out_history.values() 
            if op['results']['validation_passed']
        )
        
        return {
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
            'active_operations': len(self._active_fade_out_operations),
            'cached_validations': len(self._fade_out_validation_cache)
        }
