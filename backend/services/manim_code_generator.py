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
        pass

    def generate_manim_code(self, animation_spec: Dict[str, Any]) -> str:
        try:
            scene_description = animation_spec.get("scene_description", "Generated animation")
            bg_color = animation_spec.get("background_color", "#000000")
            objects_list: List[Dict[str, Any]] = animation_spec.get("objects", [])

            try:
                # Determine scene type based on animation spec or content
                scene_type = animation_spec.get("scene_type", "Scene")
                if scene_type == "ThreeDScene":
                    use_3d = True
                    scene_base = "ThreeDScene"
                elif scene_type == "GraphScene":
                    use_3d = False
                    scene_base = "GraphScene"
                elif scene_type == "MovingCameraScene":
                    use_3d = False
                    scene_base = "MovingCameraScene"
                else:
                    # Auto-detect based on content
                    use_3d = any(str(o.get("type", "")).lower() in {"surface", "parametric_surface", "surface3d"} for o in objects_list)
                    scene_base = "ThreeDScene" if use_3d else "Scene"
            except Exception:
                use_3d = False
                scene_base = "Scene"

            parts: List[str] = []
            parts.append("import numpy as np")
            parts.append("from manim import *")
            parts.append("")
            parts.append(f"class GeneratedScene({scene_base}):")
            parts.append("    def construct(self):")
            parts.append(f"        # Animation: {scene_description}")
            parts.append("        bg_color = '" + bg_color + "'")
            parts.append("        try:")
            parts.append("            if bg_color.lower() in ['#ffffff', '#fff', 'white', 'ffffff']:")
            parts.append("                bg_color = '#000000'")
            parts.append("            if bg_color.startswith('#'):")
            parts.append("                self.camera.background_color = rgb_to_color(hex_to_rgb(bg_color))")
            parts.append("            else:")
            parts.append("                self.camera.background_color = rgb_to_color([0, 0, 0])")
            parts.append("        except Exception:")
            parts.append("            self.camera.background_color = rgb_to_color([0, 0, 0])")
            parts.append("")
            parts.append("        try:")
            parts.append("            self.camera.frame.set(width=14, height=10)")
            parts.append("            self.camera.frame.move_to([0, 0, 0])")
            parts.append("        except Exception:")
            parts.append("            pass")
            parts.append("")

            def emit_anims(var_name: str, animations: List[Dict[str, Any]]):
                queue: List[str] = []
                for anim in animations or []:
                    a = str(anim.get('type', 'fade_in')).lower()
                    dur = float(anim.get('duration', 1.0))
                    params = anim.get('parameters', {})
                    group = anim.get('group')

                    if a == 'wait':
                        parts.append(f"        self.wait({dur})")
                    elif a == 'fade_in':
                        if group == 'parallel':
                            queue.append(f"FadeIn({var_name}, run_time={dur})")
                        else:
                            parts.append(f"        self.add({var_name})")
                            parts.append(f"        self.play(FadeIn({var_name}), run_time={dur})")
                    elif a == 'fade_out':
                        if group == 'parallel':
                            queue.append(f"FadeOut({var_name}, run_time={dur})")
                        else:
                            parts.append(f"        self.play(FadeOut({var_name}), run_time={dur})")
                    elif a == 'create':
                        if group == 'parallel':
                            queue.append(f"Create({var_name}, run_time={dur})")
                        else:
                            parts.append(f"        self.play(Create({var_name}), run_time={dur})")
                    elif a == 'write':
                        if group == 'parallel':
                            queue.append(f"Write({var_name}, run_time={dur})")
                        else:
                            parts.append(f"        self.play(Write({var_name}), run_time={dur})")
                    elif a == 'draw_border_then_fill':
                        if group == 'parallel':
                            queue.append(f"DrawBorderThenFill({var_name}, run_time={dur})")
                        else:
                            parts.append(f"        self.play(DrawBorderThenFill({var_name}), run_time={dur})")
                    elif a == 'move':
                        target_pos = params.get('target_position') or params.get('to')
                        if target_pos:
                            if group == 'parallel':
                                queue.append(f"{var_name}.animate.move_to({target_pos}).set_run_time({dur})")
                            else:
                                parts.append(f"        self.play({var_name}.animate.move_to({target_pos}), run_time={dur})")
                    elif a == 'scale':
                        scale_factor = params.get('scale_factor', 1.5)
                        if group == 'parallel':
                            queue.append(f"{var_name}.animate.scale({scale_factor}).set_run_time({dur})")
                        else:
                            parts.append(f"        self.play({var_name}.animate.scale({scale_factor}), run_time={dur})")
                    elif a == 'rotate':
                        angle = params.get('angle', 1.57)  # 90 degrees in radians
                        if group == 'parallel':
                            queue.append(f"{var_name}.animate.rotate({angle}).set_run_time({dur})")
                        else:
                            parts.append(f"        self.play({var_name}.animate.rotate({angle}), run_time={dur})")
                    elif a == 'transform':
                        target_id = params.get('target_id')
                        if target_id:
                            if group == 'parallel':
                                queue.append(f"Transform({var_name}, {target_id}, run_time={dur})")
                            else:
                                parts.append(f"        self.play(Transform({var_name}, {target_id}), run_time={dur})")
                    elif a == 'replacement_transform':
                        target_id = params.get('target_id')
                        if target_id:
                            if group == 'parallel':
                                queue.append(f"ReplacementTransform({var_name}, {target_id}, run_time={dur})")
                            else:
                                parts.append(f"        self.play(ReplacementTransform({var_name}, {target_id}), run_time={dur})")
                    elif a == 'move_along_path':
                        pts = params.get('path_points', [])
                        if pts:
                            parts.append("        path = VMobject()")
                            parts.append(f"        path.set_points_as_corners([np.array([p[0], p[1], (p[2] if len(p)>2 else 0.0)]) for p in {pts}])")
                            if group == 'parallel':
                                queue.append(f"MoveAlongPath({var_name}, path, run_time={dur})")
                            else:
                                parts.append(f"        self.play(MoveAlongPath({var_name}, path), run_time={dur})")
                    elif a == 'grow_from_center':
                        if group == 'parallel':
                            queue.append(f"GrowFromCenter({var_name}, run_time={dur})")
                        else:
                            parts.append(f"        self.play(GrowFromCenter({var_name}), run_time={dur})")
                    elif a == 'grow_from_edge':
                        if group == 'parallel':
                            queue.append(f"GrowFromEdge({var_name}, run_time={dur})")
                        else:
                            parts.append(f"        self.play(GrowFromEdge({var_name}), run_time={dur})")
                    elif a == 'show_creation':
                        if group == 'parallel':
                            queue.append(f"ShowCreation({var_name}, run_time={dur})")
                        else:
                            parts.append(f"        self.play(ShowCreation({var_name}), run_time={dur})")
                    else:
                        # Universal animation handling - try to create any Manim animation
                        anim_name = a.replace('_', '').title()  # Convert snake_case to CamelCase

                        # Try to create the animation dynamically
                        parts.append(f"        try:")
                        parts.append(f"            # Try to create {anim_name} animation")

                        # Handle special animation cases
                        if 'move' in a.lower() and 'path' in a.lower():
                            # MoveAlongPath animation
                            pts = params.get('path_points', [])
                            if pts:
                                parts.append(f"            path = VMobject()")
                                parts.append(f"            path.set_points_as_corners([np.array([p[0], p[1], (p[2] if len(p) > 2 else 0.0)]) for p in {pts}])")
                                if group == 'parallel':
                                    queue.append(f"MoveAlongPath({var_name}, path, run_time={dur})")
                                else:
                                    parts.append(f"            self.play(MoveAlongPath({var_name}, path), run_time={dur})")
                            else:
                                parts.append(f"            # MoveAlongPath requires path_points")
                                parts.append(f"            self.play(FadeIn({var_name}), run_time={dur})")
                        elif 'transform' in a.lower():
                            # Transform animation
                            target_id = params.get('target_id')
                            if target_id:
                                if group == 'parallel':
                                    queue.append(f"Transform({var_name}, {target_id}, run_time={dur})")
                                else:
                                    parts.append(f"            self.play(Transform({var_name}, {target_id}), run_time={dur})")
                            else:
                                parts.append(f"            # Transform requires target_id")
                                parts.append(f"            self.play(FadeIn({var_name}), run_time={dur})")
                        else:
                            # Try to create animation with the given name
                            anim_params = []
                            if params:
                                for key, value in params.items():
                                    if isinstance(value, str):
                                        anim_params.append(f"{key}='{value}'")
                                    elif isinstance(value, list):
                                        anim_params.append(f"{key}={value}")
                                    else:
                                        anim_params.append(f"{key}={value}")

                            param_str = ", ".join(anim_params) if anim_params else ""

                            if group == 'parallel':
                                queue.append(f"{anim_name}({var_name}, run_time={dur}{', ' + param_str if param_str else ''})")
                            else:
                                parts.append(f"            self.play({anim_name}({var_name}, run_time={dur}{', ' + param_str if param_str else ''}))")

                        parts.append(f"        except Exception as anim_e:")
                        parts.append(f"            # Fallback to FadeIn if {anim_name} fails")
                        parts.append(f"            logger.warning(f'Failed to create {anim_name} animation: {{anim_e}}, using fallback')")
                        if group == 'parallel':
                            queue.append(f"FadeIn({var_name}, run_time={dur})")
                        else:
                            parts.append(f"            self.add({var_name})")
                            parts.append(f"            self.play(FadeIn({var_name}), run_time={dur})")

                if queue:
                    parts.append(f"        self.add({var_name})")
                    parts.append(f"        self.play(AnimationGroup({', '.join(queue)}, lag_ratio=0))")

            for obj in objects_list:
                otype = str(obj.get('type', 'unknown')).lower()
                oid = obj.get('id', 'obj')
                props = obj.get('properties', {})
                parts.append(f"        # Object: {otype} ({oid})")

                if otype == 'circle':
                    pos = props.get('position', [0,0,0])
                    r = float(props.get('size', 1.0))
                    color = props.get('color', 'RED')
                    parts.append(f"        circle = Circle(radius={r}, color={color})")
                    parts.append(f"        circle.move_to({pos})")
                    emit_anims('circle', obj.get('animations', []))

                elif otype == 'square':
                    pos = props.get('position', [0,0,0])
                    s = float(props.get('size', 2.0))
                    color = props.get('color', 'BLUE')
                    parts.append(f"        square = Square(side_length={s}, color={color})")
                    parts.append(f"        square.move_to({pos})")
                    emit_anims('square', obj.get('animations', []))

                elif otype == 'dot':
                    pos = props.get('position', [0,0,0])
                    rad = float(props.get('size', 0.08))
                    color = props.get('color', 'WHITE')
                    parts.append(f"        dot = Dot(point={pos}, radius={rad}, color={color})")
                    emit_anims('dot', obj.get('animations', []))

                elif otype == 'text':
                    txt = str(props.get('text', 'Text'))
                    pos = props.get('position', [0,0,0])
                    fs = int(props.get('font_size', 36))
                    parts.append(f"        text = Text(text='{txt}', font_size={fs})")
                    parts.append(f"        text.move_to({pos})")
                    emit_anims('text', obj.get('animations', []))

                elif otype == 'axes':
                    pos = props.get('position', [0,0,0])
                    parts.append("        axes = Axes()")
                    parts.append(f"        axes.move_to({pos})")
                    emit_anims('axes', obj.get('animations', []))

                elif otype == 'polygon':
                    pts = props.get('points', [[-1,0,0],[1,0,0],[0,1,0]])
                    pos = props.get('position', [0,0,0])
                    parts.append(f"        poly = Polygon(*[tuple(p) for p in {pts}], color=BLUE)")
                    parts.append(f"        poly.move_to({pos})")
                    emit_anims('poly', obj.get('animations', []))

                elif otype in {'surface','parametric_surface','surface3d'}:
                    u = props.get('u_range', [-2,2])
                    v = props.get('v_range', [-2,2])
                    pos = props.get('position', [0,0,0])
                    parts.append("        surf = ParametricSurface(lambda u,v: np.array([u, v, 0.5*np.sin(u)*np.cos(v)]), "
                                 f"u_range={u}, v_range={v}, checkerboard_colors=[BLUE_D, BLUE_E])")
                    parts.append(f"        surf.move_to({pos})")
                    emit_anims('surf', obj.get('animations', []))

                elif otype == 'parametric_function':
                    # Handle parametric functions with enhanced support
                    pos = props.get('position', [0,0,0])
                    t_range = props.get('t_range', [0, 2*np.pi])
                    color = props.get('color', 'BLUE')

                    # Default parametric function (circle) with customizable parameters
                    parts.append(f"        func = ParametricFunction(lambda t: np.array([np.cos(t), np.sin(t), 0]), t_range={t_range}, color={color})")
                    parts.append(f"        func.move_to({pos})")
                    emit_anims('func', obj.get('animations', []))

                elif otype == 'matrix':
                    data = props.get('data', [[1,0],[0,1]])
                    pos = props.get('position', [0,0,0])
                    parts.append(f"        m = Matrix({data})")
                    parts.append(f"        m.move_to({pos})")
                    emit_anims('m', obj.get('animations', []))

                elif otype == 'table':
                    data = props.get('data', [["A","B"],["C","D"]])
                    pos = props.get('position', [0,0,0])
                    parts.append(f"        t = Table({data})")
                    parts.append(f"        t.move_to({pos})")
                    emit_anims('t', obj.get('animations', []))

                elif otype in {'valuetracker','value_tracker'}:
                    initial = float(props.get('initial', 0.0))
                    parts.append(f"        vt_{oid} = ValueTracker({initial})")
                else:
                    # Universal object creation - handle any Manim object type
                    position = props.get('position', [0, 0, 0])
                    color = props.get('color', 'WHITE')
                    size = props.get('size', 1.0)

                    # Attempt to create any Manim object dynamically
                    parts.append(f"        # Universal object creation: {otype}")
                    parts.append(f"        try:")
                    parts.append(f"            # Try to create {otype} with intelligent parameter mapping")
                    parts.append(f"            obj_params = {{}}")

                    # Map common properties to constructor parameters based on object type
                    if 'circle' in otype.lower() or 'sphere' in otype.lower():
                        parts.append(f"            obj_params['radius'] = {size}")
                    elif 'square' in otype.lower() or 'rectangle' in otype.lower():
                        parts.append(f"            obj_params['side_length'] = {size}")
                    elif 'dot' in otype.lower():
                        parts.append(f"            obj_params['radius'] = {size}")
                    elif 'text' in otype.lower():
                        text_content = props.get('text', f'{otype} object')
                        parts.append(f"            obj_params['text'] = '{text_content}'")
                        font_size = props.get('font_size', 36)
                        parts.append(f"            obj_params['font_size'] = {font_size}")

                    # Add color if applicable
                    if 'color' in props and otype.lower() not in ['text', 'tex', 'mathtex']:
                        parts.append(f"            obj_params['color'] = '{color}'")

                    # Add any custom properties that aren't position/size/color/animations
                    for key, value in props.items():
                        if key not in ['position', 'size', 'color', 'animations', 'text', 'font_size']:
                            if isinstance(value, str):
                                parts.append(f"            obj_params['{key}'] = '{value}'")
                            elif isinstance(value, list):
                                parts.append(f"            obj_params['{key}'] = {value}")
                            else:
                                parts.append(f"            obj_params['{key}'] = {value}")

                    # Create the object dynamically
                    parts.append(f"            {oid} = {otype}(**obj_params)")
                    parts.append(f"            {oid}.move_to({position})")
                    parts.append(f"            {oid}._animathic_id = '{oid}'")
                    parts.append(f"        except Exception as e:")
                    parts.append(f"            # Fallback to circle if {otype} creation fails")
                    parts.append(f"            logger.warning(f'Failed to create {otype}: {{e}}, using fallback')")
                    parts.append(f"            {oid} = Circle(radius={size}, color='{color}')")
                    parts.append(f"            {oid}.move_to({position})")
                    parts.append(f"            {oid}._animathic_id = '{oid}'")

                    emit_anims(oid, obj.get('animations', []))

            parts.append("        self.wait(2.0)")
            return "\n".join(parts)
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            raise
