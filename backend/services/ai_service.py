"""
AI Service for Animathic - Gemini 2.5 Flash Integration
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
try:
    # Newer SDK (google-genai) optional types; fall back if unavailable
    from google.genai import types as genai_types  # type: ignore
except Exception:  # pragma: no cover
    genai_types = None  # type: ignore
from dotenv import load_dotenv
import httpx

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, api_key: str):
        """Initialize AI service with Gemini"""
        genai.configure(api_key=api_key)
        # Use latest free/GA Gemini Flash; disable thinking if supported
        if genai_types is not None:
            try:
                self.model = genai.GenerativeModel(
                    'gemini-2.5-flash',
                    system_instruction=(
                        "You are an expert Manim animation planner."
                        " Always reason internally to ensure outputs are valid and executable,"
                        " but never include your reasoning in the response."
                        " Output must be a single JSON object that strictly follows the provided schema."
                        " Validate numeric ranges (e.g., axis steps must be positive, >= 0.5),"
                        " default missing fields sensibly, and avoid features that require LaTeX or GPU."
                    ),
                    config=genai_types.GenerateContentConfig(
                        thinking_config=genai_types.ThinkingConfig(thinking_budget=0)
                    ),
                )
            except Exception:
                self.model = genai.GenerativeModel(
                    'gemini-2.5-flash',
                    system_instruction=(
                        "You are an expert Manim animation planner."
                        " Always reason internally to ensure outputs are valid and executable,"
                        " but never include your reasoning in the response."
                        " Output must be a single JSON object that strictly follows the provided schema."
                        " Validate numeric ranges (e.g., axis steps must be positive, >= 0.5),"
                        " default missing fields sensibly, and avoid features that require LaTeX or GPU."
                    ),
                )
        else:
            self.model = genai.GenerativeModel(
                'gemini-2.5-flash',
                system_instruction=(
                    "You are an expert Manim animation planner."
                    " Always reason internally to ensure outputs are valid and executable,"
                    " but never include your reasoning in the response."
                    " Output must be a single JSON object that strictly follows the provided schema."
                    " Validate numeric ranges (e.g., axis steps must be positive, >= 0.5),"
                    " default missing fields sensibly, and avoid features that require LaTeX or GPU."
                ),
            )

        # Note: Avoid SDK response_schema due to field support variability; enforce via prompt and post-parse.
        
        # Animation generation prompt template
        # Strict JSON-only instruction with an explicit schema to minimize parse errors
        self.animation_prompt_template = """
You are an expert animation creator using Manim (Mathematical Animation Engine).
Given the user's prompt below, produce a STRICT JSON object that follows this schema exactly.

Rules (must follow):
- Output ONLY a JSON object. No prose, no code fences, no comments.
- Use double quotes for all keys and string values.
- No trailing commas. No NaN/Infinity. Use numbers for durations/zoom and arrays for positions.
- ALWAYS use a dark background color (#1a1a1a or #000000) unless explicitly requested otherwise
- Choose bright, contrasting colors for all objects to ensure visibility on dark backgrounds
- Axis steps must be positive and >= 0.5. If invalid or missing, default to 1.
- Prefer simple text labels (avoid LaTeX/MathTex). Keep scenes lightweight and compatible with headless Cairo.
- Placement rules: Every object must have either an explicit numeric "position" [x,y,z], or an "anchor" (e.g.,
  "center", "top_left", "bottom_right", "axis_origin", "axis_x_at:1", "axis_y_at:-2") optionally with
  an "offset" [dx,dy,dz]. Use the global bounds or axes to keep objects on-screen and non-overlapping.
- Each object must have a unique string "id" and an integer "z_index" (higher draws on top; default 0..5 sane range).
- Provide either an "axes" object or a global "bounds" field {"x":[min,max],"y":[min,max]} describing scene extents.
- Provide a top-level "timeline" array of events with fields: {"id": string, "type": string, "start": number,
  "duration": number, "parameters": object}. Use ids to reference objects unambiguously.
- Validate internally that the JSON is self-consistent and executable in Manim 0.19; silently fix minor issues.

Schema:
{
  "animation_type": string,                // e.g. "geometric", "mathematical", "text"
  "scene_description": string,             // detailed summary of the scene
  "objects": [
    {
      "id": string,                        // unique id for timeline reference
      "type": string,                      // one of: "circle" | "square" | "text" | "line" | "dot" | "axes" | "plot"
      "properties": {
        // common
        "position": [number, number, number],
        "anchor": string,                 // e.g. "center", "top_left", "axis_origin", "axis_x_at:1"
        "offset": [number, number, number],
        "z_index": number,
        "color": string,                   // Use bright colors: WHITE, YELLOW, CYAN, GREEN, RED, BLUE, MAGENTA
        "size": number,
        "text": string,

        // line-specific
        "start": [number, number, number],
        "end": [number, number, number],

        // axes-specific
        "x_range": [number, number, number],  // [min, max, step]
        "y_range": [number, number, number],
        "show_labels": boolean,

        // plot-specific
        "expression": string,                 // e.g. "sin(x)" or "x**2 - 1"
        "x_range_plot": [number, number],     // [min, max]
      },
      "animations": [
        {
          "type": string,                  // "move" | "scale" | "rotate"
          "duration": number,              // seconds
          "easing": string,                // e.g. "linear"
          "parameters": object             // e.g. {"target_position": [x,y,z]} or {"scale_factor": 1.2}
        }
      ]
    }
  ],
  "camera_settings": {"position": [number,number,number], "zoom": number},
  "bounds": {"x": [number, number], "y": [number, number]},
  "duration": number,
  "background_color": string,              // Default to #1a1a1a (dark gray) for aesthetic appeal
  "style": string,
  "timeline": [
    {"id": string, "type": string, "start": number, "duration": number, "parameters": object}
  ]
}

User Prompt:
{prompt}
"""

    async def generate_animation_spec(self, prompt: str) -> Dict[str, Any]:
        """
        Generate animation specification using Gemini
        """
        try:
            logger.info(f"Generating animation spec for prompt: {prompt}")
            
            # Format the prompt without invoking str.format on JSON braces
            formatted_prompt = self.animation_prompt_template.replace("{prompt}", prompt)
            
            # Generate response from Gemini (force JSON MIME type)
            response = self.model.generate_content(
                formatted_prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.2,
                    "top_p": 0.8,
                },
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            # Parse JSON response robustly and normalize
            raw_text = (response.text or "").strip()
            try:
                spec = json.loads(raw_text)
            except Exception:
                import re
                # Prefer fenced code blocks
                m = re.search(r"```(?:json)?\s*\n(\{[\s\S]*?\})\s*```", raw_text)
                if m:
                    spec = json.loads(m.group(1))
                else:
                    m2 = re.search(r"\{[\s\S]*\}", raw_text)
                    if not m2:
                        raise ValueError("Invalid JSON response from AI model")
                    spec = json.loads(m2.group())

            if not isinstance(spec, dict):
                # Sometimes the model returns a top-level list; wrap it
                spec = {"objects": spec}

            # Provide safe defaults to avoid KeyErrors like "animation_type"
            normalized: Dict[str, Any] = {
                "animation_type": spec.get("animation_type", "geometric"),
                "scene_description": spec.get("scene_description", f"Animation for: {prompt}"),
                "objects": spec.get("objects") or [],
                "camera_settings": spec.get("camera_settings") or {"position": [0, 0, 0], "zoom": 8},
                "duration": spec.get("duration", 5),
                "background_color": spec.get("background_color", "#1a1a1a"),  # Dark gray for aesthetic appeal
                "style": spec.get("style", "modern"),
            }
            if not isinstance(normalized["objects"], list):
                try:
                    normalized["objects"] = list(normalized["objects"])  # convert mapping->list of keys
                except Exception:
                    normalized["objects"] = []
            if not normalized["objects"]:
                normalized["objects"].append({
                    "type": "text",
                    "properties": {"text": prompt, "color": "WHITE", "size": 36, "position": [0, 0, 0]},
                    "animations": []
                })

            logger.info("Successfully generated and normalized animation specification")
            return normalized
                    
        except Exception as e:
            logger.error(f"Error generating animation spec: {e}")
            # Try local fallback generator if configured
            fallback = await self._try_local_fallback(prompt)
            if fallback is not None:
                return fallback
            raise

    def generate_manim_code(self, animation_spec: Dict[str, Any]) -> str:
        """
        Convert animation specification to Manim Python code
        """
        try:
            logger.info("Converting animation spec to Manim code")
            
            # Sanitize spec to avoid invalid shapes/values
            def _coerce_vec3(v):
                try:
                    if not isinstance(v, (list, tuple)):
                        return [0, 0, 0]
                    out = []
                    for i in range(3):
                        out.append(float(v[i]) if i < len(v) and isinstance(v[i], (int, float)) else 0.0)
                    return out
                except Exception:
                    return [0, 0, 0]

            allowed_types = {"circle", "square", "text", "line", "dot", "axes", "plot"}
            allowed_anims = {"move", "scale", "rotate", "fade_in", "fade_out", "transform"}
            sanitized_objects = []
            for obj in animation_spec.get("objects", []) or []:
                otype = str(obj.get("type", "")).lower()
                if otype not in allowed_types:
                    continue
                props = obj.get("properties", {}) or {}
                props.setdefault("position", [0, 0, 0])
                props["position"] = _coerce_vec3(props.get("position"))
                if otype == "circle":
                    try:
                        props["size"] = float(props.get("size", 1)) or 1.0
                    except Exception:
                        props["size"] = 1.0
                if otype == "square":
                    try:
                        props["size"] = float(props.get("size", 2)) or 2.0
                    except Exception:
                        props["size"] = 2.0
                if otype == "line":
                    props["start"] = _coerce_vec3(props.get("start", [-2, 0, 0]))
                    props["end"] = _coerce_vec3(props.get("end", [2, 0, 0]))
                if otype == "axes":
                    def _rng(r, d):
                        try:
                            r = list(r)
                            xmin = float(r[0])
                            xmax = float(r[1])
                            step = float(r[2])
                            # Sanitize step: must be positive and not too small
                            if step <= 0:
                                step = 1.0
                            # Coerce to reasonable tick granularity
                            if step < 0.5:
                                step = 0.5
                            return [xmin, xmax, step]
                        except Exception:
                            return d
                    props["x_range"] = _rng(props.get("x_range", [-5, 5, 1]), [-5, 5, 1])
                    props["y_range"] = _rng(props.get("y_range", [-3, 3, 1]), [-3, 3, 1])
                    props["show_labels"] = bool(props.get("show_labels", True))
                if otype == "plot":
                    try:
                        xr = props.get("x_range_plot", [-5, 5])
                        props["x_range_plot"] = [float(xr[0]), float(xr[1])]
                    except Exception:
                        props["x_range_plot"] = [-5, 5]
                    props["expression"] = str(props.get("expression", "sin(x)"))
                # Sanitize animations
                anims = []
                for anim in obj.get("animations", []) or []:
                    a = dict(anim or {})
                    a_type_raw = str(a.get("type", "move")).lower()
                    # Normalize/allow only known animations
                    if a_type_raw in {"fadein", "appear"}:
                        a["type"] = "fade_in"
                    elif a_type_raw in {"fadeout", "disappear"}:
                        a["type"] = "fade_out"
                    elif a_type_raw in {"transform_to", "morph", "transformto"}:
                        a["type"] = "transform"
                    elif a_type_raw in allowed_anims:
                        a["type"] = a_type_raw
                    else:
                        # Skip unknown animation types
                        continue
                    try:
                        a["duration"] = max(0.1, float(a.get("duration", 1)))
                    except Exception:
                        a["duration"] = 1.0
                    a.setdefault("parameters", {})
                    anims.append(a)
                sanitized_objects.append({"type": otype, "properties": props, "animations": anims})
            animation_spec = {**animation_spec, "objects": sanitized_objects}
            # Bounds defaults
            try:
                _b = animation_spec.get("bounds") or {}
                _bx = _b.get("x", [-6, 6])
                _by = _b.get("y", [-3.5, 3.5])
                x_bounds = [float(_bx[0]), float(_bx[1])]
                y_bounds = [float(_by[0]), float(_by[1])]
            except Exception:
                x_bounds = [-6.0, 6.0]
                y_bounds = [-3.5, 3.5]

            # Basic Manim scene template with numpy for plotting support
            manim_code = f'''from manim import *
import numpy as np

class GeneratedScene(MovingCameraScene):
    def construct(self):
        # Animation: {animation_spec.get('scene_description', 'Generated animation')}
        
        # Set background color - ensure dark background for aesthetic appeal
        bg_color = "{animation_spec.get('background_color', '#1a1a1a')}"
        if bg_color.lower() in ['#ffffff', '#fff', 'white', 'ffffff']:
            bg_color = "#1a1a1a"  # Force dark background if white is specified
        self.camera.background_color = bg_color
        
        def safe_color(c):
            try:
                if not isinstance(c, str):
                    return "WHITE"
                upper = c.upper()
                if upper in ["BLACK", "#000000", "#000"]:
                    return "WHITE"
                return c
            except Exception:
                return "WHITE"

        def safe_play(*args, run_time=1.0):
            try:
                self.play(*args, run_time=run_time)
            except Exception:
                pass

        # Simple layout registry and helpers
        id_to_mobject = {{}}
        id_to_meta = {{}}  # stores metadata for each object: type and z_index

        def reg(oid, mobj, z_index=0, otype=""):
            try:
                if mobj is None:
                    return
                id_to_mobject[oid] = mobj
                id_to_meta[oid] = {{'type': str(otype).lower(), 'z': int(z_index)}}
                try:
                    mobj.set_z_index(int(z_index))
                except Exception:
                    pass
            except Exception:
                pass

        def get_group(ids):
            try:
                g = VGroup(*[id_to_mobject[i] for i in ids if i in id_to_mobject])
                return g
            except Exception:
                return VGroup()

        def exit_fade(ids, duration=0.4, stagger=0.05):
            try:
                seq = []
                for i, oid in enumerate(ids):
                    m = id_to_mobject.get(oid)
                    if m is not None:
                        seq.append(FadeOut(m))
                if seq:
                    safe_play(*seq, run_time=duration)
            except Exception:
                pass

        def camera_fit(ids, margin=0.15):
            try:
                g = get_group(ids)
                if len(g) == 0:
                    return
                bbox = g.get_bounding_box()
                # Ensure minimum frame size for better visibility
                min_width = 8.0
                min_height = 6.0
                
                width = max(min_width, bbox[1][0] - bbox[0][0]) * (1.0 + margin)
                height = max(min_height, bbox[1][1] - bbox[0][1]) * (1.0 + margin)
                
                # Use the larger dimension to ensure all objects fit
                frame_width = max(width, height * 1.4)  # 1.4 aspect ratio
                
                center = g.get_center()
                self.camera.frame.set_width(frame_width)
                self.camera.frame.move_to(center)
            except Exception:
                pass

        def camera_pad(margin=0.05):
            try:
                cur_w = float(self.camera.frame.get_width())
                self.camera.frame.set_width(cur_w * (1.0 + max(0.0, float(margin))))
            except Exception:
                pass

        def dynamic_camera_adjust(active_objects, target_margin=0.2):
            """Dynamically adjust camera based on object distribution and prevent overlaps"""
            try:
                if not active_objects:
                    return
                
                # Get bounding box of all active objects
                bbox = get_bbox(active_objects)
                if not bbox:
                    return
                
                (x0, y0), (x1, y1) = bbox
                width = x1 - x0
                height = y1 - y0
                
                # Calculate optimal frame size with margin
                frame_width = max(width, height * 1.4) * (1.0 + target_margin)
                frame_height = max(height, width / 1.4) * (1.0 + target_margin)
                
                # Use the larger dimension to ensure all objects fit
                optimal_width = max(frame_width, frame_height * 1.4)
                
                # Ensure minimum frame size
                optimal_width = max(optimal_width, 10.0)
                
                # Smoothly adjust camera
                current_width = float(self.camera.frame.get_width())
                if abs(current_width - optimal_width) > 0.5:
                    # Animate camera adjustment
                    safe_play(self.camera.frame.animate.set_width(optimal_width), run_time=0.8)
                
                # Center camera on objects
                center_x = (x0 + x1) / 2
                center_y = (y0 + y1) / 2
                current_center = self.camera.frame.get_center()
                
                if abs(current_center[0] - center_x) > 0.5 or abs(current_center[1] - center_y) > 0.5:
                    safe_play(self.camera.frame.animate.move_to([center_x, center_y, 0]), run_time=0.6)
                    
            except Exception:
                pass

        def smart_screen_management(new_graph_type):
            """Intelligent screen management when adding new graphs"""
            try:
                # Count existing graphs
                existing_graphs = [oid for oid in active_ids if id_to_meta.get(oid, {{}}).get('type') in ['plot', 'axes', 'function', 'graph']]
                
                if len(existing_graphs) == 0:
                    # First graph - use default positioning
                    return
                
                elif len(existing_graphs) == 1:
                    # Second graph - check if we can fit both
                    existing_graph = id_to_mobject.get(existing_graphs[0])
                    if existing_graph:
                        bbox = _mobj_bbox(existing_graph)
                        if bbox:
                            (x0, y0), (x1, y1), w, h = bbox
                            
                            # If existing graph is small, we can fit both side by side
                            if w < 6 and h < 4:
                                # Keep existing graph, position new one to the right
                                return 'side_by_side'
                            else:
                                # Existing graph is large, fade it out
                                return 'fade_existing'
                
                else:
                    # Multiple graphs - need to manage screen space
                    total_width = 0
                    for oid in existing_graphs:
                        mobj = id_to_mobject.get(oid)
                        if mobj:
                            bbox = _mobj_bbox(mobj)
                            if bbox:
                                _, _, w, _ = bbox
                                total_width += w
                    
                    # If total width exceeds screen capacity, fade out oldest
                    if total_width > 10:
                        return 'fade_oldest'
                    else:
                        return 'reorganize'
                        
            except Exception:
                return 'default'

        def execute_screen_strategy(strategy, new_graph_obj=None):
            """Execute the chosen screen management strategy"""
            try:
                if strategy == 'side_by_side':
                    # Position new graph to the right of existing one
                    existing_graphs = [oid for oid in active_ids if id_to_meta.get(oid, {{}}).get('type') in ['plot', 'axes', 'function', 'graph']]
                    if existing_graphs and new_graph_obj:
                        existing_graph = id_to_mobject.get(existing_graphs[0])
                        if existing_graph:
                            existing_center = existing_graph.get_center()
                            new_graph_obj.move_to([existing_center[0] + 6, existing_center[1], 0])
                            
                            # Zoom out camera to show both graphs
                            safe_play(self.camera.frame.animate.set_width(16), run_time=0.8)
                
                elif strategy == 'fade_existing':
                    # Fade out existing graph and focus on new one
                    existing_graphs = [oid for oid in active_ids if id_to_meta.get(oid, {{}}).get('type') in ['plot', 'axes', 'function', 'graph']]
                    for oid in existing_graphs:
                        mobj = id_to_mobject.get(oid)
                        if mobj:
                            safe_play(FadeOut(mobj), run_time=0.6)
                            if oid in active_ids:
                                active_ids.remove(oid)
                    
                    # Center camera on new graph
                    if new_graph_obj:
                        new_center = new_graph_obj.get_center()
                        safe_play(self.camera.frame.animate.move_to(new_center).set_width(8), run_time=0.8)
                
                elif strategy == 'fade_oldest':
                    # Fade out oldest graph to make room
                    existing_graphs = [oid for oid in active_ids if id_to_meta.get(oid, {{}}).get('type') in ['plot', 'axes', 'function', 'graph']]
                    if existing_graphs:
                        oldest_graph = existing_graphs[0]  # First in list is oldest
                        mobj = id_to_mobject.get(oldest_graph)
                        if mobj:
                            safe_play(FadeOut(mobj), run_time=0.6)
                            active_ids.remove(oldest_graph)
                            
                            # Adjust camera to show remaining graphs
                            dynamic_camera_adjust(active_ids, target_margin=0.3)
                
                elif strategy == 'reorganize':
                    # Reorganize all graphs to fit better
                    resolve_graph_overlaps()
                    dynamic_camera_adjust(active_ids, target_margin=0.4)
                    
            except Exception:
                pass

        def camera_zoom(factor=1.0, anchor=None):
            try:
                factor = float(factor) if isinstance(factor, (int, float)) else 1.0
                if factor <= 0:
                    return
                new_w = float(self.camera.frame.get_width()) / factor
                self.camera.frame.set_width(new_w)
                if anchor and isinstance(anchor, (list, tuple)) and len(anchor) >= 2:
                    self.camera.frame.move_to([float(anchor[0]), float(anchor[1]), 0])
            except Exception:
                pass

        def camera_pan_to(pos, duration=0.6):
            try:
                if not isinstance(pos, (list, tuple)) or len(pos) < 2:
                    return
                safe_play(self.camera.frame.animate.move_to([float(pos[0]), float(pos[1]), 0]), run_time=float(duration))
            except Exception:
                pass

        def camera_set(frame_center=None, frame_width=None):
            try:
                if isinstance(frame_width, (int, float)) and frame_width > 0:
                    self.camera.frame.set_width(float(frame_width))
                if isinstance(frame_center, (list, tuple)) and len(frame_center) >= 2:
                    self.camera.frame.move_to([float(frame_center[0]), float(frame_center[1]), 0])
            except Exception:
                pass

        def _mobj_bbox(m):
            try:
                bb = m.get_bounding_box()
                w = max(1e-6, bb[1][0] - bb[0][0])
                h = max(1e-6, bb[1][1] - bb[0][1])
                return ((bb[0][0], bb[0][1]), (bb[1][0], bb[1][1]), w, h)
            except Exception:
                return None

        def get_bbox(ids):
            try:
                g = get_group(ids)
                if len(g) == 0:
                    return None
                bb = g.get_bounding_box()
                return ((bb[0][0], bb[0][1]), (bb[1][0], bb[1][1]))
            except Exception:
                return None

        def bbox_union(bboxes):
            try:
                xs = []
                ys = []
                for b in bboxes:
                    if not b:
                        continue
                    (x0, y0), (x1, y1) = b
                    xs += [x0, x1]
                    ys += [y0, y1]
                if not xs or not ys:
                    return None
                return ((min(xs), min(ys)), (max(xs), max(ys)))
            except Exception:
                return None

        def fits_in_view(bbox, margin=0.1):
            try:
                if not bbox:
                    return True
                (x0, y0), (x1, y1) = bbox
                bw = max(1e-6, x1 - x0)
                bh = max(1e-6, y1 - y0)
                fw = float(self.camera.frame.get_width())
                fh = float(self.camera.frame.get_height())
                return (bw <= fw * (1.0 - margin)) and (bh <= fh * (1.0 - margin))
            except Exception:
                return True

        # Track active objects and apply simple exit/camera policies
        active_ids = []

        def _is_axes(mobj):
            try:
                return 'Axes' in str(type(mobj))
            except Exception:
                return False

        def _priority_for(oid):
            try:
                t = id_to_meta.get(oid, {{}}).get('type', '')
                if t in ('text', 'dot'):
                    return 0  # secondary/annotation
                if t in ('line',):
                    return 1  # ephemeral/helpers
                if t in ('axes', 'plot', 'square', 'circle'):
                    return 2  # primary
                return 1
            except Exception:
                return 1

        def exit_minimize_to_corner(ids, corner="TR", scale=0.3, duration=0.4):
            try:
                target = {{
                    'TR': RIGHT*5 + UP*3,
                    'TL': LEFT*5 + UP*3,
                    'BR': RIGHT*5 + DOWN*3,
                    'BL': LEFT*5 + DOWN*3,
                }}.get(str(corner).upper(), RIGHT*5 + UP*3)
                anims = []
                for oid in ids:
                    m = id_to_mobject.get(oid)
                    if m is not None:
                        anims.append(m.animate.scale(float(scale)).move_to(target))
                if anims:
                    safe_play(*anims, run_time=duration)
            except Exception:
                pass

        def resolve_label_overlaps(group_ids, max_shifts=5, delta=0.3):
            """Enhanced overlap resolution with better collision detection"""
            try:
                labels = [id_to_mobject[i] for i in group_ids if i in id_to_mobject and id_to_meta.get(i, {{}}).get('type') == 'text']
                for _ in range(int(max_shifts)):
                    moved = False
                    for i in range(len(labels)):
                        for j in range(i+1, len(labels)):
                            bi = _mobj_bbox(labels[i])
                            bj = _mobj_bbox(labels[j])
                            if not bi or not bj:
                                continue
                            (ai0, aj0), (ai1, aj1), wi, hi = bi
                            (bi0, bj0), (bi1, bj1), wj, hj = bj
                            overlap = not (ai1 < bi0 or bi1 < ai0 or aj1 < bj0 or bj1 < aj0)
                            if overlap:
                                # Try different directions to avoid overlaps
                                directions = [RIGHT, LEFT, UP, DOWN, RIGHT+UP, RIGHT+DOWN, LEFT+UP, LEFT+DOWN]
                                for direction in directions:
                                    test_pos = labels[j].get_center() + direction * float(delta)
                                    # Check if this position avoids overlap
                                    labels[j].move_to(test_pos)
                                    new_bj = _mobj_bbox(labels[j])
                                    if new_bj:
                                        (new_bi0, new_bj0), (new_bi1, new_bj1), _, _ = new_bj
                                        new_overlap = not (ai1 < new_bi0 or new_bi1 < ai0 or aj1 < new_bj0 or new_bj1 < aj0)
                                        if not new_overlap:
                                            moved = True
                                            break
                                if not moved:
                                    # Fallback: move in original direction
                                    labels[j].shift(RIGHT*float(delta))
                                    moved = True
                    if not moved:
                        break
            except Exception:
                pass

        def resolve_object_overlaps():
            """Resolve overlaps between all objects, not just labels"""
            try:
                all_objects = list(id_to_mobject.values())
                for i in range(len(all_objects)):
                    for j in range(i+1, len(all_objects)):
                        obj1, obj2 = all_objects[i], all_objects[j]
                        
                        # Get bounding boxes
                        bbox1 = _mobj_bbox(obj1)
                        bbox2 = _mobj_bbox(obj2)
                        
                        if not bbox1 or not bbox2:
                            continue
                        
                        (x1_0, y1_0), (x1_1, y1_1), w1, h1 = bbox1
                        (x2_0, y2_0), (x2_1, y2_1), w2, h2 = bbox2
                        
                        # Check for overlap
                        overlap_x = not (x1_1 < x2_0 or x2_1 < x1_0)
                        overlap_y = not (y1_1 < y2_0 or y2_1 < y1_0)
                        
                        if overlap_x and overlap_y:
                            # Calculate separation distance
                            separation = max(w1, w2, h1, h2) * 0.3
                            
                            # Move objects apart
                            center1 = obj1.get_center()
                            center2 = obj2.get_center()
                            
                            # Calculate direction vector
                            direction = center2 - center1
                            if direction.norm() < 0.1:
                                direction = RIGHT  # Default direction if objects are at same position
                            else:
                                direction = direction.normalize()
                            
                            # Move objects apart
                            obj1.move_to(center1 - direction * separation * 0.5)
                            obj2.move_to(center2 + direction * separation * 0.5)
                            
            except Exception:
                pass

        def resolve_graph_overlaps():
            """Specialized overlap resolution for graphs and mathematical objects"""
            try:
                # Get all graph-like objects (plots, axes, functions)
                graph_objects = []
                for oid, mobj in id_to_mobject.items():
                    obj_type = id_to_meta.get(oid, {{}}).get('type', '')
                    if obj_type in ['plot', 'axes', 'function', 'graph']:
                        graph_objects.append((oid, mobj))
                
                if len(graph_objects) < 2:
                    return
                
                # Check for overlaps between graphs
                for i in range(len(graph_objects)):
                    for j in range(i+1, len(graph_objects)):
                        oid1, obj1 = graph_objects[i]
                        oid2, obj2 = graph_objects[j]
                        
                        bbox1 = _mobj_bbox(obj1)
                        bbox2 = _mobj_bbox(obj2)
                        
                        if not bbox1 or not bbox2:
                            continue
                        
                        (x1_0, y1_0), (x1_1, y1_1), w1, h1 = bbox1
                        (x2_0, y2_0), (x2_1, y2_1), w2, h2 = bbox2
                        
                        # Check for significant overlap
                        overlap_x = not (x1_1 < x2_0 or x2_1 < x1_0)
                        overlap_y = not (y1_1 < y2_0 or y2_1 < y1_0)
                        
                        if overlap_x and overlap_y:
                            # Calculate overlap area
                            overlap_area = min(w1, w2) * min(h1, h2)
                            total_area = w1 * h1 + w2 * h2
                            overlap_ratio = overlap_area / total_area if total_area > 0 else 0
                            
                            if overlap_ratio > 0.3:  # Significant overlap
                                # Strategy 1: Try to separate graphs horizontally
                                if w1 + w2 < 12:  # If both graphs can fit side by side
                                    # Move first graph to left, second to right
                                    left_pos = [-6 + w1/2, 0, 0]
                                    right_pos = [6 - w2/2, 0, 0]
                                    
                                    safe_play(obj1.animate.move_to(left_pos), run_time=0.8)
                                    safe_play(obj2.animate.move_to(right_pos), run_time=0.8)
                                    
                                    # Adjust camera to show both graphs
                                    dynamic_camera_adjust(active_ids, target_margin=0.4)
                                    
                                else:
                                    # Strategy 2: Fade out older graph and zoom camera for new one
                                    older_graph = obj1 if oid1 < oid2 else obj2
                                    newer_graph = obj2 if oid1 < oid2 else obj1
                                    
                                    # Fade out older graph
                                    safe_play(FadeOut(older_graph), run_time=0.6)
                                    
                                    # Center camera on newer graph with zoom
                                    newer_center = newer_graph.get_center()
                                    safe_play(self.camera.frame.animate.move_to(newer_center).set_width(8), run_time=0.8)
                                    
                                    # Remove older graph from active list
                                    if oid1 < oid2 and oid1 in active_ids:
                                        active_ids.remove(oid1)
                                    elif oid2 < oid1 and oid2 in active_ids:
                                        active_ids.remove(oid2)
                                    
            except Exception:
                pass

        def smart_graph_positioning(graph_data):
            """Intelligent positioning for graphs to avoid overlaps"""
            try:
                if not graph_data:
                    return
                
                # Sort graphs by priority (axes first, then plots, then functions)
                priority_order = {{'axes': 0, 'plot': 1, 'function': 2, 'graph': 3}}
                sorted_graphs = sorted(graph_data, key=lambda x: priority_order.get(x.get('type', 'plot'), 1))
                
                # Define screen regions for different graph types
                screen_regions = {{
                    'axes': {{'x_range': [-8, 8], 'y_range': [-6, 6]}},
                    'plot': {{'x_range': [-6, 6], 'y_range': [-4, 4]}},
                    'function': {{'x_range': [-5, 5], 'y_range': [-3, 3]}}
                }}
                
                used_regions = []
                
                for graph in sorted_graphs:
                    graph_type = graph.get('type', 'plot')
                    props = graph.get('properties', {{}})
                    
                    # Find available region
                    best_region = None
                    min_overlap = float('inf')
                    
                    for region in screen_regions.get(graph_type, screen_regions['plot']):
                        x_range = region['x_range']
                        y_range = region['y_range']
                        
                        # Check overlap with existing regions
                        overlap_count = 0
                        for used in used_regions:
                            if (x_range[0] < used['x_range'][1] and x_range[1] > used['x_range'][0] and
                                y_range[0] < used['y_range'][1] and y_range[1] > used['y_range'][0]):
                                overlap_count += 1
                        
                        if overlap_count < min_overlap:
                            min_overlap = overlap_count
                            best_region = region
                        
                        if overlap_count == 0:
                            break
                    
                    if best_region:
                        # Update graph position to use this region
                        center_x = (best_region['x_range'][0] + best_region['x_range'][1]) / 2
                        center_y = (best_region['y_range'][0] + best_region['y_range'][1]) / 2
                        props['position'] = [center_x, center_y, 0]
                        
                        # Update graph bounds if they exist
                        if 'x_range' not in props:
                            props['x_range'] = best_region['x_range']
                        if 'y_range' not in props:
                            props['y_range'] = best_region['y_range']
                        
                        used_regions.append(best_region)
                        
            except Exception:
                pass

        def resolve_label_overlaps(group_ids, max_shifts=5, delta=0.3):
            """Enhanced overlap resolution with better collision detection"""
            try:
                labels = [id_to_mobject[i] for i in group_ids if i in id_to_mobject and id_to_meta.get(i, {{}}).get('type') == 'text']
                for _ in range(int(max_shifts)):
                    moved = False
                    for i in range(len(labels)):
                        for j in range(i+1, len(labels)):
                            bi = _mobj_bbox(labels[i])
                            bj = _mobj_bbox(labels[j])
                            if not bi or not bj:
                                continue
                            (ai0, aj0), (ai1, aj1), wi, hi = bi
                            (bi0, bj0), (bi1, bj1), wj, hj = bj
                            overlap = not (ai1 < bi0 or bi1 < ai0 or aj1 < bj0 or bj1 < aj0)
                            if overlap:
                                # Try different directions to avoid overlaps
                                directions = [RIGHT, LEFT, UP, DOWN, RIGHT+UP, RIGHT+DOWN, LEFT+UP, LEFT+DOWN]
                                for direction in directions:
                                    test_pos = labels[j].get_center() + direction * float(delta)
                                    # Check if this position avoids overlap
                                    labels[j].move_to(test_pos)
                                    new_bj = _mobj_bbox(labels[j])
                                    if new_bj:
                                        (new_bi0, new_bj0), (new_bi1, new_bj1), _, _ = new_bj
                                        new_overlap = not (ai1 < new_bi0 or new_bi1 < ai0 or aj1 < new_bj0 or new_bj1 < aj0)
                                        if not new_overlap:
                                            moved = True
                                            break
                                if not moved:
                                    # Fallback: move in original direction
                                    labels[j].shift(RIGHT*float(delta))
                                    moved = True
                    if not moved:
                        break
            except Exception:
                pass

        def smart_position_objects(objects_data):
            """Smart positioning system to prevent overlaps and ensure good distribution"""
            try:
                if not objects_data:
                    return
                
                # Create a grid-based positioning system
                grid_size = 2.0
                grid_margin = 0.5
                used_positions = set()
                
                for obj_data in objects_data:
                    obj_type = obj_data.get('type', 'circle')
                    props = obj_data.get('properties', {{}})
                    
                    # Get object size for collision detection
                    if obj_type == 'circle':
                        size = props.get('size', 1.0) * 2  # diameter
                    elif obj_type == 'square':
                        size = props.get('size', 2.0)
                    elif obj_type == 'text':
                        size = max(1.0, props.get('size', 36) / 20)  # approximate text width
                    else:
                        size = 1.0
                    
                    # Find a good position that doesn't overlap
                    best_pos = [0, 0, 0]
                    min_overlap = float('inf')
                    
                    # Try grid positions first
                    for x in range(-3, 4):
                        for y in range(-2, 3):
                            test_pos = [x * grid_size, y * grid_size, 0]
                            
                            # Check overlap with existing objects
                            overlap_count = 0
                            for used_pos in used_positions:
                                dist = ((test_pos[0] - used_pos[0])**2 + (test_pos[1] - used_pos[1])**2)**0.5
                                if dist < (size + grid_margin):
                                    overlap_count += 1
                            
                            if overlap_count < min_overlap:
                                min_overlap = overlap_count
                                best_pos = test_pos
                            
                            if overlap_count == 0:
                                break
                        if min_overlap == 0:
                            break
                    
                    # Update object position
                    props['position'] = best_pos
                    used_positions.add(tuple(best_pos))
                    
            except Exception:
                pass

        def policy_exit_before(new_type):
            try:
                major_types = {"axes", "plot", "square", "circle", "line"}
                if str(new_type).lower() not in major_types:
                    return
                # Keep axes by default, prefer removing low-priority items first
                keep = []
                for oid in list(active_ids):
                    m = id_to_mobject.get(oid)
                    if m is not None and _is_axes(m):
                        keep.append(oid)
                others = [oid for oid in list(active_ids) if oid not in keep]
                # Sort by priority low->high
                others.sort(key=_priority_for)
                # Try camera fit first with current + incoming kept
                try:
                    union = get_bbox(keep + others)
                    if not fits_in_view(union, margin=0.15):
                        camera_fit(keep + others, margin=0.12)
                        camera_pad(0.04)
                except Exception:
                    pass
                # If still crowded, fade lowest priority half
                try:
                    union2 = get_bbox(keep + others)
                    if not fits_in_view(union2, margin=0.15) and others:
                        cut = max(1, len(others)//2)
                        to_drop = others[:cut]
                        exit_fade(to_drop, duration=0.25)
                        for oid in to_drop:
                            try:
                                active_ids.remove(oid)
                            except Exception:
                                pass
                except Exception:
                    pass
            except Exception:
                pass

        def activate(oid):
            try:
                if oid and oid not in active_ids:
                    active_ids.append(oid)
            except Exception:
                pass

        # Camera settings
        try:
            _cam = {animation_spec.get('camera_settings', {})}
            _zoom = _cam.get('zoom', 1.0)
            _pos = _cam.get('position', [0, 0, 0])
            # Interpret zoom as a factor: higher => more zoom-in (smaller frame width)
            _frame_width = 14 / _zoom if isinstance(_zoom, (int, float)) and _zoom not in (0, None) else 14
            self.camera.frame.set(width=_frame_width)
            self.camera.frame.move_to([{', '.join(map(str, animation_spec.get('camera_settings', {}).get('position', [0, 0, 0])))}])
        except Exception:
            pass

        # Log resolved bounds for reproducibility (avoid braces in outer f-string)
        try:
            _bx = ({x_bounds[0]}, {x_bounds[1]})
            _by = ({y_bounds[0]}, {y_bounds[1]})
            print("Resolved bounds: x=", _bx, " y=", _by)
        except Exception:
            pass
        
        # Create objects and animations
        def _safe_eval(expr, x):
            try:
                allowed = {{
                    'np': np,
                    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                    'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                    'abs': np.abs, 'pi': np.pi, 'e': np.e,
                    'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
                }}
                allowed_dict = {{**allowed, 'x': x}}
                return eval(expr, {{"__builtins__": {{}}}}, allowed_dict)
            except Exception:
                return 0
'''
            
            # Generate objects and animations
            axes_defined = False
            for _idx, obj in enumerate(animation_spec.get('objects', [])):
                obj_id = obj.get('id') or f"obj_{_idx}"
                obj_type = obj.get('type', 'circle')
                props = obj.get('properties', {})
                animations = obj.get('animations', [])
                
                # Create object with enhanced color contrast
                if obj_type == 'circle':
                    color = props.get('color', 'WHITE')
                    # Ensure bright, visible colors on dark background
                    if color.upper() in ['BLACK', '#000000', '#000']:
                        color = 'WHITE'
                    manim_code += f'''
        # Create {obj_type}
        {obj_type}_obj = None
        try:
            policy_exit_before("{obj_type}")
            {obj_type}_obj = Circle(
                radius={props.get('size', 1)},
                color=safe_color("{color}"),
                fill_opacity=0.8,
                stroke_width=2
            )
            {obj_type}_obj.move_to([{', '.join(map(str, props.get('position', [0, 0, 0])))}])
            safe_play(Create({obj_type}_obj), run_time=0.5)
            try:
                reg("{obj_id}", {obj_type}_obj, {int(props.get('z_index', 100))})
                activate("{obj_id}")
                # Resolve any overlaps after adding new object
                resolve_object_overlaps()
                # Use dynamic camera adjustment for better framing
                dynamic_camera_adjust(active_ids, target_margin=0.25)
            except Exception:
                pass
        except Exception:
            {obj_type}_obj = None
'''
                elif obj_type == 'square':
                    color = props.get('color', 'CYAN')
                    if color.upper() in ['BLACK', '#000000', '#000']:
                        color = 'CYAN'
                    manim_code += f'''
        # Create {obj_type}
        {obj_type}_obj = None
        try:
            policy_exit_before("{obj_type}")
            {obj_type}_obj = Square(
                side_length={props.get('size', 2)},
                color=safe_color("{color}"),
                fill_opacity=0.8,
                stroke_width=2
            )
            {obj_type}_obj.move_to([{', '.join(map(str, props.get('position', [0, 0, 0])))}])
            safe_play(Create({obj_type}_obj), run_time=0.5)
        
            try:
                reg("{obj_id}", {obj_type}_obj, {int(props.get('z_index', 100))})
                activate("{obj_id}")
                # Resolve any overlaps after adding new object
                resolve_object_overlaps()
                # Use dynamic camera adjustment for better framing
                dynamic_camera_adjust(active_ids, target_margin=0.25)
            except Exception:
                pass
        except Exception:
            {obj_type}_obj = None
'''
                elif obj_type == 'text':
                    color = props.get('color', 'WHITE')
                    if color.upper() in ['BLACK', '#000000', '#000']:
                        color = 'WHITE'
                    manim_code += f'''
        # Create {obj_type}
        {obj_type}_obj = None
        try:
            # Text is secondary; may not trigger exit
            {obj_type}_obj = Text(
                "{props.get('text', 'Hello')}",
                color=safe_color("{color}"),
                font_size={props.get('size', 36)}
            )
            {obj_type}_obj.move_to([{', '.join(map(str, props.get('position', [0, 0, 0])))}])
            safe_play(Write({obj_type}_obj), run_time=0.5)
            try:
                reg("{obj_id}", {obj_type}_obj, {int(props.get('z_index', 200))})
                activate("{obj_id}")
            except Exception:
                pass
        except Exception:
            {obj_type}_obj = None
'''
                elif obj_type == 'line':
                    start = props.get('start', [-2, 0, 0])
                    end = props.get('end', [2, 0, 0])
                    color = props.get('color', 'YELLOW')
                    if color.upper() in ['BLACK', '#000000', '#000']:
                        color = 'YELLOW'
                    manim_code += f'''
        # Create {obj_type}
        {obj_type}_obj = None
        try:
            policy_exit_before("{obj_type}")
            {obj_type}_obj = Line(
                start=[{', '.join(map(str, start))}],
                end=[{', '.join(map(str, end))}],
                color=safe_color("{color}"),
                stroke_width=3
            )
            safe_play(Create({obj_type}_obj), run_time=0.5)
            try:
                reg("{obj_id}", {obj_type}_obj, {int(props.get('z_index', 150))})
                activate("{obj_id}")
                # Resolve any overlaps after adding new object
                resolve_object_overlaps()
                # Use dynamic camera adjustment for better framing
                dynamic_camera_adjust(active_ids, target_margin=0.25)
            except Exception:
                pass
        except Exception:
            {obj_type}_obj = None
'''
                elif obj_type == 'dot':
                    color = props.get('color', 'YELLOW')
                    if color.upper() in ['BLACK', '#000000', '#000']:
                        color = 'YELLOW'
                    manim_code += f'''
        # Create {obj_type}
        {obj_type}_obj = None
        try:
            # Dot is secondary; may not trigger exit
            {obj_type}_obj = Dot(
                point=[{', '.join(map(str, props.get('position', [0, 0, 0])))}],
                color=safe_color("{color}"),
                radius=0.1
            )
            safe_play(FadeIn({obj_type}_obj), run_time=0.5)
            try:
                reg("{obj_id}", {obj_type}_obj, {int(props.get('z_index', 250))})
                activate("{obj_id}")
            except Exception:
                pass
        except Exception:
            {obj_type}_obj = None
'''
                elif obj_type == 'axes':
                    axes_defined = True
                    xr = props.get('x_range', [-5, 5, 1])
                    yr = props.get('y_range', [-3, 3, 1])
                    show_labels = props.get('show_labels', True)
                    manim_code += f'''
        # Create coordinate axes with enhanced visibility
        axes_obj = None
        try:
            policy_exit_before("{obj_type}")
            axes_obj = Axes(
                x_range=[{', '.join(map(str, xr))}],
                y_range=[{', '.join(map(str, yr))}],
                tips=False,
                axis_config={{
                    "stroke_color": "WHITE",
                    "stroke_width": 2,
                    "font_size": 24,
                    "color": "WHITE"
                }}
            )
            # Add default axis numbers safely (no custom tick computation)
            try:
                axes_obj.get_x_axis().add_numbers()
                axes_obj.get_y_axis().add_numbers()
            except Exception:
                pass
            safe_play(Create(axes_obj), run_time=0.8)
            try:
                reg("{obj_id}", axes_obj, {int(props.get('z_index', 80))})
                activate("{obj_id}")
                
                # Smart screen management for axes
                strategy = smart_screen_management("axes")
                execute_screen_strategy(strategy, axes_obj)
                
                # Resolve any remaining overlaps
                resolve_graph_overlaps()
                
                # Use dynamic camera adjustment for optimal viewing
                dynamic_camera_adjust(active_ids, target_margin=0.25)
            except Exception:
                pass
        except Exception:
            axes_obj = None
'''
                    if show_labels:
                        manim_code += '''
        x_label = axes_obj.get_x_axis_label(Text("x", color="WHITE", font_size=28))
        y_label = axes_obj.get_y_axis_label(Text("y", color="WHITE", font_size=28))
        safe_play(FadeIn(x_label), FadeIn(y_label), run_time=0.5)
'''
                elif obj_type == 'plot':
                    expr = props.get('expression', 'sin(x)')
                    xrp = props.get('x_range_plot', [-5, 5])
                    color = props.get('color', 'CYAN')
                    if color.upper() in ['BLACK', '#000000', '#000']:
                        color = 'CYAN'
                    # Ensure axes_obj exists
                    manim_code += f'''
        # Plot function with enhanced visibility
        try:
            if 'axes_obj' not in locals() or axes_obj is None:
                axes_obj = Axes(
                    x_range=[-5,5,1], 
                    y_range=[-3,3,1], 
                    tips=False,
                    axis_config={{
                        "stroke_color": "WHITE",
                        "stroke_width": 2,
                        "font_size": 24,
                        "color": "WHITE"
                    }}
                )
                try:
                    axes_obj.get_x_axis().add_numbers()
                    axes_obj.get_y_axis().add_numbers()
                except Exception:
                    pass
                safe_play(Create(axes_obj), run_time=0.8)
            policy_exit_before("{obj_type}")
            graph_obj = axes_obj.plot(
                lambda x: _safe_eval(r"""{expr}""", x), 
                x_range=({xrp[0]}, {xrp[1]}), 
                color=safe_color("{color}"),
                stroke_width=3
            )
            safe_play(Create(graph_obj), run_time=0.8)
            try:
                reg("{obj_id}", graph_obj, {int(props.get('z_index', 120))})
                activate("{obj_id}")
                
                # Smart screen management for graphs
                strategy = smart_screen_management("plot")
                execute_screen_strategy(strategy, graph_obj)
                
                # Resolve any remaining overlaps
                resolve_graph_overlaps()
                
                # Use dynamic camera adjustment for optimal viewing
                dynamic_camera_adjust(active_ids, target_margin=0.25)
            except Exception:
                pass
        except Exception:
            pass
'''
                
                # Add animations
                for i, anim in enumerate(animations):
                    anim_type = anim.get('type', 'move')
                    duration = anim.get('duration', 1)
                    
                    if anim_type == 'move':
                        target_pos = anim.get('parameters', {}).get('target_position', [1, 1, 0])
                        manim_code += f'''
        # Animate {obj_type} {anim_type}
        try:
            safe_play({obj_type}_obj.animate.move_to([{', '.join(map(str, target_pos))}]), run_time={duration})
        except Exception:
            pass
'''
                    elif anim_type == 'scale':
                        scale_factor = anim.get('parameters', {}).get('scale_factor', 1.5)
                        manim_code += f'''
        # Animate {obj_type} {anim_type}
        try:
            safe_play({obj_type}_obj.animate.scale({scale_factor}), run_time={duration})
        except Exception:
            pass
'''
                    elif anim_type == 'rotate':
                        angle = anim.get('parameters', {}).get('angle', PI/2)
                        manim_code += f'''
        # Animate {obj_type} {anim_type}
        try:
            safe_play(Rotate({obj_type}_obj, angle={angle}), run_time={duration})
        except Exception:
            pass
'''
                    elif anim_type == 'fade_in':
                        manim_code += f'''
        # Animate {obj_type} {anim_type}
        try:
            safe_play(FadeIn({obj_type}_obj), run_time={duration})
        except Exception:
            pass
'''
                    elif anim_type == 'fade_out':
                        manim_code += f'''
        # Animate {obj_type} {anim_type}
        try:
            safe_play(FadeOut({obj_type}_obj), run_time={duration})
        except Exception:
            pass
'''
            
            # Final overlap resolution and camera adjustment
            manim_code += '''
        # Final overlap resolution and camera optimization
        try:
            # Resolve graph-specific overlaps first
            resolve_graph_overlaps()
            # Resolve any remaining object overlaps
            resolve_object_overlaps()
            # Final camera adjustment for optimal viewing
            dynamic_camera_adjust(active_ids, target_margin=0.3)
            # Resolve label overlaps specifically
            resolve_label_overlaps(active_ids)
            # Final screen space optimization
            if len([oid for oid in active_ids if id_to_meta.get(oid, {{}}).get('type') in ['plot', 'axes', 'function', 'graph']]) > 1:
                # Multiple graphs - ensure optimal spacing
                dynamic_camera_adjust(active_ids, target_margin=0.4)
        except Exception:
            pass
        
        # Final pause
        try:
            self.wait(2)
        except Exception:
            pass
'''
            
            logger.info("Successfully generated Manim code")
            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            raise

    async def process_animation_request(self, prompt: str) -> Dict[str, Any]:
        """
        Complete animation processing workflow
        """
        try:
            # Step 1: Generate animation specification
            animation_spec = await self.generate_animation_spec(prompt)
            
            # Step 2: Convert to Manim code
            manim_code = self.generate_manim_code(animation_spec)
            
            return {
                "animation_spec": animation_spec,
                "manim_code": manim_code,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in animation processing workflow: {e}")
            return {"status": "failed", "error": str(e)}

    async def _try_local_fallback(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Attempt to generate a spec using a local inference service if available."""
        local_url = os.getenv("LOCAL_INFERENCE_URL")
        if not local_url:
            return None
        try:
            timeout = httpx.Timeout(20.0, connect=5.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(local_url, json={"prompt": prompt})
                if resp.status_code != 200:
                    logger.error(f"Local fallback returned {resp.status_code}")
                    return None
                data = resp.json()
                spec = data.get("animation_spec") or data
                if not isinstance(spec, dict):
                    return None
                # Normalize like primary path
                normalized: Dict[str, Any] = {
                    "animation_type": spec.get("animation_type", "geometric"),
                    "scene_description": spec.get("scene_description", f"Animation for: {prompt}"),
                    "objects": spec.get("objects") or [],
                    "camera_settings": spec.get("camera_settings") or {"position": [0, 0, 0], "zoom": 8},
                    "duration": spec.get("duration", 5),
                    "background_color": spec.get("background_color", "#000000"),
                    "style": spec.get("style", "modern"),
                }
                if not isinstance(normalized["objects"], list):
                    normalized["objects"] = []
                if not normalized["objects"]:
                    normalized["objects"].append({
                        "type": "text",
                        "properties": {"text": prompt, "color": "WHITE", "size": 36, "position": [0, 0, 0]},
                        "animations": []
                    })
                logger.info("Local fallback produced an animation spec")
                return normalized
        except Exception as ex:
            logger.error(f"Local fallback error: {ex}")
            return None


_ai_service_singleton: Optional[AIService] = None

def get_ai_service() -> AIService:
    global _ai_service_singleton
    if _ai_service_singleton is None:
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_AI_API_KEY is not set")
        _ai_service_singleton = AIService(api_key=api_key)
    return _ai_service_singleton
