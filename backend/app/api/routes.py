from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
import os
import subprocess
import uuid
from ..services.openai_service import generate_manim_code
from ..services.manim_service import render_animation

router = APIRouter()

# Store job statuses
job_statuses: Dict[str, dict] = {}

class AnimationRequest(BaseModel):
    prompt: str
    previous_code: Optional[str] = None

class AnimationResponse(BaseModel):
    job_id: str
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None

@router.post("/generate")
async def generate_animation(request: AnimationRequest, background_tasks: BackgroundTasks):
    try:
        # Generate unique ID for this animation
        animation_id = str(uuid.uuid4())
        
        # Initialize job status
        job_statuses[animation_id] = {
            "status": "pending",
            "video_url": None,
            "error": None
        }
        
        # Add background task for processing
        background_tasks.add_task(
            process_animation,
            animation_id,
            request.prompt,
            request.previous_code
        )
        
        return AnimationResponse(
            job_id=animation_id,
            status="pending"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_animation(animation_id: str, prompt: str, previous_code: Optional[str] = None):
    try:
        # Generate Manim code using GPT-4
        manim_code = await generate_manim_code(prompt, previous_code)
        
        # Save the code to a temporary file
        code_file = f"temp_{animation_id}.py"
        with open(code_file, "w") as f:
            f.write(manim_code)
        
        # Render the animation
        video_path = await render_animation(code_file, animation_id)
        
        # Clean up the temporary code file
        os.remove(code_file)
        
        # Update job status
        job_statuses[animation_id] = {
            "status": "completed",
            "video_url": f"/media/videos/temp_{animation_id}/480p15/MyScene.mp4",
            "error": None
        }
        
    except Exception as e:
        job_statuses[animation_id] = {
            "status": "failed",
            "video_url": None,
            "error": str(e)
        }

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in job_statuses:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = job_statuses[job_id]
    return {
        "status": status["status"],
        "video_url": status["video_url"],
        "error": status["error"]
    }

@router.post("/refine")
async def refine_animation(request: AnimationRequest, background_tasks: BackgroundTasks):
    try:
        if not request.previous_code:
            raise HTTPException(status_code=400, detail="Previous code is required for refinement")
            
        # Generate unique ID for this animation
        animation_id = str(uuid.uuid4())
        
        # Initialize job status
        job_statuses[animation_id] = {
            "status": "pending",
            "video_url": None,
            "error": None
        }
        
        # Add background task for processing
        background_tasks.add_task(
            process_animation,
            animation_id,
            request.prompt,
            request.previous_code
        )
        
        return AnimationResponse(
            job_id=animation_id,
            status="pending"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 