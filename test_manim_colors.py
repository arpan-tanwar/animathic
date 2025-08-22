#!/usr/bin/env python3
"""
Test Manim color rendering with different methods
"""

from manim import *

class ColorTest(MovingCameraScene):
    def construct(self):
        # Test 1: Basic RED color
        print("Testing basic RED color...")
        circle1 = Circle(radius=1, color=RED)
        circle1.move_to([-3, 0, 0])
        
        # Test 2: Explicit fill and stroke
        print("Testing explicit fill_color and stroke_color...")
        circle2 = Circle(
            radius=1,
            fill_color=RED,
            stroke_color=RED,
            fill_opacity=1.0,
            stroke_width=3
        )
        circle2.move_to([0, 0, 0])
        
        # Test 3: Force color after creation
        print("Testing color setting after creation...")
        circle3 = Circle(radius=1)
        circle3.set_fill(RED, opacity=1.0)
        circle3.set_stroke(RED, width=3)
        circle3.move_to([3, 0, 0])
        
        # Test 4: Different color values
        print("Testing different color values...")
        circle4 = Circle(radius=0.5, fill_color=BLUE, stroke_color=BLUE, fill_opacity=1.0)
        circle4.move_to([-1.5, 2, 0])
        
        circle5 = Circle(radius=0.5, fill_color=GREEN, stroke_color=GREEN, fill_opacity=1.0)
        circle5.move_to([1.5, 2, 0])
        
        # Add all circles
        self.add(circle1, circle2, circle3, circle4, circle5)
        
        # Print color information
        print(f"Circle 1 color: {circle1.color}, fill_color: {circle1.fill_color}, stroke_color: {circle1.stroke_color}")
        print(f"Circle 2 color: {circle2.color}, fill_color: {circle2.fill_color}, stroke_color: {circle2.stroke_color}")
        print(f"Circle 3 color: {circle3.color}, fill_color: {circle3.fill_color}, stroke_color: {circle3.stroke_color}")
        
        # Animate them in
        self.play(
            Create(circle1), Create(circle2), Create(circle3), 
            Create(circle4), Create(circle5), 
            run_time=2.0
        )
        self.wait(2)
        
        # Test fade out
        self.play(
            FadeOut(circle1), FadeOut(circle2), FadeOut(circle3),
            FadeOut(circle4), FadeOut(circle5),
            run_time=1.0
        )
        self.wait(1)
        
        print("Color test completed!")

if __name__ == "__main__":
    print("This is a Manim scene file. Run with: manim -pql test_manim_colors.py ColorTest")
