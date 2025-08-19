from __future__ import annotations

from typing import List, Dict


MANIM_SNIPPETS: List[Dict[str, str]] = [
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
]


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


