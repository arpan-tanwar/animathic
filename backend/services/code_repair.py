from __future__ import annotations

import ast
import subprocess
import tempfile
from typing import Tuple

from schemas.manim_schema import ManimScene, AnimationStep, AnimationType, ManimObject
from services.manim_compiler import ManimCompiler


class CodeRepairService:
    """
    Automated repair loop working on the structured scene first, then the compiled code.
    Keeps everything local and free-tier friendly.
    """

    def __init__(self, max_attempts: int = 3) -> None:
        self.max_attempts = max_attempts
        self.compiler = ManimCompiler()

    def repair_and_compile(self, scene: ManimScene) -> Tuple[str, ManimScene]:
        current = scene
        for attempt in range(self.max_attempts):
            code = self.compiler.compile_to_manim(current)
            if self._passes_ast(code) and self._py_compiles(code):
                return code, current
            # Structured-level simplifications per attempt
            current = self._simplify_scene(current, attempt)
        # Final attempt just return latest compile
        return self.compiler.compile_to_manim(current), current

    def _passes_ast(self, code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except Exception:
            return False

    def _py_compiles(self, code: str) -> bool:
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:
                f.write(code)
                f.flush()
                proc = subprocess.run(
                    ["python", "-m", "py_compile", f.name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return proc.returncode == 0
        except Exception:
            return False

    def _simplify_scene(self, scene: ManimScene, attempt: int) -> ManimScene:
        # Make a shallow copy manipulating lists
        scene = ManimScene.model_validate(scene.model_dump())
        if attempt == 0:
            # Keep only first few animations
            scene.animations = scene.animations[:3]
        elif attempt == 1:
            # Use basic primitives only
            scene.objects = [o for o in scene.objects if o.type in {"circle", "square", "text", "line", "dot"}]
            scene.animations = [a for a in scene.animations if a.type in {AnimationType.CREATE, AnimationType.MOVE, AnimationType.WAIT}]
            # Ensure at least one object
            if not scene.objects:
                scene.objects = [ManimObject(name="obj", type="circle", props={"radius": 1.0, "color": "BLUE"})]
                scene.animations = [AnimationStep(type=AnimationType.CREATE, target="obj", duration=1.0)]
        else:
            # Minimal working scene
            scene.objects = [ManimObject(name="obj", type="circle", props={"radius": 1.0, "color": "BLUE"})]
            scene.animations = [AnimationStep(type=AnimationType.CREATE, target="obj", duration=1.0)]
        return scene


