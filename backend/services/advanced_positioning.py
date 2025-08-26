"""
Advanced Object Positioning Algorithms for Animathic
Provides sophisticated positioning strategies for optimal object placement
"""

import logging
import math
import random
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PositionCandidate:
    """Represents a candidate position for object placement"""
    x: float
    y: float
    z: float
    score: float
    strategy: str
    reasoning: str
    collision_risk: float


@dataclass
class ScreenRegion:
    """Represents a screen region for object placement"""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    area: float
    object_count: int
    density: float
    is_available: bool


class AdvancedObjectPositioningSystem:
    """Advanced positioning system with multiple algorithms and strategies"""
    
    def __init__(self):
        """Initialize the advanced positioning system"""
        self.positioning_strategies = {
            'plot': ['empty_region_placement', 'fade_out_and_replace', 'optimal_plot_positioning'],
            'function': ['empty_region_placement', 'fade_out_and_replace', 'optimal_plot_positioning'],
            'graph': ['empty_region_placement', 'fade_out_and_replace', 'optimal_plot_positioning'],
            'circle': ['grid_based_positioning', 'spiral_positioning', 'optimal_spacing'],
            'square': ['grid_based_positioning', 'spiral_positioning', 'optimal_spacing'],
            'diamond': ['grid_based_positioning', 'spiral_positioning', 'optimal_spacing'],
            'star': ['grid_based_positioning', 'spiral_positioning', 'optimal_spacing'],
            'hexagon': ['grid_based_positioning', 'spiral_positioning', 'optimal_spacing'],
            'triangle': ['grid_based_positioning', 'spiral_positioning', 'optimal_spacing'],
            'text': ['smart_text_positioning', 'label_positioning', 'annotation_positioning'],
            'axes': ['center_positioning', 'optimal_axes_placement'],
            'dot': ['point_positioning', 'optimal_spacing', 'grid_based_positioning']
        }
        
        # Configuration
        self.config = {
            'grid_size': 8,
            'spacing_factor': 1.2,
            'collision_threshold': 0.5,
            'prefer_center': True,
            'enable_smart_spacing': True,
            'max_positioning_attempts': 10,
            'enable_adaptive_positioning': True
        }
    
    def find_optimal_position(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                            screen_bounds: Dict[str, float], object_registry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Find the optimal position for a new object using advanced algorithms
        
        Args:
            new_object: The object to position
            existing_objects: List of existing objects
            screen_bounds: Screen boundaries
            object_registry: Optional object registry for additional context
            
        Returns:
            Positioning strategy with method, position, and reasoning
        """
        try:
            obj_type = new_object.get('type', 'unknown')
            positioning_strategy = {
                'method': 'none',
                'position': None,
                'camera_adjustment': None,
                'reasoning': '',
                'confidence': 0.0,
                'alternatives': []
            }
            
            # Get available strategies for this object type
            available_strategies = self.positioning_strategies.get(obj_type, ['default_positioning'])
            
            # Try each strategy in order of preference
            best_candidate = None
            best_score = -1
            
            for strategy in available_strategies:
                candidate = self._apply_positioning_strategy(
                    strategy, new_object, existing_objects, screen_bounds, object_registry
                )
                
                if candidate and candidate.score > best_score:
                    best_score = candidate.score
                    best_candidate = candidate
                    positioning_strategy['method'] = strategy
                    positioning_strategy['reasoning'] = candidate.reasoning
            
            if best_candidate:
                positioning_strategy['position'] = [best_candidate.x, best_candidate.y, best_candidate.z]
                positioning_strategy['confidence'] = best_candidate.score
                
                # Generate alternative positions
                positioning_strategy['alternatives'] = self._generate_alternative_positions(
                    new_object, existing_objects, screen_bounds, object_registry
                )
                
                # Determine if camera adjustment is needed
                positioning_strategy['camera_adjustment'] = self._assess_camera_adjustment(
                    new_object, existing_objects, screen_bounds, best_candidate
                )
            else:
                # Fallback to default positioning
                positioning_strategy.update({
                    'method': 'default_positioning',
                    'position': [0, 0, 0],
                    'reasoning': 'Fallback to default center positioning',
                    'confidence': 0.1
                })
            
            logger.debug(f"Positioning strategy for {obj_type}: {positioning_strategy['method']} "
                        f"at {positioning_strategy['position']} (confidence: {positioning_strategy['confidence']:.2f})")
            
            return positioning_strategy
            
        except Exception as e:
            logger.error(f"Error in advanced object positioning: {e}")
            return {
                'method': 'error',
                'position': [0, 0, 0],
                'reasoning': f'Error in positioning: {str(e)}',
                'confidence': 0.0
            }
    
    def _apply_positioning_strategy(self, strategy: str, new_object: Dict[str, Any], 
                                  existing_objects: List[Dict[str, Any]], screen_bounds: Dict[str, float],
                                  object_registry: Optional[Dict[str, Any]]) -> Optional[PositionCandidate]:
        """Apply a specific positioning strategy"""
        try:
            if strategy == 'empty_region_placement':
                return self._empty_region_placement(new_object, existing_objects, screen_bounds)
            elif strategy == 'fade_out_and_replace':
                return self._fade_out_and_replace_positioning(new_object, existing_objects, screen_bounds)
            elif strategy == 'optimal_plot_positioning':
                return self._optimal_plot_positioning(new_object, existing_objects, screen_bounds, object_registry)
            elif strategy == 'grid_based_positioning':
                return self._grid_based_positioning(new_object, existing_objects, screen_bounds)
            elif strategy == 'spiral_positioning':
                return self._spiral_positioning(new_object, existing_objects, screen_bounds)
            elif strategy == 'optimal_spacing':
                return self._optimal_spacing_positioning(new_object, existing_objects, screen_bounds)
            elif strategy == 'smart_text_positioning':
                return self._smart_text_positioning(new_object, existing_objects, screen_bounds)
            elif strategy == 'label_positioning':
                return self._label_positioning(new_object, existing_objects, screen_bounds)
            elif strategy == 'annotation_positioning':
                return self._annotation_positioning(new_object, existing_objects, screen_bounds)
            elif strategy == 'center_positioning':
                return self._center_positioning(new_object, existing_objects, screen_bounds)
            elif strategy == 'optimal_axes_placement':
                return self._optimal_axes_placement(new_object, existing_objects, screen_bounds)
            elif strategy == 'point_positioning':
                return self._point_positioning(new_object, existing_objects, screen_bounds)
            else:
                return self._default_positioning(new_object, existing_objects, screen_bounds)
                
        except Exception as e:
            logger.error(f"Error applying positioning strategy {strategy}: {e}")
            return None
    
    def _empty_region_placement(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                               screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Find and use empty regions for object placement"""
        try:
            empty_regions = self._find_empty_screen_regions(existing_objects, screen_bounds)
            if not empty_regions:
                return None
            
            # Score regions based on multiple factors
            best_region = None
            best_score = -1
            
            for region in empty_regions:
                score = self._calculate_region_score(region, new_object, existing_objects, screen_bounds)
                if score > best_score:
                    best_score = score
                    best_region = region
            
            if best_region:
                return PositionCandidate(
                    x=best_region['center_x'],
                    y=best_region['center_y'],
                    z=0,
                    score=best_score,
                    strategy='empty_region_placement',
                    reasoning=f'Placed in optimal empty region (score: {best_score:.2f})',
                    collision_risk=0.1
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in empty region placement: {e}")
            return None
    
    def _find_empty_screen_regions(self, existing_objects: List[Dict[str, Any]], 
                                  screen_bounds: Dict[str, float]) -> List[Dict[str, Any]]:
        """Find empty regions in the screen using advanced algorithms"""
        try:
            grid_size = self.config['grid_size']
            grid = [[True for _ in range(grid_size)] for _ in range(grid_size)]
            
            # Mark occupied grid cells with object footprints
            for obj in existing_objects:
                self._mark_object_footprint(obj, grid, screen_bounds, grid_size)
            
            # Find empty regions using connected component analysis
            empty_regions = self._find_connected_empty_regions(grid, screen_bounds, grid_size)
            
            # Filter and rank regions
            valid_regions = []
            for region in empty_regions:
                if region['area'] > 0.5:  # Minimum area threshold
                    valid_regions.append(region)
            
            return valid_regions
            
        except Exception as e:
            logger.error(f"Error finding empty regions: {e}")
            return []
    
    def _mark_object_footprint(self, obj: Dict[str, Any], grid: List[List[bool]], 
                              screen_bounds: Dict[str, float], grid_size: int):
        """Mark the footprint of an object on the grid"""
        try:
            properties = obj.get('properties', {})
            position = properties.get('position', [0, 0, 0])
            
            # Get object dimensions
            obj_type = obj.get('type', 'unknown')
            dimensions = self._get_object_dimensions(obj_type, properties)
            
            # Convert position and dimensions to grid coordinates
            grid_x = int((position[0] - screen_bounds['min_x']) / screen_bounds['width'] * grid_size)
            grid_y = int((position[1] - screen_bounds['min_y']) / screen_bounds['height'] * grid_size)
            
            # Mark grid cells as occupied
            radius_x = int(dimensions['width'] / screen_bounds['width'] * grid_size / 2)
            radius_y = int(dimensions['height'] / screen_bounds['height'] * grid_size / 2)
            
            for dx in range(-radius_x, radius_x + 1):
                for dy in range(-radius_y, radius_y + 1):
                    nx, ny = grid_x + dx, grid_y + dy
                    if 0 <= nx < grid_size and 0 <= ny < grid_size:
                        grid[ny][nx] = False
                        
        except Exception as e:
            logger.error(f"Error marking object footprint: {e}")
    
    def _get_object_dimensions(self, obj_type: str, properties: Dict[str, Any]) -> Dict[str, float]:
        """Get default dimensions for object types"""
        default_dimensions = {
            'circle': {'width': 1.0, 'height': 1.0},
            'square': {'width': 1.0, 'height': 1.0},
            'diamond': {'width': 1.0, 'height': 1.0},
            'star': {'width': 1.0, 'height': 1.0},
            'hexagon': {'width': 1.0, 'height': 1.0},
            'triangle': {'width': 1.0, 'height': 1.0},
            'text': {'width': 2.0, 'height': 0.5},
            'plot': {'width': 4.0, 'height': 3.0},
            'function': {'width': 4.0, 'height': 3.0},
            'graph': {'width': 4.0, 'height': 3.0},
            'axes': {'width': 6.0, 'height': 4.0},
            'dot': {'width': 0.2, 'height': 0.2}
        }
        
        return default_dimensions.get(obj_type, {'width': 1.0, 'height': 1.0})
    
    def _find_connected_empty_regions(self, grid: List[List[bool]], screen_bounds: Dict[str, float], 
                                     grid_size: int) -> List[Dict[str, Any]]:
        """Find connected empty regions using flood fill algorithm"""
        try:
            visited = [[False for _ in range(grid_size)] for _ in range(grid_size)]
            regions = []
            
            for y in range(grid_size):
                for x in range(grid_size):
                    if grid[y][x] and not visited[y][x]:
                        # Found a new empty region, flood fill to find its extent
                        region = self._flood_fill_empty_region(grid, visited, x, y, grid_size)
                        if region['area'] > 0:
                            # Convert grid coordinates to screen coordinates
                            region['center_x'] = screen_bounds['min_x'] + (region['center_x'] + 0.5) * screen_bounds['width'] / grid_size
                            region['center_y'] = screen_bounds['min_y'] + (region['center_y'] + 0.5) * screen_bounds['height'] / grid_size
                            regions.append(region)
            
            return regions
            
        except Exception as e:
            logger.error(f"Error finding connected empty regions: {e}")
            return []
    
    def _flood_fill_empty_region(self, grid: List[List[bool]], visited: List[List[bool]], 
                                 start_x: int, start_y: int, grid_size: int) -> Dict[str, Any]:
        """Flood fill algorithm to find connected empty region"""
        try:
            stack = [(start_x, start_y)]
            visited[start_y][start_x] = True
            min_x, min_y = start_x, start_y
            max_x, max_y = start_x, start_y
            area = 0
            
            while stack:
                x, y = stack.pop()
                area += 1
                
                # Update boundaries
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                
                # Check neighbors
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < grid_size and 0 <= ny < grid_size and 
                        grid[ny][nx] and not visited[ny][nx]):
                        visited[ny][nx] = True
                        stack.append((nx, ny))
            
            return {
                'min_x': min_x,
                'min_y': min_y,
                'max_x': max_x,
                'max_y': max_y,
                'center_x': (min_x + max_x) / 2,
                'center_y': (min_y + max_y) / 2,
                'area': area,
                'width': max_x - min_x + 1,
                'height': max_y - min_y + 1
            }
            
        except Exception as e:
            logger.error(f"Error in flood fill: {e}")
            return {'area': 0, 'center_x': start_x, 'center_y': start_y}
    
    def _calculate_region_score(self, region: Dict[str, Any], new_object: Dict[str, Any], 
                               existing_objects: List[Dict[str, Any]], screen_bounds: Dict[str, float]) -> float:
        """Calculate a score for a region based on multiple factors"""
        try:
            score = 0.0
            
            # Factor 1: Distance from center (prefer center)
            center_distance = math.sqrt(region['center_x']**2 + region['center_y']**2)
            max_distance = math.sqrt(screen_bounds['width']**2 + screen_bounds['height']**2) / 2
            center_score = 1.0 - (center_distance / max_distance)
            score += center_score * 0.4
            
            # Factor 2: Region size (prefer larger regions)
            max_area = (screen_bounds['width'] * screen_bounds['height']) / (self.config['grid_size'] ** 2)
            size_score = min(region['area'] / max_area, 1.0)
            score += size_score * 0.3
            
            # Factor 3: Distance from existing objects (prefer more isolated regions)
            isolation_score = self._calculate_isolation_score(region, existing_objects)
            score += isolation_score * 0.3
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating region score: {e}")
            return 0.0
    
    def _calculate_isolation_score(self, region: Dict[str, Any], existing_objects: List[Dict[str, Any]]) -> float:
        """Calculate how isolated a region is from existing objects"""
        try:
            if not existing_objects:
                return 1.0
            
            min_distance = float('inf')
            for obj in existing_objects:
                properties = obj.get('properties', {})
                obj_pos = properties.get('position', [0, 0, 0])
                
                distance = math.sqrt((region['center_x'] - obj_pos[0])**2 + (region['center_y'] - obj_pos[1])**2)
                min_distance = min(min_distance, distance)
            
            # Normalize distance score (closer to 1.0 means more isolated)
            max_expected_distance = 8.0  # Based on typical screen bounds
            isolation_score = min(min_distance / max_expected_distance, 1.0)
            
            return isolation_score
            
        except Exception as e:
            logger.error(f"Error calculating isolation score: {e}")
            return 0.5
    
    def _grid_based_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                                screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Grid-based positioning for geometric objects"""
        try:
            # Count existing shapes of the same type
            obj_type = new_object.get('type', 'unknown')
            same_type_objects = [obj for obj in existing_objects if obj.get('type') == obj_type]
            shape_count = len(same_type_objects)
            
            # Calculate grid dimensions
            cols = 4
            rows = 3
            row = shape_count // cols
            col = shape_count % cols
            
            # Calculate spacing
            spacing_x = screen_bounds.get('width', 16) / (cols + 1)
            spacing_y = screen_bounds.get('height', 9) / (rows + 1)
            
            # Calculate position
            x = screen_bounds.get('min_x', -8) + (col + 1) * spacing_x
            y = screen_bounds.get('max_y', 4.5) - (row + 1) * spacing_y
            
            # Check for collisions
            collision_risk = self._calculate_collision_risk([x, y, 0], existing_objects)
            
            return PositionCandidate(
                x=x,
                y=y,
                z=0,
                score=0.8 - collision_risk,
                strategy='grid_based_positioning',
                reasoning=f'Grid position ({col}, {row}) for {obj_type} #{shape_count + 1}',
                collision_risk=collision_risk
            )
            
        except Exception as e:
            logger.error(f"Error in grid-based positioning: {e}")
            return None
    
    def _spiral_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                           screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Spiral positioning for objects when grid is full"""
        try:
            # Start from center and spiral outward
            center_x = (screen_bounds.get('min_x', -8) + screen_bounds.get('max_x', 8)) / 2
            center_y = (screen_bounds.get('min_y', -4.5) + screen_bounds.get('max_y', 4.5)) / 2
            
            # Spiral parameters
            angle_step = 0.5
            radius_step = 0.3
            max_radius = min(screen_bounds.get('width', 16), screen_bounds.get('height', 9)) / 2
            
            for radius in range(0, int(max_radius / radius_step)):
                for angle in range(0, int(2 * math.pi / angle_step)):
                    x = center_x + radius * radius_step * math.cos(angle * angle_step)
                    y = center_y + radius * radius_step * math.sin(angle * angle_step)
                    
                    # Check if position is within bounds
                    if (screen_bounds.get('min_x', -8) <= x <= screen_bounds.get('max_x', 8) and 
                        screen_bounds.get('min_y', -4.5) <= y <= screen_bounds.get('max_y', 4.5)):
                        
                        # Check collision risk
                        collision_risk = self._calculate_collision_risk([x, y, 0], existing_objects)
                        if collision_risk < 0.3:  # Acceptable collision risk
                            return PositionCandidate(
                                x=x,
                                y=y,
                                z=0,
                                score=0.7 - collision_risk,
                                strategy='spiral_positioning',
                                reasoning=f'Spiral position at radius {radius * radius_step:.1f}',
                                collision_risk=collision_risk
                            )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in spiral positioning: {e}")
            return None
    
    def _optimal_spacing_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                                   screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Optimal spacing positioning using force-directed algorithm"""
        try:
            if not existing_objects:
                return PositionCandidate(
                    x=0, y=0, z=0,
                    score=1.0,
                    strategy='optimal_spacing_positioning',
                    reasoning='No existing objects, placing at center',
                    collision_risk=0.0
                )
            
            # Use force-directed positioning
            best_position = self._force_directed_positioning(new_object, existing_objects, screen_bounds)
            
            if best_position:
                collision_risk = self._calculate_collision_risk(best_position, existing_objects)
                return PositionCandidate(
                    x=best_position[0],
                    y=best_position[1],
                    z=best_position[2],
                    score=0.9 - collision_risk,
                    strategy='optimal_spacing_positioning',
                    reasoning='Force-directed optimal spacing',
                    collision_risk=collision_risk
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in optimal spacing positioning: {e}")
            return None
    
    def _force_directed_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                                   screen_bounds: Dict[str, float]) -> Optional[List[float]]:
        """Force-directed positioning algorithm"""
        try:
            # Start with a random position
            x = random.uniform(screen_bounds['min_x'] + 1, screen_bounds['max_x'] - 1)
            y = random.uniform(screen_bounds['min_y'] + 1, screen_bounds['max_y'] - 1)
            
            # Iterative force calculation
            for iteration in range(50):
                fx, fy = 0, 0
                
                # Repulsive forces from existing objects
                for obj in existing_objects:
                    properties = obj.get('properties', {})
                    obj_pos = properties.get('position', [0, 0, 0])
                    
                    dx = x - obj_pos[0]
                    dy = y - obj_pos[1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance > 0:
                        # Repulsive force (inverse square law)
                        force = 2.0 / (distance * distance)
                        fx += force * dx / distance
                        fy += force * dy / distance
                
                # Attractive force to center
                center_x = (screen_bounds['min_x'] + screen_bounds['max_x']) / 2
                center_y = (screen_bounds['min_y'] + screen_bounds['max_y']) / 2
                
                dx = center_x - x
                dy = center_y - y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    force = 0.1  # Weak attractive force
                    fx += force * dx / distance
                    fy += force * dy / distance
                
                # Update position
                x += fx * 0.1
                y += fy * 0.1
                
                # Keep within bounds
                x = max(screen_bounds['min_x'] + 1, min(screen_bounds['max_x'] - 1, x))
                y = max(screen_bounds['min_y'] + 1, min(screen_bounds['max_y'] - 1, y))
            
            return [x, y, 0]
            
        except Exception as e:
            logger.error(f"Error in force-directed positioning: {e}")
            return None
    
    def _smart_text_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                               screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Smart positioning for text objects"""
        try:
            # Find existing text objects
            text_objects = [obj for obj in existing_objects if obj.get('type') == 'text']
            
            # Position at top with smart spacing
            base_y = screen_bounds['max_y'] - 0.5
            y_offset = len(text_objects) * 0.8
            
            # Check if we need to adjust for overlapping text
            x_offset = 0
            for text_obj in text_objects:
                properties = text_obj.get('properties', {})
                text_pos = properties.get('position', [0, 0, 0])
                if abs(text_pos[1] - (base_y - y_offset)) < 0.5:
                    x_offset = max(x_offset, 2.0)  # Move to the right
            
            x = x_offset
            y = base_y - y_offset
            
            # Ensure within bounds
            x = max(screen_bounds['min_x'] + 1, min(screen_bounds['max_x'] - 1, x))
            y = max(screen_bounds['min_y'] + 1, min(screen_bounds['max_y'] - 1, y))
            
            collision_risk = self._calculate_collision_risk([x, y, 0], existing_objects)
            
            return PositionCandidate(
                x=x,
                y=y,
                z=0,
                score=0.8 - collision_risk,
                strategy='smart_text_positioning',
                reasoning=f'Smart text positioning with {len(text_objects)} existing texts',
                collision_risk=collision_risk
            )
            
        except Exception as e:
            logger.error(f"Error in smart text positioning: {e}")
            return None
    
    def _calculate_collision_risk(self, position: List[float], existing_objects: List[Dict[str, Any]]) -> float:
        """Calculate collision risk for a position"""
        try:
            if not existing_objects:
                return 0.0
            
            min_distance = float('inf')
            for obj in existing_objects:
                properties = obj.get('properties', {})
                obj_pos = properties.get('position', [0, 0, 0])
                
                distance = math.sqrt((position[0] - obj_pos[0])**2 + (position[1] - obj_pos[1])**2)
                min_distance = min(min_distance, distance)
            
            # Convert distance to collision risk (closer = higher risk)
            collision_threshold = self.config['collision_threshold']
            if min_distance < collision_threshold:
                return 1.0 - (min_distance / collision_threshold)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating collision risk: {e}")
            return 0.5
    
    def _generate_alternative_positions(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                                      screen_bounds: Dict[str, float], object_registry: Optional[Dict[str, Any]]) -> List[List[float]]:
        """Generate alternative positions for fallback"""
        try:
            alternatives = []
            
            # Alternative 1: Slightly offset from center
            alternatives.append([0.5, 0.5, 0])
            alternatives.append([-0.5, 0.5, 0])
            alternatives.append([0.5, -0.5, 0])
            alternatives.append([-0.5, -0.5, 0])
            
            # Alternative 2: Corners
            alternatives.append([screen_bounds.get('min_x', -8) + 1, screen_bounds.get('max_y', 4.5) - 1, 0])
            alternatives.append([screen_bounds.get('max_x', 8) - 1, screen_bounds.get('max_y', 4.5) - 1, 0])
            alternatives.append([screen_bounds.get('min_x', -8) + 1, screen_bounds.get('min_y', -4.5) + 1, 0])
            alternatives.append([screen_bounds.get('max_x', 8) - 1, screen_bounds.get('min_y', -4.5) + 1, 0])
            
            # Filter out positions with high collision risk
            filtered_alternatives = []
            for alt_pos in alternatives:
                collision_risk = self._calculate_collision_risk(alt_pos, existing_objects)
                if collision_risk < 0.7:  # Acceptable collision risk
                    filtered_alternatives.append(alt_pos)
            
            return filtered_alternatives[:5]  # Return top 5 alternatives
            
        except Exception as e:
            logger.error(f"Error generating alternative positions: {e}")
            return [[0, 0, 0]]
    
    def _assess_camera_adjustment(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                                 screen_bounds: Dict[str, float], candidate: PositionCandidate) -> Optional[Dict[str, Any]]:
        """Assess if camera adjustment is needed"""
        try:
            # Check if the new object will fit in current view
            all_positions = [[candidate.x, candidate.y, candidate.z]] if candidate else []
            for obj in existing_objects:
                properties = obj.get('properties', {})
                obj_pos = properties.get('position', [0, 0, 0])
                all_positions.append(obj_pos)
            
            # Calculate bounding box
            if all_positions:
                min_x = min(pos[0] for pos in all_positions)
                max_x = max(pos[0] for pos in all_positions)
                min_y = min(pos[1] for pos in all_positions)
                max_y = max(pos[1] for pos in all_positions)
                
                # Check if we need to zoom out
                current_width = max_x - min_x
                current_height = max_y - min_y
                screen_width = screen_bounds.get('width', 16)
                screen_height = screen_bounds.get('height', 9)
                
                if current_width > screen_width * 0.8 or current_height > screen_height * 0.8:
                    return {
                        'action': 'zoom_out',
                        'reason': 'Objects exceed screen bounds',
                        'parameters': {
                            'zoom_factor': 0.7,
                            'duration': 0.5,
                            'center_x': (min_x + max_x) / 2,
                            'center_y': (min_y + max_y) / 2
                        }
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error assessing camera adjustment: {e}")
            return None
    
    def _default_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                           screen_bounds: Dict[str, float]) -> PositionCandidate:
        """Default positioning when no other strategy works"""
        return PositionCandidate(
            x=0, y=0, z=0,
            score=0.1,
            strategy='default_positioning',
            reasoning='Fallback to default center positioning',
            collision_risk=0.5
        )
    
    # Additional positioning methods for specific object types
    def _fade_out_and_replace_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                                         screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Positioning strategy that involves fading out existing objects"""
        # This would integrate with the fade-out system
        center_pos = self._calculate_center_position(screen_bounds)
        return PositionCandidate(
            x=center_pos[0], y=center_pos[1], z=center_pos[2],
            score=0.6,
            strategy='fade_out_and_replace',
            reasoning='Using fade-out strategy for optimal positioning',
            collision_risk=0.3
        )
    
    def _optimal_plot_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                                 screen_bounds: Dict[str, float], object_registry: Optional[Dict[str, Any]]) -> Optional[PositionCandidate]:
        """Optimal positioning for plot objects"""
        # Check for axes and position accordingly
        axes_objects = [obj for obj in existing_objects if obj.get('type') == 'axes']
        if axes_objects:
            return PositionCandidate(
                x=0, y=0, z=0,
                score=0.9,
                strategy='optimal_plot_positioning',
                reasoning='Positioned at axes center for optimal visualization',
                collision_risk=0.1
            )
        
        # Fallback to empty region placement
        return self._empty_region_placement(new_object, existing_objects, screen_bounds)
    
    def _label_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                          screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Positioning for label objects"""
        # Position labels near their associated objects
        return self._smart_text_positioning(new_object, existing_objects, screen_bounds)
    
    def _annotation_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                              screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Positioning for annotation objects"""
        # Position annotations with smart spacing
        return self._smart_text_positioning(new_object, existing_objects, screen_bounds)
    
    def _center_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                           screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Center positioning for important objects like axes"""
        center_pos = self._calculate_center_position(screen_bounds)
        return PositionCandidate(
            x=center_pos[0], y=center_pos[1], z=center_pos[2],
            score=0.8,
            strategy='center_positioning',
            reasoning='Centered positioning for optimal visibility',
            collision_risk=0.2
        )
    
    def _optimal_axes_placement(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                               screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Optimal placement for axes objects"""
        return self._center_positioning(new_object, existing_objects, screen_bounds)
    
    def _point_positioning(self, new_object: Dict[str, Any], existing_objects: List[Dict[str, Any]], 
                          screen_bounds: Dict[str, float]) -> Optional[PositionCandidate]:
        """Positioning for point objects"""
        # Use optimal spacing for points
        return self._optimal_spacing_positioning(new_object, existing_objects, screen_bounds)
    
    def _calculate_center_position(self, screen_bounds: Dict[str, float]) -> List[float]:
        """Calculate center position of screen"""
        try:
            center_x = (screen_bounds['min_x'] + screen_bounds['max_x']) / 2
            center_y = (screen_bounds['min_y'] + screen_bounds['max_y']) / 2
            return [center_x, center_y, 0]
        except Exception as e:
            logger.error(f"Error calculating center position: {e}")
            return [0, 0, 0]
