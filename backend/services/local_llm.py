from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

import httpx

from schemas.manim_schema import ManimScene


class LocalLLMService:
    """Minimal Ollama client to generate structured JSON for Manim scenes."""

    def __init__(self, model_name: str = "codellama:7b-instruct-q4_K_M", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    async def generate_structured_scene(self, prompt: str) -> ManimScene:
        """Ask the local LLM to produce a ManimScene JSON and parse it into Pydantic model."""
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

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()

        text: str = data.get("response", "")
        json_str = self._extract_json(text)
        return ManimScene.model_validate_json(json_str)

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


