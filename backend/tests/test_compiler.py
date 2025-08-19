from schemas.manim_schema import ManimScene, ManimObject, AnimationStep, AnimationType
from services.manim_compiler import ManimCompiler


def build_sample_scene() -> ManimScene:
    return ManimScene(
        scene_name="GeneratedScene",
        background_color="#101010",
        objects=[
            ManimObject(name="circle", type="circle", props={"radius": 1.5, "color": "RED", "fill_opacity": 0.5}),
            ManimObject(name="line", type="line", props={"start": "LEFT", "end": "RIGHT", "color": "YELLOW"}),
        ],
        animations=[
            AnimationStep(type=AnimationType.CREATE, target="circle", duration=1.2),
            AnimationStep(type=AnimationType.MOVE, target="circle", duration=1.0, parameters={"position": "UP"}),
            AnimationStep(type=AnimationType.WAIT, target="circle", duration=0.5),
        ],
    )


def test_compile_basic_scene():
    scene = build_sample_scene()
    compiler = ManimCompiler()
    code = compiler.compile_to_manim(scene)
    assert "from manim import *" in code
    assert "class GeneratedScene(Scene):" in code
    assert "Circle(" in code
    assert "self.play(Create(circle)" in code


