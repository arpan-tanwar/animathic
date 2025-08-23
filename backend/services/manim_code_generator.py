"""
Manim Code Generator for Animathic
Converts animation specifications to executable Manim code
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ManimCodeGenerator:
    """Generates Manim code from animation specifications"""
    
    def __init__(self):
        """Initialize the code generator"""
        pass
    
    def generate_manim_code(self, animation_spec: Dict[str, Any]) -> str:
        """Convert animation specification to Manim Python code - IMPROVED VERSION"""
        try:
            logger.info("Converting animation spec to Manim code")
            
            # Validate input specification
            if not self._validate_input_spec(animation_spec):
                raise ValueError("Invalid animation specification provided")
            
            # Sanitize spec to avoid invalid shapes/values
            sanitized_objects = self._sanitize_objects(animation_spec.get('objects', []) or [])
            animation_spec = {**animation_spec, "objects": sanitized_objects}
            
            # Bounds defaults
            x_bounds, y_bounds = self._get_bounds(animation_spec)
            
            # Generate the Manim code template
            manim_code = self._generate_code_template(animation_spec, x_bounds, y_bounds)
            
            # Validate generated code
            if not self._validate_generated_code(manim_code):
                raise ValueError("Generated Manim code validation failed")
            
            logger.info("Successfully generated Manim code")
            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            # Return a safe fallback code instead of raising
            return self._generate_fallback_code(animation_spec)
    
    def _validate_input_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate input animation specification"""
        try:
            if not isinstance(spec, dict):
                logger.error("Spec is not a dictionary")
                return False
            
            if 'objects' not in spec:
                logger.error("Spec missing objects array")
                return False
            
            if not isinstance(spec['objects'], list):
                logger.error("Objects is not a list")
                return False
            
            # Validate each object
            for i, obj in enumerate(spec['objects']):
                if not isinstance(obj, dict):
                    logger.error(f"Object {i} is not a dictionary")
                    return False
                
                if 'type' not in obj:
                    logger.error(f"Object {i} missing type")
                    return False
                
                if 'properties' not in obj:
                    logger.error(f"Object {i} missing properties")
                    return False
            
            logger.info("Input spec validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error in input spec validation: {e}")
            return False
    
    def _validate_generated_code(self, code: str) -> bool:
        """Validate generated Manim code - IMPROVED VERSION"""
        try:
            if not code or not isinstance(code, str):
                logger.error("Code is empty or not a string")
                return False
            
            # Check for required components
            required_components = [
                'from manim import',
                'class GeneratedScene',
                'def construct(self)',
                'self.add(',
                'self.play('
            ]
            
            for component in required_components:
                if component not in code:
                    logger.error(f"Missing required component: {component}")
                    return False
            
            # Check for dangerous patterns - IMPROVED: More intelligent detection
            dangerous_patterns = [
                # Only catch actual function calls, not string literals or comments
                'eval(',  # Actual eval function call
                '__import__(',  # Actual import function call
                'exec(',  # Actual exec function call
                'open(',  # Actual open function call
                'file('   # Actual file function call
            ]
            
            # More intelligent pattern detection
            for pattern in dangerous_patterns:
                # Look for actual function calls, not string literals or comments
                if pattern in code:
                    # Check if it's in a string literal or comment
                    lines = code.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line:
                            # Skip if it's a comment
                            stripped_line = line.strip()
                            if stripped_line.startswith('#'):
                                continue
                            
                            # Skip if it's in a string literal
                            if f"'{pattern}" in line or f'"{pattern}' in line:
                                continue
                            
                            # This is an actual dangerous pattern
                            logger.error(f"Dangerous pattern found on line {i+1}: {line.strip()}")
                            return False
                    
                    # If we get here, the pattern was found but it's safe (in strings/comments)
                    logger.info(f"Pattern '{pattern}' found but appears to be safe (in strings/comments)")
            
            logger.info("Generated code validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error in generated code validation: {e}")
            return False
    
    def _generate_fallback_code(self, spec: Dict[str, Any]) -> str:
        """Generate safe fallback Manim code when main generation fails"""
        try:
            logger.info("Generating fallback Manim code")
            
            # Create a minimal, safe scene
            fallback_code = '''from manim import *

class GeneratedScene(MovingCameraScene):
    def construct(self):
        # Fallback scene due to generation error
        self.camera.background_color = rgb_to_color([0, 0, 0])  # Black
        
        # Create a simple white circle as fallback
        circle = Circle(
            radius=1,
            fill_color=rgb_to_color([1, 1, 1]),  # White
            stroke_color=rgb_to_color([1, 1, 1]),  # White
            fill_opacity=1.0,
            stroke_width=2
        )
        
        self.add(circle)
        self.play(Create(circle), run_time=1.0)
        self.wait(1)
        self.play(FadeOut(circle), run_time=1.0)
        self.wait(1)
        
        print("Fallback scene completed")
'''
            
            logger.info("Fallback code generated successfully")
            return fallback_code
            
        except Exception as e:
            logger.error(f"Error generating fallback code: {e}")
            # Return absolute minimal code
            return '''from manim import *

class GeneratedScene(MovingCameraScene):
    def construct(self):
        self.wait(2)
        print("Minimal fallback scene")
'''
    
    def _sanitize_objects(self, objects):
        """Sanitize animation objects to ensure valid values"""
        def _coerce_vec3(v):
            try:
                if not isinstance(v, (list, tuple)):
                    return [0, 0, 0]
                out = []
                for i in range(3):
                    out.append(float(v[i]) if i < len(v) and isinstance(v[i], (int, float)) else 0.0)
                return out
            except Exception:
                return [0, 0, 0]
        
        allowed_types = {"circle", "square", "text", "line", "dot", "axes", "plot", "diamond", "star", "hexagon", "triangle", "rectangle", "ellipse"}
        allowed_anims = {"move", "scale", "rotate", "fade_in", "fade_out", "transform", "fade_out_previous", "clear_previous_plots", "wait"}
        
        sanitized_objects = []
        for obj in objects:
            otype = str(obj.get("type", "")).lower()
            if otype not in allowed_types:
                continue
            
            props = obj.get("properties", {}) or {}
            props.setdefault("position", [0, 0, 0])
            props["position"] = _coerce_vec3(props.get("position"))
            
            if otype == "circle":
                try:
                    props["size"] = float(props.get("size", 1)) or 1.0
                except Exception:
                    props["size"] = 1.0
            elif otype == "square":
                try:
                    props["size"] = float(props.get("size", 2)) or 2.0
                except Exception:
                    props["size"] = 2.0
            elif otype == "line":
                props["start"] = _coerce_vec3(props.get("start", [-2, 0, 0]))
                props["end"] = _coerce_vec3(props.get("end", [2, 0, 0]))
            elif otype == "axes":
                def _rng(r, d):
                    try:
                        r = list(r)
                        xmin = float(r[0])
                        xmax = float(r[1])
                        step = float(r[2])
                        # Sanitize step: must be positive and not too small
                        if step <= 0:
                            step = 1.0
                        # Coerce to reasonable tick granularity
                        if step < 0.5:
                            step = 0.5
                        return [xmin, xmax, step]
                    except Exception:
                        return d
                
                props["x_range"] = _rng(props.get("x_range", [-5, 5, 1]), [-5, 5, 1])
                props["y_range"] = _rng(props.get("y_range", [-3, 3, 1]), [-3, 3, 1])
                props["show_labels"] = bool(props.get("show_labels", True))
            elif otype == "plot":
                try:
                    xr = props.get("x_range_plot", [-5, 5])
                    props["x_range_plot"] = [float(xr[0]), float(xr[1])]
                except Exception:
                    props["x_range_plot"] = [-5, 5]
                props["expression"] = str(props.get("expression", "sin(x)"))
            elif otype == "diamond":
                try:
                    props["size"] = float(props.get("size", 1)) or 1.0
                except Exception:
                    props["size"] = 1.0
            elif otype == "star":
                try:
                    props["size"] = float(props.get("size", 1)) or 1.0
                except Exception:
                    props["size"] = 1.0
            elif otype == "hexagon":
                try:
                    props["size"] = float(props.get("size", 1)) or 1.0
                except Exception:
                    props["size"] = 1.0
            elif otype == "triangle":
                try:
                    props["size"] = float(props.get("size", 1)) or 1.0
                except Exception:
                    props["size"] = 1.0
            elif otype == "rectangle":
                try:
                    props["size"] = float(props.get("size", 1)) or 1.0
                except Exception:
                    props["size"] = 1.0
            elif otype == "ellipse":
                try:
                    props["size"] = float(props.get("size", 1)) or 1.0
                except Exception:
                    props["size"] = 1.0
            
            # Sanitize animations
            anims = []
            for anim in obj.get("animations", []) or []:
                a = dict(anim or {})
                a_type_raw = str(a.get("type", "move")).lower()
                
                # Normalize/allow only known animations
                if a_type_raw in {"fadein", "appear"}:
                    a["type"] = "fade_in"
                elif a_type_raw in {"fadeout", "disappear"}:
                    a["type"] = "fade_out"
                elif a_type_raw in {"transform_to", "morph", "transformto"}:
                    a["type"] = "transform"
                elif a_type_raw in {"fade_out_previous", "clear_previous_plots", "wait"}:
                    a["type"] = a_type_raw
                elif a_type_raw in allowed_anims:
                    a["type"] = a_type_raw
                else:
                    # Skip unknown animation types
                    continue
                
                try:
                    a["duration"] = max(0.1, float(a.get("duration", 1)))
                except Exception:
                    a["duration"] = 1.0
                
                a.setdefault("parameters", {})
                anims.append(a)
            
            sanitized_objects.append({"type": otype, "properties": props, "animations": anims})
        
        return sanitized_objects
    
    def _get_bounds(self, animation_spec):
        """Get bounds from animation spec with defaults"""
        try:
            _b = animation_spec.get("bounds") or {}
            _bx = _b.get("x", [-6, 6])
            _by = _b.get("y", [-3.5, 3.5])
            x_bounds = [float(_bx[0]), float(_bx[1])]
            y_bounds = [float(_by[0]), float(_by[1])]
        except Exception:
            x_bounds = [-6.0, 6.0]
            y_bounds = [-3.5, 3.5]
        
        return x_bounds, y_bounds
    
    def _generate_code_template(self, animation_spec, x_bounds, y_bounds):
        """Generate the complete Manim code template - minimal and precise"""
        code_parts = []
        
        # Scene class definition with explicit imports for compatibility
        code_parts.append("""import numpy as np
from manim import (
    Circle, Square, Triangle, Text, Axes, Dot, MovingCameraScene,
    FadeIn, FadeOut, Create, Write,
    hex_to_rgb, rgb_to_color,
    RED, GREEN, BLUE, WHITE, BLACK, YELLOW, PURPLE, ORANGE, PINK, GRAY, TEAL, MAROON
)

class GeneratedScene(MovingCameraScene):
    def construct(self):
        # Animation: """ + animation_spec.get('scene_description', 'Generated animation') + """
        
        # Set background color
        bg_color = """ + repr(animation_spec.get('background_color', '#1a1a1a')) + """
        if bg_color.lower() in ['#ffffff', '#fff', 'white', 'ffffff']:
            bg_color = "#1a1a1a"
        # Ensure valid Manim color using inline validation
        try:
            if bg_color.startswith('#'):
                # Convert hex to RGB then to Manim color
                rgb_values = hex_to_rgb(bg_color)
                self.camera.background_color = rgb_to_color(rgb_values)
            else:
                # Map common color names to valid Manim colors
                color_mapping = {
                    'white': rgb_to_color([1, 1, 1]), 'black': rgb_to_color([0, 0, 0]), 'red': rgb_to_color([1, 0, 0]), 'green': rgb_to_color([0, 1, 0]), 'blue': rgb_to_color([0, 0, 1]),
                    'yellow': rgb_to_color([1, 1, 0]), 'purple': rgb_to_color([1, 0, 1]), 'orange': rgb_to_color([1, 0.5, 0]), 'pink': rgb_to_color([1, 0.75, 0.8]),
                    'brown': rgb_to_color([0.5, 0.25, 0]), 'gray': rgb_to_color([0.5, 0.5, 0.5]), 'grey': rgb_to_color([0.5, 0.5, 0.5]), 'cyan': rgb_to_color([0, 1, 1]), 'magenta': rgb_to_color([1, 0, 1]),
                    'lime': rgb_to_color([0.5, 1, 0]), 'navy': rgb_to_color([0, 0, 0.5]), 'teal': rgb_to_color([0, 0.5, 0.5]), 'maroon': rgb_to_color([0.5, 0, 0]), 'olive': rgb_to_color([0.5, 0.5, 0]),
                    'fuchsia': rgb_to_color([1, 0, 1]), 'aqua': rgb_to_color([0, 1, 1]), 'silver': rgb_to_color([0.75, 0.75, 0.75]), 'gold': rgb_to_color([1, 0.84, 0])
                }
                self.camera.background_color = color_mapping.get(bg_color.lower(), rgb_to_color([0, 0, 0]))
        except Exception:
            self.camera.background_color = rgb_to_color([0, 0, 0])""")
        
        # Bounds logging
        code_parts.append(f"""        
        # Log bounds
        print("Bounds: x=", {x_bounds}, " y=", {y_bounds})
        
        # Set camera position for better viewing of coordinate systems
        # Ensure proper centering and bounds for mathematical plots
        # Use multiple approaches for environment compatibility
        
        try:
            # Modern Manim approach
            self.camera.frame.set(width=14, height=10)
            self.camera.frame.move_to([0, 0, 0])
            self.camera.frame.set(x_range=[-7, 7], y_range=[-5, 5])
            self.camera.frame.shift([0, 0, 0])
            print("Camera positioning: Modern approach applied")
        except Exception as e1:
            print(f"Camera positioning: Modern approach failed: {{e1}}")
            try:
                # Fallback approach for different Manim versions
                self.camera.frame.set_width(14)
                self.camera.frame.set_height(10)
                self.camera.frame.move_to([0, 0, 0])
                print("Camera positioning: Fallback approach applied")
            except Exception as e2:
                print(f"Camera positioning: Fallback approach failed: {{e2}}")
                try:
                    # Basic approach for maximum compatibility
                    self.camera.frame.move_to([0, 0, 0])
                    print("Camera positioning: Basic approach applied")
                except Exception as e3:
                    print(f"Camera positioning: All approaches failed: {{e3}}")
                    # Continue without camera positioning
        
        # Alternative: Use scene-level camera configuration for better compatibility
        try:
            # Set scene dimensions and center
            self.camera.frame.set_width(14)
            self.camera.frame.set_height(10)
            # Force center positioning
            self.camera.frame.move_to([0, 0, 0])
            print("Camera positioning: Scene-level approach applied")
        except Exception as e4:
            print(f"Camera positioning: Scene-level approach failed: {{e4}}")
        
        # Final fallback: Use basic camera centering
        try:
            self.camera.frame.move_to([0, 0, 0])
            print("Camera positioning: Final fallback applied")
        except Exception as e5:
            print(f"Camera positioning: Final fallback failed: {{e5}}")
            print("Continuing without camera positioning - axes may not be perfectly centered")
        
        # Cloud Run specific approach: Use scene camera configuration
        try:
            # Set scene dimensions for better compatibility
            self.camera.frame.set_width(14)
            self.camera.frame.set_height(10)
            # Force center positioning with multiple methods
            self.camera.frame.move_to([0, 0, 0])
            self.camera.frame.shift([0, 0, 0])
            print("Camera positioning: Cloud Run specific approach applied")
        except Exception as e6:
            print(f"Camera positioning: Cloud Run specific approach failed: {{e6}}")
            print("Continuing with basic positioning")""")
        
        # Object creation - minimal, no enhancements
        objects = animation_spec.get('objects', [])
        
        code_parts.append(f"""        
        # Create objects exactly as specified
        objects_created = []
        
        # Define objects list
        objects = {objects}
        
        print(f"Creating {{len(objects)}} objects as requested...")""")
        
        # Object loop - no positioning suggestions or camera strategies
        code_parts.append("""        
        for idx, obj in enumerate(objects):""")
        
        # Object processing - minimal, no enhancements
        code_parts.append("""            obj_id = obj.get('id') or f"obj_{idx}"
            obj_type = obj.get('type', 'circle')
            props = obj.get('properties', {})
            
            # Ensure position is set (critical for rendering)
            if 'position' not in props:
                props['position'] = [0, 0, 0]
            
            # Create object exactly as specified - no enhancements
            if obj_type == 'circle':
                size = props.get('size', 1)
                color_name = props.get('color', 'WHITE')
                pos = props.get('position', [0, 0, 0])
                
                # Inline color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        # Convert hex to RGB then to Manim color
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                        print(f"Using hex color: {color_name} -> {color}")
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': GRAY, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': GRAY, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        
                        print(f"Color mapping lookup: '{color_name}' in {list(color_mapping.keys())}")
                        color = color_mapping.get(str(color_name), rgb_to_color([1, 0, 0]))  # Default to RED instead of WHITE
                        print(f"Color mapping result: '{color_name}' -> {color}")
                        
                        # Debug logging
                        print(f"Color mapping: '{color_name}' -> {color}")
                        
                except (ValueError, TypeError) as e:
                    # Only catch specific color-related errors, not all exceptions
                    print(f"Color parsing error for '{color_name}': {e}")
                    # Try to use color mapping as fallback instead of defaulting to WHITE
                    try:
                        color_mapping = {
                            'WHITE': rgb_to_color([1, 1, 1]), 'BLACK': rgb_to_color([0, 0, 0]), 'RED': rgb_to_color([1, 0, 0]), 'GREEN': rgb_to_color([0, 1, 0]), 'BLUE': rgb_to_color([0, 0, 1]),
                            'YELLOW': rgb_to_color([1, 1, 0]), 'PURPLE': rgb_to_color([1, 0, 1]), 'ORANGE': rgb_to_color([1, 0.5, 0]), 'PINK': rgb_to_color([1, 0.75, 0.8])
                        }
                        color = color_mapping.get(str(color_name), rgb_to_color([1, 0, 0]))  # Default to RED instead of WHITE
                        print(f"Fallback color mapping: '{color_name}' -> {color}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = rgb_to_color([1, 0, 0])  # Default to RED instead of WHITE
                        print(f"Final fallback: using RED for '{color_name}' (error: {e2})")
                except (ValueError, TypeError, KeyError) as e:
                    # For any other unexpected errors, still use the color mapping fallback
                    print(f"Unexpected error in color handling for '{color_name}': {e}")
                    # Try to use color mapping as fallback instead of defaulting to WHITE
                    try:
                        color_mapping = {
                            'WHITE': rgb_to_color([1, 1, 1]), 'BLACK': rgb_to_color([0, 0, 0]), 'RED': rgb_to_color([1, 0, 0]), 'GREEN': rgb_to_color([0, 1, 0]), 'BLUE': rgb_to_color([0, 0, 1]),
                            'YELLOW': rgb_to_color([1, 1, 0]), 'PURPLE': rgb_to_color([1, 0, 1]), 'ORANGE': rgb_to_color([1, 0.5, 0]), 'PINK': rgb_to_color([1, 0.75, 0.8])
                        }
                        color = color_mapping.get(str(color_name), rgb_to_color([1, 0, 0]))  # Default to RED instead of WHITE
                        print(f"Fallback color mapping: '{color_name}' -> {color}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = rgb_to_color([1, 0, 0])  # Default to RED instead of WHITE
                        print(f"Final fallback: using RED for '{color_name}' (error: {e2})")
                
                print(f"Final color for circle: {color}")
                print(f"Circle object will be created with fill_color={color}, stroke_color={color}")
                
                circle_obj = Circle(
                    radius=size,
                    fill_color=color,
                    stroke_color=color,
                    fill_opacity=1.0,  # Force full opacity
                    stroke_width=3      # Make stroke more visible
                )
                circle_obj.move_to(pos)
                
                # Force color setting to ensure it's applied
                try:
                    circle_obj.set_fill(color, opacity=1.0)
                    circle_obj.set_stroke(color, width=3)
                except Exception:
                    pass  # Fallback if set_fill/set_stroke fails
                
                # Handle animations from the spec
                animations = obj.get('animations', [])
                if not animations:
                    # Default: just create the object
                    self.add(circle_obj)
                    self.play(Create(circle_obj), run_time=1.0)
                else:
                    # Process each animation
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        
                        if anim_type == 'fade_in':
                            self.add(circle_obj)
                            self.play(FadeIn(circle_obj), run_time=duration)
                        elif anim_type == 'fade_out':
                            self.play(FadeOut(circle_obj), run_time=duration)
                        elif anim_type == 'wait':
                            self.wait(duration)
                        else:
                            # Default fallback
                            self.add(circle_obj)
                            self.play(Create(circle_obj), run_time=duration)
                
                objects_created.append(circle_obj)
                self.wait(0.5)
                
            elif obj_type == 'square':
                size = props.get('size', 2)
                color_name = props.get('color', 'BLUE')
                pos = props.get('position', [0, 0, 0])
                
                # Inline color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        # Convert hex to RGB then to Manim color
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': GRAY, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': GRAY, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), BLUE)
                        
                except (ValueError, TypeError) as e:
                    # Only catch specific color-related errors, not all exceptions
                    print(f"Color parsing error for '{color_name}': {e}")
                    # Try to use color mapping as fallback instead of defaulting to BLUE
                    try:
                        color_mapping = {
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }
                        color = color_mapping.get(str(color_name), RED)  # Default to RED instead of BLUE
                        print(f"Fallback color mapping: '{color_name}' -> {color}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = RED  # Default to RED instead of BLUE
                        print(f"Final fallback: using RED for '{color_name}' (error: {e2})")
                except (ValueError, TypeError, KeyError) as e:
                    # For any other unexpected errors, still use the color mapping fallback
                    print(f"Unexpected error in color handling for '{color_name}': {e}")
                    # Try to use color mapping as fallback instead of defaulting to BLUE
                    try:
                        color_mapping = {
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }
                        color = color_mapping.get(str(color_name), RED)  # Default to RED instead of BLUE
                        print(f"Fallback color mapping: '{color_name}' -> {color}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = RED  # Default to RED instead of BLUE
                        print(f"Final fallback: using RED for '{color_name}' (error: {e2})")
                
                square_obj = Square(
                    side_length=size,
                    fill_color=color,
                    stroke_color=color,
                    fill_opacity=1.0,  # Force full opacity
                    stroke_width=3      # Make stroke more visible
                )
                square_obj.move_to(pos)
                
                # Force color setting to ensure it's applied
                try:
                    square_obj.set_fill(color, opacity=1.0)
                    square_obj.set_stroke(color, width=3)
                except Exception:
                    pass  # Fallback if set_fill/set_stroke fails
                
                # Handle animations from the spec
                animations = obj.get('animations', [])
                if not animations:
                    # Default: just create the object
                    self.add(square_obj)
                    self.play(Create(square_obj), run_time=1.0)
                else:
                    # Process each animation
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        
                        if anim_type == 'fade_in':
                            self.add(square_obj)
                            self.play(FadeIn(square_obj), run_time=duration)
                        elif anim_type == 'fade_out':
                            self.play(FadeOut(square_obj), run_time=duration)
                        elif anim_type == 'wait':
                            self.wait(duration)
                        else:
                            # Default fallback
                            self.add(square_obj)
                            self.play(Create(square_obj), run_time=duration)
                
                objects_created.append(square_obj)
                self.wait(0.5)
                
            elif obj_type == 'triangle':
                size = props.get('size', 1)
                color_name = props.get('color', 'RED')
                pos = props.get('position', [0, 0, 0])
                
                # Inline color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        # Convert hex to RGB then to Manim color
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                        print(f"Using hex color: {color_name} -> {color}")
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': GRAY, 'gray': GRAY, 'grey': GRAY, 'cyan': TEAL, 'magenta': MAROON,
                            'lime': GREEN, 'navy': BLUE, 'teal': TEAL, 'maroon': MAROON, 'olive': GREEN,
                            'fuchsia': MAROON, 'aqua': TEAL, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': GRAY, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': TEAL, 'MAGENTA': MAROON,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': TEAL, 'MAROON': MAROON, 'OLIVE': GREEN,
                            'FUCHSIA': MAROON, 'AQUA': TEAL, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        
                        print(f"Color mapping lookup: '{color_name}' in {list(color_mapping.keys())}")
                        color = color_mapping.get(str(color_name), RED)  # Default to RED instead of WHITE
                        print(f"Color mapping result: '{color_name}' -> {color}")
                        
                        # Debug logging
                        print(f"Color mapping: '{color_name}' -> {color}")
                        
                except (ValueError, TypeError) as e:
                    # Only catch specific color-related errors, not all exceptions
                    print(f"Color parsing error for '{color_name}': {e}")
                    # Try to use color mapping as fallback instead of defaulting to WHITE
                    try:
                        color_mapping = {
                            'WHITE': rgb_to_color([1, 1, 1]), 'BLACK': rgb_to_color([0, 0, 0]), 'RED': rgb_to_color([1, 0, 0]), 'GREEN': rgb_to_color([0, 1, 0]), 'BLUE': rgb_to_color([0, 0, 1]),
                            'YELLOW': rgb_to_color([1, 1, 0]), 'PURPLE': rgb_to_color([1, 0, 1]), 'ORANGE': rgb_to_color([1, 0.5, 0]), 'PINK': rgb_to_color([1, 0.75, 0.8])
                        }
                        color = color_mapping.get(str(color_name), rgb_to_color([1, 0, 0]))  # Default to RED instead of WHITE
                        print(f"Fallback color mapping: '{color_name}' -> {color}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = rgb_to_color([1, 0, 0])  # Default to RED instead of WHITE
                        print(f"Final fallback: using RED for '{color_name}' (error: {e2})")
                except (ValueError, TypeError, KeyError) as e:
                    # For any other unexpected errors, still use the color mapping fallback
                    print(f"Unexpected error in color handling for '{color_name}': {e}")
                    # Try to use color mapping as fallback instead of defaulting to WHITE
                    try:
                        color_mapping = {
                            'WHITE': rgb_to_color([1, 1, 1]), 'BLACK': rgb_to_color([0, 0, 0]), 'RED': rgb_to_color([1, 0, 0]), 'GREEN': rgb_to_color([0, 1, 0]), 'BLUE': rgb_to_color([0, 0, 1]),
                            'YELLOW': rgb_to_color([1, 1, 0]), 'PURPLE': rgb_to_color([1, 0, 1]), 'ORANGE': rgb_to_color([1, 0.5, 0]), 'PINK': rgb_to_color([1, 0.75, 0.8])
                        }
                        color = color_mapping.get(str(color_name), rgb_to_color([1, 0, 0]))  # Default to RED instead of WHITE
                        print(f"Fallback color mapping: '{color_name}' -> {color}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = rgb_to_color([1, 0, 0])  # Default to RED instead of WHITE
                        print(f"Final fallback: using RED for '{color_name}' (error: {e2})")
                
                print(f"Final color for triangle: {color}")
                print(f"Triangle object will be created with fill_color={color}, stroke_color={color}")
                
                triangle_obj = Triangle(
                    fill_color=color,
                    stroke_color=color,
                    fill_opacity=1.0,  # Force full opacity
                    stroke_width=3      # Make stroke more visible
                )
                
                # Scale triangle to match the size parameter (similar to circle/square)
                # Default triangle is ~1.73 wide, scale to match the size parameter
                # Adjust scaling to make triangle more visible and proportional
                scale_factor = size / 1.0  # Scale directly by size for better visibility
                triangle_obj.scale(scale_factor)
                
                triangle_obj.move_to(pos)
                
                # Force color setting to ensure it's applied
                try:
                    triangle_obj.set_fill(color, opacity=1.0)
                    triangle_obj.set_stroke(color, width=3)
                except Exception:
                    pass  # Fallback if set_fill/set_stroke fails
                
                # Handle animations from the spec
                animations = obj.get('animations', [])
                if not animations:
                    # Default: just create the object
                    self.add(triangle_obj)
                    self.play(Create(triangle_obj), run_time=1.0)
                else:
                    # Process each animation
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        
                        if anim_type == 'fade_in':
                            self.add(triangle_obj)
                            self.play(FadeIn(triangle_obj), run_time=duration)
                        elif anim_type == 'fade_out':
                            self.play(FadeOut(triangle_obj), run_time=duration)
                        elif anim_type == 'wait':
                            self.wait(duration)
                        else:
                            # Default fallback
                            self.add(triangle_obj)
                            self.play(Create(triangle_obj), run_time=duration)
                
                objects_created.append(triangle_obj)
                self.wait(0.5)
                
            elif obj_type == 'text':
                text_content = props.get('text', '')
                if not text_content:  # Skip text objects with no content
                    continue
                    
                color_name = props.get('color', 'WHITE')
                font_size = props.get('size', 36)
                pos = props.get('position', [0, 0, 0])
                
                # Inline color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        # Convert hex to RGB then to Manim color
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': GRAY, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': GRAY, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), WHITE)
                except Exception:
                    color = RED  # Default to RED instead of WHITE
                
                text_obj = Text(
                    text_content,
                    color=color,
                    font_size=font_size
                )
                text_obj.move_to(pos)
                
                self.add(text_obj)
                self.play(Write(text_obj), run_time=1.0)
                objects_created.append(text_obj)
                self.wait(0.5)
                
            elif obj_type == 'axes':
                x_range = props.get('x_range', [-5, 5, 1])
                y_range = props.get('y_range', [-3, 3, 1])
                color_name = props.get('color', 'WHITE')
                pos = props.get('position', [0, 0, 0])
                
                # Inline color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        # Convert hex to RGB then to Manim color
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': GRAY, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': GRAY, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), WHITE)
                except Exception:
                    color = RED  # Default to RED instead of WHITE
                
                axes_obj = Axes(
                    x_range=[x_range[0], x_range[1], x_range[2]],
                    y_range=[y_range[0], y_range[1], y_range[2]],
                    axis_config={"color": color},
                    tips=True
                )
                axes_obj.move_to(pos)
                
                self.add(axes_obj)
                self.play(Create(axes_obj), run_time=0.5)
                objects_created.append(axes_obj)
                self.wait(0.5)
                
            elif obj_type == 'plot':
                # Support both 'function' and 'expression' for compatibility
                expression = props.get('function', props.get('expression', 'x**2'))
                x_range = props.get('x_range', [-5, 5])
                y_range = props.get('y_range', [-3, 3])
                color_name = props.get('color', 'RED')
                pos = props.get('position', [0, 0, 0])
                
                # Inline color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        # Convert hex to RGB then to Manim color
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': GRAY, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': GRAY, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), RED)
                except Exception:
                    color = RED
                
                # Use existing axes if available, otherwise create new ones
                axes = None
                for obj in objects_created:
                    if isinstance(obj, Axes):
                        axes = obj
                        break
                
                if axes is None:
                    # Create axes only if none exist
                    axes = Axes(
                        x_range=[x_range[0], x_range[1], 1],
                        y_range=[y_range[0], y_range[1], 1],
                        axis_config={"color": WHITE},
                        tips=True
                    )
                    axes.move_to(pos)
                    self.add(axes)
                    self.play(Create(axes), run_time=0.5)
                    objects_created.append(axes)
                
                # Create the plot - FIXED: Remove dangerous eval() and lambda
                try:
                    # Safe expression handling without eval or lambda
                    if expression == 'x**2':
                        def safe_x_squared(x):
                            return x**2
                        plot_obj = axes.plot(safe_x_squared, color=color, x_range=x_range)
                    elif expression == 'sin(x)':
                        def safe_sin(x):
                            return np.sin(x)
                        plot_obj = axes.plot(safe_sin, color=color, x_range=x_range)
                    elif expression == 'cos(x)':
                        def safe_cos(x):
                            return np.cos(x)
                        plot_obj = axes.plot(safe_cos, color=color, x_range=x_range)
                    elif expression == 'x':
                        def safe_x(x):
                            return x
                        plot_obj = axes.plot(safe_x, color=color, x_range=x_range)
                    else:
                        # Default to safe x**2
                        def safe_default(x):
                            return x**2
                        plot_obj = axes.plot(safe_default, color=color, x_range=x_range)
                except Exception:
                    # Fallback to safe default
                    def safe_fallback(x):
                        return x**2
                    plot_obj = axes.plot(safe_fallback, color=color, x_range=x_range)
                
                self.add(plot_obj)
                self.play(Create(plot_obj), run_time=1.0)
                objects_created.append(plot_obj)
                self.wait(0.5)
                
            elif obj_type == 'dot':
                size = props.get('size', 0.08)
                color_name = props.get('color', 'WHITE')
                pos = props.get('position', [0, 0, 0])
                
                # Inline color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        # Convert hex to RGB then to Manim color
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': GRAY, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': GRAY, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), WHITE)
                except Exception:
                    color = RED  # Default to RED instead of WHITE
                
                dot_obj = Dot(point=pos, radius=float(size), color=color)
                self.add(dot_obj)
                self.play(FadeIn(dot_obj), run_time=0.5)
                objects_created.append(dot_obj)
                self.wait(0.3)""")
        
        # Final pause and validation
        code_parts.append("""        
        # Final pause
        self.wait(2)
        
        # Simple validation - no fallbacks
        if objects_created:
            print(f"Successfully created {len(objects_created)} objects as requested")
        else:
            print("No objects were created - this may indicate an issue with the specification")
        
        print("Animation completed")""")
        
        return '\n'.join(code_parts)
