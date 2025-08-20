"""
Animathic - Complete AI Animation Generator API

Complete workflow:
1. User provides prompt
2. Gemini 2.5 Flash generates structured JSON
3. JSON converts to Manim Python code
4. Code is compiled and provided to user
5. User feedback collected for fine-tuning
"""

import os
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import get_db, init_database
from models.database import User, Video, GenerationJob, Feedback
from schemas import (
    GenerateRequest, GenerateResponse, StatusResponse, 
    VideoResponse, FeedbackRequest, HealthResponse
)
from services.ai_service import get_ai_service

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Animathic API",
    description="AI-powered animation generation using Gemini and Manim",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_database()

# In-memory storage for generation jobs (in production, use Redis or database)
generation_jobs = {}

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Animathic API - AI Animation Generator",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "generate": "/api/generate",
            "status": "/api/status/{job_id}",
            "videos": "/api/videos",
            "feedback": "/api/feedback/{video_id}"
        },
        "workflow": [
            "1. Send prompt to /api/generate",
            "2. Poll /api/status/{job_id} for progress",
            "3. Download generated video",
            "4. Provide feedback for improvement"
        ]
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database="supabase"
    )

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_animation(
    request: GenerateRequest,
    db: Session = Depends(get_db)
):
    """Start animation generation process"""
    try:
        logger.info(f"Starting animation generation for user {request.user_id}")
        
        # Create or get user
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            user = User(id=request.user_id, email=f"user_{request.user_id}@example.com")
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create generation job
        job = GenerationJob(
            user_id=request.user_id,
            prompt=request.prompt,
            status="pending",
            current_step=0,
            total_steps=4
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Store job in memory for status tracking
        generation_jobs[job.id] = {
            "status": "pending",
            "current_step": 0,
            "total_steps": 4,
            "prompt": request.prompt,
            "user_id": request.user_id,
            "created_at": datetime.utcnow()
        }
        
        # Start async processing
        import asyncio
        asyncio.create_task(process_generation_job(job.id, request.prompt, db))
        
        return GenerateResponse(
            id=job.id,
            status="started",
            message="Animation generation started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error starting generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_generation_job(job_id: str, prompt: str, db: Session):
    """Process animation generation asynchronously"""
    try:
        logger.info(f"Processing generation job {job_id}")
        
        # Update job status
        generation_jobs[job_id]["status"] = "processing"
        generation_jobs[job_id]["current_step"] = 1
        
        # Step 1: Generate animation specification with Gemini
        logger.info(f"Step 1: Generating animation spec for job {job_id}")
        ai_result = await get_ai_service().process_animation_request(prompt)
        
        if ai_result["status"] == "failed":
            raise Exception(f"AI generation failed: {ai_result.get('error', 'Unknown error')}")
        
        # Update job with AI response
        generation_jobs[job_id]["current_step"] = 2
        generation_jobs[job_id]["ai_response"] = ai_result["animation_spec"]
        generation_jobs[job_id]["manim_code"] = ai_result["manim_code"]
        
        # Step 2: Create video record
        logger.info(f"Step 2: Creating video record for job {job_id}")
        video = Video(
            user_id=generation_jobs[job_id]["user_id"],
            prompt=prompt,
            status="completed",
            generation_job_id=job_id
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Step 3: Generate sample video URL (in production, this would be actual video generation)
        logger.info(f"Step 3: Generating video for job {job_id}")
        generation_jobs[job_id]["current_step"] = 3
        
        # For now, create a placeholder video URL
        video_url = f"/api/videos/{video.id}/download"
        video.video_url = video_url
        db.commit()
        
        # Update job status
        generation_jobs[job_id]["status"] = "completed"
        generation_jobs[job_id]["current_step"] = 4
        generation_jobs[job_id]["video_url"] = video_url
        
        logger.info(f"Generation job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing generation job {job_id}: {e}")
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = str(e)
        
        # Update video status if it exists
        try:
            video = db.query(Video).filter(Video.generation_job_id == job_id).first()
            if video:
                video.status = "failed"
                video.error_message = str(e)
                db.commit()
        except Exception as db_error:
            logger.error(f"Error updating video status: {db_error}")

@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_generation_status(job_id: str):
    """Get the status of a generation job"""
    try:
        if job_id not in generation_jobs:
            raise HTTPException(status_code=404, detail="Generation job not found")
        
        job = generation_jobs[job_id]
        
        return StatusResponse(
            id=job_id,
            status=job["status"],
            current_step=job["current_step"],
            total_steps=job["total_steps"],
            video_url=job.get("video_url"),
            error=job.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/videos", response_model=List[VideoResponse])
async def get_user_videos(
    user_id: str = Header(..., alias="user-id"),
    db: Session = Depends(get_db)
):
    """Get all videos for a user"""
    try:
        logger.info(f"Fetching videos for user {user_id}")
        
        videos = db.query(Video).filter(Video.user_id == user_id).all()
        
        return [VideoResponse.from_orm(video) for video in videos]
        
    except Exception as e:
        logger.error(f"Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """Get a specific video by ID"""
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return VideoResponse.from_orm(video)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/videos/{video_id}")
async def delete_video(
    video_id: str,
    user_id: str = Header(..., alias="user-id"),
    db: Session = Depends(get_db)
):
    """Delete a video"""
    try:
        video = db.query(Video).filter(
            Video.id == video_id,
            Video.user_id == user_id
        ).first()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        db.delete(video)
        db.commit()
        
        return {"message": "Video deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback/{video_id}")
async def submit_feedback(
    video_id: str,
    feedback: FeedbackRequest,
    user_id: str = Header(..., alias="user-id"),
    db: Session = Depends(get_db)
):
    """Submit feedback for a video"""
    try:
        # Check if video exists and belongs to user
        video = db.query(Video).filter(
            Video.id == video_id,
            Video.user_id == user_id
        ).first()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Create feedback record
        feedback_record = Feedback(
            user_id=user_id,
            video_id=video_id,
            rating=feedback.rating,
            feedback_text=feedback.feedback_text
        )
        
        db.add(feedback_record)
        db.commit()
        
        logger.info(f"Feedback submitted for video {video_id}: rating={feedback.rating}")
        
        return {"message": "Feedback submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/videos/{video_id}/download")
async def download_video(video_id: str, db: Session = Depends(get_db)):
    """Download a video file"""
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # For now, return a placeholder response
        # In production, this would serve the actual video file
        return JSONResponse(
            content={
                "message": "Video download endpoint",
                "video_id": video_id,
                "note": "This is a placeholder. In production, this would serve the actual video file."
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)