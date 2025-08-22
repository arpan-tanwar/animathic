#!/usr/bin/env python3
"""
Simple Manim test to verify RED color rendering
"""

from manim import *

class SimpleColorTest(MovingCameraScene):
    def construct(self):
        # Test 1: Simple red circle with default settings
        print("Creating red circle with default settings...")
        red_circle1 = Circle(
            radius=1,
            color=RED
        )
        red_circle1.move_to([-2, 0, 0])
        
        print(f"Circle 1 color: {red_circle1.color}")
        print(f"Circle 1 fill_opacity: {red_circle1.fill_opacity}")
        print(f"Circle 1 stroke_width: {red_circle1.stroke_width}")
        
        # Test 2: Red circle with explicit fill and stroke
        print("Creating red circle with explicit fill and stroke...")
        red_circle2 = Circle(
            radius=1,
            color=RED,
            fill_opacity=1.0,  # Full opacity
            stroke_width=3      # Thicker stroke
        )
        red_circle2.move_to([0, 0, 0])
        
        print(f"Circle 2 color: {red_circle2.color}")
        print(f"Circle 2 fill_opacity: {red_circle2.fill_opacity}")
        print(f"Circle 2 stroke_width: {red_circle2.stroke_width}")
        
        # Test 3: Red circle with fill_color and stroke_color separately
        print("Creating red circle with separate fill and stroke colors...")
        red_circle3 = Circle(
            radius=1,
            fill_color=RED,
            stroke_color=RED,
            fill_opacity=1.0,
            stroke_width=3
        )
        red_circle3.move_to([2, 0, 0])
        
        print(f"Circle 3 fill_color: {red_circle3.fill_color}")
        print(f"Circle 3 stroke_color: {red_circle3.stroke_color}")
        print(f"Circle 3 fill_opacity: {red_circle3.fill_opacity}")
        print(f"Circle 3 stroke_width: {red_circle3.stroke_width}")
        
        # Add all circles
        self.add(red_circle1, red_circle2, red_circle3)
        self.play(Create(red_circle1), Create(red_circle2), Create(red_circle3), run_time=2.0)
        self.wait(2)
        
        # Test fade out
        print("Fading out all circles...")
        self.play(FadeOut(red_circle1), FadeOut(red_circle2), FadeOut(red_circle3), run_time=1.0)
        self.wait(1)
        
        print("Test completed!")

if __name__ == "__main__":
    # This would normally be run with: manim -pql test_simple_manim.py SimpleColorTest
    print("This is a Manim scene file. Run with: manim -pql test_simple_manim.py SimpleColorTest")
