"""
Object Tracking System for Animathic
Manages object registry, state tracking, and visibility management
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ObjectTrackingSystem:
    """Enhanced object tracking and state management system"""
    
    def __init__(self):
        """Initialize the object tracking system"""
        self.object_registry = {
            'active_objects': {},      # id -> mobject
            'object_states': {},       # id -> {'type', 'z_index', 'position', 'bbox', 'is_visible', 'creation_time'}
            'animation_history': [],     # track what animations have been applied
            'overlap_groups': {},      # group objects that might overlap by type
            'fade_out_queue': [],       # objects waiting to be faded out
            'creation_order': [],       # order in which objects were created
            'type_registry': {},      # objects grouped by type
            'visibility_states': {},  # current visibility state of each object
            'pending_operations': []    # operations waiting to be executed
        }
        
        # Legacy compatibility
        self.active_ids = []
        self.id_to_mobject = {}
        self.id_to_meta = {}
    
    def init_object_registry(self):
        """Initialize the enhanced object registry"""
        self.object_registry['active_objects'] = {}
        self.object_registry['object_states'] = {}
        self.object_registry['animation_history'] = []
        self.object_registry['overlap_groups'] = {}
        self.object_registry['fade_out_queue'] = []
        self.object_registry['creation_order'] = []
        self.object_registry['type_registry'] = {}
        self.object_registry['visibility_states'] = {}
        self.object_registry['pending_operations'] = []
        
        # Legacy compatibility
        self.active_ids = []
        self.id_to_mobject = {}
        self.id_to_meta = {}
    
    def enhanced_reg(self, obj_id, mobj, z_index=0, otype="", position=None):
        """Enhanced object registration with comprehensive tracking"""
        try:
            if mobj is None or obj_id is None:
                return
            
            # Store the mobject
            self.object_registry['active_objects'][obj_id] = mobj
            
            # Create comprehensive state tracking
            current_time = len(self.object_registry['creation_order'])
            bbox = self._mobj_bbox(mobj) if mobj else None
            
            self.object_registry['object_states'][obj_id] = {
                'type': str(otype).lower() if otype else 'unknown',
                'z_index': int(z_index),
                'position': position or (mobj.get_center() if mobj else [0, 0, 0]),
                'bbox': bbox,
                'is_visible': True,
                'creation_time': current_time,
                'last_modified': current_time,
                'opacity': 1.0,
                'scale': 1.0,
                'rotation': 0.0
            }
            
            # Track creation order
            if obj_id not in self.object_registry['creation_order']:
                self.object_registry['creation_order'].append(obj_id)
            
            # Group by type
            obj_type = str(otype).lower() if otype else 'unknown'
            if obj_type not in self.object_registry['type_registry']:
                self.object_registry['type_registry'][obj_type] = []
            if obj_id not in self.object_registry['type_registry'][obj_type]:
                self.object_registry['type_registry'][obj_type].append(obj_id)
            
            # Initialize visibility state
            self.object_registry['visibility_states'][obj_id] = {
                'is_visible': True,
                'opacity': 1.0,
                'fade_out_in_progress': False,
                'fade_in_in_progress': False
            }
            
            # Set z-index on the mobject
            try:
                mobj.set_z_index(int(z_index))
            except Exception:
                pass
            
            # Log the registration
            self.object_registry['animation_history'].append({
                'action': 'register',
                'object_id': obj_id,
                'type': obj_type,
                'timestamp': current_time,
                'z_index': z_index
            })
            
            # Also add to legacy active_ids for backward compatibility
            if obj_id not in self.active_ids:
                self.active_ids.append(obj_id)
            
            # Also add to legacy id_to_mobject and id_to_meta for backward compatibility
            self.id_to_mobject[obj_id] = mobj
            self.id_to_meta[obj_id] = {'type': str(otype).lower(), 'z': int(z_index)}
            
        except Exception as e:
            logger.error(f"Error in enhanced_reg: {e}")
    
    def _mobj_bbox(self, m):
        """Get bounding box of a Manim object"""
        try:
            bb = m.get_bounding_box()
            w = max(1e-6, bb[1][0] - bb[0][0])
            h = max(1e-6, bb[1][1] - bb[0][1])
            return ((bb[0][0], bb[0][1]), (bb[1][0], bb[1][1]), w, h)
        except Exception:
            return None
    
    def get_object_by_id(self, obj_id):
        """Get object by ID with state information"""
        if obj_id in self.object_registry['active_objects']:
            return {
                'mobject': self.object_registry['active_objects'][obj_id],
                'state': self.object_registry['object_states'].get(obj_id, {}),
                'visibility': self.object_registry['visibility_states'].get(obj_id, {})
            }
        return None
    
    def get_objects_by_type(self, obj_type):
        """Get all objects of a specific type with their states"""
        obj_type = str(obj_type).lower()
        result = []
        
        for obj_id in self.object_registry['type_registry'].get(obj_type, []):
            obj_info = self.get_object_by_id(obj_id)
            if obj_info:
                result.append(obj_info)
        
        return result
    
    def get_creation_sequence(self):
        """Get objects in their creation order"""
        result = []
        for obj_id in self.object_registry['creation_order']:
            obj_info = self.get_object_by_id(obj_id)
            if obj_info:
                result.append(obj_info)
        return result
    
    def update_visibility_state(self, obj_id, is_visible, opacity=1.0):
        """Update the visibility state of an object"""
        try:
            if obj_id in self.object_registry['visibility_states']:
                self.object_registry['visibility_states'][obj_id].update({
                    'is_visible': is_visible,
                    'opacity': opacity,
                    'last_updated': len(self.object_registry['animation_history'])
                })
                
                # Update object state
                if obj_id in self.object_registry['object_states']:
                    self.object_registry['object_states'][obj_id]['is_visible'] = is_visible
                    self.object_registry['object_states'][obj_id]['opacity'] = opacity
                    self.object_registry['object_states'][obj_id]['last_modified'] = len(self.object_registry['animation_history'])
                
                # Log the change
                self.object_registry['animation_history'].append({
                    'action': 'visibility_change',
                    'object_id': obj_id,
                    'is_visible': is_visible,
                    'opacity': opacity,
                    'timestamp': len(self.object_registry['animation_history'])
                })
                
        except Exception as e:
            logger.error(f"Error updating visibility state: {e}")
    
    def get_tracking_status(self) -> Dict[str, Any]:
        """Get comprehensive tracking status"""
        return {
            'active_objects_count': len(self.object_registry['active_objects']),
            'total_objects_created': len(self.object_registry['creation_order']),
            'type_distribution': {k: len(v) for k, v in self.object_registry['type_registry'].items()},
            'recent_animations': self.object_registry['animation_history'][-5:],
            'pending_operations': len(self.object_registry['pending_operations']),
            'fade_out_queue_length': len(self.object_registry['fade_out_queue'])
        }
    
    def suggest_object_positions(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest optimal positions for multiple objects to avoid overlap"""
        if len(objects) <= 1:
            return {}
        
        suggestions = {}
        spacing = 2.0  # Base spacing between objects
        
        for i, obj in enumerate(objects):
            obj_id = obj.get('id', f'obj_{i}')
            obj_type = obj.get('type', 'circle')
            
            # Calculate position based on object type and index
            if obj_type == 'axes':
                # Place axes at center
                suggestions[obj_id] = [0, 0, 0]
            elif obj_type == 'plot':
                # Place plots near axes
                suggestions[obj_id] = [0, 0, 0]
            elif obj_type in ['circle', 'square', 'diamond', 'star', 'hexagon', 'triangle']:
                # Place shapes in a grid pattern
                row = i // 3
                col = i % 3
                x = (col - 1) * spacing
                y = (1 - row) * spacing
                suggestions[obj_id] = [x, y, 0]
            elif obj_type == 'text':
                # Place text at top
                suggestions[obj_id] = [0, 2.5, 0]
            else:
                # Default positioning
                suggestions[obj_id] = [0, 0, 0]
        
        return suggestions
    
    def debug_object_state(self, obj_id):
        """Debug information for a specific object"""
        try:
            if obj_id in self.object_registry['active_objects']:
                return {
                    'object_id': obj_id,
                    'state': self.object_registry['object_states'].get(obj_id, {}),
                    'visibility': self.object_registry['visibility_states'].get(obj_id, {}),
                    'in_fade_out_queue': any(op['object_id'] == obj_id for op in self.object_registry['fade_out_queue']),
                    'creation_position': self.object_registry['creation_order'].index(obj_id) if obj_id in self.object_registry['creation_order'] else -1
                }
            else:
                return {'error': f'Object {obj_id} not found in registry'}
        except Exception as e:
            return {'error': str(e)}
    
    def clear_tracking_data(self):
        """Clear all tracking data (useful for testing)"""
        try:
            self.init_object_registry()
            return {'status': 'cleared', 'message': 'All tracking data cleared'}
        except Exception as e:
            return {'error': str(e)}
    
    # Legacy compatibility methods
    def reg(self, obj_id, mobj, z_index=0, otype=""):
        """Legacy registration function - now calls enhanced_reg"""
        self.enhanced_reg(obj_id, mobj, z_index, otype)
    
    def get_group(self, ids):
        """Get group of objects by IDs"""
        try:
            mobjects = []
            for obj_id in ids:
                obj_info = self.get_object_by_id(obj_id)
                if obj_info and obj_info['mobject']:
                    mobjects.append(obj_info['mobject'])
            
            if mobjects:
                from manim import VGroup
                return VGroup(*mobjects)
            from manim import VGroup
            return VGroup()
        except Exception:
            from manim import VGroup
            return VGroup()

    def detect_object_overlaps(self, threshold=0.1):
        """Detect overlapping objects in real-time"""
        overlaps = []
        active_objects = list(self.object_registry['active_objects'].items())
        
        for i, (obj_id1, mobj1) in enumerate(active_objects):
            bbox1 = self.object_registry['object_states'].get(obj_id1, {}).get('bbox')
            if not bbox1:
                continue
                
            for j, (obj_id2, mobj2) in enumerate(active_objects[i+1:], i+1):
                bbox2 = self.object_registry['object_states'].get(obj_id2, {}).get('bbox')
                if not bbox2:
                    continue
                
                # Calculate overlap
                overlap_area = self._calculate_bbox_overlap(bbox1, bbox2)
                if overlap_area > threshold:
                    overlaps.append({
                        'object1': {
                            'id': obj_id1,
                            'type': self.object_registry['object_states'].get(obj_id1, {}).get('type', 'unknown'),
                            'bbox': bbox1
                        },
                        'object2': {
                            'id': obj_id2,
                            'type': self.object_registry['object_states'].get(obj_id2, {}).get('type', 'unknown'),
                            'bbox': bbox2
                        },
                        'overlap_area': overlap_area,
                        'severity': 'high' if overlap_area > 0.5 else 'medium' if overlap_area > 0.2 else 'low'
                    })
        
        return overlaps
    
    def _calculate_bbox_overlap(self, bbox1, bbox2):
        """Calculate overlap area between two bounding boxes"""
        try:
            (x1_min, y1_min), (x1_max, y1_max), w1, h1 = bbox1
            (x2_min, y2_min), (x2_max, y2_max), w2, h2 = bbox2
            
            # Calculate intersection
            x_left = max(x1_min, x2_min)
            y_bottom = max(y1_min, y2_min)
            x_right = min(x1_max, x2_max)
            y_top = min(y1_max, y2_max)
            
            if x_right < x_left or y_top < y_bottom:
                return 0.0  # No overlap
            
            intersection_area = (x_right - x_left) * (y_top - y_bottom)
            area1 = w1 * h1
            area2 = w2 * h2
            
            # Return overlap ratio (0.0 to 1.0)
            return intersection_area / min(area1, area2)
            
        except Exception:
            return 0.0
    
    def auto_resolve_overlaps(self, overlaps):
        """Automatically resolve overlapping objects"""
        resolved_count = 0
        
        for overlap in overlaps:
            obj1_id = overlap['object1']['id']
            obj2_id = overlap['object2']['id']
            
            # Get current positions
            pos1 = self.object_registry['object_states'].get(obj1_id, {}).get('position', [0, 0, 0])
            pos2 = self.object_registry['object_states'].get(obj2_id, {}).get('position', [0, 0, 0])
            
            # Calculate new positions to avoid overlap
            new_pos1, new_pos2 = self._calculate_non_overlapping_positions(
                overlap['object1']['bbox'], 
                overlap['object2']['bbox'],
                pos1, pos2
            )
            
            # Update positions
            if new_pos1 and new_pos2:
                self.object_registry['object_states'][obj1_id]['position'] = new_pos1
                self.object_registry['object_states'][obj2_id]['position'] = new_pos2
                
                # Update mobject positions
                mobj1 = self.object_registry['active_objects'].get(obj1_id)
                mobj2 = self.object_registry['active_objects'].get(obj2_id)
                
                if mobj1:
                    mobj1.move_to(new_pos1)
                if mobj2:
                    mobj2.move_to(new_pos2)
                
                resolved_count += 1
        
        return resolved_count
    
    def _calculate_non_overlapping_positions(self, bbox1, bbox2, pos1, pos2):
        """Calculate new positions to avoid overlap"""
        try:
            (x1_min, y1_min), (x1_max, y1_max), w1, h1 = bbox1
            (x2_min, y2_min), (x2_max, y2_max), w2, h2 = bbox2
            
            # Calculate required separation
            min_separation = max(w1, h1, w2, h2) * 0.2
            
            # Calculate center points
            center1 = [(x1_min + x1_max) / 2, (y1_min + y1_max) / 2, 0]
            center2 = [(x2_min + x2_max) / 2, (y2_min + y2_max) / 2, 0]
            
            # Calculate direction vector
            direction = [center2[0] - center1[0], center2[1] - center1[1], 0]
            distance = (direction[0]**2 + direction[1]**2)**0.5
            
            if distance < min_separation:
                # Objects are too close, move them apart
                if distance > 0:
                    # Normalize direction and scale
                    scale = (min_separation - distance) / distance
                    direction = [d * scale for d in direction]
                else:
                    # Objects are at same position, move in opposite directions
                    direction = [min_separation, 0, 0]
                
                # Move objects apart
                new_pos1 = [pos1[0] - direction[0]/2, pos1[1] - direction[1]/2, pos1[2]]
                new_pos2 = [pos2[0] + direction[0]/2, pos2[1] + direction[1]/2, pos2[2]]
                
                return new_pos1, new_pos2
            
            return pos1, pos2
            
        except Exception:
            return pos1, pos2
    
    def get_overlap_risk_assessment(self):
        """Get comprehensive overlap risk assessment"""
        overlaps = self.detect_object_overlaps()
        
        risk_level = 'low'
        if any(o['severity'] == 'high' for o in overlaps):
            risk_level = 'high'
        elif any(o['severity'] == 'medium' for o in overlaps):
            risk_level = 'medium'
        
        return {
            'risk_level': risk_level,
            'total_overlaps': len(overlaps),
            'high_risk_overlaps': len([o for o in overlaps if o['severity'] == 'high']),
            'medium_risk_overlaps': len([o for o in overlaps if o['severity'] == 'medium']),
            'low_risk_overlaps': len([o for o in overlaps if o['severity'] == 'low']),
            'overlaps': overlaps
        }
