#!/usr/bin/env python3
"""
Test color lookup and mapping
"""

def test_color_mapping():
    """Test the exact color mapping logic"""
    print("🔍 Testing Color Mapping Logic...")
    
    # Simulate the exact color mapping from the generated code
    color_name = "RED"  # This is what the AI generates
    
    print(f"Input color_name: '{color_name}'")
    print(f"Type: {type(color_name)}")
    print(f"Length: {len(color_name)}")
    
    # Simulate the color mapping dictionary
    color_mapping = {
        # Lowercase mappings
        'white': 'WHITE_CONST', 'black': 'BLACK_CONST', 'red': 'RED_CONST', 'green': 'GREEN_CONST', 'blue': 'BLUE_CONST',
        'yellow': 'YELLOW_CONST', 'purple': 'PURPLE_CONST', 'orange': 'ORANGE_CONST', 'pink': 'PINK_CONST',
        'brown': 'BROWN_CONST', 'gray': 'GRAY_CONST', 'grey': 'GRAY_CONST', 'cyan': 'BLUE_CONST', 'magenta': 'PURPLE_CONST',
        'lime': 'GREEN_CONST', 'navy': 'BLUE_CONST', 'teal': 'BLUE_CONST', 'maroon': 'RED_CONST', 'olive': 'GREEN_CONST',
        'fuchsia': 'PURPLE_CONST', 'aqua': 'BLUE_CONST', 'silver': 'GRAY_CONST', 'gold': 'YELLOW_CONST',
        # Uppercase mappings (for when AI generates RED, BLUE, etc.)
        'WHITE': 'WHITE_CONST', 'BLACK': 'BLACK_CONST', 'RED': 'RED_CONST', 'GREEN': 'GREEN_CONST', 'BLUE': 'BLUE_CONST',
        'YELLOW': 'YELLOW_CONST', 'PURPLE': 'PURPLE_CONST', 'ORANGE': 'ORANGE_CONST', 'PINK': 'PINK_CONST',
        'BROWN': 'BROWN_CONST', 'GRAY': 'GRAY_CONST', 'GREY': 'GRAY_CONST', 'CYAN': 'BLUE_CONST', 'MAGENTA': 'PURPLE_CONST',
        'LIME': 'GREEN_CONST', 'NAVY': 'BLUE_CONST', 'TEAL': 'BLUE_CONST', 'MAROON': 'RED_CONST', 'OLIVE': 'GREEN_CONST',
        'FUCHSIA': 'PURPLE_CONST', 'AQUA': 'BLUE_CONST', 'SILVER': 'GRAY_CONST', 'GOLD': 'YELLOW_CONST'
    }
    
    print(f"\nColor mapping dictionary keys:")
    for key in sorted(color_mapping.keys()):
        if 'RED' in key or 'red' in key:
            print(f"  '{key}' -> {color_mapping[key]}")
    
    print(f"\nTesting color lookup:")
    print(f"  color_mapping.get('{color_name}') = {color_mapping.get(color_name)}")
    print(f"  color_mapping.get('{color_name}', 'DEFAULT') = {color_mapping.get(color_name, 'DEFAULT')}")
    
    # Test the exact lookup used in the code
    result = color_mapping.get(str(color_name), 'WHITE_CONST')
    print(f"  color_mapping.get(str(color_name), 'WHITE_CONST') = {result}")
    
    # Test if the key exists
    print(f"  '{color_name}' in color_mapping = {color_name in color_mapping}")
    print(f"  Keys containing 'RED': {[k for k in color_mapping.keys() if 'RED' in k]}")
    
    return result

if __name__ == "__main__":
    result = test_color_mapping()
    print(f"\n🎯 Final Result: {result}")
