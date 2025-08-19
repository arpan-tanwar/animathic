from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional
import os

import httpx

from schemas.manim_schema import ManimScene


class LocalLLMService:
    """Minimal Ollama client to generate structured JSON for Manim scenes."""

    def __init__(self, model_name: Optional[str] = None, base_url: Optional[str] = None):
        env_model = os.getenv("OLLAMA_MODEL", "codellama:7b-instruct-q4_K_M")
        env_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = (model_name or env_model)
        self.base_url = (base_url or env_base).rstrip("/")
        # Optional direct inference server (FastAPI) that serves /generate
        # If set, this takes precedence over Ollama-compatible endpoint
        self.infer_url = os.getenv("LOCAL_INFER_URL", "").rstrip("/")

    async def generate_structured_scene(self, prompt: str) -> ManimScene:
        """Ask the local LLM to produce a ManimScene JSON and parse it into Pydantic model.
        Falls back to a heuristic structured scene on timeout or parse errors.
        """
        formatted = self._build_structured_prompt(prompt)
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "prompt": formatted,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_ctx": 4096,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, read=300.0, connect=10.0)) as client:
                if self.infer_url:
                    # Direct inference server, expects {"prompt": str, "max_new_tokens": int}
                    resp = await client.post(f"{self.infer_url}/generate", json={"prompt": formatted, "max_new_tokens": 400})
                    resp.raise_for_status()
                    data = resp.json()
                    # Expect {"json": {...}}
                    scene_obj = data.get("json")
                    if not scene_obj:
                        raise ValueError("Inference server returned no 'json' field")
                    return ManimScene.model_validate(scene_obj)
                else:
                    # Ollama-compatible fallback
                    resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    text: str = data.get("response", "")
                    json_str = self._extract_json(text)
                    return ManimScene.model_validate_json(json_str)
        except Exception:
            # Heuristic fallback: simple parser based on keywords
            return self._fallback_scene(prompt)

    def _build_structured_prompt(self, user_prompt: str) -> str:
        schema_hint = (
            "Return ONLY a JSON object with keys: scene_name, background_color, resolution, imports, objects, animations.\n"
            "imports MUST be ['from manim import *']\n"
            "objects: [{name: string, type: one of [axes,graph,circle,square,rectangle,ellipse,triangle,text,line,dot,number_line], props: object}]\n"
            "For graph: props MUST include function (e.g. 'lambda x: sin(x)') and axes (name of Axes object).\n"
            "animations: [{type: one of [create,transform,move,rotate,scale,fade,wait,set_color,set_stroke,set_fill], target: string, duration: number, parameters: object, wait_after: number}]\n"
            "No markdown. No code fences. JSON only."
        )
        return f"Task: Create a structured Manim animation for: {user_prompt}\n{schema_hint}\nJSON:"

    def _extract_json(self, text: str) -> str:
        # Remove markdown fences if present
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(json)?", "", text).strip()
            if text.endswith("```"):
                text = text[: -3].strip()

        # Try to find the first JSON object
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            candidate = m.group(0)
            # Quick validation
            json.loads(candidate)
            return candidate
        # Fallback: attempt loads directly
        json.loads(text)
        return text

    def _fallback_scene(self, prompt: str) -> ManimScene:
        p = prompt.lower()
        objects = []
        animations = []

        handled = False
        if any(k in p for k in ["sin", "cos", "sine", "cosine", "graph", "axes"]):
            # Fallback to a deterministic axes + sine/cos graph scene
            objects = [
                {"name": "axes", "type": "axes", "props": {"x_range": "[-5,5,1]", "y_range": "[-2,2,1]"}},
                {"name": "sin_graph", "type": "graph", "props": {"function": "lambda x: np.sin(x)", "axes": "axes", "color": "BLUE"}},
                {"name": "cos_graph", "type": "graph", "props": {"function": "lambda x: np.cos(x)", "axes": "axes", "color": "GREEN"}},
            ]
            animations = [
                {"type": "create", "target": "axes", "duration": 1.0, "parameters": {}, "wait_after": 0.2},
                {"type": "create", "target": "sin_graph", "duration": 1.2, "parameters": {}, "wait_after": 0.2},
                {"type": "create", "target": "cos_graph", "duration": 1.2, "parameters": {}, "wait_after": 0.2},
            ]
            handled = True
        elif "circle" in p:
            color = "BLUE" if "blue" in p else "RED" if "red" in p else "WHITE"
            objects.append({"name": "obj", "type": "circle", "props": {"radius": 1.2, "color": color}})
        elif "rectangle" in p or "rect" in p:
            objects.append({"name": "obj", "type": "rectangle", "props": {"width": 4.0, "height": 2.0, "color": "GREEN"}})
        else:
            objects.append({"name": "obj", "type": "square", "props": {"side_length": 2.0, "color": "YELLOW"}})
        if not handled:
            animations.append({"type": "create", "target": "obj", "duration": 1.0, "parameters": {}, "wait_after": 0.5})
            if "rotate" in p:
                animations.append({"type": "rotate", "target": "obj", "duration": 0.8, "parameters": {"angle": "PI/3"}, "wait_after": 0.5})
            if "scale" in p:
                animations.append({"type": "scale", "target": "obj", "duration": 0.8, "parameters": {"factor": 1.2}, "wait_after": 0.5})

        scene = {
            "scene_name": "GeneratedScene",
            "background_color": "#000000",
            "resolution": [1280, 720],
            "imports": ["from manim import *"],
            "objects": objects,
            "animations": animations,
        }
        return ManimScene.model_validate(scene)


