"""
Robust Fade-Out System for Animathic
Manages object fade-out with validation and fallback strategies
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class FadeOutSystem:
    """Enhanced fade-out system with validation and fallbacks"""
    
    def __init__(self):
        """Initialize the fade-out system"""
        pass
    
    def robust_fade_out_system(self, object_ids, object_registry, validation=True):
        """Enhanced fade-out system with validation and fallbacks"""
        results = {
            'successfully_faded': [],
            'failed_fades': [],
            'validation_passed': False,
            'fallback_methods_used': [],
            'total_objects_processed': len(object_ids)
        }
        
        # Phase 1: Fade out objects
        for obj_id in object_ids:
            try:
                mobj = object_registry['active_objects'].get(obj_id)
                if mobj is not None:
                    # Use multiple fade-out strategies
                    fade_success = False
                    
                    # Strategy 1: Try native fade_out method
                    if hasattr(mobj, 'fade_out'):
                        try:
                            from .manim_utilities import safe_play
                            safe_play(None, mobj.fade_out(), run_time=0.3)
                            fade_success = True
                        except Exception as e:
                            logger.debug(f"Native fade_out failed for {obj_id}: {e}")
                    
                    # Strategy 2: Use FadeOut animation
                    if not fade_success:
                        try:
                            from manim import FadeOut
                            from .manim_utilities import safe_play
                            safe_play(None, FadeOut(mobj), run_time=0.3)
                            fade_success = True
                        except Exception as e:
                            logger.debug(f"FadeOut animation failed for {obj_id}: {e}")
                    
                    # Strategy 3: Manual opacity reduction
                    if not fade_success:
                        try:
                            mobj.set_opacity(0.0)
                            fade_success = True
                            results['fallback_methods_used'].append({
                                'object_id': obj_id,
                                'method': 'manual_opacity_set',
                                'reason': 'fade_animations_failed'
                            })
                        except Exception as e:
                            logger.debug(f"Manual opacity setting failed for {obj_id}: {e}")
                    
                    if fade_success:
                        results['successfully_faded'].append(obj_id)
                        
                        # Remove from tracking
                        if obj_id in object_registry['active_objects']:
                            del object_registry['active_objects'][obj_id]
                        
                        # Update type registry
                        obj_type = object_registry['object_states'].get(obj_id, {}).get('type', 'unknown')
                        if obj_type in object_registry['type_registry']:
                            if obj_id in object_registry['type_registry'][obj_type]:
                                object_registry['type_registry'][obj_type].remove(obj_id)
                        
                        # Update visibility state
                        if obj_id in object_registry['visibility_states']:
                            object_registry['visibility_states'][obj_id].update({
                                'is_visible': False,
                                'opacity': 0.0,
                                'fade_out_in_progress': False
                            })
                    else:
                        results['failed_fades'].append({
                            'id': obj_id, 
                            'error': 'All fade-out strategies failed',
                            'object_type': object_registry['object_states'].get(obj_id, {}).get('type', 'unknown')
                        })
                        
            except Exception as e:
                results['failed_fades'].append({
                    'id': obj_id, 
                    'error': str(e),
                    'object_type': object_registry['object_states'].get(obj_id, {}).get('type', 'unknown')
                })
        
        # Phase 2: Validation (if enabled)
        if validation:
            results['validation_passed'] = self.validate_fade_out_completion(object_ids, object_registry)
            
            # If validation failed, try alternative methods
            if not results['validation_passed']:
                alternative_results = self.alternative_fade_out_methods(object_ids, object_registry)
                results.update(alternative_results)
                
                # Re-validate after alternative methods
                results['validation_passed'] = self.validate_fade_out_completion(object_ids, object_registry)
        
        # Phase 3: Final cleanup
        results['final_cleanup'] = self.perform_final_cleanup(object_ids, object_registry)
        
        return results
    
    def validate_fade_out_completion(self, faded_object_ids, object_registry):
        """Validate that fade-out actually completed successfully"""
        validation_results = {
            'passed': True,
            'failed_objects': [],
            'partial_successes': [],
            'validation_details': {}
        }
        
        try:
            for obj_id in faded_object_ids:
                mobj = object_registry['active_objects'].get(obj_id)
                validation_detail = {
                    'object_id': obj_id,
                    'object_type': object_registry['object_states'].get(obj_id, {}).get('type', 'unknown'),
                    'opacity_check': False,
                    'visibility_check': False,
                    'registry_check': False
                }
                
                if mobj is not None:
                    # Check if object is still visible
                    try:
                        opacity = mobj.get_opacity()
                        if opacity <= 0.1:  # Successfully faded
                            validation_detail['opacity_check'] = True
                        else:
                            validation_detail['opacity_check'] = False
                            validation_results['passed'] = False
                    except Exception:
                        # If we can't check opacity, assume it failed
                        validation_detail['opacity_check'] = False
                        validation_results['passed'] = False
                    
                    # Check visibility state
                    visibility_state = object_registry['visibility_states'].get(obj_id, {})
                    if visibility_state.get('is_visible', True) == False:
                        validation_detail['visibility_check'] = True
                    else:
                        validation_detail['visibility_check'] = False
                        validation_results['passed'] = False
                    
                    # Check if still in active objects
                    if obj_id not in object_registry['active_objects']:
                        validation_detail['registry_check'] = True
                    else:
                        validation_detail['registry_check'] = False
                        validation_results['passed'] = False
                    
                    # Determine overall object status
                    checks_passed = sum([validation_detail['opacity_check'], 
                                       validation_detail['visibility_check'], 
                                       validation_detail['registry_check']])
                    
                    if checks_passed == 3:
                        # Fully successful
                        pass
                    elif checks_passed >= 1:
                        # Partial success
                        validation_results['partial_successes'].append(obj_id)
                        validation_results['passed'] = False
                    else:
                        # Complete failure
                        validation_results['failed_objects'].append(obj_id)
                        validation_results['passed'] = False
                else:
                    # Object not found - might have been successfully removed
                    validation_detail['registry_check'] = True
                    validation_detail['opacity_check'] = True
                    validation_detail['visibility_check'] = True
                
                validation_results['validation_details'][obj_id] = validation_detail
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in fade-out validation: {e}")
            return {'passed': False, 'error': str(e)}
    
    def alternative_fade_out_methods(self, object_ids, object_registry):
        """Try alternative fade-out methods if primary methods fail"""
        alternative_results = {
            'alternative_methods_used': [],
            'successful_alternatives': [],
            'failed_alternatives': []
        }
        
        try:
            for obj_id in object_ids:
                mobj = object_registry['active_objects'].get(obj_id)
                if mobj is None:
                    continue
                
                # Try alternative method 1: Scale down
                try:
                    from manim import Scale
                    from .manim_utilities import safe_play
                    safe_play(None, Scale(mobj, 0.0), run_time=0.3)
                    alternative_results['alternative_methods_used'].append({
                        'object_id': obj_id,
                        'method': 'scale_down',
                        'success': True
                    })
                    alternative_results['successful_alternatives'].append(obj_id)
                    continue
                except Exception as e:
                    logger.debug(f"Scale down failed for {obj_id}: {e}")
                
                # Try alternative method 2: Move off-screen
                try:
                    from manim import MoveToTarget
                    mobj.generate_target()
                    mobj.target.move_to([1000, 1000, 0])  # Move far off-screen
                    from .manim_utilities import safe_play
                    safe_play(None, MoveToTarget(mobj), run_time=0.2)
                    alternative_results['alternative_methods_used'].append({
                        'object_id': obj_id,
                        'method': 'move_off_screen',
                        'success': True
                    })
                    alternative_results['successful_alternatives'].append(obj_id)
                    continue
                except Exception as e:
                    logger.debug(f"Move off-screen failed for {obj_id}: {e}")
                
                # Try alternative method 3: Color change to transparent
                try:
                    mobj.set_color(alpha=0.0)
                    alternative_results['alternative_methods_used'].append({
                        'object_id': obj_id,
                        'method': 'color_transparency',
                        'success': True
                    })
                    alternative_results['successful_alternatives'].append(obj_id)
                    continue
                except Exception as e:
                    logger.debug(f"Color transparency failed for {obj_id}: {e}")
                
                # All alternatives failed
                alternative_results['alternative_methods_used'].append({
                    'object_id': obj_id,
                    'method': 'all_alternatives_failed',
                    'success': False
                })
                alternative_results['failed_alternatives'].append(obj_id)
            
            return alternative_results
            
        except Exception as e:
            logger.error(f"Error in alternative fade-out methods: {e}")
            return alternative_results
    
    def batch_fade_out_objects(self, object_ids, object_registry, batch_size=3):
        """Fade out objects in batches for better performance"""
        batch_results = {
            'total_batches': (len(object_ids) + batch_size - 1) // batch_size,
            'batch_results': [],
            'overall_success': True
        }
        
        try:
            for i in range(0, len(object_ids), batch_size):
                batch = object_ids[i:i + batch_size]
                batch_result = self.robust_fade_out_system(batch, object_registry, validation=True)
                
                batch_results['batch_results'].append({
                    'batch_number': i // batch_size + 1,
                    'objects_in_batch': batch,
                    'batch_result': batch_result
                })
                
                if not batch_result['validation_passed']:
                    batch_results['overall_success'] = False
                
                # Small delay between batches to prevent overwhelming the system
                import time
                time.sleep(0.1)
            
            return batch_results
            
        except Exception as e:
            logger.error(f"Error in batch fade-out: {e}")
            return batch_results
    
    def smart_fade_out_strategy(self, object_ids, object_registry, context='general'):
        """Choose the best fade-out strategy based on context"""
        strategy_selection = {
            'strategy': 'standard',
            'reason': '',
            'parameters': {}
        }
        
        try:
            # Analyze objects to determine best strategy
            object_types = []
            for obj_id in object_ids:
                obj_type = object_registry['object_states'].get(obj_id, {}).get('type', 'unknown')
                object_types.append(obj_type)
            
            # Strategy selection based on context and object types
            if context == 'plot_sequence':
                if len(object_ids) > 2:
                    strategy_selection.update({
                        'strategy': 'batch_with_validation',
                        'reason': 'Multiple plot objects need careful sequencing',
                        'parameters': {'batch_size': 2, 'validation_delay': 0.3}
                    })
                else:
                    strategy_selection.update({
                        'strategy': 'sequential_with_pause',
                        'reason': 'Plot objects need clear separation',
                        'parameters': {'pause_duration': 0.2, 'validation': True}
                    })
            
            elif context == 'shape_cleanup':
                if len(object_ids) > 5:
                    strategy_selection.update({
                        'strategy': 'batch_fast',
                        'reason': 'Many shapes can be removed quickly',
                        'parameters': {'batch_size': 5, 'fast_mode': True}
                    })
                else:
                    strategy_selection.update({
                        'strategy': 'individual_smooth',
                        'reason': 'Few shapes need smooth removal',
                        'parameters': {'smooth_transition': True, 'duration': 0.2}
                    })
            
            elif context == 'text_removal':
                strategy_selection.update({
                    'strategy': 'fade_out_smooth',
                    'reason': 'Text objects benefit from smooth transitions',
                    'parameters': {'duration': 0.4, 'easing': 'ease_in_out'}
                })
            
            else:  # General context
                if len(object_ids) > 3:
                    strategy_selection.update({
                        'strategy': 'batch_standard',
                        'reason': 'Multiple objects need efficient removal',
                        'parameters': {'batch_size': 3, 'validation': True}
                    })
                else:
                    strategy_selection.update({
                        'strategy': 'individual_robust',
                        'reason': 'Few objects need reliable removal',
                        'parameters': {'validation': True, 'fallback_methods': True}
                    })
            
            return strategy_selection
            
        except Exception as e:
            logger.error(f"Error in smart fade-out strategy selection: {e}")
            return strategy_selection
    
    def get_fade_out_performance_metrics(self, object_registry):
        """Get performance metrics for fade-out operations"""
        try:
            # Calculate success rates
            total_fade_outs = len(object_registry.get('animation_history', []))
            successful_fade_outs = len([h for h in object_registry.get('animation_history', []) 
                                      if h.get('action') == 'fade_out' and h.get('success', False)])
            
            success_rate = (successful_fade_outs / total_fade_outs * 100) if total_fade_outs > 0 else 0
            
            # Calculate average fade-out time
            fade_out_times = [h.get('duration', 0) for h in object_registry.get('animation_history', [])
                             if h.get('action') == 'fade_out']
            avg_fade_out_time = sum(fade_out_times) / len(fade_out_times) if fade_out_times else 0
            
            # Get current fade-out queue status
            current_queue = object_registry.get('fade_out_queue', [])
            
            return {
                'total_fade_outs': total_fade_outs,
                'successful_fade_outs': successful_fade_outs,
                'success_rate_percentage': round(success_rate, 2),
                'average_fade_out_time': round(avg_fade_out_time, 3),
                'current_queue_length': len(current_queue),
                'queue_status': 'active' if current_queue else 'empty'
            }
            
        except Exception as e:
            logger.error(f"Error getting fade-out performance metrics: {e}")
            return {'error': str(e)}
    
    # Legacy compatibility methods
    def exit_fade(self, ids, duration=0.4, stagger=0.05, id_to_mobject=None, scene=None):
        """Legacy fade-out function for backward compatibility"""
        try:
            if not id_to_mobject or not scene:
                return
            
            seq = []
            for i, obj_id in enumerate(ids):
                m = id_to_mobject.get(obj_id)
                if m is not None:
                    from manim import FadeOut
                    seq.append(FadeOut(m))
            if seq:
                from .manim_utilities import safe_play
                safe_play(scene, *seq, run_time=duration)
        except Exception:
            pass
    
    def force_clear_all_plots(self, object_registry, scene=None):
        """Force clear all plots using the enhanced tracking system."""
        try:
            # Get all plot-like objects using the enhanced system
            plot_types = ['plot', 'function', 'graph']
            plot_objects = []
            
            for obj_type in plot_types:
                objects_of_type = []
                for obj_id in object_registry.get('type_registry', {}).get(obj_type, []):
                    if obj_id in object_registry['active_objects']:
                        objects_of_type.append(obj_id)
                plot_objects.extend(objects_of_type)
            
            # Queue all plots for fade-out with high priority
            for obj_id in plot_objects:
                if obj_id in object_registry['active_objects']:
                    # Mark for immediate removal
                    if obj_id in object_registry['visibility_states']:
                        object_registry['visibility_states'][obj_id].update({
                            'is_visible': False,
                            'opacity': 0.0
                        })
                    
                    # Remove from active objects
                    if obj_id in object_registry['active_objects']:
                        del object_registry['active_objects'][obj_id]
                    
                    # Update type registry
                    obj_type = object_registry['object_states'].get(obj_id, {}).get('type', 'unknown')
                    if obj_type in object_registry['type_registry']:
                        if obj_id in object_registry['type_registry'][obj_type]:
                            object_registry['type_registry'][obj_type].remove(obj_id)
            
            # Also check for any untracked plot objects in the scene
            if scene:
                for obj in scene.mobjects:
                    if hasattr(obj, 'plot_function') or hasattr(obj, 'graph'):
                        try:
                            from manim import FadeOut
                            from .manim_utilities import safe_play
                            safe_play(scene, FadeOut(obj), run_time=0.3)
                        except Exception:
                            pass
            
            # Log the operation
            object_registry['animation_history'].append({
                'action': 'force_clear_all_plots',
                'objects_cleared': len(plot_objects),
                'timestamp': len(object_registry['animation_history'])
            })
            
            return len(plot_objects)
            
        except Exception as e:
            logger.error(f"Error in force_clear_all_plots: {e}")
            return 0

    def pre_clear_plots(self, object_registry):
        """Clear any existing plots before new ones"""
        try:
            if 'active_objects' in object_registry:
                plot_ids = []
                for obj_id, mobj in object_registry['active_objects'].items():
                    if hasattr(mobj, 'axes') or 'plot' in str(type(mobj)).lower():
                        plot_ids.append(obj_id)
                
                if plot_ids:
                    return self.robust_fade_out_system(plot_ids, object_registry, validation=False)
            return {'status': 'no_plots_found'}
        except Exception as e:
            logger.error(f"Error in pre_clear_plots: {e}")
            return {'status': 'error', 'message': str(e)}

    def smart_plot_management(self, new_plot_type, object_registry):
        """Smart management of plot objects to prevent overcrowding"""
        try:
            if 'active_objects' not in object_registry:
                return {'status': 'no_registry'}
                
            active_plots = []
            for obj_id, mobj in object_registry['active_objects'].items():
                if hasattr(mobj, 'axes') or 'plot' in str(type(mobj)).lower():
                    active_plots.append(obj_id)
            
            # If we have too many plots, clear some
            max_plots = 3
            if len(active_plots) >= max_plots:
                # Remove oldest plots first
                to_remove = active_plots[:len(active_plots) - max_plots + 1]
                result = self.robust_fade_out_system(to_remove, object_registry, validation=False)
                result['management_action'] = f'removed_{len(to_remove)}_old_plots'
                return result
            
            return {'status': 'no_action_needed', 'active_plots_count': len(active_plots)}
        except Exception as e:
            logger.error(f"Error in smart_plot_management: {e}")
            return {'status': 'error', 'message': str(e)}

    def queue_fade_out(self, obj_id, object_registry, priority=0, duration=0.5):
        """Queue an object for fade-out with priority"""
        try:
            if 'fade_out_queue' not in object_registry:
                object_registry['fade_out_queue'] = []
            
            if obj_id in object_registry['active_objects']:
                fade_out_operation = {
                    'object_id': obj_id,
                    'priority': priority,
                    'duration': duration,
                    'timestamp': len(object_registry.get('animation_history', [])),
                    'status': 'queued'
                }
                
                object_registry['fade_out_queue'].append(fade_out_operation)
                
                # Sort by priority (higher priority = lower number = executed first)
                object_registry['fade_out_queue'].sort(key=lambda x: x['priority'])
                
                # Log the queue operation
                if 'animation_history' not in object_registry:
                    object_registry['animation_history'] = []
                object_registry['animation_history'].append({
                    'action': 'queue_fade_out',
                    'object_id': obj_id,
                    'priority': priority,
                    'timestamp': len(object_registry['animation_history'])
                })
                
                return {'status': 'queued', 'queue_length': len(object_registry['fade_out_queue'])}
            else:
                return {'status': 'object_not_found'}
        except Exception as e:
            logger.error(f"Error in queue_fade_out: {e}")
            return {'status': 'error', 'message': str(e)}

    def execute_fade_out_queue(self, object_registry, scene=None):
        """Execute all queued fade-out operations"""
        try:
            if 'fade_out_queue' not in object_registry:
                return {'status': 'no_queue', 'executed': []}
            
            executed = []
            
            for operation in object_registry['fade_out_queue'][:]:  # Copy to avoid modification during iteration
                if operation['status'] == 'queued':
                    obj_id = operation['object_id']
                    duration = operation['duration']
                    
                    # Execute the fade-out
                    if obj_id in object_registry['active_objects']:
                        mobj = object_registry['active_objects'][obj_id]
                        
                        # Mark as fading out
                        operation['status'] = 'executing'
                        if obj_id in object_registry.get('visibility_states', {}):
                            object_registry['visibility_states'][obj_id].update({
                                'is_visible': False,
                                'opacity': 0.0
                            })
                        
                        # Perform the fade-out
                        try:
                            if scene:
                                from manim import FadeOut
                                from .manim_utilities import safe_play
                                safe_play(scene, FadeOut(mobj), run_time=duration)
                            
                            # Remove from active objects
                            del object_registry['active_objects'][obj_id]
                            operation['status'] = 'completed'
                            executed.append(obj_id)
                            
                        except Exception as e:
                            operation['status'] = 'failed'
                            operation['error'] = str(e)
                            logger.error(f"Failed to fade out {obj_id}: {e}")
                    else:
                        operation['status'] = 'object_not_found'
            
            # Remove completed/failed operations from queue
            object_registry['fade_out_queue'] = [
                op for op in object_registry['fade_out_queue'] 
                if op['status'] == 'queued'
            ]
            
            return {'status': 'completed', 'executed': executed}
        except Exception as e:
            logger.error(f"Error in execute_fade_out_queue: {e}")
            return {'status': 'error', 'message': str(e)}
