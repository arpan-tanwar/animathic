"""
Enhanced JSON Schema Validation Service for Animathic
Provides comprehensive validation with overlap detection, sequence analysis, and intelligent suggestions
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import math

logger = logging.getLogger(__name__)


class EnhancedValidationService:
    """Enhanced validation service with intelligent analysis and suggestions"""
    
    def __init__(self):
        """Initialize the enhanced validation service"""
        self.validation_config = {
            'enable_overlap_detection': True,
            'enable_sequence_analysis': True,
            'enable_schema_validation': True,
            'enable_performance_analysis': True,
            'overlap_threshold': 1.0,  # Distance threshold for overlap detection
            'validation_level': 'comprehensive'  # 'minimal', 'standard', 'comprehensive'
        }
        
        # Allowed object types from prompts.py
        self.allowed_object_types = {
            "circle", "square", "text", "line", "dot", "axes", "plot", 
            "diamond", "star", "hexagon", "triangle", "rectangle", "ellipse"
        }
        
        # Allowed animation types from prompts.py
        self.allowed_animation_types = {
            "move", "scale", "rotate", "fade_in", "fade_out", 
            "transform", "fade_out_previous", "clear_previous_plots", "wait"
        }
        
        logger.info("EnhancedValidationService initialized")
    
    def enhanced_animation_validation(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced validation with overlap detection and suggestions"""
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': [],
            'overlap_analysis': {},
            'sequence_analysis': {},
            'schema_validation': {},
            'performance_analysis': {},
            'enhancement_opportunities': []
        }
        
        try:
            # Phase 1: Basic schema validation
            if self.validation_config['enable_schema_validation']:
                schema_result = self._validate_schema_structure(animation_spec)
                validation_result['schema_validation'] = schema_result
                if not schema_result['is_valid']:
                    validation_result['is_valid'] = False
                    validation_result['errors'].extend(schema_result['errors'])
            
            # Phase 2: Overlap detection
            if self.validation_config['enable_overlap_detection']:
                overlap_result = self._detect_potential_overlaps(animation_spec)
                validation_result['overlap_analysis'] = overlap_result
                if overlap_result['has_overlaps']:
                    validation_result['warnings'].append({
                        'type': 'potential_overlap',
                        'message': 'Detected potential object overlaps',
                        'details': overlap_result['overlap_details']
                    })
                    validation_result['suggestions'].extend(
                        self._generate_overlap_solutions(overlap_result)
                    )
            
            # Phase 3: Animation sequence logic analysis
            if self.validation_config['enable_sequence_analysis']:
                sequence_result = self._analyze_animation_sequence_logic(animation_spec)
                validation_result['sequence_analysis'] = sequence_result
                if sequence_result['has_issues']:
                    validation_result['warnings'].append({
                        'type': 'sequence_issue',
                        'message': 'Animation sequence may have logical issues',
                        'details': sequence_result['issues']
                    })
                    validation_result['suggestions'].extend(
                        self._generate_sequence_solutions(sequence_result)
                    )
            
            # Phase 4: Performance analysis
            if self.validation_config['enable_performance_analysis']:
                performance_result = self._analyze_performance_considerations(animation_spec)
                validation_result['performance_analysis'] = performance_result
                if performance_result['requires_optimization']:
                    validation_result['suggestions'].extend(
                        self._generate_performance_suggestions(performance_result)
                    )
            
            # Phase 5: Enhancement opportunities
            validation_result['enhancement_opportunities'] = self._identify_enhancement_opportunities(
                animation_spec, validation_result
            )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error in enhanced animation validation: {e}")
            validation_result['is_valid'] = False
            validation_result['errors'].append({
                'type': 'validation_error',
                'message': f'Validation process failed: {str(e)}'
            })
            return validation_result
    
    def _validate_schema_structure(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the basic structure of the animation specification"""
        schema_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'structure_issues': []
        }
        
        try:
            # Check required top-level fields
            required_fields = ['objects']
            for field in required_fields:
                if field not in animation_spec:
                    schema_result['errors'].append({
                        'field': field,
                        'issue': 'missing_required_field',
                        'message': f'Required field "{field}" is missing'
                    })
                    schema_result['is_valid'] = False
            
            # Validate objects array
            objects = animation_spec.get('objects', [])
            if not isinstance(objects, list):
                schema_result['errors'].append({
                    'field': 'objects',
                    'issue': 'invalid_type',
                    'message': 'Objects field must be an array'
                })
                schema_result['is_valid'] = False
            else:
                # Validate each object
                for i, obj in enumerate(objects):
                    obj_validation = self._validate_object_structure(obj, i)
                    if not obj_validation['is_valid']:
                        schema_result['errors'].extend(obj_validation['errors'])
                        schema_result['is_valid'] = False
                    
                    if obj_validation['warnings']:
                        schema_result['warnings'].extend(obj_validation['warnings'])
            
            # Validate optional fields if present
            if 'camera_settings' in animation_spec:
                camera_validation = self._validate_camera_settings(animation_spec['camera_settings'])
                if not camera_validation['is_valid']:
                    schema_result['warnings'].extend(camera_validation['warnings'])
            
            return schema_result
            
        except Exception as e:
            logger.error(f"Error in schema structure validation: {e}")
            schema_result['is_valid'] = False
            schema_result['errors'].append({
                'field': 'unknown',
                'issue': 'validation_error',
                'message': f'Schema validation failed: {str(e)}'
            })
            return schema_result
    
    def _validate_object_structure(self, obj: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate individual object structure"""
        obj_validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'object_index': index
        }
        
        try:
            # Check required object fields
            if not isinstance(obj, dict):
                obj_validation['errors'].append({
                    'field': f'objects[{index}]',
                    'issue': 'invalid_type',
                    'message': 'Object must be a dictionary'
                })
                obj_validation['is_valid'] = False
                return obj_validation
            
            # Check object type
            obj_type = obj.get('type')
            if not obj_type:
                obj_validation['errors'].append({
                    'field': f'objects[{index}].type',
                    'issue': 'missing_required_field',
                    'message': 'Object type is required'
                })
                obj_validation['is_valid'] = False
            elif obj_type not in self.allowed_object_types:
                obj_validation['warnings'].append({
                    'field': f'objects[{index}].type',
                    'issue': 'unknown_type',
                    'message': f'Unknown object type: {obj_type}'
                })
            
            # Check object ID
            obj_id = obj.get('id')
            if not obj_id:
                obj_validation['warnings'].append({
                    'field': f'objects[{index}].id',
                    'issue': 'missing_id',
                    'message': 'Object ID is recommended for better tracking'
                })
            
            # Validate properties
            properties = obj.get('properties', {})
            if not isinstance(properties, dict):
                obj_validation['errors'].append({
                    'field': f'objects[{index}].properties',
                    'issue': 'invalid_type',
                    'message': 'Properties must be a dictionary'
                })
                obj_validation['is_valid'] = False
            else:
                # Validate position if present
                position = properties.get('position')
                if position is not None:
                    if not isinstance(position, list) or len(position) < 2:
                        obj_validation['warnings'].append({
                            'field': f'objects[{index}].properties.position',
                            'issue': 'invalid_position',
                            'message': 'Position should be [x, y, z] array'
                        })
                
                # Validate size if present
                size = properties.get('size')
                if size is not None and (not isinstance(size, (int, float)) or size <= 0):
                    obj_validation['warnings'].append({
                        'field': f'objects[{index}].properties.size',
                        'issue': 'invalid_size',
                        'message': 'Size should be a positive number'
                    })
            
            # Validate animations
            animations = obj.get('animations', [])
            if not isinstance(animations, list):
                obj_validation['errors'].append({
                    'field': f'objects[{index}].animations',
                    'issue': 'invalid_type',
                    'message': 'Animations must be an array'
                })
                obj_validation['is_valid'] = False
            else:
                for j, anim in enumerate(animations):
                    anim_validation = self._validate_animation_structure(anim, index, j)
                    if not anim_validation['is_valid']:
                        obj_validation['errors'].extend(anim_validation['errors'])
                        obj_validation['is_valid'] = False
                    
                    if anim_validation['warnings']:
                        obj_validation['warnings'].extend(anim_validation['warnings'])
            
            return obj_validation
            
        except Exception as e:
            logger.error(f"Error in object structure validation: {e}")
            obj_validation['is_valid'] = False
            obj_validation['errors'].append({
                'field': f'objects[{index}]',
                'issue': 'validation_error',
                'message': f'Object validation failed: {str(e)}'
            })
            return obj_validation
    
    def _validate_animation_structure(self, anim: Dict[str, Any], obj_index: int, anim_index: int) -> Dict[str, Any]:
        """Validate individual animation structure"""
        anim_validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'object_index': obj_index,
            'animation_index': anim_index
        }
        
        try:
            if not isinstance(anim, dict):
                anim_validation['errors'].append({
                    'field': f'objects[{obj_index}].animations[{anim_index}]',
                    'issue': 'invalid_type',
                    'message': 'Animation must be a dictionary'
                })
                anim_validation['is_valid'] = False
                return anim_validation
            
            # Check animation type
            anim_type = anim.get('type')
            if not anim_type:
                anim_validation['errors'].append({
                    'field': f'objects[{obj_index}].animations[{anim_index}].type',
                    'issue': 'missing_required_field',
                    'message': 'Animation type is required'
                })
                anim_validation['is_valid'] = False
            elif anim_type not in self.allowed_animation_types:
                anim_validation['warnings'].append({
                    'field': f'objects[{obj_index}].animations[{anim_index}].type',
                    'issue': 'unknown_type',
                    'message': f'Unknown animation type: {anim_type}'
                })
            
            # Check duration
            duration = anim.get('duration')
            if duration is not None:
                if not isinstance(duration, (int, float)) or duration < 0:
                    anim_validation['warnings'].append({
                        'field': f'objects[{obj_index}].animations[{anim_index}].duration',
                        'issue': 'invalid_duration',
                        'message': 'Duration should be a non-negative number'
                    })
            
            # Check parameters
            parameters = anim.get('parameters', {})
            if not isinstance(parameters, dict):
                anim_validation['warnings'].append({
                    'field': f'objects[{obj_index}].animations[{anim_index}].parameters',
                    'issue': 'invalid_type',
                    'message': 'Parameters should be a dictionary'
                })
            
            return anim_validation
            
        except Exception as e:
            logger.error(f"Error in animation structure validation: {e}")
            anim_validation['is_valid'] = False
            anim_validation['errors'].append({
                'field': f'objects[{obj_index}].animations[{anim_index}]',
                'issue': 'validation_error',
                'message': f'Animation validation failed: {str(e)}'
            })
            return anim_validation
    
    def _validate_camera_settings(self, camera_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate camera settings structure"""
        camera_validation = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        try:
            if not isinstance(camera_settings, dict):
                camera_validation['errors'].append({
                    'field': 'camera_settings',
                    'issue': 'invalid_type',
                    'message': 'Camera settings must be a dictionary'
                })
                camera_validation['is_valid'] = False
                return camera_validation
            
            # Validate position if present
            position = camera_settings.get('position')
            if position is not None:
                if not isinstance(position, list) or len(position) < 2:
                    camera_validation['warnings'].append({
                        'field': 'camera_settings.position',
                        'issue': 'invalid_position',
                        'message': 'Camera position should be [x, y, z] array'
                    })
            
            # Validate zoom if present
            zoom = camera_settings.get('zoom')
            if zoom is not None and (not isinstance(zoom, (int, float)) or zoom <= 0):
                camera_validation['warnings'].append({
                    'field': 'camera_settings.zoom',
                    'issue': 'invalid_zoom',
                    'message': 'Camera zoom should be a positive number'
                })
            
            return camera_validation
            
        except Exception as e:
            logger.error(f"Error in camera settings validation: {e}")
            camera_validation['is_valid'] = False
            camera_validation['errors'].append({
                'field': 'camera_settings',
                'issue': 'validation_error',
                'message': f'Camera settings validation failed: {str(e)}'
            })
            return camera_validation
    
    def _detect_potential_overlaps(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential overlaps between objects"""
        overlaps = {
            'has_overlaps': False,
            'overlap_details': [],
            'risk_assessment': 'low',
            'total_overlaps': 0
        }
        
        try:
            objects = animation_spec.get('objects', [])
            if len(objects) <= 1:
                return overlaps
            
            overlap_count = 0
            high_risk_overlaps = 0
            
            for i, obj1 in enumerate(objects):
                pos1 = obj1.get('properties', {}).get('position', [0, 0, 0])
                type1 = obj1.get('type', 'unknown')
                size1 = obj1.get('properties', {}).get('size', 1.0)
                
                for j, obj2 in enumerate(objects[i+1:], i+1):
                    pos2 = obj2.get('properties', {}).get('position', [0, 0, 0])
                    type2 = obj2.get('type', 'unknown')
                    size2 = obj2.get('properties', {}).get('size', 1.0)
                    
                    # Calculate distance and overlap risk
                    if len(pos1) >= 2 and len(pos2) >= 2:
                        distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                        
                        # Calculate combined size for overlap detection
                        combined_size = (size1 + size2) / 2
                        
                        # Detect overlaps based on distance and size
                        if distance < combined_size:
                            overlap_count += 1
                            
                            # Assess risk level
                            if type1 == type2:
                                risk_level = 'high'
                                high_risk_overlaps += 1
                            elif distance < self.validation_config['overlap_threshold']:
                                risk_level = 'medium'
                            else:
                                risk_level = 'low'
                            
                            overlaps['overlap_details'].append({
                                'object1': {
                                    'index': i,
                                    'id': obj1.get('id', f'obj_{i}'),
                                    'type': type1,
                                    'position': pos1,
                                    'size': size1
                                },
                                'object2': {
                                    'index': j,
                                    'id': obj2.get('id', f'obj_{j}'),
                                    'type': type2,
                                    'position': pos2,
                                    'size': size2
                                },
                                'distance': distance,
                                'combined_size': combined_size,
                                'risk_level': risk_level,
                                'overlap_severity': combined_size - distance
                            })
            
            overlaps['total_overlaps'] = overlap_count
            overlaps['has_overlaps'] = overlap_count > 0
            
            # Determine overall risk assessment
            if high_risk_overlaps > 0:
                overlaps['risk_assessment'] = 'high'
            elif overlap_count > 2:
                overlaps['risk_assessment'] = 'medium'
            else:
                overlaps['risk_assessment'] = 'low'
            
            return overlaps
            
        except Exception as e:
            logger.error(f"Error in overlap detection: {e}")
            overlaps['has_overlaps'] = False
            overlaps['overlap_details'] = []
            overlaps['risk_assessment'] = 'unknown'
            return overlaps
    
    def _generate_overlap_solutions(self, overlap_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent solutions for overlap issues"""
        solutions = []
        
        try:
            for overlap in overlap_analysis.get('overlap_details', []):
                obj1 = overlap['object1']
                obj2 = overlap['object2']
                distance = overlap['distance']
                combined_size = overlap['combined_size']
                risk_level = overlap['risk_level']
                
                # Calculate optimal spacing
                optimal_distance = combined_size * 1.2  # 20% margin
                
                # Generate specific solutions based on object types
                if obj1['type'] == 'text' or obj2['type'] == 'text':
                    # Text objects need special handling
                    solutions.append({
                        'type': 'text_positioning',
                        'priority': 'high' if risk_level == 'high' else 'medium',
                        'message': f'Reposition text object "{obj1["id"] if obj1["type"] == "text" else obj2["id"]}" to avoid overlap',
                        'suggested_action': 'adjust_text_position',
                        'parameters': {
                            'optimal_distance': optimal_distance,
                            'current_distance': distance,
                            'required_adjustment': optimal_distance - distance
                        }
                    })
                
                elif obj1['type'] in ['plot', 'function', 'graph'] or obj2['type'] in ['plot', 'function', 'graph']:
                    # Mathematical objects - suggest camera adjustment
                    solutions.append({
                        'type': 'camera_adjustment',
                        'priority': 'medium',
                        'message': 'Adjust camera to provide more space for mathematical content',
                        'suggested_action': 'zoom_out_camera',
                        'parameters': {
                            'zoom_factor': 0.8,
                            'reason': 'mathematical_content_overlap'
                        }
                    })
                
                else:
                    # Geometric shapes - suggest repositioning
                    solutions.append({
                        'type': 'object_repositioning',
                        'priority': 'medium' if risk_level == 'high' else 'low',
                        'message': f'Reposition objects to maintain {optimal_distance:.2f} units spacing',
                        'suggested_action': 'adjust_object_position',
                        'parameters': {
                            'optimal_distance': optimal_distance,
                            'current_distance': distance,
                            'required_adjustment': optimal_distance - distance
                        }
                    })
            
            # Add general overlap prevention suggestions
            if overlap_analysis['risk_assessment'] == 'high':
                solutions.append({
                    'type': 'general_optimization',
                    'priority': 'high',
                    'message': 'Consider using sequential display to prevent overlaps',
                    'suggested_action': 'enable_sequential_display',
                    'parameters': {
                        'fade_out_previous': True,
                        'sequential_timing': True
                    }
                })
            
            return solutions
            
        except Exception as e:
            logger.error(f"Error generating overlap solutions: {e}")
            return []
    
    def _analyze_animation_sequence_logic(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze animation sequence logic for potential issues"""
        sequence_analysis = {
            'has_issues': False,
            'issues': [],
            'sequence_complexity': 'simple',
            'timing_issues': [],
            'dependency_issues': []
        }
        
        try:
            objects = animation_spec.get('objects', [])
            if len(objects) <= 1:
                return sequence_analysis
            
            # Analyze animation sequences
            for obj in objects:
                animations = obj.get('animations', [])
                if len(animations) > 1:
                    # Check for conflicting animations
                    fade_in_count = sum(1 for anim in animations if anim.get('type') == 'fade_in')
                    fade_out_count = sum(1 for anim in animations if anim.get('type') == 'fade_out')
                    
                    if fade_in_count > 1:
                        sequence_analysis['issues'].append({
                            'object_id': obj.get('id', 'unknown'),
                            'type': 'multiple_fade_in',
                            'message': 'Object has multiple fade-in animations',
                            'severity': 'medium'
                        })
                        sequence_analysis['has_issues'] = True
                    
                    if fade_out_count > 1:
                        sequence_analysis['issues'].append({
                            'object_id': obj.get('id', 'unknown'),
                            'type': 'multiple_fade_out',
                            'message': 'Object has multiple fade-out animations',
                            'severity': 'medium'
                        })
                        sequence_analysis['has_issues'] = True
                    
                    # Check for conflicting timing
                    for i, anim1 in enumerate(animations):
                        for j, anim2 in enumerate(animations[i+1:], i+1):
                            if anim1.get('type') == 'fade_out' and anim2.get('type') == 'fade_in':
                                sequence_analysis['issues'].append({
                                    'object_id': obj.get('id', 'unknown'),
                                    'type': 'conflicting_animations',
                                    'message': 'Fade-out followed by fade-in may cause flickering',
                                    'severity': 'high'
                                })
                                sequence_analysis['has_issues'] = True
            
            # Determine sequence complexity
            total_animations = sum(len(obj.get('animations', [])) for obj in objects)
            if total_animations > 10:
                sequence_analysis['sequence_complexity'] = 'complex'
            elif total_animations > 5:
                sequence_analysis['sequence_complexity'] = 'moderate'
            else:
                sequence_analysis['sequence_complexity'] = 'simple'
            
            return sequence_analysis
            
        except Exception as e:
            logger.error(f"Error in sequence logic analysis: {e}")
            sequence_analysis['has_issues'] = False
            sequence_analysis['issues'] = []
            return sequence_analysis
    
    def _generate_sequence_solutions(self, sequence_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate solutions for sequence logic issues"""
        solutions = []
        
        try:
            for issue in sequence_analysis.get('issues', []):
                if issue['type'] == 'multiple_fade_in':
                    solutions.append({
                        'type': 'animation_consolidation',
                        'priority': 'medium',
                        'message': f'Consolidate multiple fade-in animations for object {issue["object_id"]}',
                        'suggested_action': 'merge_fade_animations',
                        'parameters': {
                            'target_object': issue['object_id'],
                            'animation_type': 'fade_in'
                        }
                    })
                
                elif issue['type'] == 'multiple_fade_out':
                    solutions.append({
                        'type': 'animation_consolidation',
                        'priority': 'medium',
                        'message': f'Consolidate multiple fade-out animations for object {issue["object_id"]}',
                        'suggested_action': 'merge_fade_animations',
                        'parameters': {
                            'target_object': issue['object_id'],
                            'animation_type': 'fade_out'
                        }
                    })
                
                elif issue['type'] == 'conflicting_animations':
                    solutions.append({
                        'type': 'timing_adjustment',
                        'priority': 'high',
                        'message': f'Add delay between conflicting animations for object {issue["object_id"]}',
                        'suggested_action': 'add_animation_delay',
                        'parameters': {
                            'target_object': issue['object_id'],
                            'delay_duration': 0.5,
                            'reason': 'prevent_flickering'
                        }
                    })
            
            # Add general sequence optimization suggestions
            if sequence_analysis['sequence_complexity'] == 'complex':
                solutions.append({
                    'type': 'sequence_optimization',
                    'priority': 'medium',
                    'message': 'Consider using sequential display for complex animations',
                    'suggested_action': 'enable_sequential_display',
                    'parameters': {
                        'sequential_timing': True,
                        'batch_size': 3
                    }
                })
            
            return solutions
            
        except Exception as e:
            logger.error(f"Error generating sequence solutions: {e}")
            return []
    
    def _analyze_performance_considerations(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance considerations for the animation"""
        performance_analysis = {
            'requires_optimization': False,
            'complexity_score': 0,
            'rendering_estimate': 'fast',
            'memory_usage': 'low',
            'optimization_recommendations': []
        }
        
        try:
            objects = animation_spec.get('objects', [])
            
            # Calculate complexity score
            for obj in objects:
                obj_type = obj.get('type', 'unknown')
                if obj_type in ['plot', 'function', 'graph']:
                    performance_analysis['complexity_score'] += 3
                elif obj_type in ['axes', 'text']:
                    performance_analysis['complexity_score'] += 1
                else:
                    performance_analysis['complexity_score'] += 2
                
                # Add complexity for animations
                animations = obj.get('animations', [])
                performance_analysis['complexity_score'] += len(animations) * 0.5
            
            # Determine performance characteristics
            if performance_analysis['complexity_score'] <= 5:
                performance_analysis['rendering_estimate'] = 'fast'
                performance_analysis['memory_usage'] = 'low'
            elif performance_analysis['complexity_score'] <= 12:
                performance_analysis['rendering_estimate'] = 'moderate'
                performance_analysis['memory_usage'] = 'medium'
            else:
                performance_analysis['rendering_estimate'] = 'slow'
                performance_analysis['memory_usage'] = 'high'
                performance_analysis['requires_optimization'] = True
            
            # Generate optimization recommendations
            if performance_analysis['complexity_score'] > 10:
                performance_analysis['optimization_recommendations'].append('consider_batching_animations')
                performance_analysis['optimization_recommendations'].append('optimize_object_positions')
            
            if len(objects) > 6:
                performance_analysis['optimization_recommendations'].append('use_sequential_display')
            
            if performance_analysis['complexity_score'] > 15:
                performance_analysis['optimization_recommendations'].append('reduce_animation_complexity')
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
            performance_analysis['requires_optimization'] = False
            performance_analysis['complexity_score'] = 0
            return performance_analysis
    
    def _generate_performance_suggestions(self, performance_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance optimization suggestions"""
        solutions = []
        
        try:
            for recommendation in performance_analysis.get('optimization_recommendations', []):
                if recommendation == 'consider_batching_animations':
                    solutions.append({
                        'type': 'performance_optimization',
                        'priority': 'medium',
                        'message': 'Batch animations to improve performance',
                        'suggested_action': 'enable_animation_batching',
                        'parameters': {
                            'batch_size': 3,
                            'batch_delay': 0.2
                        }
                    })
                
                elif recommendation == 'optimize_object_positions':
                    solutions.append({
                        'type': 'performance_optimization',
                        'priority': 'low',
                        'message': 'Optimize object positions to reduce rendering complexity',
                        'suggested_action': 'enable_position_optimization',
                        'parameters': {
                            'overlap_prevention': True,
                            'spatial_optimization': True
                        }
                    })
                
                elif recommendation == 'use_sequential_display':
                    solutions.append({
                        'type': 'performance_optimization',
                        'priority': 'medium',
                        'message': 'Use sequential display for better performance',
                        'suggested_action': 'enable_sequential_display',
                        'parameters': {
                            'sequential_timing': True,
                            'fade_out_previous': True
                        }
                    })
                
                elif recommendation == 'reduce_animation_complexity':
                    solutions.append({
                        'type': 'performance_optimization',
                        'priority': 'high',
                        'message': 'Reduce animation complexity for better performance',
                        'suggested_action': 'simplify_animations',
                        'parameters': {
                            'max_animations_per_object': 2,
                            'simplify_timing': True
                        }
                    })
            
            return solutions
            
        except Exception as e:
            logger.error(f"Error generating performance suggestions: {e}")
            return []
    
    def _identify_enhancement_opportunities(self, animation_spec: Dict[str, Any], validation_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities for workflow enhancements"""
        opportunities = []
        
        try:
            objects = animation_spec.get('objects', [])
            
            # Check for mathematical content enhancement opportunities
            math_objects = [obj for obj in objects if obj.get('type') in ['plot', 'function', 'graph', 'axes']]
            if len(math_objects) > 1:
                opportunities.append({
                    'type': 'mathematical_optimization',
                    'priority': 'medium',
                    'message': 'Multiple mathematical objects detected - enable mathematical optimization',
                    'enhancement': 'enable_mathematical_optimization',
                    'benefit': 'Improved mathematical content positioning and camera management'
                })
            
            # Check for text annotation opportunities
            text_objects = [obj for obj in objects if obj.get('type') == 'text']
            if text_objects:
                opportunities.append({
                    'type': 'text_optimization',
                    'priority': 'low',
                    'message': 'Text objects detected - enable text readability optimization',
                    'enhancement': 'enable_text_optimization',
                    'benefit': 'Better text positioning and readability'
                })
            
            # Check for geometric shape opportunities
            geometric_objects = [obj for obj in objects if obj.get('type') in ['circle', 'square', 'triangle', 'diamond']]
            if len(geometric_objects) > 2:
                opportunities.append({
                    'type': 'geometric_optimization',
                    'priority': 'low',
                    'message': 'Multiple geometric shapes detected - enable shape framing optimization',
                    'enhancement': 'enable_geometric_optimization',
                    'benefit': 'Optimal shape positioning and camera framing'
                })
            
            # Check for sequence optimization opportunities
            total_animations = sum(len(obj.get('animations', [])) for obj in objects)
            if total_animations > 8:
                opportunities.append({
                    'type': 'sequence_optimization',
                    'priority': 'medium',
                    'message': 'Complex animation sequence detected - enable sequence optimization',
                    'enhancement': 'enable_sequence_optimization',
                    'benefit': 'Better animation timing and performance'
                })
            
            # Check for camera optimization opportunities
            if len(objects) > 4:
                opportunities.append({
                    'type': 'camera_optimization',
                    'priority': 'medium',
                    'message': 'Multiple objects detected - enable camera optimization',
                    'enhancement': 'enable_camera_optimization',
                    'benefit': 'Automatic camera positioning and framing'
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error identifying enhancement opportunities: {e}")
            return []
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of validation results"""
        try:
            summary = {
                'overall_status': 'valid' if validation_result['is_valid'] else 'invalid',
                'total_warnings': len(validation_result['warnings']),
                'total_errors': len(validation_result['errors']),
                'total_suggestions': len(validation_result['suggestions']),
                'enhancement_opportunities': len(validation_result.get('enhancement_opportunities', [])),
                'risk_level': validation_result.get('overlap_analysis', {}).get('risk_assessment', 'unknown'),
                'sequence_complexity': validation_result.get('sequence_analysis', {}).get('sequence_complexity', 'unknown'),
                'performance_estimate': validation_result.get('performance_analysis', {}).get('rendering_estimate', 'unknown')
            }
            
            # Add priority breakdown
            high_priority_issues = sum(1 for warning in validation_result['warnings'] 
                                     if warning.get('priority') == 'high')
            medium_priority_issues = sum(1 for warning in validation_result['warnings'] 
                                       if warning.get('priority') == 'medium')
            
            summary['priority_breakdown'] = {
                'high': high_priority_issues,
                'medium': medium_priority_issues,
                'low': len(validation_result['warnings']) - high_priority_issues - medium_priority_issues
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating validation summary: {e}")
            return {'overall_status': 'error', 'error_message': str(e)}


# Global instance
enhanced_validator = EnhancedValidationService()
