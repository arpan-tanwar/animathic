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
            objects_list = animation_spec.get('objects', [])
            
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
        
        # Initialize tracking for fade-out management
        self.transient_objects_to_fade_out = []
        
        # Create all objects
        objects_created = []
        
        # Process each object
        for obj in {objects_list}:
            obj_type = obj.get('type', 'unknown')
            obj_id = obj.get('id', 'unknown')
            props = obj.get('properties', {{}})
            
            print(f"Creating {{obj_type}} object: {{obj_id}}")
            
            if obj_type == 'circle':
                # Create circle geometric shape
                size = props.get('size', 1)
                color_name = props.get('color', 'RED')
                pos = props.get('position', [0, 0, 0])
                
                # Color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), RED)
                except:
                    color = RED
                
                circle_obj = Circle(
                    radius=size,
                    fill_color=color,
                    stroke_color=color,
                    fill_opacity=1.0,
                    stroke_width=3
                )
                circle_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    self.add(circle_obj)
                    self.play(Create(circle_obj), run_time=0.8)
                else:
                    # Process animations with timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 0.8)
                        start_time = anim.get('start_time', 'immediate')
                        
                        if start_time == 'before_next':
                            self.add(circle_obj)
                            self.play(FadeIn(circle_obj), run_time=0.3)
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(circle_obj)
                        elif start_time == 'after_previous_fade':
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            self.wait(0.1)
                            self.add(circle_obj)
                            self.play(FadeIn(circle_obj), run_time=duration)
                        elif start_time == 'immediate':
                            # Object appears immediately
                            self.add(circle_obj)
                            self.play(FadeIn(circle_obj), run_time=duration)
                        elif start_time == 'after_persistent_display':
                            # Object appears after persistent objects (axes, plots) are visible
                            # Wait a bit for persistent objects to be fully visible
                            self.wait(0.5)
                            self.add(circle_obj)
                            self.play(FadeIn(circle_obj), run_time=duration)
                        elif start_time == 'before_next_transient':
                            # This transient object should fade out before the next transient object
                            self.add(circle_obj)
                            self.play(FadeIn(circle_obj), run_time=0.3)
                            # Store for fade-out when next transient object appears
                            if not hasattr(self, 'transient_objects_to_fade_out'):
                                self.transient_objects_to_fade_out = []
                            self.transient_objects_to_fade_out.append(circle_obj)
                        elif start_time == 'after_previous_transient_fade':
                            # This transient object should fade in after the previous transient object fades out
                            if hasattr(self, 'transient_objects_to_fade_out') and self.transient_objects_to_fade_out:
                                prev_obj = self.transient_objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            
                            # Small delay for smooth transition
                            self.wait(0.1)
                            self.add(circle_obj)
                            self.play(FadeIn(circle_obj), run_time=duration)
                        else:
                            # Default animation handling
                            if anim_type == 'fade_in':
                                self.add(circle_obj)
                                self.play(FadeIn(circle_obj), run_time=duration)
                            elif anim_type == 'fade_out':
                                self.play(FadeOut(circle_obj), run_time=duration)
                            elif anim_type == 'wait':
                                self.wait(duration)
                            else:
                                self.add(circle_obj)
                                self.play(Create(circle_obj), run_time=duration)
                
                objects_created.append(circle_obj)
                self.wait(0.3)
                
            elif obj_type == 'square':
                # Create square geometric shape
                size = props.get('size', 2)
                color_name = props.get('color', 'BLUE')
                pos = props.get('position', [0, 0, 0])
                
                # Color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), BLUE)
                except:
                    color = BLUE
                
                square_obj = Square(
                    side_length=size,
                    fill_color=color,
                    stroke_color=color,
                    fill_opacity=1.0,
                    stroke_width=3
                )
                square_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    self.add(square_obj)
                    self.play(Create(square_obj), run_time=0.8)
                else:
                    # Process animations with timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 0.8)
                        start_time = anim.get('start_time', 'immediate')
                        
                        if start_time == 'before_next':
                            self.add(square_obj)
                            self.play(FadeIn(square_obj), run_time=0.3)
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(square_obj)
                        elif start_time == 'after_previous_fade':
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            self.wait(0.1)
                            self.add(square_obj)
                            self.play(FadeIn(square_obj), run_time=duration)
                        elif start_time == 'immediate':
                            # Object appears immediately
                            self.add(square_obj)
                            self.play(FadeIn(square_obj), run_time=duration)
                        elif start_time == 'after_persistent_display':
                            # Object appears after persistent objects (axes, plots) are visible
                            # Wait a bit for persistent objects to be fully visible
                            self.wait(0.5)
                            self.add(square_obj)
                            self.play(FadeIn(square_obj), run_time=duration)
                        elif start_time == 'before_next_transient':
                            # This transient object should fade out before the next transient object
                            self.add(square_obj)
                            self.play(FadeIn(square_obj), run_time=0.3)
                            # Store for fade-out when next transient object appears
                            if not hasattr(self, 'transient_objects_to_fade_out'):
                                self.transient_objects_to_fade_out = []
                            self.transient_objects_to_fade_out.append(square_obj)
                        elif start_time == 'after_previous_transient_fade':
                            # This transient object should fade in after the previous transient object fades out
                            if hasattr(self, 'transient_objects_to_fade_out') and self.transient_objects_to_fade_out:
                                prev_obj = self.transient_objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            
                            # Small delay for smooth transition
                            self.wait(0.1)
                            self.add(square_obj)
                            self.play(FadeIn(square_obj), run_time=duration)
                        else:
                            # Default animation handling
                            if anim_type == 'fade_in':
                                self.add(square_obj)
                                self.play(FadeIn(square_obj), run_time=duration)
                            elif anim_type == 'fade_out':
                                self.play(FadeOut(square_obj), run_time=duration)
                            elif anim_type == 'wait':
                                self.wait(duration)
                            else:
                                self.add(square_obj)
                                self.play(Create(square_obj), run_time=duration)
                
                objects_created.append(square_obj)
                self.wait(0.3)
                
            elif obj_type == 'axes':
                # Create coordinate axes
                x_range = props.get('x_range', [-4, 4, 1])
                y_range = props.get('y_range', [-3, 3, 1])
                pos = props.get('position', [0, 0, 0])
                color_name = props.get('color', 'WHITE')
                show_labels = props.get('show_labels', True)
                
                # Color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), WHITE)
                except:
                    color = WHITE
                
                axes_obj = Axes(
                    x_range=x_range,
                    y_range=y_range,
                    axis_config={{"color": color}},
                    tips=True
                )
                axes_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    self.add(axes_obj)
                    self.play(Create(axes_obj), run_time=1.0)
                else:
                    # Process animations with timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        start_time = anim.get('start_time', 'immediate')
                        
                        if start_time == 'before_next':
                            self.add(axes_obj)
                            self.play(FadeIn(axes_obj), run_time=0.3)
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(axes_obj)
                        elif start_time == 'after_previous_fade':
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            self.wait(0.1)
                            self.add(axes_obj)
                            self.play(FadeIn(axes_obj), run_time=duration)
                        elif start_time == 'immediate':
                            # Object appears immediately
                            self.add(axes_obj)
                            self.play(FadeIn(axes_obj), run_time=duration)
                        elif start_time == 'after_persistent_display':
                            # Object appears after persistent objects (axes, plots) are visible
                            # Wait a bit for persistent objects to be fully visible
                            self.wait(0.5)
                            self.add(axes_obj)
                            self.play(FadeIn(axes_obj), run_time=duration)
                        elif start_time == 'before_next_transient':
                            # This transient object should fade out before the next transient object
                            self.add(axes_obj)
                            self.play(FadeIn(axes_obj), run_time=0.3)
                            # Store for fade-out when next transient object appears
                            if not hasattr(self, 'transient_objects_to_fade_out'):
                                self.transient_objects_to_fade_out = []
                            self.transient_objects_to_fade_out.append(axes_obj)
                        elif start_time == 'after_previous_transient_fade':
                            # This transient object should fade in after the previous transient object fades out
                            if hasattr(self, 'transient_objects_to_fade_out') and self.transient_objects_to_fade_out:
                                prev_obj = self.transient_objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            
                            # Small delay for smooth transition
                            self.wait(0.1)
                            self.add(axes_obj)
                            self.play(FadeIn(axes_obj), run_time=duration)
                        else:
                            # Default animation handling
                            if anim_type == 'fade_in':
                                self.add(axes_obj)
                                self.play(FadeIn(axes_obj), run_time=duration)
                            elif anim_type == 'fade_out':
                                self.play(FadeOut(axes_obj), run_time=duration)
                            elif anim_type == 'wait':
                                self.wait(duration)
                            else:
                                self.add(axes_obj)
                                self.play(Create(axes_obj), run_time=duration)
                
                objects_created.append(axes_obj)
                self.wait(0.5)
                
            elif obj_type == 'plot':
                # Create function plots
                color_name = props.get('color', 'YELLOW')
                pos = props.get('position', [0, 0, 0])
                function_type = props.get('function', 'sine')
                
                # Color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), YELLOW)
                except:
                    color = YELLOW
                
                # Create plot based on function type
                if function_type == 'sine':
                    plot_obj = FunctionGraph(
                        lambda x: np.sin(x),
                        x_range=[-4, 4],
                    color=color,
                        stroke_width=3
                    )
                elif function_type == 'cosine':
                    plot_obj = FunctionGraph(
                        lambda x: np.cos(x),
                        x_range=[-4, 4],
                        color=color,
                        stroke_width=3
                    )
                elif function_type == 'tangent':
                    plot_obj = FunctionGraph(
                        lambda x: np.tan(x),
                        x_range=[-1.5, 1.5],
                        color=color,
                        stroke_width=3
                    )
                elif function_type == 'exponential':
                    plot_obj = FunctionGraph(
                        lambda x: np.exp(x),
                        x_range=[-2, 2],
                        color=color,
                        stroke_width=3
                    )
                else:
                    # Default to sine
                    plot_obj = FunctionGraph(
                        lambda x: np.sin(x),
                        x_range=[-4, 4],
                        color=color,
                        stroke_width=3
                    )
                
                plot_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    self.add(plot_obj)
                    self.play(Create(plot_obj), run_time=1.0)
                else:
                    # Process animations with timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        start_time = anim.get('start_time', 'immediate')
                        
                        if start_time == 'before_next':
                            self.add(plot_obj)
                            self.play(FadeIn(plot_obj), run_time=0.3)
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(plot_obj)
                        elif start_time == 'after_previous_fade':
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            self.wait(0.1)
                            self.add(plot_obj)
                            self.play(FadeIn(plot_obj), run_time=duration)
                        elif start_time == 'immediate':
                            # Object appears immediately
                            self.add(plot_obj)
                            self.play(FadeIn(plot_obj), run_time=duration)
                        elif start_time == 'after_persistent_display':
                            # Object appears after persistent objects (axes, plots) are visible
                            # Wait a bit for persistent objects to be fully visible
                            self.wait(0.5)
                            self.add(plot_obj)
                            self.play(FadeIn(plot_obj), run_time=duration)
                        elif start_time == 'before_next_transient':
                            # This transient object should fade out before the next transient object
                            self.add(plot_obj)
                            self.play(FadeIn(plot_obj), run_time=0.3)
                            # Store for fade-out when next transient object appears
                            if not hasattr(self, 'transient_objects_to_fade_out'):
                                self.transient_objects_to_fade_out = []
                            self.transient_objects_to_fade_out.append(plot_obj)
                        elif start_time == 'after_previous_transient_fade':
                            # This transient object should fade in after the previous transient object fades out
                            if hasattr(self, 'transient_objects_to_fade_out') and self.transient_objects_to_fade_out:
                                prev_obj = self.transient_objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            
                            # Small delay for smooth transition
                            self.wait(0.1)
                            self.add(plot_obj)
                            self.play(FadeIn(plot_obj), run_time=duration)
                        else:
                            # Default animation handling
                            if anim_type == 'fade_in':
                                self.add(plot_obj)
                                self.play(FadeIn(plot_obj), run_time=duration)
                            elif anim_type == 'fade_out':
                                self.play(FadeOut(plot_obj), run_time=duration)
                            elif anim_type == 'wait':
                                self.wait(duration)
                            else:
                                self.add(plot_obj)
                                self.play(Create(plot_obj), run_time=duration)
                
                objects_created.append(plot_obj)
                self.wait(0.5)
                
            elif obj_type == 'dot':
                # Create geometric points
                size = props.get('size', 0.1)
                color_name = props.get('color', 'RED')
                pos = props.get('position', [0, 0, 0])
                
                # Color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), RED)
                except:
                    color = RED
                
                dot_obj = Dot(
                    radius=size,
                    color=color,
                    fill_opacity=1.0
                )
                dot_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    self.add(dot_obj)
                    self.play(Create(dot_obj), run_time=0.5)
                else:
                    # Process animations with timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 0.5)
                        start_time = anim.get('start_time', 'immediate')
                        
                        if start_time == 'before_next':
                            self.add(dot_obj)
                            self.play(FadeIn(dot_obj), run_time=0.3)
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(dot_obj)
                        elif start_time == 'after_previous_fade':
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            self.wait(0.1)
                            self.add(dot_obj)
                            self.play(FadeIn(dot_obj), run_time=duration)
                        elif start_time == 'immediate':
                            # Object appears immediately
                            self.add(dot_obj)
                            self.play(FadeIn(dot_obj), run_time=duration)
                        elif start_time == 'after_persistent_display':
                            # Object appears after persistent objects (axes, plots) are visible
                            # Wait a bit for persistent objects to be fully visible
                            self.wait(0.5)
                            self.add(dot_obj)
                            self.play(FadeIn(dot_obj), run_time=duration)
                        elif start_time == 'before_next_transient':
                            # This transient object should fade out before the next transient object
                            self.add(dot_obj)
                            self.play(FadeIn(dot_obj), run_time=0.3)
                            # Store for fade-out when next transient object appears
                            if not hasattr(self, 'transient_objects_to_fade_out'):
                                self.transient_objects_to_fade_out = []
                            self.transient_objects_to_fade_out.append(dot_obj)
                        elif start_time == 'after_previous_transient_fade':
                            # This transient object should fade in after the previous transient object fades out
                            if hasattr(self, 'transient_objects_to_fade_out') and self.transient_objects_to_fade_out:
                                prev_obj = self.transient_objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            
                            # Small delay for smooth transition
                            self.wait(0.1)
                            self.add(dot_obj)
                            self.play(FadeIn(dot_obj), run_time=duration)
                        else:
                            # Default animation handling
                            if anim_type == 'fade_in':
                                self.add(dot_obj)
                                self.play(FadeIn(dot_obj), run_time=duration)
                            elif anim_type == 'fade_out':
                                self.play(FadeOut(dot_obj), run_time=duration)
                            elif anim_type == 'wait':
                                self.wait(duration)
                            else:
                                self.add(dot_obj)
                                self.play(Create(dot_obj), run_time=duration)
                
                objects_created.append(dot_obj)
                self.wait(0.3)
                
            elif obj_type == 'text':
                # Create text annotations
                content = props.get('text', 'Text')
                size = props.get('size', 0.5)
                color_name = props.get('color', 'WHITE')
                pos = props.get('position', [0, 0, 0])
                
                # Color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), WHITE)
                except:
                    color = WHITE
                
                # Convert size to font size
                font_size = int(size * 48)  # Scale factor for readable text
                
                text_obj = Text(
                    content,
                    font_size=font_size,
                    color=color
                )
                text_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    self.add(text_obj)
                    self.play(FadeIn(text_obj), run_time=0.5)
                else:
                    # Process animations with timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 0.5)
                        start_time = anim.get('start_time', 'immediate')
                        
                        if start_time == 'before_next':
                            self.add(text_obj)
                            self.play(FadeIn(text_obj), run_time=0.3)
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(text_obj)
                        elif start_time == 'after_previous_fade':
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            self.wait(0.1)
                            self.add(text_obj)
                            self.play(FadeIn(text_obj), run_time=duration)
                        elif start_time == 'immediate':
                            # Object appears immediately
                            self.add(text_obj)
                            self.play(FadeIn(text_obj), run_time=duration)
                        elif start_time == 'after_persistent_display':
                            # Object appears after persistent objects (axes, plots) are visible
                            # Wait a bit for persistent objects to be fully visible
                            self.wait(0.5)
                            self.add(text_obj)
                            self.play(FadeIn(text_obj), run_time=duration)
                        elif start_time == 'after_previous_transient_fade':
                            # This transient object should fade out before the next transient object
                            self.add(text_obj)
                            self.play(FadeIn(text_obj), run_time=0.3)
                            self.play(FadeOut(text_obj), run_time=0.3)
                        else:
                            # Default animation handling
                            if anim_type == 'fade_in':
                                self.add(text_obj)
                                self.play(FadeIn(text_obj), run_time=duration)
                            elif anim_type == 'fade_out':
                                self.play(FadeOut(text_obj), run_time=duration)
                            elif anim_type == 'wait':
                                self.wait(duration)
                            else:
                                self.add(text_obj)
                                self.play(Create(text_obj), run_time=duration)
                
                objects_created.append(text_obj)
                self.wait(0.3)
                
            elif obj_type == 'triangle':
                # Create triangle geometric shape
                size = props.get('size', 1)
                color_name = props.get('color', 'GREEN')
                pos = props.get('position', [0, 0, 0])
                
                # Color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), GREEN)
                except:
                    color = GREEN
                
                triangle_obj = Triangle(
                        fill_color=color, 
                        stroke_color=color, 
                        fill_opacity=1.0, 
                        stroke_width=3
                    )
                triangle_obj.scale(size)
                triangle_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    self.add(triangle_obj)
                    self.play(Create(triangle_obj), run_time=0.8)
                else:
                    # Process animations with timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 0.8)
                        start_time = anim.get('start_time', 'immediate')
                        
                        if start_time == 'before_next':
                            self.add(triangle_obj)
                            self.play(FadeIn(triangle_obj), run_time=0.3)
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(triangle_obj)
                        elif start_time == 'after_previous_fade':
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            self.wait(0.1)
                            self.add(triangle_obj)
                            self.play(FadeIn(triangle_obj), run_time=duration)
                        elif start_time == 'immediate':
                            # Object appears immediately
                            self.add(triangle_obj)
                            self.play(FadeIn(triangle_obj), run_time=duration)
                        elif start_time == 'after_persistent_display':
                            # Object appears after persistent objects (axes, plots) are visible
                            # Wait a bit for persistent objects to be fully visible
                            self.wait(0.5)
                            self.add(triangle_obj)
                            self.play(FadeIn(triangle_obj), run_time=duration)
                        elif start_time == 'before_next_transient':
                            # This transient object should fade out before the next transient object
                            self.add(triangle_obj)
                            self.play(FadeIn(triangle_obj), run_time=0.3)
                            # Store for fade-out when next transient object appears
                            if not hasattr(self, 'transient_objects_to_fade_out'):
                                self.transient_objects_to_fade_out = []
                            self.transient_objects_to_fade_out.append(triangle_obj)
                        elif start_time == 'after_previous_transient_fade':
                            # This transient object should fade in after the previous transient object fades out
                            if hasattr(self, 'transient_objects_to_fade_out') and self.transient_objects_to_fade_out:
                                prev_obj = self.transient_objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            
                            # Small delay for smooth transition
                            self.wait(0.1)
                            self.add(triangle_obj)
                            self.play(FadeIn(triangle_obj), run_time=duration)
                        else:
                            # Default animation handling
                            if anim_type == 'fade_in':
                                self.add(triangle_obj)
                                self.play(FadeIn(triangle_obj), run_time=duration)
                            elif anim_type == 'fade_out':
                                self.play(FadeOut(triangle_obj), run_time=duration)
                            elif anim_type == 'wait':
                                self.wait(duration)
                            else:
                                self.add(triangle_obj)
                                self.play(Create(triangle_obj), run_time=duration)
                
                objects_created.append(triangle_obj)
                self.wait(0.3)
                
            elif obj_type == 'diamond':
                # Create diamond geometric shape (using square rotated 45 degrees)
                size = props.get('size', 1)
                color_name = props.get('color', 'PURPLE')
                pos = props.get('position', [0, 0, 0])
                
                # Color validation
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {{
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK
                        }}
                        color = color_mapping.get(str(color_name), PURPLE)
                except:
                    color = PURPLE
                
                diamond_obj = Square(
                    side_length=size, 
                    fill_color=color, 
                    stroke_color=color, 
                    fill_opacity=1.0, 
                    stroke_width=3
                )
                diamond_obj.rotate(np.pi/4)  # Rotate 45 degrees
                diamond_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    self.add(diamond_obj)
                    self.play(Create(diamond_obj), run_time=0.8)
                else:
                    # Process animations with timing
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 0.8)
                        start_time = anim.get('start_time', 'immediate')
                        
                        if start_time == 'before_next':
                            self.add(diamond_obj)
                            self.play(FadeIn(diamond_obj), run_time=0.3)
                            if not hasattr(self, 'objects_to_fade_out'):
                                self.objects_to_fade_out = []
                            self.objects_to_fade_out.append(diamond_obj)
                        elif start_time == 'after_previous_fade':
                            if hasattr(self, 'objects_to_fade_out') and self.objects_to_fade_out:
                                prev_obj = self.objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            self.wait(0.1)
                            self.add(diamond_obj)
                            self.play(FadeIn(diamond_obj), run_time=duration)
                        elif start_time == 'immediate':
                            # Object appears immediately
                            self.add(diamond_obj)
                            self.play(FadeIn(diamond_obj), run_time=duration)
                        elif start_time == 'after_persistent_display':
                            # Object appears after persistent objects (axes, plots) are visible
                            # Wait a bit for persistent objects to be fully visible
                            self.wait(0.5)
                            self.add(diamond_obj)
                            self.play(FadeIn(diamond_obj), run_time=duration)
                        elif start_time == 'before_next_transient':
                            # This transient object should fade out before the next transient object
                            self.add(diamond_obj)
                            self.play(FadeIn(diamond_obj), run_time=duration)
                            # Store for fade-out when next transient object appears
                            if not hasattr(self, 'transient_objects_to_fade_out'):
                                self.transient_objects_to_fade_out = []
                            self.transient_objects_to_fade_out.append(diamond_obj)
                        elif start_time == 'after_previous_transient_fade':
                            # This transient object should fade in after the previous transient object fades out
                            if hasattr(self, 'transient_objects_to_fade_out') and self.transient_objects_to_fade_out:
                                prev_obj = self.transient_objects_to_fade_out.pop(0)
                                self.play(FadeOut(prev_obj), run_time=0.3)
                            
                            # Small delay for smooth transition
                            self.wait(0.1)
                            self.add(diamond_obj)
                            self.play(FadeIn(diamond_obj), run_time=duration)
                        else:
                            # Default animation handling
                            if anim_type == 'fade_in':
                                self.add(diamond_obj)
                                self.play(FadeIn(diamond_obj), run_time=duration)
                            elif anim_type == 'fade_out':
                                self.play(FadeOut(diamond_obj), run_time=duration)
                            elif anim_type == 'wait':
                                self.wait(duration)
                            else:
                                self.add(diamond_obj)
                                self.play(Create(diamond_obj), run_time=duration)
                
                objects_created.append(diamond_obj)
                self.wait(0.3)
                
            else:
                # Unknown object type - skip
                print(f"Unknown object type: {{obj_type}} for object {{obj_id}}")
                continue
        
        # Final wait to show all objects
        self.wait(2.0)
        print(f"Animation completed with {{len(objects_created)}} objects")
"""

            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {{e}}")
            raise
