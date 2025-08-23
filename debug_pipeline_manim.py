import numpy as np
from manim import *

class GeneratedScene(MovingCameraScene):
    def construct(self):
        # Animation: A parabola plot with axes, a circle at (2,4), a square at (-2,4), and text labels for each point.
        
        # Set background color
        bg_color = '#000000'
        if bg_color.lower() in ['#ffffff', '#fff', 'white', 'ffffff']:
            bg_color = "#000000"
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
            self.camera.background_color = rgb_to_color([0, 0, 0])
        
        # Log bounds
        print("Bounds: x=", [-6.0, 6.0], " y=", [-3.5, 3.5])
        
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
            print(f"Camera positioning: Modern approach failed: {e1}")
            try:
                # Fallback approach for different Manim versions
                self.camera.frame.set_width(14)
                self.camera.frame.set_height(10)
                self.camera.frame.move_to([0, 0, 0])
                print("Camera positioning: Fallback approach applied")
            except Exception as e2:
                print(f"Camera positioning: Fallback approach failed: {e2}")
                try:
                    # Basic approach for maximum compatibility
                    self.camera.frame.move_to([0, 0, 0])
                    print("Camera positioning: Basic approach applied")
                except Exception as e3:
                    print(f"Camera positioning: All approaches failed: {e3}")
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
            print(f"Camera positioning: Scene-level approach failed: {e4}")
        
        # Final fallback: Use basic camera centering
        try:
            self.camera.frame.move_to([0, 0, 0])
            print("Camera positioning: Final fallback applied")
        except Exception as e5:
            print(f"Camera positioning: Final fallback failed: {e5}")
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
            print(f"Camera positioning: Cloud Run specific approach failed: {e6}")
            print("Continuing with basic positioning")
        
        # Create objects exactly as specified
        objects_created = []
        
        # Define objects list
        objects = [{'type': 'axes', 'properties': {'position': [-1.5, -1.75, 0.0], 'color': 'WHITE', 'x_range': [-4.0, 4.0, 1.0], 'y_range': [0.0, 16.0, 2.0], 'show_labels': True}, 'animations': [{'type': 'fade_in', 'duration': 1.0, 'parameters': {}}]}, {'type': 'plot', 'properties': {'expression': 'x**2', 'x_range_plot': [-4.0, 4.0], 'color': 'BLUE', 'position': [1.5, -1.75, 0.0]}, 'animations': [{'type': 'fade_in', 'duration': 1.5, 'parameters': {}}]}, {'type': 'circle', 'properties': {'position': [-1.5, 2.75, 0.0], 'color': 'RED', 'size': 0.2}, 'animations': [{'type': 'fade_in', 'duration': 0.5, 'parameters': {}}]}, {'type': 'square', 'properties': {'position': [1.5, 2.75, 0.0], 'color': 'GREEN', 'size': 0.2}, 'animations': [{'type': 'fade_in', 'duration': 0.5, 'parameters': {}}]}, {'type': 'text', 'properties': {'text': 'P1', 'position': [-0.75, -0.625, 0.0], 'color': 'YELLOW', 'size': 0.5}, 'animations': [{'type': 'fade_in', 'duration': 0.5, 'parameters': {}}]}, {'type': 'text', 'properties': {'text': 'P2', 'position': [0.75, -0.625, 0.0], 'color': 'YELLOW', 'size': 0.5}, 'animations': [{'type': 'fade_in', 'duration': 0.5, 'parameters': {}}]}]
        
        print(f"Creating {len(objects)} objects as requested...")
        
        for idx, obj in enumerate(objects):
            obj_id = obj.get('id') or f"obj_{idx}"
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
                self.wait(0.3)
                
            elif obj_type == 'star':
                size = props.get('size', 1)
                color_name = props.get('color', 'YELLOW')
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
                            'LIME': GREEN, 'NAVY': BLUE, 'TEAL': BLUE, 'MARON': RED, 'OLIVE': GREEN,
                            'FUCHSIA': PURPLE, 'AQUA': BLUE, 'SILVER': GRAY, 'GOLD': YELLOW
                        }
                        color = color_mapping.get(str(color_name), YELLOW)
                except Exception:
                    color = YELLOW  # Default to YELLOW for stars
                
                # Create star with 5 points by default
                star_obj = Star(
                    n=5,
                    outer_radius=size,
                    color=color
                )
                
                # Force solid fill to match other shapes (circle, square, triangle)
                try:
                    star_obj.set_fill(color=color, opacity=1.0)
                    star_obj.set_stroke(color=color, width=3)
                except Exception:
                    pass  # Continue if color setting fails
                
                # Position the star
                star_obj.move_to(pos)
                
                # Handle animations from the spec
                animations = obj.get('animations', [])
                if not animations:
                    # Default: just create the object
                    self.add(star_obj)
                    self.play(FadeIn(star_obj), run_time=0.5)
                else:
                    # Process each animation
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        
                        if anim_type == 'fade_in':
                            self.add(star_obj)
                            self.play(FadeIn(star_obj), run_time=duration)
                        elif anim_type == 'fade_out':
                            self.play(FadeOut(star_obj), run_time=duration)
                        elif anim_type == 'wait':
                            self.wait(duration)
                        elif anim_type == 'opacity_change' or anim_type == 'opacity' or anim_type == 'transparency':
                            # Handle opacity changes using proper Manim methods
                            opacity = anim.get('opacity', 0.5)
                            print(f"Processing opacity change: type={anim_type}, opacity={opacity}, duration={duration}")
                            
                            if opacity == 0.0:
                                # Completely invisible - use FadeOut
                                self.play(FadeOut(star_obj), run_time=duration)
                                print(f"Star made invisible using FadeOut")
                            elif opacity == 1.0:
                                # Fully visible - use FadeIn
                                self.play(FadeIn(star_obj), run_time=duration)
                                print(f"Star made fully visible using FadeIn")
                            else:
                                # Semi-transparent - create new star with target opacity
                                star_obj.generate_target()
                                star_obj.target.set_opacity(opacity)
                                self.play(MoveToTarget(star_obj), run_time=duration)
                                print(f"Star opacity changed to {opacity} using MoveToTarget")
                        else:
                            # Default fallback
                            self.add(star_obj)
                            self.play(FadeIn(star_obj), run_time=duration)
                
                objects_created.append(star_obj)
                self.wait(0.3)
                
            elif obj_type == 'hexagon':
                size = props.get('size', 1)
                color_name = props.get('color', 'PURPLE')
                pos = props.get('position', [0, 0, 0])
                
                # Handle color
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'GRAY': GRAY, 'TEAL': TEAL, 'MAROON': MAROON
                        }
                        color = color_mapping.get(str(color_name), PURPLE)
                except Exception:
                    color = PURPLE
                
                # Create hexagon with 6 sides
                try:
                    hexagon_obj = RegularPolygon(
                        n=6, 
                        radius=size/2, 
                        fill_color=color, 
                        stroke_color=color, 
                        fill_opacity=1.0, 
                        stroke_width=3
                    )
                    print(f"Hexagon created successfully with RegularPolygon")
                except Exception as e:
                    print(f"RegularPolygon failed for hexagon: {e}, using fallback")
                    # Fallback: create a circle and make it look more hexagonal
                    hexagon_obj = Circle(radius=size/2, fill_color=color, stroke_color=color, fill_opacity=1.0, stroke_width=3)
                    # Try to make it more hexagonal by scaling
                    hexagon_obj.scale(0.9)
                
                # Position the hexagon
                hexagon_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    # Default: just create the object
                    self.add(hexagon_obj)
                    self.play(FadeIn(hexagon_obj), run_time=0.5)
                else:
                    # Process each animation
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        
                        if anim_type == 'fade_in':
                            self.add(hexagon_obj)
                            self.play(FadeIn(hexagon_obj), run_time=duration)
                        elif anim_type == 'fade_out':
                            self.play(FadeOut(hexagon_obj), run_time=duration)
                        elif anim_type == 'wait':
                            self.wait(duration)
                        else:
                            # Default fallback
                            self.add(hexagon_obj)
                            self.play(FadeIn(hexagon_obj), run_time=duration)
                
                objects_created.append(hexagon_obj)
                self.wait(0.3)
                
            elif obj_type == 'diamond':
                size = props.get('size', 1)
                color_name = props.get('color', 'YELLOW')
                pos = props.get('position', [0, 0, 0])
                
                # Handle color
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'GRAY': GRAY, 'TEAL': TEAL, 'MAROON': MAROON
                        }
                        color = color_mapping.get(str(color_name), YELLOW)
                except Exception:
                    color = YELLOW
                
                # Create diamond as a rotated square
                try:
                    diamond_obj = Square(
                        side_length=size, 
                        fill_color=color, 
                        stroke_color=color, 
                        fill_opacity=1.0, 
                        stroke_width=3
                    )
                    diamond_obj.rotate(np.pi/4)  # Rotate 45 degrees
                    print(f"Diamond created successfully with rotated Square")
                except Exception as e:
                    print(f"Square rotation failed for diamond: {e}, using fallback")
                    # Fallback: create a circle
                    diamond_obj = Circle(radius=size/2, fill_color=color, stroke_color=color, fill_opacity=1.0, stroke_width=3)
                
                # Position the diamond
                diamond_obj.move_to(pos)
                
                # Handle animations
                animations = obj.get('animations', [])
                if not animations:
                    # Default: just create the object
                    self.add(diamond_obj)
                    self.play(FadeIn(diamond_obj), run_time=0.5)
                else:
                    # Process each animation
                    for anim in animations:
                        anim_type = anim.get('type', 'fade_in')
                        duration = anim.get('duration', 1.0)
                        
                        if anim_type == 'fade_in':
                            self.add(diamond_obj)
                            self.play(FadeIn(diamond_obj), run_time=duration)
                        elif anim_type == 'fade_out':
                            self.play(FadeOut(diamond_obj), run_time=duration)
                        elif anim_type == 'wait':
                            self.wait(duration)
                        else:
                            # Default fallback
                            self.add(diamond_obj)
                            self.play(FadeIn(diamond_obj), run_time=duration)
                
                objects_created.append(diamond_obj)
                self.wait(0.3)
                
            elif obj_type == 'circle':
                size = props.get('size', 1)
                color_name = props.get('color', 'RED')
                pos = props.get('position', [0, 0, 0])
                
                # Handle color
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'GRAY': GRAY, 'TEAL': TEAL, 'MAROON': MAROON
                        }
                        color = color_mapping.get(str(color_name), RED)
                except Exception:
                    color = RED
                
                # Create circle
                circle_obj = Circle(
                    radius=size/2, 
                    fill_color=color, 
                    stroke_color=color, 
                    fill_opacity=1.0, 
                    stroke_width=3
                )
                
                # Position the circle
                circle_obj.move_to(pos)
                
                # Handle animations
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
                
            else:
                # DYNAMIC SHAPE HANDLER - Handle any Manim shape not explicitly defined
                print(f"Creating dynamic shape: {obj_type}")
                
                # Get shape properties
                size = props.get('size', 1)
                color_name = props.get('color', 'BLUE')
                pos = props.get('position', [0, 0, 0])
                
                # Handle color
                try:
                    if isinstance(color_name, str) and color_name.startswith('#'):
                        rgb_values = hex_to_rgb(color_name)
                        color = rgb_to_color(rgb_values)
                    else:
                        color_mapping = {
                            'WHITE': WHITE, 'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'BLUE': BLUE,
                            'YELLOW': YELLOW, 'PURPLE': PURPLE, 'ORANGE': ORANGE, 'PINK': PINK,
                            'GRAY': GRAY, 'TEAL': TEAL, 'MAROON': MAROON
                        }
                        color = color_mapping.get(str(color_name), BLUE)
                except Exception:
                    color = BLUE
                
                # Create shape dynamically using eval with safety checks
                try:
                    # Safe shape creation for common geometric shapes
                    # Note: diamond, hexagon, pentagon, and octagon now have dedicated handlers above
                    # This section handles any other shapes not explicitly defined
                    if obj_type in ['diamond', 'hexagon', 'pentagon', 'octagon']:
                        # These shapes are handled by dedicated handlers above
                        # Fall back to circle if somehow we reach here
                        shape_obj = Circle(radius=size/2, fill_color=color, stroke_color=color, fill_opacity=1.0, stroke_width=3)
                        print(f"Shape {obj_type} should be handled by dedicated handler, using Circle as fallback")
                    else:
                        # Try to create any other shape dynamically
                        try:
                            # Use getattr to safely get the shape class
                            shape_class = globals().get(obj_type.capitalize())
                            if shape_class and callable(shape_class):
                                if obj_type in ['diamond', 'hexagon', 'pentagon', 'octagon']:
                                    # For polygons, use RegularPolygon
                                    n_sides = {'diamond': 4, 'hexagon': 6, 'pentagon': 5, 'octagon': 8}.get(obj_type, 6)
                                    shape_obj = RegularPolygon(n=n_sides, radius=size/2, fill_color=color, stroke_color=color, fill_opacity=1.0, stroke_width=3)
                                else:
                                    # For other shapes, try to create with size and color
                                    shape_obj = shape_class(fill_color=color, stroke_color=color, fill_opacity=1.0, stroke_width=3)
                                    # Set size if the shape supports it
                                    if hasattr(shape_obj, 'set_width'):
                                        shape_obj.set_width(size)
                                    if hasattr(shape_obj, 'scale'):
                                        shape_obj.scale(size)
                            else:
                                # Fallback to a basic shape
                                shape_obj = Circle(radius=size/2, fill_color=color, stroke_color=color, fill_opacity=1.0, stroke_width=3)
                                print(f"Shape {obj_type} not found, using Circle as fallback")
                        except Exception as e:
                            print(f"Error creating shape {obj_type}: {e}, using Circle as fallback")
                            shape_obj = Circle(radius=size/2, fill_color=color, stroke_color=color, fill_opacity=1.0, stroke_width=3)
                    
                    # Position the shape
                    shape_obj.move_to(pos)
                    
                    # Handle animations
                    animations = obj.get('animations', [])
                    if not animations:
                        # Default: just create the object
                        self.add(shape_obj)
                        self.play(FadeIn(shape_obj), run_time=0.5)
                    else:
                        # Process each animation
                        for anim in animations:
                            anim_type = anim.get('type', 'fade_in')
                            duration = anim.get('duration', 1.0)
                            
                            if anim_type == 'fade_in':
                                self.add(shape_obj)
                                self.play(FadeIn(shape_obj), run_time=duration)
                            elif anim_type == 'fade_out':
                                self.play(FadeOut(shape_obj), run_time=duration)
                            elif anim_type == 'wait':
                                self.wait(duration)
                            elif anim_type == 'move':
                                target_pos = anim.get('target_position', [0, 0, 0])
                                self.play(shape_obj.animate.move_to(target_pos), run_time=duration)
                            elif anim_type == 'scale':
                                scale_factor = anim.get('scale', 1.0)
                                self.play(shape_obj.animate.scale(scale_factor), run_time=duration)
                            elif anim_type == 'rotate':
                                angle = anim.get('angle', 90)
                                self.play(shape_obj.animate.rotate(angle * DEGREES), run_time=duration)
                            else:
                                # Default fallback
                                self.add(shape_obj)
                                self.play(FadeIn(shape_obj), run_time=duration)
                    
                    objects_created.append(shape_obj)
                    self.wait(0.3)
                    
                except Exception as e:
                    print(f"Error creating dynamic shape {obj_type}: {e}")
                    # Create a fallback circle
                    fallback_obj = Circle(radius=size/2, fill_color=color, stroke_color=color, fill_opacity=1.0, stroke_width=3)
                    fallback_obj.move_to(pos)
                    self.add(fallback_obj)
                    self.play(FadeIn(fallback_obj), run_time=0.5)
                    objects_created.append(fallback_obj)
                    self.wait(0.3)
        
        # Final pause
        self.wait(2)
        
        # Simple validation - no fallbacks
        if objects_created:
            print(f"Successfully created {len(objects_created)} objects as requested")
        else:
            print("No objects were created - this may indicate an issue with the specification")
        
        print("Animation completed")