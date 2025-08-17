from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Create the introduction text "Hello"
        hello_text = Text("Hello")
        self.play(Write(hello_text))
        self.wait(1)
        self.play(FadeOut(hello_text)) # Remove "Hello" to make space for the graph

        # Create the axes for the graph
        x_axis = Line(start=[-4, 0, 0], end=[4, 0, 0], color=WHITE)
        y_axis = Line(start=[0, -3, 0], end=[0, 3, 0], color=WHITE)
        axes = VGroup(x_axis, y_axis)

        # Create two points
        # Point 1: (1, 1)
        point1 = Circle(radius=0.08, color=BLUE, fill_opacity=1).move_to([1, 1, 0])
        # Point 2: (-2, 0.5)
        point2 = Circle(radius=0.08, color=RED, fill_opacity=1).move_to([-2, 0.5, 0])

        # Animate the creation of the axes and the points
        self.play(Create(axes))
        self.play(Create(point1), Create(point2))
        self.wait(2)