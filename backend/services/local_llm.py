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
            "Return ONLY a JSON object for a Manim scene with keys: scene_name (CamelCase string), "
            "background_color (hex string), resolution ([int,int]), imports (list of strings), "
            "objects (list of {name,type,props}), animations (list of {type,target,duration,parameters,wait_after}). "
            "Object types: circle, square, triangle, text, line, dot. Animation types: create, transform, move, rotate, scale, fade, wait. "
            "Do not include markdown or code fences. No explanations."
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

        if "circle" in p:
            color = "BLUE" if "blue" in p else "RED" if "red" in p else "WHITE"
            objects.append({"name": "obj", "type": "circle", "props": {"radius": 1.2, "color": color}})
        elif "rectangle" in p or "rect" in p:
            objects.append({"name": "obj", "type": "rectangle", "props": {"width": 4.0, "height": 2.0, "color": "GREEN"}})
        else:
            objects.append({"name": "obj", "type": "square", "props": {"side_length": 2.0, "color": "YELLOW"}})

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


