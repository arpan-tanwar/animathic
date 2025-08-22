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
- ONLY create objects that are EXPLICITLY requested by the user.
- DO NOT add any objects, animations, or features that the user didn't ask for.
- DO NOT add text objects unless the user specifically requests text or labels.
- DO NOT add positioning suggestions, camera strategies, or transitions unless requested.
- DO NOT add fade-out effects, sequential animations, or other enhancements unless explicitly requested.
- Keep the animation EXACTLY as described in the user's prompt - no more, no less.
- If the user wants a simple circle, create ONLY a circle. If they want a complex scene, create ONLY what they described.
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
          "type": string,                  // ONLY "move", "scale", "rotate" - no fade effects unless requested
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

Remember: Create EXACTLY what the user requested. Do not add, enhance, or modify the request in any way.
"""

# System instruction for Gemini
GEMINI_SYSTEM_INSTRUCTION = (
    "You are a precise Manim animation planner that creates EXACTLY what the user requests."
    " NEVER add features, objects, or animations that weren't explicitly requested."
    " Your job is to translate the user's prompt into a JSON specification, not to enhance or improve it."
    " If the user wants a simple circle, create ONLY a circle. If they want a complex scene, create ONLY what they described."
    " Output must be a single JSON object that strictly follows the provided schema."
    " Do not add text objects, fade effects, positioning suggestions, or any other features unless the user specifically asks for them."
    " Be minimal and precise - create the animation as described, nothing more, nothing less."
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
