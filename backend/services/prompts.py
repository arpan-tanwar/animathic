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

COORDINATE POSITIONING RULES (CRITICAL):
- ALWAYS use EXACT coordinates as specified in the user prompt
- If user says "at (2,4)", place the object EXACTLY at [2, 4, 0]
- If user says "at (-2,4)", place the object EXACTLY at [-2, 4, 0]
- NEVER change or approximate coordinates unless explicitly requested
- Use the [x, y, 0] format for all positions
- Coordinate system should cover the requested coordinates with margin

COORDINATE EXAMPLES:
- "circle at (2,4)" → position: [2, 4, 0]
- "square at (-2,4)" → position: [-2, 4, 0]
- "point at (0,0)" → position: [0, 0, 0]
- "text at (1,1)" → position: [1, 1, 0]

COORDINATE SYSTEM SETUP:
- Set x_range to cover requested x-coordinates ±2 (e.g., for x=2, use [-4, 4])
- Set y_range to cover requested y-coordinates ±2 (e.g., for y=4, use [2, 6])
- Ensure axes are centered and visible

TEXT LABEL RULES (IMPORTANT):
- If the user mentions "text labels", "labels", "annotations", "text", or "names" - you MUST create text objects.
- For generic requests like "text labels for each point", create simple labels like "Point A", "Point B", etc.
- For mathematical objects, use simple labels like "A", "B", "P1", "P2", etc.
- Always include the "text" property with actual text content when creating text objects.
- Position text labels near but not overlapping with the objects they describe.
- Use simple, short text labels - avoid long descriptive text.

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
        "function": string,                   // e.g. "sine", "cosine", "tangent", "exponential", "polynomial"
        "expression": string,                 // e.g. "sin(x)" or "x**2 - 1" (optional, function takes priority)
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
  "background_color": string,              // Default to #000000 (black)
  "style": string
}

FUNCTION PLOT RULES (CRITICAL):
- For "sine" → use "function": "sine" (creates sin(x) plot)
- For "cosine" → use "function": "cosine" (creates cos(x) plot)  
- For "tangent" → use "function": "tangent" (creates tan(x) plot)
- For "exponential" → use "function": "exponential" (creates exp(x) plot)
- Each function plot must be a separate object with unique id
- Use different colors for each plot: sine=YELLOW, cosine=BLUE, tangent=GREEN, exponential=RED
- Function plots should be positioned at [0, 0, 0] (origin) for proper coordinate system layout
- Multiple function plots can overlap at origin - this is expected and desired for good visual layout

COORDINATE SYSTEM LAYOUT RULES:
- When creating "coordinate system with multiple function plots", all plots should be at origin [0, 0, 0]
- Axes should be centered at [0, 0, 0] with appropriate ranges
- Geometric shapes should be placed at their specified coordinates (e.g., "at key points")
- Text annotations should be positioned near their corresponding objects
- Function plots overlapping at origin is PERFECT and should not be prevented

TEXT ANNOTATION TIMING:
- Text labels should appear shortly after their corresponding objects
- For function plots, text should appear right after the plot becomes visible
- For geometric shapes, text should appear with or shortly after the shape
- Use simple, descriptive labels like "sine", "cosine", "Point A", etc.
- All plots should have position: [0, 0, 0] (center on axes)

MULTIPLE FUNCTIONS EXAMPLE:
User says: "sine, cosine, tangent, exponential plots"
Create 4 separate plot objects:
{"id": "plot_sine", "type": "plot", "properties": {"function": "sine", "color": "YELLOW", "position": [0, 0, 0]}}
{"id": "plot_cosine", "type": "plot", "properties": {"function": "cosine", "color": "BLUE", "position": [0, 0, 0]}}
{"id": "plot_tangent", "type": "plot", "properties": {"function": "tangent", "color": "GREEN", "position": [0, 0, 0]}}
{"id": "plot_exponential", "type": "plot", "properties": {"function": "exponential", "color": "RED", "position": [0, 0, 0]}}

TEXT GENERATION EXAMPLES:
- "text labels for each point" → Create text objects with "A", "B", "C", etc.
- "label the functions" → Create text objects with "f(x)", "g(x)", etc.
- "add names" → Create text objects with simple names like "A", "B", "P1", "P2"
- "annotate the plot" → Create text objects with simple labels like "A", "B", "C"

User Prompt:
{prompt}

Remember: Create EXACTLY what the user requested, including fade effects, colors, text labels, and precise coordinates when mentioned.
"""

# System instruction for Gemini
GEMINI_SYSTEM_INSTRUCTION = (
    "You are a precise Manim animation planner that creates EXACTLY what the user requests."
    " CRITICAL: For multiple function plots, create separate plot objects for each function type."
    " If user mentions 'sine, cosine, tangent, exponential', create 4 separate plot objects with different colors."
    " Use 'function' property: 'sine', 'cosine', 'tangent', 'exponential' for math functions."
    " If the user mentions fade effects, colors, or specific animations - include them."
    " If the user mentions text labels, labels, annotations, or names - you MUST create text objects with actual text content."
    " For generic text requests like 'text labels for each point', create simple labels like 'A', 'B', 'C', etc."
    " For mathematical objects, use simple labels like 'A', 'B', 'P1', 'P2', etc."
    " When coordinates are specified like 'at (2,4)', use those EXACT coordinates - do not change or approximate them."
    " Position objects precisely at the specified coordinates using [x, y, 0] format."
    " Your job is to translate the user's prompt into a JSON specification with proper animations, colors, text labels, and precise coordinates."
    " If the user wants a red circle that fades in and out, create a circle with color RED and animations for fade_in and fade_out."
    " If the user wants text labels, create text objects with the 'text' property containing simple, short text content."
    " If the user specifies coordinates, use them exactly as written."
    " Output must be a single JSON object that strictly follows the provided schema."
    " Be precise and include all requested features - create the animation as described."
    " IMPORTANT: Create separate objects for each element mentioned - don't combine multiple functions into one plot object."
)

# Default animation specification
DEFAULT_ANIMATION_SPEC = {
    "animation_type": "geometric",
    "scene_description": "Generated animation",
    "objects": [],
    "camera_settings": {"position": [0, 0, 0], "zoom": 8},
    "duration": 5,
    "background_color": "#000000",
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
