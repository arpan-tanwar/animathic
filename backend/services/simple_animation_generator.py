"""
Simple, Robust Animation Generator for Animathic
A streamlined system that creates reliable animations without unnecessary complexity
"""

import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AnimationConfig:
    """Simple configuration for animation generation"""
    default_duration: float = 1.0
    default_color: str = "WHITE"
    camera_width: float = 14.0
    camera_height: float = 10.0
    background_color: str = "#000000"


class SimpleAnimationGenerator:
    """
    A simple, robust animation generator that focuses on reliability over complexity.
    Handles the most common animation patterns with clean, predictable results.
    """

    def __init__(self, config: Optional[AnimationConfig] = None):
        self.config = config or AnimationConfig()

    def generate_animation(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a simple, reliable animation from any prompt.
        This method focuses on understanding intent and creating clean animations.
        """
        try:
            logger.info(f"Generating simple animation for: {prompt[:100]}...")

            # Step 1: Simple prompt analysis
            analysis = self._simple_prompt_analysis(prompt)

            # Step 2: Create basic animation spec
            spec = self._create_basic_spec(analysis)

            # Step 3: Generate clean Manim code
            manim_code = self._generate_clean_code(spec)

            # Step 4: Validate the result
            if self._validate_simple_code(manim_code):
                logger.info("Simple animation generated successfully")
                return {
                    'animation_spec': spec,
                    'manim_code': manim_code,
                    'workflow_type': 'simple',
                    'complexity_analysis': analysis
                }
            else:
                logger.warning("Simple animation validation failed, using minimal fallback")
                return self._generate_minimal_fallback(prompt)

        except Exception as e:
            logger.error(f"Simple animation generation failed: {e}")
            return self._generate_minimal_fallback(prompt)

    def generate_animation_from_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate animation from an existing specification.
        This method takes a pre-created spec and generates the final result.
        """
        try:
            logger.info("Generating animation from existing spec")

            # Generate clean Manim code from spec
            manim_code = self._generate_clean_code(spec)

            # Validate the result
            if self._validate_simple_code(manim_code):
                logger.info("Animation generated from spec successfully")
                return {
                    'animation_spec': spec,
                    'manim_code': manim_code,
                    'workflow_type': 'simple',
                    'complexity_analysis': {'complexity': 'simple'}
                }
            else:
                logger.warning("Animation generation from spec failed, using minimal fallback")
                return self._generate_minimal_fallback("Generated from spec")

        except Exception as e:
            logger.error(f"Animation generation from spec failed: {e}")
            return self._generate_minimal_fallback("Generated from spec")

    def _simple_prompt_analysis(self, prompt: str) -> Dict[str, Any]:
        """Simple, reliable prompt analysis that doesn't overcomplicate things"""
        prompt_lower = prompt.lower()

        # Basic object detection
        objects = []

        # Geometric shapes
        if any(word in prompt_lower for word in ['circle', 'circles']):
            objects.append({'type': 'circle', 'confidence': 0.9})
        if any(word in prompt_lower for word in ['square', 'squares', 'rectangle', 'rectangles']):
            objects.append({'type': 'square', 'confidence': 0.9})
        if any(word in prompt_lower for word in ['triangle', 'triangles']):
            objects.append({'type': 'triangle', 'confidence': 0.8})

        # Text
        if any(word in prompt_lower for word in ['text', 'write', 'say', 'show']):
            objects.append({'type': 'text', 'confidence': 0.8})

        # Mathematical objects
        if any(word in prompt_lower for word in ['function', 'plot', 'graph', 'axis', 'axes']):
            objects.append({'type': 'axes', 'confidence': 0.7})
            objects.append({'type': 'plot', 'confidence': 0.6})

        # Basic animations
        animations = []
        if any(word in prompt_lower for word in ['fade', 'appear', 'show']):
            animations.append('fade_in')
        if any(word in prompt_lower for word in ['move', 'moving']):
            animations.append('move')
        if any(word in prompt_lower for word in ['rotate', 'spin', 'turn']):
            animations.append('rotate')
        if any(word in prompt_lower for word in ['scale', 'grow', 'shrink']):
            animations.append('scale')

        # Determine complexity (very simple scale)
        object_count = len(objects)
        animation_count = len(animations)

        if object_count <= 2 and animation_count <= 2:
            complexity = 'simple'
        elif object_count <= 4 and animation_count <= 3:
            complexity = 'moderate'
        else:
            complexity = 'complex'

        return {
            'objects': objects,
            'animations': animations,
            'complexity': complexity,
            'object_count': object_count,
            'animation_count': animation_count
        }

    def _create_basic_spec(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic, clean animation specification"""
        objects = []
        animations = []

        # Generate objects with simple, reliable positioning
        for i, obj_info in enumerate(analysis['objects']):
            obj_type = obj_info['type']

            # Simple object creation with safe defaults
            obj = {
                'id': f'obj_{i}',
                'type': obj_type,
                'properties': self._get_default_properties(obj_type, i),
                'animations': []
            }

            objects.append(obj)

            # Add simple animations
            for anim_type in analysis['animations']:
                obj['animations'].append({
                    'type': anim_type,
                    'duration': self.config.default_duration,
                    'parameters': {}
                })

        return {
            'scene_description': 'Simple animation',
            'objects': objects,
            'camera_settings': {
                'position': [0, 0, 0],
                'zoom': 8
            },
            'duration': 5,
            'background_color': self.config.background_color,
            'style': 'simple'
        }

    def _get_default_properties(self, obj_type: str, index: int) -> Dict[str, Any]:
        """Get safe default properties for any object type"""
        base_props = {
            'position': [0, 0, 0],
            'color': self.config.default_color
        }

        # Position objects in a simple grid to avoid overlaps
        positions = [
            [0, 0, 0],      # Center
            [-2, 1, 0],     # Top-left
            [2, 1, 0],      # Top-right
            [-2, -1, 0],    # Bottom-left
            [2, -1, 0],     # Bottom-right
            [0, 2, 0],      # Top
            [0, -2, 0],     # Bottom
        ]

        if index < len(positions):
            base_props['position'] = positions[index]

        # Object-specific properties
        if obj_type == 'circle':
            base_props.update({
                'radius': 1.0,
                'color': 'BLUE'
            })
        elif obj_type == 'square':
            base_props.update({
                'side_length': 2.0,
                'color': 'GREEN'
            })
        elif obj_type == 'text':
            base_props.update({
                'text': 'Hello',
                'font_size': 36,
                'color': 'WHITE'
            })
        elif obj_type == 'axes':
            base_props.update({
                'x_range': [-4, 4, 1],
                'y_range': [-3, 3, 1]
            })
        elif obj_type == 'plot':
            base_props.update({
                'function': 'sine',
                'x_range_plot': [-4, 4],
                'color': 'YELLOW'
            })

        return base_props

    def _generate_clean_code(self, spec: Dict[str, Any]) -> str:
        """Generate clean, reliable Manim code with enhanced robustness"""
        objects = spec.get('objects', [])

        code_parts = [
            "import numpy as np",
            "from manim import *",
            "",
            "class GeneratedScene(Scene):",
            "    def construct(self):",
            "        # Simple, clean animation with robust setup",
            "",
            "        # Basic scene setup",
            "        self.camera.background_color = BLACK",
            "",
            "        # Create objects safely"
        ]

        # Generate object creation code
        for obj in objects:
            obj_code = self._generate_simple_object_code(obj)
            code_parts.extend(obj_code)

        # Generate animation code
        anim_code = self._generate_simple_animation_code(objects)
        code_parts.extend(anim_code)

        # Add final wait
        code_parts.append("        self.wait(1.0)")

        return "\n".join(code_parts)

    def _generate_simple_object_code(self, obj: Dict[str, Any]) -> List[str]:
        """Generate simple, reliable object creation code with enhanced safety"""
        obj_id = obj['id']
        obj_type = obj['type']
        props = obj['properties']

        code_lines = []

        try:
            if obj_type == 'circle':
                radius = max(0.1, min(props.get('radius', 1.0), 5.0))  # Safe radius bounds
                color = props.get('color', 'BLUE')
                position = props.get('position', [0, 0, 0])
                code_lines.append(f"        {obj_id} = Circle(radius={radius}, color=\"{color}\")")
                code_lines.append(f"        {obj_id}.move_to({position})")

            elif obj_type == 'square':
                side_length = max(0.5, min(props.get('side_length', 2.0), 4.0))  # Safe size bounds
                color = props.get('color', 'GREEN')
                position = props.get('position', [0, 0, 0])
                code_lines.append(f"        {obj_id} = Square(side_length={side_length}, color=\"{color}\")")
                code_lines.append(f"        {obj_id}.move_to({position})")

            elif obj_type == 'text':
                text = props.get('text', 'Hello').replace('"', '\\"').replace("'", "\\'")[:50]  # Safe text
                font_size = max(24, min(props.get('font_size', 36), 72))  # Safe font size
                color = props.get('color', 'WHITE')
                position = props.get('position', [0, 0, 0])
                code_lines.append(f'        {obj_id} = Text("{text}", font_size={font_size}, color="{color}")')
                code_lines.append(f"        {obj_id}.move_to({position})")

            elif obj_type == 'axes':
                x_range = props.get('x_range', [-4, 4, 1])
                y_range = props.get('y_range', [-3, 3, 1])
                position = props.get('position', [0, 0, 0])
                code_lines.append(f"        {obj_id} = Axes(x_range={x_range}, y_range={y_range})")
                code_lines.append(f"        {obj_id}.move_to({position})")

            elif obj_type == 'plot':
                function = props.get('function', 'sine')
                x_range = props.get('x_range_plot', [-4, 4])
                color = props.get('color', 'YELLOW')
                position = props.get('position', [0, 0, 0])

                # Simple function mapping with safe expressions
                func_map = {
                    'sine': 'lambda x: np.sin(x)',
                    'cosine': 'lambda x: np.cos(x)',
                    'linear': 'lambda x: x'
                }
                lambda_expr = func_map.get(function, 'lambda x: np.sin(x)')

                code_lines.append(f"        {obj_id} = FunctionGraph({lambda_expr}, x_range={x_range}, color=\"{color}\")")
                code_lines.append(f"        {obj_id}.move_to({position})")

            else:
                # Fallback for unknown types - use safe defaults
                position = props.get('position', [0, 0, 0])
                code_lines.append(f"        {obj_id} = Circle(radius=1.0, color=\"WHITE\")")
                code_lines.append(f"        {obj_id}.move_to({position})")

        except Exception as e:
            logger.warning(f"Error generating object code for {obj_type}: {e}")
            # Simple fallback with safe defaults
            position = props.get('position', [0, 0, 0])
            code_lines.append(f"        {obj_id} = Circle(radius=1.0, color=\"WHITE\")")
            code_lines.append(f"        {obj_id}.move_to({position})")

        return code_lines

    def _generate_simple_animation_code(self, objects: List[Dict[str, Any]]) -> List[str]:
        """Generate simple, reliable animation code with enhanced safety"""
        code_lines = ["", "        # Simple animations"]

        for obj in objects:
            obj_id = obj['id']
            animations = obj.get('animations', [])

            for anim in animations:
                anim_type = anim.get('type', 'fade_in')
                duration = max(0.5, min(anim.get('duration', 1.0), 3.0))  # Safe duration bounds

                try:
                    if anim_type == 'fade_in':
                        # FadeIn automatically adds the object to the scene
                        code_lines.append(f"        self.play(FadeIn({obj_id}), run_time={duration})")

                    elif anim_type == 'fade_out':
                        # For fade_out, ensure object is visible first
                        code_lines.append(f"        self.play(FadeOut({obj_id}), run_time={duration})")

                    elif anim_type == 'move':
                        # For move, object should already be in scene
                        current_pos = obj['properties'].get('position', [0, 0, 0])
                        target_pos = [current_pos[0] + 1, current_pos[1] + 1, current_pos[2]]
                        code_lines.append(f"        self.play({obj_id}.animate.move_to({target_pos}), run_time={duration})")

                    elif anim_type == 'rotate':
                        # For rotate, object should already be in scene
                        code_lines.append(f"        self.play({obj_id}.animate.rotate(3.14159), run_time={duration})")

                    elif anim_type == 'scale':
                        # For scale, object should already be in scene
                        code_lines.append(f"        self.play({obj_id}.animate.scale(1.5), run_time={duration})")

                except Exception as e:
                    logger.warning(f"Error generating animation code for {anim_type}: {e}")
                    # Simple fallback animation with safe duration
                    code_lines.append(f"        self.play(FadeIn({obj_id}), run_time=1.0)")

        return code_lines

    def _validate_simple_code(self, code: str) -> bool:
        """Simple validation that doesn't overcomplicate things"""
        try:
            # Basic syntax check
            compile(code, '<string>', 'exec')

            # Check for required components
            required_patterns = [
                'import numpy as np',
                'from manim import',
                'class GeneratedScene',
                'def construct',
                'self.wait'
            ]

            for pattern in required_patterns:
                if pattern not in code:
                    logger.warning(f"Missing required pattern: {pattern}")
                    return False

            return True

        except SyntaxError:
            logger.error("Generated code has syntax errors")
            return False
        except Exception as e:
            logger.error(f"Code validation error: {e}")
            return False

    def _generate_minimal_fallback(self, prompt: str) -> Dict[str, Any]:
        """Generate a minimal, guaranteed-to-work animation"""
        logger.info("Using minimal fallback animation")

        minimal_spec = {
            'scene_description': 'Minimal fallback animation',
            'objects': [{
                'id': 'circle',
                'type': 'circle',
                'properties': {
                    'position': [0, 0, 0],
                    'radius': 1.0,
                    'color': 'BLUE'
                },
                'animations': [{
                    'type': 'fade_in',
                    'duration': 1.0,
                    'parameters': {}
                }]
            }],
            'camera_settings': {'position': [0, 0, 0], 'zoom': 8},
            'duration': 3,
            'background_color': '#000000',
            'style': 'minimal'
        }

        minimal_code = '''import numpy as np
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Minimal fallback animation

        # Camera setup
        self.camera.frame.set(width=14, height=10)
        self.camera.frame.move_to([0, 0, 0])

        # Create a simple circle
        circle = Circle(radius=1.0, color=BLUE)
        circle.move_to([0, 0, 0])

        # Simple animation
        self.add(circle)
        self.play(FadeIn(circle), run_time=1.0)
        self.wait(2.0)
'''

        return {
            'animation_spec': minimal_spec,
            'manim_code': minimal_code,
            'workflow_type': 'fallback',
            'complexity_analysis': {'complexity': 'minimal'}
        }
