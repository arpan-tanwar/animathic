from __future__ import annotations

from typing import List

from schemas.manim_schema import ManimScene, ManimObject, AnimationStep, AnimationType


class ManimCompiler:
    def compile_to_manim(self, scene: ManimScene) -> str:
        """Convert a structured ManimScene into executable Python code."""
        lines: List[str] = []

        # Imports
        for imp in scene.imports:
            lines.append(imp)
        lines.append("")

        # Scene class
        lines.append(f"class {scene.scene_name}(Scene):")
        lines.append("    def construct(self):")
        # Background color
        lines.append(f"        self.camera.background_color = \"{scene.background_color}\"")
        lines.append("")

        # Objects
        for obj in scene.objects:
            lines.extend(self._compile_object(obj))

        if scene.objects:
            lines.append("")

        # Animations
        for step in scene.animations:
            lines.extend(self._compile_animation(step))

        # Final wait
        lines.append("        self.wait(2)")

        return "\n".join(lines) + "\n"

    def _compile_object(self, obj: ManimObject) -> List[str]:
        name = obj.name
        t = obj.type
        p = obj.props

        if t == "circle":
            radius = p.get("radius", 1.0)
            color = p.get("color", "BLUE")
            fill_opacity = p.get("fill_opacity", 0.0)
            return [f"        {name} = Circle(radius={radius}, color={color}, fill_opacity={fill_opacity})"]
        if t == "square":
            side = p.get("side_length", 2.0)
            color = p.get("color", "BLUE")
            fill_opacity = p.get("fill_opacity", 0.0)
            return [f"        {name} = Square(side_length={side}, color={color}, fill_opacity={fill_opacity})"]
        if t == "rectangle":
            width = p.get("width", 4.0)
            height = p.get("height", 2.0)
            color = p.get("color", "BLUE")
            fill_opacity = p.get("fill_opacity", 0.0)
            return [f"        {name} = Rectangle(width={width}, height={height}, color={color}, fill_opacity={fill_opacity})"]
        if t == "ellipse":
            width = p.get("width", 4.0)
            height = p.get("height", 2.0)
            color = p.get("color", "BLUE")
            fill_opacity = p.get("fill_opacity", 0.0)
            return [f"        {name} = Ellipse(width={width}, height={height}, color={color}, fill_opacity={fill_opacity})"]
        if t == "triangle":
            color = p.get("color", "BLUE")
            return [f"        {name} = Triangle(color={color})"]
        if t == "text":
            text = p.get("text", "Hello")
            color = p.get("color", "WHITE")
            return [f"        {name} = Text(\"{text}\", color={color})"]
        if t == "line":
            start = p.get("start", "LEFT")
            end = p.get("end", "RIGHT")
            color = p.get("color", "WHITE")
            return [f"        {name} = Line({start}, {end}, color={color})"]
        if t == "dot":
            color = p.get("color", "WHITE")
            return [f"        {name} = Dot(color={color})"]
        if t == "axes":
            x_range = p.get("x_range", "[-3,3,1]")
            y_range = p.get("y_range", "[-2,2,1]")
            return [f"        {name} = Axes(x_range={x_range}, y_range={y_range})"]
        if t == "number_line":
            x_range = p.get("x_range", "[-5,5,1]")
            return [f"        {name} = NumberLine(x_range={x_range})"]
        if t == "graph":
            # Requires an axes object reference 'axes'
            func = p.get("function", "lambda x: x**2")
            axes_ref = p.get("axes", "axes")
            color = p.get("color", "YELLOW")
            return [f"        {name} = {axes_ref}.plot({func}, color={color})"]

        # Fallback unknown objects to a Dot
        return [f"        {name} = Dot()"]

    def _compile_animation(self, step: AnimationStep) -> List[str]:
        t = step.type
        target = step.target
        params = step.parameters or {}
        dur = step.duration

        lines: List[str] = []
        if t == AnimationType.CREATE:
            lines.append(f"        self.play(Create({target}), run_time={dur})")
        elif t == AnimationType.TRANSFORM:
            to_obj = params.get("to", target)
            lines.append(f"        self.play(Transform({target}, {to_obj}), run_time={dur})")
        elif t == AnimationType.MOVE:
            pos = params.get("position", "ORIGIN")
            lines.append(f"        self.play({target}.animate.move_to({pos}), run_time={dur})")
        elif t == AnimationType.ROTATE:
            angle = params.get("angle", "PI/2")
            lines.append(f"        self.play(Rotate({target}, angle={angle}), run_time={dur})")
        elif t == AnimationType.SCALE:
            factor = params.get("factor", 1.0)
            lines.append(f"        self.play({target}.animate.scale({factor}), run_time={dur})")
        elif t == AnimationType.FADE:
            direction = params.get("direction", "in")
            if direction == "in":
                lines.append(f"        self.play(FadeIn({target}), run_time={dur})")
            else:
                lines.append(f"        self.play(FadeOut({target}), run_time={dur})")
        elif t == AnimationType.WAIT:
            lines.append(f"        self.wait({dur})")
        elif t == AnimationType.SET_COLOR:
            color = params.get("color", "WHITE")
            lines.append(f"        {target}.set_color({color})")
        elif t == AnimationType.SET_STROKE:
            color = params.get("color", "WHITE")
            width = params.get("width", 2)
            lines.append(f"        {target}.set_stroke({color}, width={width})")
        elif t == AnimationType.SET_FILL:
            color = params.get("color", "WHITE")
            opacity = params.get("opacity", 0.5)
            lines.append(f"        {target}.set_fill({color}, opacity={opacity})")

        if step.wait_after and step.wait_after > 0:
            lines.append(f"        self.wait({step.wait_after})")

        return lines


