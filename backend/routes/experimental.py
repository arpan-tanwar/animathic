from __future__ import annotations

from fastapi import APIRouter, HTTPException

from services.local_llm import LocalLLMService
from services.manim_compiler import ManimCompiler
from services.rag_service import RAGService
from config import is_production


router = APIRouter(prefix="/api/exp", tags=["experimental"])


@router.post("/compile")
async def compile_from_prompt(payload: dict):
    """Generate structured JSON via local LLM, compile to Manim code, return code (no render)."""
    if is_production():
        raise HTTPException(status_code=404, detail="Not available in production")
    prompt = (payload or {}).get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt'")

    rag = RAGService()
    enhanced = rag.enhance_prompt(prompt)

    llm = LocalLLMService()
    scene = await llm.generate_structured_scene(enhanced)

    compiler = ManimCompiler()
    code = compiler.compile_to_manim(scene)
    return {"scene": scene.model_dump(), "code": code}


