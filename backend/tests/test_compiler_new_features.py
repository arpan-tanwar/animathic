from schemas.manim_schema import ManimScene, ManimObject, AnimationStep, AnimationType
from services.manim_compiler import ManimCompiler


def test_axes_graph_and_style():
    scene = ManimScene(
        scene_name="GraphScene",
        objects=[
            ManimObject(name="axes", type="axes", props={"x_range": "[-3,3,1]", "y_range": "[-2,2,1]"}),
            ManimObject(name="parabola", type="graph", props={"axes": "axes", "function": "lambda x: x**2", "color": "YELLOW"}),
        ],
        animations=[
            AnimationStep(type=AnimationType.CREATE, target="axes", duration=1.0),
            AnimationStep(type=AnimationType.CREATE, target="parabola", duration=1.0),
            AnimationStep(type=AnimationType.SET_STROKE, target="parabola", duration=0.0, parameters={"color": "RED", "width": 4}),
        ],
    )
    code = ManimCompiler().compile_to_manim(scene)
    assert "Axes(" in code
    assert ".plot(" in code
    assert "set_stroke(RED, width=4)" in code


