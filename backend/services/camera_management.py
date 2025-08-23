"""
Camera Management System for Animathic
Manages dynamic camera adjustments and screen space optimization
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CameraManagementSystem:
    """Smart camera management with object awareness"""
    
    def __init__(self):
        """Initialize the camera management system"""
        pass
    
    def calculate_total_bounding_box(self, objects, object_registry):
        """Calculate the total bounding box that encompasses all objects"""
        if not objects:
            return None
        
        try:
            min_x, min_y = float('inf'), float('inf')
            max_x, max_y = float('-inf'), float('-inf')
            
            valid_objects = 0
            
            for obj in objects:
                bbox = None
                
                # Try to get bbox from object state first
                if hasattr(obj, 'get') and 'id' in obj:
                    obj_id = obj['id']
                    if obj_id in object_registry.get('object_states', {}):
                        bbox = object_registry['object_states'][obj_id].get('bbox')
                
                # If no bbox in state, try to calculate from mobject
                if not bbox:
                    mobj = None
                    if hasattr(obj, 'get') and 'id' in obj:
                        obj_id = obj['id']
                        mobj = object_registry.get('active_objects', {}).get(obj_id)
                    elif hasattr(obj, 'get_center'):
                        mobj = obj
                    
                    if mobj:
                        bbox = self._mobj_bbox(mobj)
                
                if bbox:
                    (x0, y0), (x1, y1), w, h = bbox
                    min_x = min(min_x, x0)
                    min_y = min(min_y, y0)
                    max_x = max(max_x, x1)
                    max_y = max(max_y, y1)
                    valid_objects += 1
            
            if valid_objects == 0:
                return None
            
            width = max_x - min_x
            height = max_y - min_y
            
            return {
                'min_x': min_x,
                'min_y': min_y,
                'max_x': max_x,
                'max_y': max_y,
                'width': width,
                'height': height,
                'center_x': (min_x + max_x) / 2,
                'center_y': (min_y + max_y) / 2,
                'object_count': valid_objects
            }
            
        except Exception as e:
            logger.error(f"Error calculating total bounding box: {e}")
            return None
    
    def _mobj_bbox(self, m):
        """Get bounding box of a Manim object"""
        try:
            bb = m.get_bounding_box()
            w = max(1e-6, bb[1][0] - bb[0][0])
            h = max(1e-6, bb[1][1] - bb[0][1])
            return ((bb[0][0], bb[0][1]), (bb[1][0], bb[1][1]), w, h)
        except Exception:
            return None
    
    def get_screen_bounds(self):
        """Get the current screen/camera bounds"""
        try:
            # Default Manim camera bounds (can be customized based on actual camera)
            return {
                'min_x': -8,
                'min_y': -4.5,
                'max_x': 8,
                'max_y': 4.5,
                'width': 16,
                'height': 9,
                'center_x': 0,
                'center_y': 0,
                'aspect_ratio': 16/9
            }
        except Exception as e:
            logger.error(f"Error getting screen bounds: {e}")
            # Return safe defaults
            return {
                'min_x': -8, 'min_y': -4.5, 'max_x': 8, 'max_y': 4.5,
                'width': 16, 'height': 9, 'center_x': 0, 'center_y': 0,
                'aspect_ratio': 16/9
            }
    
    def fits_in_screen(self, total_bbox, screen_bbox, margin=0.2):
        """Check if the total bounding box fits in screen with given margin"""
        if not total_bbox or not screen_bbox:
            return True
        
        try:
            # Calculate required dimensions with margin
            required_width = total_bbox['width'] * (1 + margin * 2)
            required_height = total_bbox['height'] * (1 + margin * 2)
            
            # Check if it fits
            fits_width = required_width <= screen_bbox['width']
            fits_height = required_height <= screen_bbox['height']
            
            return fits_width and fits_height
            
        except Exception as e:
            logger.error(f"Error checking screen fit: {e}")
            return True  # Assume it fits if we can't determine
    
    def intelligent_camera_management(self, new_object, existing_objects, object_registry):
        """Smart camera management that considers all objects"""
        camera_strategy = {
            'action': 'none',
            'reason': '',
            'parameters': {},
            'priority': 'low'
        }
        
        try:
            # Analyze screen space usage
            total_bbox = self.calculate_total_bounding_box(existing_objects + [new_object], object_registry)
            screen_bbox = self.get_screen_bounds()
            
            if not total_bbox or not screen_bbox:
                return camera_strategy
            
            # Check if objects fit in screen
            if not self._fits_in_screen(total_bbox, screen_bbox, margin=0.2):
                # Need to adjust camera
                if len(existing_objects) > 0:
                    # Multiple objects - use zoom out strategy
                    camera_strategy.update({
                        'action': 'zoom_out',
                        'reason': 'multiple_objects_need_more_space',
                        'parameters': {
                            'zoom_factor': 0.8,
                            'duration': 0.5,
                            'target_objects': [obj.get('id', 'unknown') for obj in existing_objects + [new_object]]
                        },
                        'priority': 'medium'
                    })
                else:
                    # Single object - use fit strategy
                    camera_strategy.update({
                        'action': 'fit_object',
                        'reason': 'single_object_optimization',
                        'parameters': {
                            'margin': 0.15,
                            'duration': 0.3,
                            'target_object': new_object.get('id', 'unknown')
                        },
                        'priority': 'low'
                    })
            
            # Check for objects outside optimal screen area
            out_of_bounds_objects = self._detect_out_of_bounds_objects(existing_objects + [new_object], screen_bbox)
            if out_of_bounds_objects:
                camera_strategy.update({
                    'action': 'pan_camera',
                    'reason': 'objects_positioned_outside_optimal_area',
                    'parameters': {
                        'target_center': self._calculate_optimal_camera_center(total_bbox, screen_bbox),
                        'duration': 0.4,
                        'out_of_bounds_objects': out_of_bounds_objects
                    },
                    'priority': 'high'
                })
            
            # NEW: Smart camera positioning based on object types
            camera_strategy = self._enhance_camera_strategy_with_object_awareness(
                camera_strategy, new_object, existing_objects, total_bbox, screen_bbox
            )
            
            # NEW: Dynamic camera adjustment for mathematical plots
            if self._has_mathematical_content(existing_objects + [new_object]):
                camera_strategy = self._optimize_for_mathematical_content(
                    camera_strategy, total_bbox, screen_bbox
                )
            
            return camera_strategy
            
        except Exception as e:
            logger.error(f"Error in intelligent camera management: {e}")
            return camera_strategy
    
    def _enhance_camera_strategy_with_object_awareness(self, camera_strategy, new_object, existing_objects, total_bbox, screen_bbox):
        """Enhance camera strategy based on object types and their relationships"""
        try:
            new_obj_type = new_object.get('type', 'unknown')
            
            # Special handling for mathematical objects
            if new_obj_type in ['plot', 'function', 'graph', 'axes']:
                # Ensure mathematical plots have optimal viewing
                if camera_strategy['action'] == 'none':
                    camera_strategy.update({
                        'action': 'optimize_math_view',
                        'reason': 'mathematical_content_optimization',
                        'parameters': {
                            'margin': 0.1,  # Tighter margin for math
                            'duration': 0.3,
                            'preserve_aspect_ratio': True
                        },
                        'priority': 'high'
                    })
            
            # Special handling for text annotations
            elif new_obj_type == 'text':
                # Position camera to ensure text is readable
                if camera_strategy['action'] == 'none':
                    camera_strategy.update({
                        'action': 'ensure_text_readability',
                        'reason': 'text_annotation_optimization',
                        'parameters': {
                            'margin': 0.2,
                            'duration': 0.2,
                            'text_priority': 'high'
                        },
                        'priority': 'medium'
                    })
            
            # Special handling for geometric shapes
            elif new_obj_type in ['circle', 'square', 'triangle', 'diamond']:
                # Ensure geometric shapes are properly framed
                if camera_strategy['action'] == 'none':
                    camera_strategy.update({
                        'action': 'frame_geometric_shapes',
                        'reason': 'geometric_shape_optimization',
                        'parameters': {
                            'margin': 0.25,
                            'duration': 0.3,
                            'shape_count': len([obj for obj in existing_objects + [new_object] if obj.get('type') in ['circle', 'square', 'triangle', 'diamond']])
                        },
                        'priority': 'medium'
                    })
            
            return camera_strategy
            
        except Exception as e:
            logger.error(f"Error enhancing camera strategy with object awareness: {e}")
            return camera_strategy
    
    def _has_mathematical_content(self, objects):
        """Check if the scene contains mathematical content"""
        try:
            math_types = ['plot', 'function', 'graph', 'axes']
            return any(obj.get('type') in math_types for obj in objects)
        except Exception:
            return False
    
    def _optimize_for_mathematical_content(self, camera_strategy, total_bbox, screen_bbox):
        """Optimize camera for mathematical content"""
        try:
            if camera_strategy['action'] != 'none':
                return camera_strategy
            
            # For mathematical content, ensure optimal viewing
            camera_strategy.update({
                'action': 'math_optimization',
                'reason': 'mathematical_content_requires_precise_viewing',
                'parameters': {
                    'margin': 0.08,  # Very tight margin for math
                    'duration': 0.4,
                    'preserve_coordinate_system': True,
                    'ensure_axis_visibility': True
                },
                'priority': 'high'
            })
            
            return camera_strategy
            
        except Exception as e:
            logger.error(f"Error optimizing for mathematical content: {e}")
            return camera_strategy
    
    def _fits_in_screen(self, total_bbox, screen_bbox, margin=0.2):
        """Check if total bounding box fits within screen bounds with margin"""
        try:
            if not total_bbox or not screen_bbox:
                return True
            
            # Apply margin to screen bounds
            margin_x = screen_bbox['width'] * margin
            margin_y = screen_bbox['height'] * margin
            
            effective_min_x = screen_bbox['min_x'] + margin_x
            effective_max_x = screen_bbox['max_x'] - margin_x
            effective_min_y = screen_bbox['min_y'] + margin_y
            effective_max_y = screen_bbox['max_y'] - margin_y
            
            # Check if total bbox fits within effective screen bounds
            return (total_bbox['min_x'] >= effective_min_x and 
                    total_bbox['max_x'] <= effective_max_x and
                    total_bbox['min_y'] >= effective_min_y and 
                    total_bbox['max_y'] <= effective_max_y)
                    
        except Exception:
            return True
    
    def _detect_out_of_bounds_objects(self, objects, screen_bbox):
        """Detect objects positioned outside optimal screen area"""
        out_of_bounds = []
        
        try:
            # Define optimal screen area (80% of screen)
            optimal_margin = 0.1
            optimal_min_x = screen_bbox['min_x'] + screen_bbox['width'] * optimal_margin
            optimal_max_x = screen_bbox['max_x'] - screen_bbox['width'] * optimal_margin
            optimal_min_y = screen_bbox['min_y'] + screen_bbox['height'] * optimal_margin
            optimal_max_y = screen_bbox['max_y'] - screen_bbox['height'] * optimal_margin
            
            for obj in objects:
                properties = obj.get('properties', {})
                position = properties.get('position', [0, 0, 0])
                
                # Check if position is outside optimal area
                if (position[0] < optimal_min_x or position[0] > optimal_max_x or
                    position[1] < optimal_min_y or position[1] > optimal_max_y):
                    out_of_bounds.append({
                        'object_id': obj.get('id', 'unknown'),
                        'type': obj.get('type', 'unknown'),
                        'current_position': position,
                        'optimal_bounds': {
                            'x': [optimal_min_x, optimal_max_x],
                            'y': [optimal_min_y, optimal_max_y]
                        }
                    })
            
            return out_of_bounds
            
        except Exception as e:
            logger.error(f"Error detecting out of bounds objects: {e}")
            return []
    
    def _calculate_optimal_camera_center(self, total_bbox, screen_bbox):
        """Calculate optimal camera center to frame all objects"""
        try:
            if not total_bbox:
                return [0, 0, 0]
            
            # Calculate center of total bounding box
            bbox_center_x = total_bbox['center_x']
            bbox_center_y = total_bbox['center_y']
            
            # Ensure center is within screen bounds
            optimal_center_x = max(screen_bbox['min_x'] + screen_bbox['width'] * 0.1,
                                 min(screen_bbox['max_x'] - screen_bbox['width'] * 0.1, bbox_center_x))
            optimal_center_y = max(screen_bbox['min_y'] + screen_bbox['height'] * 0.1,
                                 min(screen_bbox['max_y'] - screen_bbox['height'] * 0.1, bbox_center_y))
            
            return [optimal_center_x, optimal_center_y, 0]
            
        except Exception:
            return [0, 0, 0]
    
    def advanced_object_positioning(self, new_object, existing_objects, screen_bounds, object_registry):
        """Advanced positioning that considers all existing objects"""
        positioning_strategy = {
            'method': 'none',
            'position': None,
            'camera_adjustment': None,
            'reasoning': ''
        }
        
        try:
            obj_type = new_object.get('type', '')
            
            if obj_type in ['plot', 'function', 'graph']:
                # For plots, find optimal position considering existing objects
                optimal_position = self._find_optimal_plot_position(new_object, existing_objects, screen_bounds, object_registry)
                if optimal_position:
                    positioning_strategy.update({
                        'method': 'optimal_plot_positioning',
                        'position': optimal_position,
                        'reasoning': 'Positioned to avoid overlap with existing objects'
                    })
                else:
                    # No optimal position found, use fade-out strategy
                    positioning_strategy.update({
                        'method': 'fade_out_and_replace',
                        'position': self._calculate_center_position(screen_bounds),
                        'reasoning': 'Using fade-out strategy due to space constraints'
                    })
            
            elif obj_type in ['circle', 'square', 'diamond', 'star', 'hexagon', 'triangle']:
                # For shapes, use grid-based positioning
                grid_position = self._calculate_grid_position(new_object, existing_objects, screen_bounds)
                positioning_strategy.update({
                    'method': 'grid_based_positioning',
                    'position': grid_position,
                    'reasoning': 'Grid-based positioning for optimal spacing'
                })
            
            elif obj_type == 'text':
                # For text, position at top with smart spacing
                text_position = self._calculate_text_position(new_object, existing_objects, screen_bounds)
                positioning_strategy.update({
                    'method': 'smart_text_positioning',
                    'position': text_position,
                    'reasoning': 'Smart text positioning to avoid overlap'
                })
            
            else:
                # Default positioning
                positioning_strategy.update({
                    'method': 'default_positioning',
                    'position': [0, 0, 0],
                    'reasoning': 'Default center positioning'
                })
            
            return positioning_strategy
            
        except Exception as e:
            logger.error(f"Error in advanced object positioning: {e}")
            return positioning_strategy
    
    def _find_optimal_plot_position(self, new_object, existing_objects, screen_bounds, object_registry):
        """Find optimal position for plot objects"""
        try:
            # Check if we have axes
            axes_objects = [obj for obj in existing_objects if obj.get('type') == 'axes']
            if axes_objects:
                # Position plot at axes center
                return [0, 0, 0]
            
            # Check for existing plots
            plot_objects = [obj for obj in existing_objects if obj.get('type') in ['plot', 'function', 'graph']]
            if plot_objects:
                # Find empty regions
                empty_regions = self._find_empty_screen_regions(existing_objects, screen_bounds)
                if empty_regions:
                    return self._select_best_empty_region(empty_regions, new_object)
            
            # Default to center
            return [0, 0, 0]
            
        except Exception:
            return [0, 0, 0]
    
    def _find_empty_screen_regions(self, existing_objects, screen_bounds):
        """Find empty regions in the screen"""
        try:
            # Simple grid-based approach
            grid_size = 4
            grid = [[True for _ in range(grid_size)] for _ in range(grid_size)]
            
            # Mark occupied grid cells
            for obj in existing_objects:
                properties = obj.get('properties', {})
                position = properties.get('position', [0, 0, 0])
                
                # Convert position to grid coordinates
                grid_x = int((position[0] - screen_bounds['min_x']) / screen_bounds['width'] * grid_size)
                grid_y = int((position[1] - screen_bounds['min_y']) / screen_bounds['height'] * grid_size)
                
                # Mark as occupied
                if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size:
                    grid[grid_y][grid_x] = False
            
            # Find empty regions
            empty_regions = []
            for y in range(grid_size):
                for x in range(grid_size):
                    if grid[y][x]:
                        # Convert grid coordinates back to screen coordinates
                        screen_x = screen_bounds['min_x'] + (x + 0.5) * screen_bounds['width'] / grid_size
                        screen_y = screen_bounds['min_y'] + (y + 0.5) * screen_bounds['height'] / grid_size
                        empty_regions.append([screen_x, screen_y, 0])
            
            return empty_regions
            
        except Exception:
            return []
    
    def _select_best_empty_region(self, empty_regions, new_object):
        """Select the best empty region for the new object"""
        try:
            if not empty_regions:
                return [0, 0, 0]
            
            # Prefer regions closer to center
            center = [0, 0, 0]
            best_region = empty_regions[0]
            min_distance = float('inf')
            
            for region in empty_regions:
                distance = ((region[0] - center[0])**2 + (region[1] - center[1])**2)**0.5
                if distance < min_distance:
                    min_distance = distance
                    best_region = region
            
            return best_region
            
        except Exception:
            return [0, 0, 0]
    
    def _calculate_grid_position(self, new_object, existing_objects, screen_bounds):
        """Calculate grid-based position for shape objects"""
        try:
            # Count existing shapes
            shape_count = len([obj for obj in existing_objects if obj.get('type') in ['circle', 'square', 'diamond', 'star', 'hexagon', 'triangle']])
            
            # Calculate grid position
            cols = 3
            row = shape_count // cols
            col = shape_count % cols
            
            # Calculate spacing
            spacing_x = screen_bounds['width'] / (cols + 1)
            spacing_y = screen_bounds['height'] / 4
            
            # Calculate position
            x = screen_bounds['min_x'] + (col + 1) * spacing_x
            y = screen_bounds['max_y'] - (row + 1) * spacing_y
            
            return [x, y, 0]
            
        except Exception:
            return [0, 0, 0]
    
    def _calculate_text_position(self, new_object, existing_objects, screen_bounds):
        """Calculate optimal position for text objects"""
        try:
            # Find existing text objects
            text_objects = [obj for obj in existing_objects if obj.get('type') == 'text']
            
            # Position at top with vertical spacing
            base_y = screen_bounds['max_y'] - 0.5
            y_offset = len(text_objects) * 0.8
            
            return [0, base_y - y_offset, 0]
            
        except Exception:
            return [0, 2.5, 0]
    
    def _calculate_center_position(self, screen_bounds):
        """Calculate center position of screen"""
        try:
            center_x = (screen_bounds['min_x'] + screen_bounds['max_x']) / 2
            center_y = (screen_bounds['min_y'] + screen_bounds['max_y']) / 2
            return [center_x, center_y, 0]
        except Exception:
            return [0, 0, 0]
    
    def apply_camera_strategy(self, strategy, scene):
        """Apply the camera strategy to the scene"""
        try:
            if strategy['action'] == 'none' or strategy['action'] == 'error':
                return True
            
            action = strategy['action']
            params = strategy.get('parameters', {})
            duration = params.get('duration', 0.5)
            
            if action == 'zoom_out':
                zoom_factor = params.get('zoom_factor', 0.8)
                center_x = params.get('center_x', 0)
                center_y = params.get('center_y', 0)
                
                # Apply zoom out animation
                from .manim_utilities import safe_play
                safe_play(
                    scene,
                    scene.camera.frame.animate.scale(1/zoom_factor).move_to([center_x, center_y, 0]),
                    run_time=duration
                )
                
            elif action == 'fit_object':
                margin = params.get('margin', 0.15)
                center_x = params.get('center_x', 0)
                center_y = params.get('center_y', 0)
                target_width = params.get('target_width', 4)
                target_height = params.get('target_height', 3)
                
                # Calculate the scale needed to fit the object
                screen_bounds = self.get_screen_bounds()
                scale_x = (screen_bounds['width'] * (1 - margin * 2)) / target_width
                scale_y = (screen_bounds['height'] * (1 - margin * 2)) / target_height
                scale = min(scale_x, scale_y, 1.0)  # Don't zoom in beyond 1.0
                
                if scale < 1.0:
                    from .manim_utilities import safe_play
                    safe_play(
                        scene,
                        scene.camera.frame.animate.scale(scale).move_to([center_x, center_y, 0]),
                        run_time=duration
                    )
                else:
                    from .manim_utilities import safe_play
                    safe_play(
                        scene,
                        scene.camera.frame.animate.move_to([center_x, center_y, 0]),
                        run_time=duration
                    )
            
            elif action == 'recenter':
                center_x = params.get('center_x', 0)
                center_y = params.get('center_y', 0)
                
                from .manim_utilities import safe_play
                safe_play(
                    scene,
                    scene.camera.frame.animate.move_to([center_x, center_y, 0]),
                    run_time=duration
                )
            
            # NEW: Handle enhanced camera actions
            elif action == 'optimize_math_view':
                margin = params.get('margin', 0.1)
                preserve_aspect = params.get('preserve_aspect_ratio', True)
                
                # Optimize camera for mathematical content
                self._apply_math_optimization(scene, margin, preserve_aspect, duration)
            
            elif action == 'ensure_text_readability':
                margin = params.get('margin', 0.2)
                text_priority = params.get('text_priority', 'high')
                
                # Ensure text is readable
                self._apply_text_readability_optimization(scene, margin, text_priority, duration)
            
            elif action == 'frame_geometric_shapes':
                margin = params.get('margin', 0.25)
                shape_count = params.get('shape_count', 1)
                
                # Frame geometric shapes optimally
                self._apply_geometric_shape_framing(scene, margin, shape_count, duration)
            
            elif action == 'math_optimization':
                margin = params.get('margin', 0.08)
                preserve_coords = params.get('preserve_coordinate_system', True)
                ensure_axes = params.get('ensure_axis_visibility', True)
                
                # Apply mathematical optimization
                self._apply_mathematical_optimization(scene, margin, preserve_coords, ensure_axes, duration)
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying camera strategy: {e}")
            return False
    
    def _apply_math_optimization(self, scene, margin, preserve_aspect, duration):
        """Apply mathematical content optimization to camera"""
        try:
            # Ensure tight margins for mathematical precision
            current_width = float(scene.camera.frame.get_width())
            optimal_width = current_width * (1 - margin * 2)
            
            if preserve_aspect:
                # Maintain aspect ratio for mathematical plots
                scene.camera.frame.set_width(optimal_width)
            else:
                # Allow independent width/height adjustment
                current_height = float(scene.camera.frame.get_height())
                optimal_height = current_height * (1 - margin * 2)
                scene.camera.frame.set_width(optimal_width)
                scene.camera.frame.set_height(optimal_height)
            
            logger.info(f"Applied math optimization: margin={margin}, preserve_aspect={preserve_aspect}")
            
        except Exception as e:
            logger.error(f"Error applying math optimization: {e}")
    
    def _apply_text_readability_optimization(self, scene, margin, text_priority, duration):
        """Ensure text is readable by optimizing camera position"""
        try:
            # For text readability, ensure adequate spacing
            current_width = float(scene.camera.frame.get_width())
            optimal_width = current_width * (1 + margin)  # Increase width for text
            
            scene.camera.frame.set_width(optimal_width)
            
            # Center the camera to ensure text is visible
            scene.camera.frame.move_to([0, 0, 0])
            
            logger.info(f"Applied text readability optimization: margin={margin}, priority={text_priority}")
            
        except Exception as e:
            logger.error(f"Error applying text readability optimization: {e}")
    
    def _apply_geometric_shape_framing(self, scene, margin, shape_count, duration):
        """Optimally frame geometric shapes"""
        try:
            # Calculate optimal frame size based on shape count
            base_margin = margin
            if shape_count > 3:
                base_margin += 0.1  # Increase margin for more shapes
            
            current_width = float(scene.camera.frame.get_width())
            optimal_width = current_width * (1 + base_margin)
            
            scene.camera.frame.set_width(optimal_width)
            
            # Ensure shapes are centered
            scene.camera.frame.move_to([0, 0, 0])
            
            logger.info(f"Applied geometric shape framing: margin={base_margin}, shape_count={shape_count}")
            
        except Exception as e:
            logger.error(f"Error applying geometric shape framing: {e}")
    
    def _apply_mathematical_optimization(self, scene, margin, preserve_coords, ensure_axes, duration):
        """Apply comprehensive mathematical optimization"""
        try:
            # Very tight margins for mathematical precision
            current_width = float(scene.camera.frame.get_width())
            optimal_width = current_width * (1 - margin * 2)
            
            scene.camera.frame.set_width(optimal_width)
            
            if preserve_coords:
                # Preserve coordinate system integrity
                scene.camera.frame.set(x_range=[-7, 7], y_range=[-5, 5])
            
            if ensure_axes:
                # Ensure axes remain visible
                scene.camera.frame.move_to([0, 0, 0])
            
            logger.info(f"Applied mathematical optimization: margin={margin}, preserve_coords={preserve_coords}, ensure_axes={ensure_axes}")
            
        except Exception as e:
            logger.error(f"Error applying mathematical optimization: {e}")
    
    def get_camera_management_status(self, object_registry):
        """Get current status of the camera management system"""
        try:
            screen_bounds = self.get_screen_bounds()
            active_objects = list(object_registry.get('active_objects', {}).keys())
            
            # Calculate current total bbox if there are objects
            total_bbox = None
            if active_objects:
                objects_data = []
                for obj_id in active_objects:
                    objects_data.append({'id': obj_id})
                total_bbox = self.calculate_total_bounding_box(objects_data, object_registry)
            
            return {
                'screen_bounds': screen_bounds,
                'active_objects_count': len(active_objects),
                'total_bbox': total_bbox,
                'screen_usage': {
                    'width_percentage': (total_bbox['width'] / screen_bounds['width'] * 100) if total_bbox else 0,
                    'height_percentage': (total_bbox['height'] / screen_bounds['height'] * 100) if total_bbox else 0
                } if total_bbox else None,
                'system_status': 'active'
            }
            
        except Exception as e:
            return {'error': str(e), 'system_status': 'error'}
    
    # Legacy camera functions for backward compatibility
    def camera_fit(self, ids, margin=0.15, get_group_func=None, scene=None):
        """Fit camera to show specific objects"""
        try:
            if not get_group_func or not scene:
                return
            
            g = get_group_func(ids)
            if len(g) == 0:
                return
            
            bbox = g.get_bounding_box()
            # Ensure minimum frame size for better visibility
            min_width = 8.0
            min_height = 6.0
            
            width = max(min_width, bbox[1][0] - bbox[0][0]) * (1.0 + margin)
            height = max(min_height, bbox[1][1] - bbox[0][1]) * (1.0 + margin)
            
            # Use the larger dimension to ensure all objects fit
            frame_width = max(width, height * 1.4)  # 1.4 aspect ratio
            
            center = g.get_center()
            scene.camera.frame.set_width(frame_width)
            scene.camera.frame.move_to(center)
        except Exception:
            pass
    
    def camera_pad(self, margin=0.05, scene=None):
        """Add padding to camera frame"""
        try:
            if not scene:
                return
            
            cur_w = float(scene.camera.frame.get_width())
            scene.camera.frame.set_width(cur_w * (1.0 + max(0.0, float(margin))))
        except Exception:
            pass
    
    def dynamic_camera_adjust(self, active_objects, target_margin=0.2, get_bbox_func=None, scene=None):
        """Dynamically adjust camera based on object distribution and prevent overlaps"""
        try:
            if not active_objects or not get_bbox_func or not scene:
                return
            
            # Get bounding box of all active objects
            bbox = get_bbox_func(active_objects)
            if not bbox:
                return
            
            (x0, y0), (x1, y1) = bbox
            width = x1 - x0
            height = y1 - y0
            
            # Calculate optimal frame size with margin
            frame_width = max(width, height * 1.4) * (1.0 + target_margin)
            frame_height = max(height, width / 1.4) * (1.0 + target_margin)
            
            # Use the larger dimension to ensure all objects fit
            optimal_width = max(frame_width, frame_height * 1.4)
            
            # Ensure minimum frame size
            optimal_width = max(optimal_width, 10.0)
            
            # Smoothly adjust camera
            current_width = float(scene.camera.frame.get_width())
            if abs(current_width - optimal_width) > 0.5:
                # Animate camera adjustment
                from .manim_utilities import safe_play
                safe_play(scene, scene.camera.frame.animate.set_width(optimal_width), run_time=0.8)
            
            # Center camera on objects
            center_x = (x0 + x1) / 2
            center_y = (y0 + y1) / 2
            current_center = scene.camera.frame.get_center()
            
            if abs(current_center[0] - center_x) > 0.5 or abs(current_center[1] - center_y) > 0.5:
                from .manim_utilities import safe_play
                safe_play(scene, scene.camera.frame.animate.move_to([center_x, center_y, 0]), run_time=0.6)
                
        except Exception:
            pass
    
    # Legacy camera functions for backward compatibility
    def camera_zoom(self, factor=1.0, anchor=None, scene=None):
        """Legacy camera zoom function"""
        try:
            if not scene:
                return
            factor = float(factor) if isinstance(factor, (int, float)) else 1.0
            if factor <= 0:
                return
            new_w = float(scene.camera.frame.get_width()) / factor
            scene.camera.frame.set_width(new_w)
            if anchor and isinstance(anchor, (list, tuple)) and len(anchor) >= 2:
                scene.camera.frame.move_to([float(anchor[0]), float(anchor[1]), 0])
        except Exception:
            pass
    
    def camera_pan_to(self, pos, duration=0.6, scene=None):
        """Legacy camera pan function"""
        try:
            if not scene or not isinstance(pos, (list, tuple)) or len(pos) < 2:
                return
            from .manim_utilities import safe_play
            safe_play(scene, scene.camera.frame.animate.move_to([float(pos[0]), float(pos[1]), 0]), run_time=float(duration))
        except Exception:
            pass
    
    def camera_set(self, frame_center=None, frame_width=None, scene=None):
        """Legacy camera set function"""
        try:
            if not scene:
                return
            if isinstance(frame_width, (int, float)) and frame_width > 0:
                scene.camera.frame.set_width(float(frame_width))
            if isinstance(frame_center, (list, tuple)) and len(frame_center) >= 2:
                scene.camera.frame.move_to([float(frame_center[0]), float(frame_center[1]), 0])
        except Exception:
            pass
    
    # Screen management functions
    def smart_screen_management(self, new_graph_type, active_ids, id_to_meta, id_to_mobject):
        """Intelligent screen management when adding new graphs"""
        try:
            # Count existing graphs
            existing_graphs = [obj_id for obj_id in active_ids if id_to_meta.get(obj_id, {}).get('type') in ['plot', 'axes', 'function', 'graph']]
            
            if len(existing_graphs) == 0:
                # First graph - use default positioning
                return 'default'
            
            elif len(existing_graphs) == 1:
                # Second graph - check if we can fit both
                existing_graph = id_to_mobject.get(existing_graphs[0])
                if existing_graph:
                    bbox = self._mobj_bbox(existing_graph)
                    if bbox:
                        (x0, y0), (x1, y1), w, h = bbox
                        
                        # If existing graph is small, we can fit both side by side
                        if w < 6 and h < 4:
                            # Keep existing graph, position new one to the right
                            return 'side_by_side'
                        else:
                            # Existing graph is large, fade it out
                            return 'fade_existing'
            
            else:
                # Multiple graphs - need to manage screen space
                total_width = 0
                for obj_id in existing_graphs:
                    mobj = id_to_mobject.get(obj_id)
                    if mobj:
                        bbox = self._mobj_bbox(mobj)
                        if bbox:
                            _, _, w, _ = bbox
                            total_width += w
                
                # If total width exceeds screen capacity, fade out oldest
                if total_width > 10:
                    return 'fade_oldest'
                else:
                    return 'reorganize'
                    
        except Exception:
            return 'default'
    
    def execute_screen_strategy(self, strategy, new_graph_obj=None, active_ids=None, id_to_meta=None, id_to_mobject=None, scene=None):
        """Execute the chosen screen management strategy"""
        try:
            if not scene or not active_ids or not id_to_meta or not id_to_mobject:
                return
            
            if strategy == 'side_by_side':
                # Position new graph to the right of existing one
                existing_graphs = [obj_id for obj_id in active_ids if id_to_meta.get(obj_id, {}).get('type') in ['plot', 'axes', 'function', 'graph']]
                if existing_graphs and new_graph_obj:
                    existing_graph = id_to_mobject.get(existing_graphs[0])
                    if existing_graph:
                        existing_center = existing_graph.get_center()
                        new_graph_obj.move_to([existing_center[0] + 6, existing_center[1], 0])
                        
                        # Zoom out camera to show both graphs
                        from .manim_utilities import safe_play
                        safe_play(scene, scene.camera.frame.animate.set_width(16), run_time=0.8)
            
            elif strategy == 'fade_existing':
                # Fade out existing graph and focus on new one
                existing_graphs = [obj_id for obj_id in active_ids if id_to_meta.get(obj_id, {}).get('type') in ['plot', 'axes', 'function', 'graph']]
                for obj_id in existing_graphs:
                    mobj = id_to_mobject.get(obj_id)
                    if mobj:
                        from manim import FadeOut
                        from .manim_utilities import safe_play
                        safe_play(scene, FadeOut(mobj), run_time=0.6)
                        if obj_id in active_ids:
                            active_ids.remove(obj_id)
                
                # Center camera on new graph
                if new_graph_obj:
                    new_center = new_graph_obj.get_center()
                    from .manim_utilities import safe_play
                    safe_play(scene, scene.camera.frame.animate.move_to(new_center).set_width(8), run_time=0.8)
            
            elif strategy == 'fade_oldest':
                # Fade out oldest graph to make room
                existing_graphs = [obj_id for obj_id in active_ids if id_to_meta.get(obj_id, {}).get('type') in ['plot', 'axes', 'function', 'graph']]
                if existing_graphs:
                    oldest_graph = existing_graphs[0]  # First in list is oldest
                    mobj = id_to_mobject.get(oldest_graph)
                    if mobj:
                        from manim import FadeOut
                        from .manim_utilities import safe_play
                        safe_play(scene, FadeOut(mobj), run_time=0.6)
                        active_ids.remove(oldest_graph)
                        
                        # Adjust camera to show remaining graphs
                        self.dynamic_camera_adjust(active_ids, target_margin=0.3, scene=scene)
            
        except Exception:
            pass
    
    def policy_exit_before(self, new_type, active_ids, id_to_meta, id_to_mobject, get_bbox_func, scene):
        """Exit policy before adding new objects"""
        try:
            major_types = {"axes", "plot", "square", "circle", "line"}
            if str(new_type).lower() not in major_types:
                return
            
            # Keep axes by default, prefer removing low-priority items first
            keep = []
            for obj_id in list(active_ids):
                m = id_to_mobject.get(obj_id)
                from .manim_utilities import _is_axes
                if m is not None and _is_axes(m):
                    keep.append(obj_id)
            
            others = [obj_id for obj_id in list(active_ids) if obj_id not in keep]
            # Sort by priority low->high
            from .manim_utilities import _priority_for
            others.sort(key=lambda x: _priority_for(x, id_to_meta))
            
            # Try camera fit first with current + incoming kept
            try:
                union = get_bbox_func(keep + others)
                from .manim_utilities import fits_in_view
                if not fits_in_view(union, scene.camera.frame, margin=0.15):
                    self.camera_fit(keep + others, margin=0.12, scene=scene)
                    self.camera_pad(0.04, scene=scene)
            except Exception:
                pass
            
            # If still crowded, fade lowest priority half
            try:
                union2 = get_bbox_func(keep + others)
                from .manim_utilities import fits_in_view
                if not fits_in_view(union2, scene.camera.frame, margin=0.15) and others:
                    cut = max(1, len(others)//2)
                    to_drop = others[:cut]
                    
                    # Fade out objects
                    from manim import FadeOut
                    from .manim_utilities import safe_play
                    seq = []
                    for obj_id in to_drop:
                        m = id_to_mobject.get(obj_id)
                        if m is not None:
                            seq.append(FadeOut(m))
                    if seq:
                        safe_play(scene, *seq, run_time=0.25)
                    
                    for obj_id in to_drop:
                        try:
                            active_ids.remove(obj_id)
                        except Exception:
                            pass
            except Exception:
                pass
        except Exception:
            pass
    
    def exit_minimize_to_corner(self, ids, corner="TR", scale=0.3, duration=0.4, id_to_mobject=None, scene=None):
        """Minimize objects to corner"""
        try:
            if not id_to_mobject or not scene:
                return
            
            from manim import RIGHT, LEFT, UP, DOWN
            target = {
                'TR': RIGHT*5 + UP*3,
                'TL': LEFT*5 + UP*3,
                'BR': RIGHT*5 + DOWN*3,
                'BL': LEFT*5 + DOWN*3,
            }.get(str(corner).upper(), RIGHT*5 + UP*3)
            
            anims = []
            for obj_id in ids:
                m = id_to_mobject.get(obj_id)
                if m is not None:
                    anims.append(m.animate.scale(float(scale)).move_to(target))
            if anims:
                from .manim_utilities import safe_play
                safe_play(scene, *anims, run_time=duration)
        except Exception:
            pass
