#!/usr/bin/env python3
"""
Simple Manim test to verify basic functionality
"""

from manim import *

class SimpleTest(MovingCameraScene):
    def construct(self):
        print("Starting simple test...")
        
        # Test 1: Basic circle with RED color
        print("Creating red circle...")
        try:
            circle = Circle(
                radius=1,
                fill_color=RED,
                stroke_color=RED,
                fill_opacity=1.0,
                stroke_width=3
            )
            print(f"Circle created successfully with color: {circle.fill_color}")
            
            self.add(circle)
            self.play(Create(circle), run_time=1.0)
            self.wait(1)
            
            # Test fade out
            self.play(FadeOut(circle), run_time=1.0)
            self.wait(1)
            
            print("Simple test completed successfully!")
            
        except Exception as e:
            print(f"Error in simple test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("This is a Manim scene file. Run with: manim -pql test_simple_manim.py SimpleTest")
