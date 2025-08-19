from schemas.manim_schema import ManimScene, ManimObject, AnimationStep, AnimationType
from services.manim_compiler import ManimCompiler


def test_transform_rotate_scale():
    scene = ManimScene(
        scene_name="EdgeScene",
        objects=[
            ManimObject(name="a", type="circle", props={}),
            ManimObject(name="b", type="square", props={"side_length": 2}),
        ],
        animations=[
            AnimationStep(type=AnimationType.TRANSFORM, target="a", duration=1.0, parameters={"to": "b"}),
            AnimationStep(type=AnimationType.ROTATE, target="a", duration=0.5, parameters={"angle": "PI/3"}),
            AnimationStep(type=AnimationType.SCALE, target="a", duration=0.5, parameters={"factor": 1.2}),
        ],
    )
    code = ManimCompiler().compile_to_manim(scene)
    assert "Transform(a, b)" in code
    assert "Rotate(a, angle=PI/3)" in code
    assert ".animate.scale(1.2)" in code


