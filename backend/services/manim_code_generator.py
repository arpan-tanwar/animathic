"""
Manim Code Generator for Animathic
Generates clean, working Manim Python code from animation specifications
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ManimCodeGenerator:
    """Generates Manim Python code from animation specifications"""
    
    def __init__(self):
        """Initialize the Manim code generator"""
        pass
    
    def generate_manim_code(self, animation_spec: Dict[str, Any]) -> str:
        """Generate Manim Python code from animation specification"""
        try:
            # Extract values for proper f-string formatting
            scene_description = animation_spec.get('scene_description', 'Generated animation')
            bg_color = animation_spec.get('background_color', '#1a1a1a')
            objects = animation_spec.get('objects', [])
            
            # Generate the complete Manim code as a single f-string
            manim_code = f"""import numpy as np
from manim import *

class GeneratedScene(MovingCameraScene):
    def construct(self):
        # Animation: {scene_description}
        
        # Set background color
        bg_color = "{bg_color}"
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
                color_mapping = {{
                    'white': rgb_to_color([1, 1, 1]), 'black': rgb_to_color([0, 0, 0]), 'red': rgb_to_color([1, 0, 0]), 'green': rgb_to_color([0, 1, 0]), 'blue': rgb_to_color([0, 0, 1]),
                    'yellow': rgb_to_color([1, 1, 0]), 'purple': rgb_to_color([1, 0, 1]), 'orange': rgb_to_color([1, 0.5, 0]), 'pink': rgb_to_color([1, 0.75, 0.8]),
                    'brown': rgb_to_color([0.5, 0.25, 0]), 'gray': rgb_to_color([0.5, 0.5, 0.5]), 'grey': rgb_to_color([0.5, 0.5, 0.5]), 'cyan': rgb_to_color([0, 1, 1]), 'magenta': rgb_to_color([1, 0, 1]),
                    'lime': rgb_to_color([0.5, 1, 0]), 'navy': rgb_to_color([0, 0, 0.5]), 'teal': rgb_to_color([0, 0.5, 0.5]), 'maroon': rgb_to_color([0.5, 0, 0]), 'olive': rgb_to_color([0.5, 0.5, 0]),
                    'fuchsia': rgb_to_color([1, 0, 1]), 'aqua': rgb_to_color([0, 1, 1]), 'silver': rgb_to_color([0.75, 0.75, 0.75]), 'gold': rgb_to_color([1, 0.84, 0])
                }}
                self.camera.background_color = color_mapping.get(bg_color.lower(), rgb_to_color([0, 0, 0]))
        except Exception:
            self.camera.background_color = rgb_to_color([0, 0, 0])
        
        # Log bounds
        print("Bounds: x=", [-6.0, 6.0], " y=", [-3.5, 3.5])
        
        # FIXED: Simplified camera positioning - no more conflicting setup
        try:
            # Set camera frame dimensions and center it properly
            self.camera.frame.set(width=14, height=10)
            self.camera.frame.move_to([0, 0, 0])
            
            # Set coordinate system bounds for mathematical plots
            self.camera.frame.set(x_range=[-7, 7], y_range=[-5, 5])
            
            print("Camera positioning: Applied - centered at (0,0) with 14x10 dimensions")
        except Exception as e:
            print(f"Camera positioning failed: {{e}}")
            print("Continuing with default camera settings")
        
        # Object creation - minimal, no enhancements
        objects = {objects}
        
        # Create objects exactly as specified
        objects_created = []
        
        # Define objects list
        print(f"Creating {{len(objects)}} objects as requested...")
        
        # Object loop - no positioning suggestions or camera strategies
        for idx, obj in enumerate(objects):
            obj_id = obj.get('id') or f"obj_{{idx}}"
            obj_type = obj.get('type', 'circle')
            props = obj.get('properties', {{}})
            
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
                        print(f"Using hex color: {{color_name}} -> {{color}}")
                    else:
                        # Handle both uppercase and lowercase color names
                        color_mapping = {{
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
                        }}
                        
                        print(f"Color mapping lookup: '{{color_name}}' in {{list(color_mapping.keys())}}")
                        color = color_mapping.get(str(color_name), rgb_to_color([1, 0, 0]))  # Default to RED instead of WHITE
                        print(f"Color mapping result: '{{color_name}}' -> {{color}}")
                        
                        # Debug logging
                        print(f"Color mapping: '{{color_name}}' -> {{color}}")
                        
                except (ValueError, TypeError) as e:
                    # Only catch specific color-related errors, not all exceptions
                    print(f"Color parsing error for '{{color_name}}': {{e}}")
                    # Try to use color mapping as fallback instead of defaulting to WHITE
                    try:
                        color_mapping = {{
                            'WHITE': rgb_to_color([1, 1, 1]), 'BLACK': rgb_to_color([0, 0, 0]), 'RED': rgb_to_color([1, 0, 0]), 'GREEN': rgb_to_color([0, 1, 0]), 'BLUE': rgb_to_color([0, 0, 1]),
                            'YELLOW': rgb_to_color([1, 1, 0]), 'PURPLE': rgb_to_color([1, 0, 1]), 'ORANGE': rgb_to_color([1, 0.5, 0]), 'PINK': rgb_to_color([1, 0.75, 0.8])
                        }}
                        color = color_mapping.get(str(color_name), rgb_to_color([1, 0, 0]))  # Default to RED instead of WHITE
                        print(f"Fallback color mapping: '{{color_name}}' -> {{color}}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = rgb_to_color([1, 0, 0])  # Default to RED instead of WHITE
                        print(f"Final fallback: using RED for '{{color_name}}' (error: {{e2}})")
                except (ValueError, TypeError, KeyError) as e:
                    # For any other unexpected errors, still use the color mapping fallback
                    print(f"Unexpected error in color handling for '{{color_name}}': {{e}}")
                    # Try to use color mapping as fallback instead of defaulting to WHITE
                    try:
                        color_mapping = {{
                            'WHITE': rgb_to_color([1, 1, 1]), 'BLACK': rgb_to_color([0, 0, 0]), 'RED': rgb_to_color([1, 0, 0]), 'GREEN': rgb_to_color([0, 1, 0]), 'BLUE': rgb_to_color([0, 0, 1]),
                            'YELLOW': rgb_to_color([1, 1, 0]), 'PURPLE': rgb_to_color([1, 0, 1]), 'ORANGE': rgb_to_color([1, 0.5, 0]), 'PINK': rgb_to_color([1, 0.75, 0.8])
                        }}
                        color = color_mapping.get(str(color_name), rgb_to_color([1, 0, 0]))  # Default to RED instead of WHITE
                        print(f"Fallback color mapping: '{{color_name}}' -> {{color}}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = rgb_to_color([1, 0, 0])  # Default to RED instead of WHITE
                        print(f"Final fallback: using RED for '{{color_name}}' (error: {{e2}})")
                
                circle_obj = Circle(
                    radius=size/2,
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
                except Exception as e:
                    print(f"Error setting circle colors: {{e}}")
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    # Default: just create the object
                    self.add(circle_obj)
                    self.play(Create(circle_obj), run_time=1.0)
                else:
                    # Process each animation with proper timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        start_time = anim.get('start_time', 'immediate')
                        reason = anim.get('reason', 'default')
                        
                        # Handle timing-based animations
                        if start_time == 'before_next':
                            # This object should fade out before the next object appears
                            # Don't fade out immediately - wait for next object
                            self.add(circle_obj)
                            self.play(FadeIn(circle_obj), run_time=0.3)
                            # Store this object to fade out later when next object appears
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(circle_obj)
                        elif start_time == 'after_previous_fade':
                            # This object should fade in after the previous object fades out
                            # First, fade out the previous object if it exists
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            
                            # Small delay for smooth transition
                            self.wait(0.1)
                            self.add(circle_obj)
                            self.play(FadeIn(circle_obj), run_time=duration)
                        else:
                            # Immediate animation
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
                        color_mapping = {{
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
                        }}
                        color = color_mapping.get(str(color_name), BLUE)
                        
                except (ValueError, TypeError) as e:
                    # Only catch specific color-related errors, not all exceptions
                    print(f"Color parsing error for '{{color_name}}': {{e}}")
                    # Try to use color mapping as fallback instead of defaulting to BLUE
                    try:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), RED)  # Default to RED instead of BLUE
                        print(f"Fallback color mapping: '{{color_name}}' -> {{color}}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = RED  # Default to RED instead of BLUE
                        print(f"Final fallback: using RED for '{{color_name}}' (error: {{e2}})")
                except (ValueError, TypeError, KeyError) as e:
                    # For any other unexpected errors, still use the color mapping fallback
                    print(f"Unexpected error in color handling for '{{color_name}}': {{e}}")
                    # Try to use color mapping as fallback instead of defaulting to BLUE
                    try:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), RED)  # Default to RED instead of BLUE
                        print(f"Fallback color mapping: '{{color_name}}' -> {{color}}")
                    except (ValueError, TypeError, KeyError) as e2:
                        color = RED  # Default to RED instead of BLUE
                        print(f"Final fallback: using RED for '{{color_name}}' (error: {{e2}})")
                
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
                except Exception as e:
                    print(f"Error setting square colors: {{e}}")
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    # Default: just create the object
                    self.add(square_obj)
                    self.play(Create(square_obj), run_time=1.0)
                else:
                    # Process each animation with proper timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        start_time = anim.get('start_time', 'immediate')
                        reason = anim.get('reason', 'default')
                        
                        # Handle timing-based animations
                        if start_time == 'before_next':
                            # This object should fade out before the next object appears
                            # Don't fade out immediately - wait for next object
                            self.add(square_obj)
                            self.play(FadeIn(square_obj), run_time=0.3)
                            # Store this object to fade out later when next object appears
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(square_obj)
                        elif start_time == 'after_previous_fade':
                            # This object should fade in after the previous object fades out
                            # First, fade out the previous object if it exists
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            
                            # Small delay for smooth transition
                            self.wait(0.1)
                            self.add(square_obj)
                            self.play(FadeIn(square_obj), run_time=duration)
                        else:
                            # Immediate animation
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
                
            # Add more object types here as needed...
            
        # Final pause and validation
        self.wait(2)
        
        # Simple validation - no fallbacks
        if objects_created:
            print(f"Successfully created {{len(objects_created)}} objects as requested")
        else:
            print("No objects were created - this may indicate an issue with the specification")
        
        print("Animation completed")
"""
            
            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            # Return a minimal fallback code
            return f"""import numpy as np
from manim import *

class GeneratedScene(MovingCameraScene):
    def construct(self):
        # Error in code generation: {e}
        self.wait(2)
        print("Animation generation failed")
"""
