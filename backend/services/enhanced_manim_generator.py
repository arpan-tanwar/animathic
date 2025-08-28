"""
Enhanced Manim Code Generator for Animathic
Generates optimized Manim Python code from animation specifications
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional
from services.manim_api_docs import ManimSymbol

logger = logging.getLogger(__name__)


class EnhancedManimCodeGenerator:
    """Enhanced Manim code generator with API validation"""
    
    def __init__(self, manim_docs=None):
        """Initialize the enhanced code generator"""
        self.manim_docs = manim_docs
        logger.info("Enhanced Manim code generator initialized")
    
    def generate_manim_code(self, animation_spec: Dict[str, Any]) -> str:
        """Generate Manim Python code from animation specification"""
        try:
            # Validate the specification
            if not self._validate_specification(animation_spec):
                logger.warning("Invalid specification, using fallback generation")
                return self._generate_fallback_code(animation_spec)
            
            # Generate optimized code
            code = self._generate_optimized_code(animation_spec)
            
            # Post-process the code
            code = self._post_process_code(code)
            
            logger.info("Successfully generated enhanced Manim code")
            return code
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return self._generate_fallback_code(animation_spec)
    
    def _validate_specification(self, spec: Dict[str, Any]) -> bool:
        """Validate the animation specification (relaxed)"""
        try:
            objs = spec.get('objects')
            return isinstance(objs, list)
        except Exception:
            return False
    
    def _generate_optimized_code(self, spec: Dict[str, Any]) -> str:
        """Generate optimized Manim code"""
        scene_type = spec.get('scene_type', 'Scene')
        objects = spec.get('objects', [])
        animations = spec.get('animations', [])

        # Build object registry for animation mapping
        self.object_registry = {}
        for i, obj in enumerate(objects):
            obj_id = obj.get('id', f'obj_{i}')
            self.object_registry[obj_id] = obj

        # For debugging, try a very simple approach first
        if not objects:
            # Generate minimal fallback
            return self._generate_minimal_scene()

        base = '''import numpy as np
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Animation: {description}

        # Set background color
        bg_color = "#000000"
        self.camera.background_color = self._parse_color(bg_color)

        # Enhanced camera management
        self._setup_camera()

        # Create all objects
        %%OBJECTS_CODE%%

        # Auto-layout texts to avoid overlap
        self._layout_texts(objects_created)

        # Execute animations (stabilized sequencing)
        %%ANIMATIONS_CODE%%

    def _parse_color(self, color_str):
        """Parse color string to Manim color"""
        try:
            if color_str.startswith('#'):
                rgb_values = self._hex_to_rgb(color_str)
                return rgb_to_color(rgb_values)
            else:
                color_mapping = {{
                    'white': rgb_to_color([1, 1, 1]), 'black': rgb_to_color([0, 0, 0]),
                    'red': rgb_to_color([1, 0, 0]), 'green': rgb_to_color([0, 1, 0]),
                    'blue': rgb_to_color([0, 0, 1]), 'yellow': rgb_to_color([1, 1, 0])
                }}
                return color_mapping.get(color_str.lower(), rgb_to_color([0, 0, 0]))
        except Exception:
            return rgb_to_color([0, 0, 0])

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]

    def _setup_camera(self):
        """Setup camera with optimal settings"""
        try:
            self.camera.frame.set(width=14, height=10)
            self.camera.frame.move_to([0, 0, 0])
            self.camera.frame.set(x_range=[-7, 7], y_range=[-5, 5])
            print("Camera positioning: Applied - centered at (0,0) with 14x10 dimensions")
        except Exception as e:
            print(f"Camera positioning failed: {{e}}")

    def _layout_texts(self, objects_created):
        """Arrange text objects to avoid overlap and improve readability"""
        try:
            texts = [m for m in objects_created if isinstance(m, Text)]
            if len(texts) >= 2:
                # Check if this looks like a typography animation (letters with different x positions)
                x_positions = [text.get_center()[0] for text in texts]
                min_x, max_x = min(x_positions), max(x_positions)

                # If letters are already spread out horizontally (span > 1.0), preserve typography positioning
                if max_x - min_x > 1.0:
                    # This looks like typography - only adjust vertical positioning if severely overlapping
                    y_positions = [text.get_center()[1] for text in texts]
                    min_y, max_y = min(y_positions), max(y_positions)

                    # If vertical span is too small, add some vertical spacing
                    if max_y - min_y < 0.5:
                        for i, text in enumerate(texts):
                            text.shift([0, i * 0.3, 0])  # Add vertical spacing
                else:
                    # Not typography - apply standard vertical layout
                    VGroup(*texts).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(LEFT, buff=0.5)
        except Exception:
            pass
'''

        # Safe description text
        description = spec.get('description', 'Generated animation')
        template = base.replace('{description}', description)
        template = template.replace('%%OBJECTS_CODE%%', self._generate_objects_code(objects))

        # Replace animation code placeholder
        animation_code = self._generate_animations_code(objects, animations)
        template = template.replace('%%ANIMATIONS_CODE%%', animation_code)

        return template

    def _generate_minimal_scene(self) -> str:
        """Generate a minimal working scene for testing"""
        return '''import numpy as np
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Minimal test scene
        circle = Circle(radius=1, color=BLUE)
        self.add(circle)
        self.play(Create(circle), run_time=1)
        self.wait(1)
'''

    def _generate_objects_code(self, objects: List[Dict]) -> str:
        """Generate code for object creation"""
        if not objects:
            return "objects_created = []"
        
        code = "objects_created = []\n        \n        # Process each object\n"
        
        for i, obj in enumerate(objects):
            obj_type = obj.get('type', 'unknown')
            obj_id = obj.get('id', f'obj_{i}')
            props = obj.get('properties', {})
            obj_anims = obj.get('animations', [])
            
            # Clamp common numeric props
            def _clamp(v, lo, hi, dv):
                try:
                    x = float(v)
                    if not np.isfinite(x):
                        return dv
                    return max(lo, min(hi, x))
                except Exception:
                    return dv
            
            if obj_type.lower() == 'circle':
                raw_radius = props.get('size', 1)
                radius = _clamp(raw_radius, 0.1, 3.5, 1.0)
                color = props.get('color', 'WHITE')
                position = props.get('position', [0, 0, 0])
                code += f"""        # Create circle geometric shape (clamped size)
        {obj_id} = Circle(radius={radius}, color={color}, stroke_width=3)
        print(f"DEBUG: Generating move_to for {obj_id} with position {position}")
        {obj_id}.move_to([{position[0]}, {position[1]}, {position[2]}])
        self.add({obj_id})
        objects_created.append({obj_id})
"""
            elif obj_type.lower() == 'text':
                content = props.get('text', 'Text')
                color = props.get('color', 'WHITE')
                font_size = int(_clamp(props.get('font_size', 36), 18, 64, 36))
                position = props.get('position', [0, 0, 0])
                code += f"""        # Create text object (z-indexed)
        {obj_id} = Text(""" + repr(content) + f""", color={color}, font_size={font_size})
        print(f"DEBUG: Generating move_to for {obj_id} with position {position}")
        {obj_id}.move_to([{position[0]}, {position[1]}, {position[2]}])
        {obj_id}.set_z_index(10)
        self.add({obj_id})
        objects_created.append({obj_id})
"""
            elif obj_type.lower() == 'axes':
                x_range = props.get('x_range', [-4, 4, 1])
                y_range = props.get('y_range', [-3, 3, 1])
                position = props.get('position', [0, 0, 0])
                color = props.get('color', 'WHITE')
                code += f"""        # Create coordinate axes
        {obj_id} = Axes(x_range={x_range}, y_range={y_range}, axis_config={{"color": {color}}}, tips=True)
        print(f"DEBUG: Generating move_to for {obj_id} with position {position}")
        {obj_id}.move_to([{position[0]}, {position[1]}, {position[2]}])
        self.add({obj_id})
        objects_created.append({obj_id})
"""
            elif obj_type.lower() == 'triangle':
                size = float(props.get('size', 1.0))
                color = props.get('color', 'WHITE')
                position = props.get('position', [0, 0, 0])
                # Create a simple triangle polygon around origin then move
                p1 = [-size, -size, 0]
                p2 = [ size, -size, 0]
                p3 = [ 0,    size, 0]
                code += f"""        # Create triangle polygon
        {obj_id} = Polygon({tuple(p1)}, {tuple(p2)}, {tuple(p3)}, color={color})
        print(f"DEBUG: Generating move_to for {obj_id} with position {position}")
        {obj_id}.move_to([{position[0]}, {position[1]}, {position[2]}])
        self.add({obj_id})
        objects_created.append({obj_id})
"""
            elif obj_type.lower() == 'square':
                size = float(props.get('size', 1.0))
                color = props.get('color', 'WHITE')
                position = props.get('position', [0, 0, 0])
                code += f"""        # Create square
        {obj_id} = Square(side_length={size * 2}, color={color}, stroke_width=3)
        print(f"DEBUG: Generating move_to for {obj_id} with position {position}")
        {obj_id}.move_to([{position[0]}, {position[1]}, {position[2]}])
        self.add({obj_id})
        objects_created.append({obj_id})
"""
            elif obj_type.lower() == 'matrix':
                data = props.get('data', [[1,0],[0,1]])
                position = props.get('position', [0, 0, 0])
                code += f"""        # Create matrix object
        {obj_id} = Matrix({data})
        print(f"DEBUG: Generating move_to for {obj_id} with position {position}")
        {obj_id}.move_to([{position[0]}, {position[1]}, {position[2]}])
        self.add({obj_id})
        objects_created.append({obj_id})
"""
            else:
                # Generic fallback object (non-intrusive dot)
                position = props.get('position', [0, 0, 0])
                code += f"""        # Create generic fallback object (Dot)
        {obj_id} = Dot(color=WHITE, radius=0.06)
        print(f"DEBUG: Generating move_to for {obj_id} with position {position}")
        {obj_id}.move_to([{position[0]}, {position[1]}, {position[2]}])
        self.add({obj_id})
        objects_created.append({obj_id})
"""

        return code

    def _generate_animations_code(self, objects: List[Dict], animations: List[Dict]) -> str:
        """Generate code for animations with stabilized sequencing and easing"""
        if not animations:
            # If no global animations, generate per-object animations
            return self._generate_object_animations(objects)

        # Build animation expressions with reduced flicker
        lines: List[str] = []
        lines.append("anims = []")

        for anim in animations:
            anim_type = anim.get('type', 'Create')
            obj_id = anim.get('object_id', anim.get('target', 'objects_created[0]'))
            duration = max(0.8, float(anim.get('duration', 1.0)))
            params = anim.get('parameters', {})

            # Find the actual object variable name
            obj_var_name = self._get_object_variable_name(obj_id, objects)
            if not obj_var_name:
                continue

            # Map 'move' and 'MoveAlongPath'
            if str(anim_type).lower() == 'move':
                target = params.get('target_position') or params.get('to') or params.get('position')
                if target is not None:
                    lines.append(f"        anims.append(ApplyMethod({obj_var_name}.move_to, {target}, rate_func=smooth, run_time={duration}))")
                continue

            if anim_type in ('MoveAlongPath', 'move_along_path'):
                path_points = params.get('path_points') or anim.get('path_points') or []
                if path_points:
                    lines.append(f"        _path = VMobject()")
                    lines.append(f"        _path.set_points_as_corners([np.array([p[0], p[1], (p[2] if len(p)>2 else 0.0)]) for p in {path_points}])")
                    lines.append(f"        anims.append(MoveAlongPath({obj_var_name}, _path, rate_func=smooth, run_time={duration}))")
                continue

            # Map FadeIn to Create for non-text; Use Write for Text
            lines.append(f"        if isinstance({obj_var_name}, Text):")
            if anim_type in ['FadeIn', 'Create', 'Write']:
                lines.append(f"            anims.append(Write({obj_var_name}, rate_func=smooth, run_time={duration}))")
            elif anim_type == 'FadeOut':
                lines.append(f"            anims.append(FadeOut({obj_var_name}, rate_func=smooth, run_time=max(0.5, {duration} - 0.3)))")
            else:
                lines.append(f"            anims.append({anim_type}({obj_var_name}, rate_func=smooth, run_time={duration}))")
            lines.append("        else:")
            if anim_type == 'FadeIn':
                lines.append(f"            anims.append(Create({obj_var_name}, rate_func=smooth, run_time={duration}))")
            elif anim_type == 'FadeOut':
                lines.append(f"            anims.append(FadeOut({obj_var_name}, rate_func=smooth, run_time=max(0.5, {duration} - 0.3)))")
            else:
                lines.append(f"            anims.append({anim_type}({obj_var_name}, rate_func=smooth, run_time={duration}))")

        # Play animations in sequence to avoid temporal overlap flicker
        if lines and len(lines) > 1:
            lines.append("        self.play(Succession(*anims))")
            lines.append("        self.wait(0.5)")

        return "\n".join(lines) if lines else "        self.wait(1)"

    def _get_object_variable_name(self, obj_id: str, objects: List[Dict]) -> Optional[str]:
        """Get the variable name for an object ID"""
        for i, obj in enumerate(objects):
            if obj.get('id') == obj_id:
                return obj.get('id', f'obj_{i}')
        return None

    def _generate_object_animations(self, objects: List[Dict]) -> str:
        """Generate animations based on per-object animation specs"""
        lines: List[str] = []

        for i, obj in enumerate(objects):
            obj_id = obj.get('id', f'obj_{i}')
            obj_anims = obj.get('animations', [])

            if not obj_anims:
                continue

            for anim in obj_anims:
                anim_type = anim.get('type', 'fade_in')
                duration = max(0.8, float(anim.get('duration', 1.0)))

                # Generate appropriate animation based on object type and animation type
                if str(anim_type).lower() in ['fade_in', 'appear', 'create']:
                    lines.append(f"        self.play(Create({obj_id}), run_time={duration})")
                elif str(anim_type).lower() in ['write']:
                    lines.append(f"        self.play(Write({obj_id}), run_time={duration})")
                elif str(anim_type).lower() in ['fade_out', 'disappear']:
                    lines.append(f"        self.play(FadeOut({obj_id}), run_time={duration})")
                elif str(anim_type).lower() == 'wait':
                    lines.append(f"        self.wait({duration})")

        if not lines:
            return "        self.wait(1)"

        return "\n".join(lines)

    def _post_process_code(self, code: str) -> str:
        """Post-process the generated code"""
        # Remove extra whitespace
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.strip():
                cleaned_lines.append(line)
            else:
                cleaned_lines.append('')
        
        return '\n'.join(cleaned_lines)

    def _generate_fallback_code(self, spec: Dict[str, Any]) -> str:
        """Generate fallback Manim code (non-intrusive, no fade-out)"""
        return """import numpy as np
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Fallback animation generation
        circle = Circle(color=WHITE, stroke_width=3)
        self.add(circle)
        self.play(Create(circle), rate_func=smooth, run_time=1.0)
        self.wait(1)
"""
