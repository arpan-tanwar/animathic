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
        """Convert animation specification to Manim Python code"""
        try:
            logger.info("Converting animation spec to Manim code")
            
            # Sanitize spec to avoid invalid shapes/values
            sanitized_objects = self._sanitize_objects(animation_spec.get('objects', []) or [])
            animation_spec = {**animation_spec, "objects": sanitized_objects}
            
            # Bounds defaults
            x_bounds, y_bounds = self._get_bounds(animation_spec)
            
            # Generate the Manim code template
            manim_code = self._generate_code_template(animation_spec, x_bounds, y_bounds)
            
            logger.info("Successfully generated Manim code")
            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            raise
    
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
        
        # Scene class definition
        code_parts.append("""from manim import *
import numpy as np

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
                self.camera.background_color = Color(bg_color)
            else:
                # Map common color names to valid Manim colors
                color_mapping = {
                    'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                    'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                    'brown': BROWN, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                    'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                    'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW
                }
                self.camera.background_color = color_mapping.get(bg_color.lower(), BLACK)
        except Exception:
            self.camera.background_color = BLACK""")
        
        # Bounds logging
        code_parts.append(f"""        
        # Log bounds
        print("Bounds: x=", {x_bounds}, " y=", {y_bounds})""")
        
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
                        color = Color(color_name)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': BROWN, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': BROWN, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), WHITE)
                        
                        # Debug logging
                        print(f"Color mapping: '{color_name}' -> {color}")
                except Exception:
                    color = WHITE
                    print(f"Color mapping failed for '{color_name}', using WHITE")
                
                circle_obj = Circle(
                    radius=size,
                    color=color,
                    fill_opacity=0.8,
                    stroke_width=2
                )
                circle_obj.move_to(pos)
                
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
                        color = Color(color_name)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': BROWN, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': BROWN, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), BLUE)
                except Exception:
                    color = BLUE
                
                square_obj = Square(
                    side_length=size,
                    color=color,
                    fill_opacity=0.8,
                    stroke_width=2
                )
                square_obj.move_to(pos)
                
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
                        color = Color(color_name)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': BROWN, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': BROWN, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), WHITE)
                except Exception:
                    color = WHITE
                
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
                        color = Color(color_name)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': BROWN, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': BROWN, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), WHITE)
                except Exception:
                    color = WHITE
                
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
                expression = props.get('expression', 'x**2')
                x_range = props.get('x_range_plot', [-5, 5])
                color_name = props.get('color', 'RED')
                pos = props.get('position', [0, 0, 0])
                
                # Inline color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        color = Color(color_name)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': BROWN, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': BROWN, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), RED)
                except Exception:
                    color = RED
                
                # Create axes for the plot
                axes = Axes(
                    x_range=[x_range[0], x_range[1], 1],
                    y_range=[-5, 25, 5],
                    axis_config={"color": WHITE},
                    tips=True
                )
                axes.move_to(pos)
                
                # Create the plot
                plot_obj = axes.plot(lambda x: eval(expression.replace('x', 'x')), color=color, x_range=x_range)
                
                self.add(axes)
                self.play(Create(axes), run_time=0.5)
                self.add(plot_obj)
                self.play(Create(plot_obj), run_time=1.0)
                objects_created.extend([axes, plot_obj])
                self.wait(0.5)
                
            elif obj_type == 'dot':
                size = props.get('size', 0.08)
                color_name = props.get('color', 'WHITE')
                pos = props.get('position', [0, 0, 0])
                
                # Inline color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        color = Color(color_name)
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {
                            # Lowercase mappings
                            'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN, 'blue': BLUE,
                            'yellow': YELLOW, 'purple': PURPLE, 'orange': ORANGE, 'pink': PINK,
                            'brown': BROWN, 'gray': GRAY, 'grey': GRAY, 'cyan': BLUE, 'magenta': PURPLE,
                            'lime': GREEN, 'navy': BLUE, 'teal': BLUE, 'maroon': RED, 'olive': GREEN,
                            'fuchsia': PURPLE, 'aqua': BLUE, 'silver': GRAY, 'gold': YELLOW,
                            # Uppercase mappings (for when AI generates RED, BLUE, etc.)
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'BROWN': BROWN, 'GRAY': GRAY, 'GREY': GRAY, 'CYAN': BLUE, 'MAGENTA': PURPLE,
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MAROON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), WHITE)
                except Exception:
                    color = WHITE
                
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
