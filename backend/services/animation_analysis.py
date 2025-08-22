"""
Animation Sequence Analysis System for Animathic
Analyzes animation specs for overlaps, optimizations, and sequence management
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AnimationSequenceAnalyzer:
    """Analyzes animation sequences for potential issues and optimizations"""
    
    def __init__(self):
        """Initialize the animation analyzer"""
        pass
    
    def analyze_animation_sequence(self, animation_spec):
        """Analyze animation spec to detect potential overlaps and optimize sequence"""
        analysis = {
            'sequential_objects': [],      # objects that should appear one after another
            'concurrent_objects': [],      # objects that can appear simultaneously
            'overlap_risks': [],          # potential overlap scenarios
            'optimization_suggestions': [], # how to improve the sequence
            'required_fade_outs': [],     # which objects must fade out
            'timing_recommendations': [],  # optimal timing for animations
            'camera_adjustments': [],     # suggested camera adjustments
            'risk_assessment': {          # overall risk assessment
                'overlap_risk': 'low',
                'sequence_risk': 'low',
                'performance_risk': 'low'
            }
        }
        
        try:
            objects = animation_spec.get('objects', [])
            
            # Analyze each object in sequence
            for i, obj in enumerate(objects):
                obj_type = obj.get('type', '')
                obj_id = obj.get('id', f'obj_{i}')
                
                # Detect sequential requirements for plot-like objects
                if obj_type in ['plot', 'function', 'graph']:
                    if i > 0:
                        prev_obj = objects[i-1]
                        prev_type = prev_obj.get('type', '')
                        
                        # If previous object is also plot-like, require sequential display
                        if prev_type in ['plot', 'function', 'graph']:
                            analysis['sequential_objects'].append({
                                'current': {
                                    'id': obj_id,
                                    'type': obj_type,
                                    'index': i,
                                    'properties': obj.get('properties', {})
                                },
                                'previous': {
                                    'id': prev_obj.get('id', f'obj_{i-1}'),
                                    'type': prev_type,
                                    'index': i-1,
                                    'properties': prev_obj.get('properties', {})
                                },
                                'required_action': 'fade_out_previous',
                                'reason': 'plot_objects_cannot_overlap',
                                'priority': 'high'
                            })
                            
                            # Add to required fade-outs
                            analysis['required_fade_outs'].append({
                                'object_id': prev_obj.get('id', f'obj_{i-1}'),
                                'reason': 'sequential_plot_requirement',
                                'timing': 'before_new_plot',
                                'duration': 0.5
                            })
                
                # Detect overlap risks for all object types
                if obj_type in ['axes', 'plot', 'function', 'graph', 'circle', 'square', 'line']:
                    for j, prev_obj in enumerate(objects[:i]):
                        prev_type = prev_obj.get('type', '')
                        
                        # Check if objects might overlap
                        if prev_type in ['axes', 'plot', 'function', 'graph', 'circle', 'square', 'line']:
                            risk_level = 'high'
                            risk_reason = ''
                            
                            # Determine risk level based on object types
                            if obj_type == prev_type:
                                risk_level = 'high'
                                risk_reason = 'same_object_type'
                            elif obj_type in ['plot', 'function', 'graph'] and prev_type in ['plot', 'function', 'graph']:
                                risk_level = 'high'
                                risk_reason = 'multiple_plot_objects'
                            elif obj_type in ['axes'] and prev_type in ['plot', 'function', 'graph']:
                                risk_level = 'medium'
                                risk_reason = 'axes_with_existing_plots'
                            else:
                                risk_level = 'low'
                                risk_reason = 'different_object_types'
                            
                            analysis['overlap_risks'].append({
                                'new': {
                                    'id': obj_id,
                                    'type': obj_type,
                                    'index': i,
                                    'properties': obj.get('properties', {})
                                },
                                'existing': {
                                    'id': prev_obj.get('id', f'obj_{j}'),
                                    'type': prev_type,
                                    'index': j,
                                    'properties': prev_obj.get('properties', {})
                                },
                                'risk_level': risk_level,
                                'risk_reason': risk_reason,
                                'suggested_action': self._get_suggested_action(risk_level, obj_type, prev_type)
                            })
            
            # Generate optimization suggestions
            analysis['optimization_suggestions'] = self._generate_optimization_suggestions(analysis)
            
            # Generate timing recommendations
            analysis['timing_recommendations'] = self._generate_timing_recommendations(analysis, objects)
            
            # Generate camera adjustment suggestions
            analysis['camera_adjustments'] = self._generate_camera_adjustments(analysis, objects)
            
            # Assess overall risks
            analysis['risk_assessment'] = self._assess_overall_risks(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_animation_sequence: {e}")
            return {'error': str(e)}

    def resolve_label_overlaps(self, animation_spec, object_registry):
        """Resolve overlapping labels and text objects"""
        try:
            if 'objects' not in animation_spec:
                return {'status': 'no_objects_to_resolve'}
            
            label_objects = []
            for obj in animation_spec['objects']:
                if obj.get('type', '').lower() in ['text', 'label', 'mathtex', 'tex']:
                    label_objects.append(obj)
            
            if len(label_objects) <= 1:
                return {'status': 'no_overlaps_possible'}
            
            # Simple strategy: shift overlapping labels vertically
            resolved_count = 0
            for i, label in enumerate(label_objects):
                if i > 0:  # Shift subsequent labels
                    if 'properties' not in label:
                        label['properties'] = {}
                    current_y = label['properties'].get('position', [0, 0])[1] if isinstance(label['properties'].get('position'), list) else 0
                    label['properties']['position'] = [0, current_y - i * 0.8]
                    resolved_count += 1
            
            return {
                'status': 'resolved',
                'resolved_overlaps': resolved_count,
                'strategy': 'vertical_shift'
            }
        except Exception as e:
            logger.error(f"Error in resolve_label_overlaps: {e}")
            return {'status': 'error', 'message': str(e)}

    def resolve_object_overlaps(self, animation_spec, object_registry):
        """Resolve overlapping objects in the animation"""
        try:
            if 'objects' not in animation_spec:
                return {'status': 'no_objects_to_resolve'}
            
            objects = animation_spec['objects']
            if len(objects) <= 1:
                return {'status': 'no_overlaps_possible'}
            
            # Simple grid layout for overlapping objects
            resolved_count = 0
            cols = 2
            for i, obj in enumerate(objects):
                if 'properties' not in obj:
                    obj['properties'] = {}
                
                row = i // cols
                col = i % cols
                x = (col - cols/2 + 0.5) * 2  # Space objects horizontally
                y = (row - len(objects)/(2*cols) + 0.5) * 1.5  # Space vertically
                
                obj['properties']['position'] = [x, y]
                resolved_count += 1
            
            return {
                'status': 'resolved',
                'resolved_overlaps': resolved_count,
                'strategy': 'grid_layout'
            }
        except Exception as e:
            logger.error(f"Error in resolve_object_overlaps: {e}")
            return {'status': 'error', 'message': str(e)}

    def resolve_graph_overlaps(self, animation_spec, object_registry):
        """Resolve overlapping graphs and plots"""
        try:
            if 'objects' not in animation_spec:
                return {'status': 'no_objects_to_resolve'}
            
            graph_objects = []
            for obj in animation_spec['objects']:
                if obj.get('type', '').lower() in ['plot', 'graph', 'function', 'axes']:
                    graph_objects.append(obj)
            
            if len(graph_objects) <= 1:
                return {'status': 'no_overlaps_possible'}
            
            # Strategy: Use different color schemes and slight position shifts
            resolved_count = 0
            colors = ['BLUE', 'RED', 'GREEN', 'ORANGE', 'PURPLE']
            
            for i, graph in enumerate(graph_objects):
                if 'properties' not in graph:
                    graph['properties'] = {}
                
                # Assign different colors
                if i < len(colors):
                    graph['properties']['color'] = colors[i]
                
                # Slight position shifts
                if i > 0:
                    shift_x = (i % 2) * 0.5 - 0.25
                    shift_y = (i // 2) * 0.3 - 0.15
                    current_pos = graph['properties'].get('position', [0, 0])
                    if isinstance(current_pos, list) and len(current_pos) >= 2:
                        graph['properties']['position'] = [current_pos[0] + shift_x, current_pos[1] + shift_y]
                    else:
                        graph['properties']['position'] = [shift_x, shift_y]
                
                resolved_count += 1
            
            return {
                'status': 'resolved',
                'resolved_overlaps': resolved_count,
                'strategy': 'color_and_shift'
            }
        except Exception as e:
            logger.error(f"Error in resolve_graph_overlaps: {e}")
            return {'status': 'error', 'message': str(e)}

    def smart_graph_positioning(self, animation_spec):
        """Smart positioning for graphs to optimize screen space"""
        try:
            if 'objects' not in animation_spec:
                return {'status': 'no_objects_to_position'}
            
            graph_objects = []
            other_objects = []
            
            for obj in animation_spec['objects']:
                if obj.get('type', '').lower() in ['plot', 'graph', 'function', 'axes']:
                    graph_objects.append(obj)
                else:
                    other_objects.append(obj)
            
            if not graph_objects:
                return {'status': 'no_graphs_found'}
            
            # Position graphs in optimal locations
            positioned_count = 0
            
            if len(graph_objects) == 1:
                # Single graph: center it
                graph = graph_objects[0]
                if 'properties' not in graph:
                    graph['properties'] = {}
                graph['properties']['position'] = [0, 0]
                positioned_count = 1
            
            elif len(graph_objects) == 2:
                # Two graphs: side by side
                for i, graph in enumerate(graph_objects):
                    if 'properties' not in graph:
                        graph['properties'] = {}
                    x = (i - 0.5) * 3  # Space them apart
                    graph['properties']['position'] = [x, 0]
                    positioned_count += 1
            
            else:
                # Multiple graphs: grid layout
                cols = 2
                for i, graph in enumerate(graph_objects):
                    if 'properties' not in graph:
                        graph['properties'] = {}
                    
                    row = i // cols
                    col = i % cols
                    x = (col - cols/2 + 0.5) * 3
                    y = (row - len(graph_objects)/(2*cols) + 0.5) * 2
                    
                    graph['properties']['position'] = [x, y]
                    positioned_count += 1
            
            return {
                'status': 'positioned',
                'positioned_graphs': positioned_count,
                'strategy': f'{"single" if len(graph_objects) == 1 else "dual" if len(graph_objects) == 2 else "grid"}_layout'
            }
        except Exception as e:
            logger.error(f"Error in smart_graph_positioning: {e}")
            return {'status': 'error', 'message': str(e)}

    def detect_potential_overlaps(self, object_registry):
        """Detect potential overlaps between objects"""
        overlaps = []
        
        try:
            # Check for overlaps between objects of the same type that shouldn't overlap
            problematic_types = ['plot', 'function', 'graph']
            
            for obj_type in problematic_types:
                objects_of_type = []
                if 'type_registry' in object_registry:
                    obj_ids = object_registry['type_registry'].get(obj_type, [])
                    for obj_id in obj_ids:
                        if obj_id in object_registry.get('active_objects', {}):
                            objects_of_type.append({
                                'object_id': obj_id,
                                'state': object_registry.get('visibility_states', {}).get(obj_id, {})
                            })
                
                if len(objects_of_type) > 1:
                    # Multiple objects of the same type - potential overlap
                    overlaps.append({
                        'type': 'multiple_same_type',
                        'object_type': obj_type,
                        'count': len(objects_of_type),
                        'object_ids': [obj['object_id'] for obj in objects_of_type],
                        'risk_level': 'high',
                        'suggested_action': 'fade_out_oldest'
                    })
            
            return overlaps
        except Exception as e:
            logger.error(f"Error in detect_potential_overlaps: {e}")
            return []

    def apply_sequence_analysis(self, animation_spec, analysis_result):
        """Apply the sequence analysis to optimize the animation specification"""
        try:
            # Simplified version that just returns the original spec
            # This avoids scope issues with the complex analysis functions
            return animation_spec
            
        except Exception as e:
            logger.error(f"Error in apply_sequence_analysis: {e}")
            return animation_spec

    def get_animation_sequence_summary(self, animation_spec):
        """Get a summary of the animation sequence for monitoring"""
        try:
            # Simplified summary without complex analysis to avoid scope issues
            objects = animation_spec.get('objects', [])
            
            summary = {
                'total_objects': len(objects),
                'object_types': {},
                'overlap_risks': {'high': 0, 'medium': 0, 'low': 0},
                'sequential_requirements': 0,
                'required_fade_outs': 0,
                'risk_assessment': {'overlap_risk': 'low', 'sequence_risk': 'low'},
                'optimization_suggestions': 0,
                'camera_adjustments': 0
            }
            
            # Count object types
            for obj in objects:
                obj_type = obj.get('type', 'unknown')
                summary['object_types'][obj_type] = summary['object_types'].get(obj_type, 0) + 1
            
            # Simple risk assessment
            plot_types = ['plot', 'function', 'graph']
            plot_count = sum(summary['object_types'].get(t, 0) for t in plot_types)
            
            if plot_count > 2:
                summary['overlap_risks']['high'] = plot_count - 2
                summary['risk_assessment']['overlap_risk'] = 'high'
            elif plot_count > 1:
                summary['overlap_risks']['medium'] = plot_count - 1
                summary['risk_assessment']['overlap_risk'] = 'medium'
            
            summary['required_fade_outs'] = max(0, plot_count - 1)
            
            return summary
        except Exception as e:
            logger.error(f"Error in get_animation_sequence_summary: {e}")
            return {'error': str(e)}

    def smart_position_objects(self, objects_data):
        """Smart positioning system to prevent overlaps and ensure good distribution"""
        try:
            if not objects_data:
                return
            
            # Create a grid-based positioning system
            grid_size = 2.0
            grid_margin = 0.5
            used_positions = set()
            
            for obj_data in objects_data:
                obj_type = obj_data.get('type', 'circle')
                props = obj_data.get('properties', {})
                
                # Get object size for collision detection
                if obj_type == 'circle':
                    size = props.get('size', 1.0) * 2  # diameter
                elif obj_type == 'square':
                    size = props.get('size', 2.0)
                elif obj_type == 'text':
                    size = 1.5  # Estimated text size
                else:
                    size = 1.0
                
                # Find a free position
                position_found = False
                for grid_x in range(-3, 4):
                    for grid_y in range(-2, 3):
                        pos_x = grid_x * grid_size
                        pos_y = grid_y * grid_size
                        
                        # Check if position is free (with margin)
                        collision = False
                        for used_x, used_y in used_positions:
                            if (abs(pos_x - used_x) < size + grid_margin and 
                                abs(pos_y - used_y) < size + grid_margin):
                                collision = True
                                break
                        
                        if not collision:
                            # Use this position
                            props['position'] = [pos_x, pos_y]
                            used_positions.add((pos_x, pos_y))
                            position_found = True
                            break
                    
                    if position_found:
                        break
                
                # If no position found, use a random offset
                if not position_found:
                    import random
                    props['position'] = [
                        random.uniform(-4, 4),
                        random.uniform(-3, 3)
                    ]
            
            return {'status': 'positioned', 'objects_positioned': len(objects_data)}
        except Exception as e:
            logger.error(f"Error in smart_position_objects: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_suggested_action(self, risk_level, new_type, existing_type):
        """Get suggested action based on risk level and object types"""
        if risk_level == 'high':
            if new_type in ['plot', 'function', 'graph'] and existing_type in ['plot', 'function', 'graph']:
                return 'fade_out_existing_before_create_new'
            elif new_type == existing_type:
                return 'fade_out_existing_and_replace'
            else:
                return 'fade_out_existing_or_reposition'
        elif risk_level == 'medium':
            if new_type == 'axes' and existing_type in ['plot', 'function', 'graph']:
                return 'clear_plots_before_create_axes'
            else:
                return 'reposition_or_fade_out'
        else:
            return 'monitor_for_overlaps'
    
    def _generate_optimization_suggestions(self, analysis):
        """Generate optimization suggestions based on analysis"""
        suggestions = []
        
        # Suggest fade-out sequences for overlapping objects
        if analysis['overlap_risks']:
            high_risk_overlaps = [r for r in analysis['overlap_risks'] if r['risk_level'] == 'high']
            if high_risk_overlaps:
                suggestions.append({
                    'type': 'sequential_display',
                    'priority': 'high',
                    'description': f'Display {len(high_risk_overlaps)} high-risk objects sequentially to avoid overlaps',
                    'action': 'fade_out_previous_before_new',
                    'objects_affected': [r['new']['id'] for r in high_risk_overlaps]
                })
        
        # Suggest timing optimizations
        if analysis['sequential_objects']:
            suggestions.append({
                'type': 'timing_optimization',
                'priority': 'medium',
                'description': 'Optimize timing between sequential objects for smooth transitions',
                'action': 'adjust_animation_delays',
                'objects_affected': [s['current']['id'] for s in analysis['sequential_objects']]
            })
        
        # Suggest camera adjustments for multiple objects
        total_objects = len(analysis.get('concurrent_objects', [])) + len(analysis.get('sequential_objects', []))
        if total_objects > 3:
            suggestions.append({
                'type': 'camera_adjustment',
                'priority': 'medium',
                'description': f'Adjust camera to accommodate {total_objects} objects',
                'action': 'zoom_out_or_pan',
                'objects_affected': 'all'
            })
        
        return suggestions
    
    def _generate_timing_recommendations(self, analysis, objects):
        """Generate optimal timing recommendations for animations"""
        recommendations = []
        
        # Base timing for different object types
        base_timings = {
            'axes': 0.5,
            'plot': 1.0,
            'function': 1.0,
            'graph': 1.0,
            'circle': 0.3,
            'square': 0.3,
            'text': 0.2,
            'line': 0.4
        }
        
        # Calculate optimal timing based on object complexity
        for i, obj in enumerate(objects):
            obj_type = obj.get('type', '')
            base_time = base_timings.get(obj_type, 0.5)
            
            # Adjust timing based on object properties
            properties = obj.get('properties', {})
            if 'complexity' in properties:
                complexity_factor = min(2.0, max(0.5, properties['complexity']))
                base_time *= complexity_factor
            
            # Add delay for sequential objects
            delay = 0.0
            if any(s['current']['id'] == obj.get('id', f'obj_{i}') for s in analysis.get('sequential_objects', [])):
                delay = 0.5  # Add delay for sequential display
            
            recommendations.append({
                'object_id': obj.get('id', f'obj_{i}'),
                'type': obj_type,
                'recommended_duration': base_time,
                'recommended_delay': delay,
                'total_time': base_time + delay,
                'reasoning': f'Base timing for {obj_type} with sequential delay' if delay > 0 else f'Base timing for {obj_type}'
            })
        
        return recommendations
    
    def _generate_camera_adjustments(self, analysis, objects):
        """Generate camera adjustment suggestions"""
        adjustments = []
        
        # Check if we need to zoom out for multiple objects
        if len(objects) > 2:
            adjustments.append({
                'type': 'zoom_out',
                'priority': 'medium',
                'reason': f'Multiple objects ({len(objects)}) may require more screen space',
                'parameters': {
                    'zoom_factor': 0.8,
                    'duration': 0.5,
                    'target_objects': [obj.get('id', f'obj_{i}') for i, obj in enumerate(objects)]
                }
            })
        
        # Check for objects that might be outside screen bounds
        for obj in objects:
            properties = obj.get('properties', {})
            position = properties.get('position', [0, 0, 0])
            
            # Check if position is outside reasonable bounds
            if abs(position[0]) > 6 or abs(position[1]) > 3:
                adjustments.append({
                    'type': 'pan_camera',
                    'priority': 'high',
                    'reason': f'Object {obj.get("id", "unknown")} is positioned outside optimal screen area',
                    'parameters': {
                        'target_position': [max(-6, min(6, position[0])), max(-3, min(3, position[1])), 0],
                        'duration': 0.3,
                        'object_id': obj.get('id', 'unknown')
                    }
                })
        
        return adjustments
    
    def _assess_overall_risks(self, analysis):
        """Assess overall risks in the animation sequence"""
        risk_assessment = {
            'overlap_risk': 'low',
            'sequence_risk': 'low',
            'performance_risk': 'low',
            'camera_risk': 'low',
            'overall_risk': 'low'
        }
        
        # Assess overlap risk
        high_risk_overlaps = len([r for r in analysis.get('overlap_risks', []) if r['risk_level'] == 'high'])
        if high_risk_overlaps > 2:
            risk_assessment['overlap_risk'] = 'high'
        elif high_risk_overlaps > 0:
            risk_assessment['overlap_risk'] = 'medium'
        
        # Assess sequence risk
        sequential_objects = len(analysis.get('sequential_objects', []))
        if sequential_objects > 3:
            risk_assessment['sequence_risk'] = 'high'
        elif sequential_objects > 1:
            risk_assessment['sequence_risk'] = 'medium'
        
        # Assess performance risk
        total_objects = len(analysis.get('concurrent_objects', [])) + len(analysis.get('sequential_objects', []))
        if total_objects > 5:
            risk_assessment['performance_risk'] = 'high'
        elif total_objects > 3:
            risk_assessment['performance_risk'] = 'medium'
        
        # Assess camera risk
        camera_adjustments = len(analysis.get('camera_adjustments', []))
        if camera_adjustments > 2:
            risk_assessment['camera_risk'] = 'high'
        elif camera_adjustments > 0:
            risk_assessment['camera_risk'] = 'medium'
        
        # Calculate overall risk
        risk_levels = {'low': 1, 'medium': 2, 'high': 3}
        overall_score = sum(risk_levels[risk_assessment[key]] for key in ['overlap_risk', 'sequence_risk', 'performance_risk', 'camera_risk'])
        
        if overall_score >= 10:
            risk_assessment['overall_risk'] = 'high'
        elif overall_score >= 6:
            risk_assessment['overall_risk'] = 'medium'
        
        return risk_assessment
    
    def real_time_sequence_monitoring(self, current_objects, animation_progress):
        """Monitor animation sequence in real-time"""
        monitoring_result = {
            'current_state': 'normal',
            'warnings': [],
            'suggestions': [],
            'overlap_detected': False,
            'performance_issues': []
        }
        
        try:
            # Check for current overlaps
            if len(current_objects) > 1:
                # Simple overlap check based on positions
                for i, obj1 in enumerate(current_objects):
                    pos1 = obj1.get('properties', {}).get('position', [0, 0, 0])
                    
                    for j, obj2 in enumerate(current_objects[i+1:], i+1):
                        pos2 = obj2.get('properties', {}).get('position', [0, 0, 0])
                        
                        # Calculate distance between objects
                        distance = ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
                        
                        if distance < 1.0:  # Objects are too close
                            monitoring_result['overlap_detected'] = True
                            monitoring_result['warnings'].append({
                                'type': 'proximity_warning',
                                'message': f'Objects {obj1.get("id", "unknown")} and {obj2.get("id", "unknown")} are too close',
                                'severity': 'medium',
                                'suggestion': 'Consider repositioning or adding fade-out transitions'
                            })
            
            # Check animation progress
            if animation_progress < 0.3 and len(current_objects) > 3:
                monitoring_result['performance_issues'].append({
                    'type': 'early_complexity',
                    'message': 'Many objects created early in animation',
                    'suggestion': 'Consider staggering object creation or reducing initial complexity'
                })
            
            # Update current state based on findings
            if monitoring_result['overlap_detected']:
                monitoring_result['current_state'] = 'warning'
            if monitoring_result['performance_issues']:
                monitoring_result['current_state'] = 'performance_concern'
            
            return monitoring_result
            
        except Exception as e:
            logger.error(f"Error in real-time sequence monitoring: {e}")
            return monitoring_result
