from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Create points (nodes) with labels
        node_A_circle = Circle(radius=0.4, color=RED, fill_opacity=0.8)
        node_A_label = Text("A", font_size=48, color=WHITE)
        node_A = VGroup(node_A_circle, node_A_label).move_to([-3, 0, 0])
        node_A_label.move_to(node_A_circle.get_center()) # Center label in circle

        node_B_circle = Circle(radius=0.4, color=BLUE, fill_opacity=0.8)
        node_B_label = Text("B", font_size=48, color=WHITE)
        node_B = VGroup(node_B_circle, node_B_label).move_to([0, 0, 0])
        node_B_label.move_to(node_B_circle.get_center())

        node_C_circle = Circle(radius=0.4, color=GREEN, fill_opacity=0.8)
        node_C_label = Text("C", font_size=48, color=WHITE)
        node_C = VGroup(node_C_circle, node_C_label).move_to([3, 0, 0])
        node_C_label.move_to(node_C_circle.get_center())

        # Create edges (lines) connecting the points
        edge_AB = Line(node_A_circle.get_center(), node_B_circle.get_center(), color=YELLOW, stroke_width=5)
        edge_BC = Line(node_B_circle.get_center(), node_C_circle.get_center(), color=YELLOW, stroke_width=5)

        # Animate the creation of the graph
        self.play(Create(node_A), run_time=1.5)
        self.play(Create(node_B), run_time=1.5)
        self.play(Create(node_C), run_time=1.5)

        self.play(Create(edge_AB), run_time=1.5)
        self.play(Create(edge_BC), run_time=1.5)

        self.wait(1.5)