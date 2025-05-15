from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import traceback
import logging
from dotenv import load_dotenv
from services.storage import StorageService
from services.manim import ManimService
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Manim Generator",
    description="An AI-powered web application that generates mathematical animations using Manim",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the media directory for serving generated videos
app.mount("/media", StaticFiles(directory="media"), name="media")

# Initialize services
storage_service = StorageService()
manim_service = ManimService()

# Store video generation status
video_statuses: Dict[str, Dict[str, Any]] = {}

class GenerateRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None  # Make user_id optional for testing

class VideoResponse(BaseModel):
    id: str
    video_url: str
    metadata: Dict[str, Any]
    status: str = "completed"

class StatusResponse(BaseModel):
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None

@app.post("/api/generate", response_model=VideoResponse)
async def generate_video(request: GenerateRequest, user_id: str = Header(...)):
    """Generate a video based on the provided prompt."""
    try:
        logger.info(f"Received request with prompt: {request.prompt} from user: {user_id}")
        
        # Generate the video using Manim
        logger.info("Generating video with Manim...")
        video_path = await manim_service.generate_video(request.prompt)
        logger.info(f"Video generated at: {video_path}")
        
        if not os.path.exists(video_path):
            raise HTTPException(
                status_code=500,
                detail="Generated video file not found"
            )
        
        # Upload to storage
        logger.info("Uploading video to storage...")
        try:
            result = await storage_service.upload_video(
                user_id=user_id,
                prompt=request.prompt,
                video_path=video_path
            )
            logger.info("Video uploaded successfully")
        except Exception as upload_error:
            logger.error(f"Error uploading video: {str(upload_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload video: {str(upload_error)}"
            )
        
        # Clean up the temporary file
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info("Temporary file cleaned up")
        except Exception as cleanup_error:
            logger.warning(f"Failed to clean up temporary file: {str(cleanup_error)}")
        
        # Get the video ID from the result
        video_id = result["metadata"].get("id")
        if not video_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to get video ID from storage"
            )
        
        # Store the status
        video_statuses[video_id] = {
            "status": "completed",
            "video_url": result["video_url"],
            "error": None
        }
        
        # Return the response with the video ID
        return VideoResponse(
            id=video_id,
            video_url=result["video_url"],
            metadata=result["metadata"],
            status="completed"
        )
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )

@app.get("/api/status/{video_id}", response_model=StatusResponse)
async def get_video_status(video_id: str, user_id: str = Header(...)):
    """Get the status of a video generation."""
    try:
        if not video_id or video_id == "undefined":
            raise HTTPException(status_code=400, detail="Invalid video ID")
            
        if video_id not in video_statuses:
            # Try to get the video from storage
            try:
                video = await storage_service.get_video(user_id, video_id)
                video_statuses[video_id] = {
                    "status": "completed",
                    "video_url": video["video_url"],
                    "error": None
                }
            except Exception as e:
                logger.error(f"Error retrieving video: {str(e)}")
                raise HTTPException(status_code=404, detail="Video not found")
        
        return StatusResponse(**video_statuses[video_id])
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting video status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get video status: {str(e)}"
        )

@app.get("/api/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, user_id: str = Header(...)):
    """Get a specific video by ID."""
    try:
        video = await storage_service.get_video(user_id, video_id)
        return VideoResponse(
            id=video_id,
            video_url=video["video_url"],
            metadata=video["metadata"],
            status="completed"
        )
    except Exception as e:
        logger.error(f"Error getting video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get video: {str(e)}"
        )

@app.get("/api/videos", response_model=list)
async def list_videos(user_id: str = Header(...)):
    """List all videos for a user."""
    try:
        logger.info(f"Fetching videos for user: {user_id}")
        videos = await storage_service.list_user_videos(user_id)
        logger.info(f"Found {len(videos)} videos")
        
        # Transform the data to match the frontend's expected structure
        transformed_videos = []
        for video in videos:
            try:
                # Generate a new signed URL for each video
                signed_url_response = storage_service.supabase.storage.from_(storage_service.bucket_name).create_signed_url(
                    video["file_path"],
                    3600  # URL valid for 1 hour
                )
                
                signed_url = signed_url_response.get('signedURL', '')
                if not signed_url:
                    logger.warning(f"Failed to generate signed URL for video {video['id']}")
                    continue
                
                transformed_videos.append({
                    "id": video["id"],
                    "video_url": signed_url,
                    "prompt": video["prompt"],
                    "created_at": video["created_at"],
                    "status": video.get("status", "completed")
                })
            except Exception as e:
                logger.error(f"Error processing video {video.get('id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Successfully transformed {len(transformed_videos)} videos")
        return transformed_videos
    except Exception as e:
        logger.error(f"Error in list_videos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list videos: {str(e)}"
        )

@app.delete("/api/videos/{video_id}")
async def delete_video(video_id: str, user_id: str = Header(...)):
    """Delete a video by ID."""
    try:
        success = await storage_service.delete_video(user_id, video_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete video")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete video: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to AI Manim Generator API"} 