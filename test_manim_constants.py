#!/usr/bin/env python3
"""
Test if Manim color constants are properly available
"""

try:
    from manim import *
    print("✅ Manim imported successfully")
    
    # Test if color constants are available
    print(f"RED: {RED}")
    print(f"WHITE: {WHITE}")
    print(f"BLUE: {BLUE}")
    print(f"GREEN: {GREEN}")
    
    # Test if they are the expected types
    print(f"RED type: {type(RED)}")
    print(f"WHITE type: {type(WHITE)}")
    
    # Test if they can be used in color mapping
    color_mapping = {
        'RED': RED,
        'WHITE': WHITE,
        'BLUE': BLUE,
        'GREEN': GREEN
    }
    
    print(f"Color mapping test: {color_mapping.get('RED')}")
    print(f"Color mapping test: {color_mapping.get('WHITE')}")
    
    print("✅ All Manim color constants are working correctly")
    
except ImportError as e:
    print(f"❌ Manim import failed: {e}")
except Exception as e:
    print(f"❌ Error with Manim constants: {e}")
    import traceback
    traceback.print_exc()
