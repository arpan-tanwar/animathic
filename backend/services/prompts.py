"""
Prompt Templates and Schema Definitions for Animathic
Contains all AI prompts and JSON schemas
"""

# Animation generation prompt template
ANIMATION_PROMPT_TEMPLATE = """
You are an expert animation creator using Manim (Mathematical Animation Engine).
Given the user's prompt below, produce a STRICT JSON object that follows this schema exactly.

CRITICAL RULES (must follow exactly):
- Output ONLY a JSON object. No prose, no code fences, no comments.
- Use double quotes for all keys and string values.
- No trailing commas. No NaN/Infinity. Use numbers for durations/zoom and arrays for positions.
- Create objects and animations EXACTLY as described in the user's prompt.
- If the user mentions "fade in", "fade out", "appears", "disappears" - include those animations.
- If the user mentions colors like "red", "blue", "green" - use those exact colors.
- Keep the animation EXACTLY as described in the user's prompt - no more, no less.
- The JSON should be a direct translation of the user's request, not an interpretation with added features.

Schema:
{
  "animation_type": string,                // e.g. "geometric", "mathematical", "text"
  "scene_description": string,             // brief summary matching the user's request
  "objects": [
    {
      "id": string,                        // unique id for timeline reference
      "type": string,                      // one of: "circle" | "square" | "text" | "line" | "dot" | "axes" | "plot" | "diamond" | "star" | "hexagon" | "triangle" | "rectangle" | "ellipse"
      "properties": {
        // common
        "position": [number, number, number],
        "color": string,                   // Use bright colors: WHITE, YELLOW, CYAN, GREEN, RED, BLUE, MAGENTA
        "size": number,

        // text-specific (ONLY if user requests text)
        "text": string,                    // ONLY include if text is explicitly requested

        // line-specific (ONLY if user requests lines)
        "start": [number, number, number],
        "end": [number, number, number],

        // axes-specific (ONLY if user requests axes)
        "x_range": [number, number, number],  // [min, max, step]
        "y_range": [number, number, number],
        "show_labels": boolean,

        // plot-specific (ONLY if user requests plots)
        "expression": string,                 // e.g. "sin(x)" or "x**2 - 1"
        "x_range_plot": [number, number],     // [min, max]
      },
      "animations": [
        {
          "type": string,                  // "fade_in", "fade_out", "move", "scale", "rotate", "wait"
          "duration": number,              // seconds
          "parameters": object             // e.g. {"target_position": [x,y,z]} or {"scale_factor": 1.2}
        }
      ]
    }
  ],
  "camera_settings": {"position": [number,number,number], "zoom": number},
  "duration": number,
  "background_color": string,              // Default to #1a1a1a (dark gray)
  "style": string
}

User Prompt:
{prompt}

Remember: Create EXACTLY what the user requested, including fade effects and colors when mentioned.
"""

# System instruction for Gemini
GEMINI_SYSTEM_INSTRUCTION = (
    "You are a precise Manim animation planner that creates EXACTLY what the user requests."
    " If the user mentions fade effects, colors, or specific animations - include them."
    " Your job is to translate the user's prompt into a JSON specification with proper animations and colors."
    " If the user wants a red circle that fades in and out, create a circle with color RED and animations for fade_in and fade_out."
    " Output must be a single JSON object that strictly follows the provided schema."
    " Be precise and include all requested features - create the animation as described."
)

# Default animation specification
DEFAULT_ANIMATION_SPEC = {
    "animation_type": "geometric",
    "scene_description": "Generated animation",
    "objects": [],
    "camera_settings": {"position": [0, 0, 0], "zoom": 8},
    "duration": 5,
    "background_color": "#1a1a1a",
    "style": "modern"
}

# Allowed object types
ALLOWED_OBJECT_TYPES = {
    "circle", "square", "text", "line", "dot", "axes", "plot", 
    "diamond", "star", "hexagon", "triangle", "rectangle", "ellipse"
}

# Allowed animation types
ALLOWED_ANIMATION_TYPES = {
    "move", "scale", "rotate", "fade_in", "fade_out", 
    "transform", "fade_out_previous", "clear_previous_plots", "wait"
}

# Default bounds
DEFAULT_BOUNDS = {
    "x": [-6, 6],
    "y": [-3.5, 3.5]
}
