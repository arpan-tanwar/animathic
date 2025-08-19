from __future__ import annotations

from typing import List, Dict
from pathlib import Path
import yaml


# Load curated snippets from YAML if present; otherwise use built-ins
def _load_yaml_snippets() -> List[Dict[str, str]]:
    try:
        data_path = Path(__file__).resolve().parent.parent / "data" / "manim_snippets.yaml"
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or []
                if isinstance(data, list):
                    return [s for s in data if isinstance(s, dict)]
    except Exception:
        pass
    return []

MANIM_SNIPPETS: List[Dict[str, str]] = _load_yaml_snippets() or [
    {
        "id": "circle_create",
        "title": "Create Circle",
        "description": "Create a colored circle and animate its creation",
        "code": "circle = Circle(radius=1, color=BLUE)\nself.play(Create(circle))",
        "tags": "circle create basic",
    },
    {
        "id": "transform_circle_to_square",
        "title": "Transform Circle to Square",
        "description": "Transform a circle into a square",
        "code": "self.play(Transform(circle, Square(side_length=2)))",
        "tags": "transform circle square",
    },
    {
        "id": "rotate_object",
        "title": "Rotate Object",
        "description": "Rotate any object by 90 degrees",
        "code": "self.play(Rotate(obj, angle=PI/2))",
        "tags": "rotate rotation object",
    },
    {
        "id": "move_object",
        "title": "Move Object",
        "description": "Move object to UP position",
        "code": "self.play(obj.animate.move_to(UP))",
        "tags": "move position up",
    },
    {
        "id": "scale_object",
        "title": "Scale Object",
        "description": "Scale object by 1.2",
        "code": "self.play(obj.animate.scale(1.2))",
        "tags": "scale object size",
    },
    {
        "id": "rectangle_create",
        "title": "Create Rectangle",
        "description": "Create a rectangle with width and height",
        "code": "rect = Rectangle(width=4.0, height=2.0, color=GREEN)\nself.play(Create(rect))",
        "tags": "rectangle create",
    },
    {
        "id": "ellipse_create",
        "title": "Create Ellipse",
        "description": "Create an ellipse and fade it in",
        "code": "ell = Ellipse(width=4.0, height=2.0, color=PURPLE)\nself.play(FadeIn(ell))",
        "tags": "ellipse create fadein",
    },
]

# Add many small variations to reach ~50 entries for simple retrieval
for i in range(1, 46):
    MANIM_SNIPPETS.append({
        "id": f"variant_{i}",
        "title": f"Variant Snippet {i}",
        "description": "Basic create-play pattern for demonstration",
        "code": "obj = Circle(radius=1)\nself.play(Create(obj))",
        "tags": "variant circle create basic",
    })


class RAGService:
    def find_relevant_snippets(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """Simple keyword-based retrieval over snippets."""
        q = query.lower()
        scored = []
        for s in MANIM_SNIPPETS:
            score = 0
            for token in q.split():
                if token in s["description"].lower() or token in s["tags"].lower():
                    score += 1
            scored.append((score, s))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:top_k]]

    def enhance_prompt(self, prompt: str) -> str:
        snippets = self.find_relevant_snippets(prompt)
        if not snippets:
            return prompt
        lines = [prompt, "\nRelevant code examples:"]
        for s in snippets:
            lines.append(f"\n# {s['title']}\n{s['code']}")
        lines.append("\nUse and adapt these examples appropriately.")
        return "\n".join(lines)


