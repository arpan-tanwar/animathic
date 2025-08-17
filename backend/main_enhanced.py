"""
Enhanced FastAPI main application with comprehensive database integration
"""
import os
import traceback
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from services.enhanced_storage import EnhancedStorageService
from services.enhanced_manim import EnhancedManimService
from models.database import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize database
try:
    init_database()
    logger.info("✅ Database initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize database: {str(e)}")
    raise

# Create FastAPI app
app = FastAPI(
    title="Animathic - AI Manim Generator",
    description="An AI-powered web application that generates mathematical animations using Manim with comprehensive database tracking",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React dev server
        "http://localhost:8080",  # Alternative dev server
        "http://127.0.0.1:5173",  # Local IP variations
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "https://animathic.com",  # Production frontend URL
    ],
    allow_origin_regex=r"https://.*\.animathic\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "Content-Type", 
        "Authorization",
        "user-id",
        "User-Id",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=600,
)

# Initialize services
try:
    storage_service = EnhancedStorageService()
    manim_service = EnhancedManimService()
    logger.info("✅ Services initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize services: {str(e)}")
    raise

# Request/Response Models
class GenerateRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None

class VideoResponse(BaseModel):
    video_id: str
    video_url: Optional[str] = None
    metadata: Dict[str, Any]
    status: str

class StatusResponse(BaseModel):
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None

class UserAnalyticsResponse(BaseModel):
    user_id: str
    email: Optional[str]
    name: Optional[str]
    member_since: Optional[str]
    last_activity: Optional[str]
    total_videos: int
    completed_videos: int
    failed_videos: int
    total_generation_time: float
    avg_generation_time: float
    total_storage_used: int
    avg_video_duration: float

class UpdateTagsRequest(BaseModel):
    tags: List[str]

# Middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    """Log incoming requests for debugging."""
    logger.info(f"📨 {request.method} {request.url}")
    
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, user-id, User-Id, X-Requested-With, Accept, Origin"
        response.headers["Access-Control-Max-Age"] = "600"
        logger.info(f"✅ OPTIONS response: {response.status_code}")
        return response
        
    response = await call_next(request)
    logger.info(f"✅ Response: {response.status_code}")
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "services": {
            "database": "connected",
            "storage": "connected",
            "ai": "connected"
        }
    }

# Enhanced video generation endpoint
@app.post("/api/generate", response_model=VideoResponse)
async def generate_video(
    request: GenerateRequest, 
    user_id: Optional[str] = Header(None, alias="user-id")
):
    """Generate a video with comprehensive database tracking."""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Missing user_id header")
        
        logger.info(f"🎬 Video generation request from user: {user_id}")
        logger.info(f"📝 Prompt: {request.prompt}")
        
        # Generate video with database integration
        result = await manim_service.generate_video_with_database(
            user_id=user_id,
            prompt=request.prompt,
            title=request.title,
            email=request.email,
            name=request.name
        )
        
        logger.info(f"✅ Video generation completed: {result['video_id']}")
        
        return VideoResponse(
            video_id=result["video_id"],
            video_url=result["video_url"],
            metadata=result["metadata"],
            status="completed"
        )
        
    except HTTPException as he:
        logger.error(f"❌ HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )

# Get video by ID
@app.get("/api/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    user_id: Optional[str] = Header(None, alias="user-id")
):
    """Get a specific video by ID."""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Missing user_id header")
        
        result = await storage_service.get_video(user_id, video_id)
        
        return VideoResponse(
            video_id=result["video_id"],
            video_url=result["video_url"],
            metadata=result["metadata"],
            status=result["metadata"]["status"]
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"❌ Error retrieving video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve video: {str(e)}"
        )

# List user videos
@app.get("/api/videos")
async def list_videos(
    user_id: Optional[str] = Header(None, alias="user-id"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Maximum number of videos to return")
):
    """List all videos for a user with optional filtering."""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Missing user_id header")
        
        videos = await storage_service.list_user_videos(user_id, status, limit)
        
        return {
            "videos": videos,
            "count": len(videos),
            "filters": {
                "status": status,
                "limit": limit
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"❌ Error listing videos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list videos: {str(e)}"
        )

# Delete video
@app.delete("/api/videos/{video_id}")
async def delete_video(
    video_id: str,
    user_id: Optional[str] = Header(None, alias="user-id")
):
    """Delete a video and its metadata."""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Missing user_id header")
        
        success = await storage_service.delete_video(user_id, video_id)
        
        if success:
            return {"message": "Video deleted successfully", "video_id": video_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete video")
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"❌ Error deleting video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete video: {str(e)}"
        )

# Update video tags
@app.put("/api/videos/{video_id}/tags")
async def update_video_tags(
    video_id: str,
    request: UpdateTagsRequest,
    user_id: Optional[str] = Header(None, alias="user-id")
):
    """Update tags for a video."""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Missing user_id header")
        
        success = await storage_service.update_video_tags(user_id, video_id, request.tags)
        
        if success:
            return {"message": "Tags updated successfully", "video_id": video_id, "tags": request.tags}
        else:
            raise HTTPException(status_code=500, detail="Failed to update tags")
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"❌ Error updating tags: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update tags: {str(e)}"
        )

# User analytics endpoint
@app.get("/api/analytics", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    user_id: Optional[str] = Header(None, alias="user-id")
):
    """Get comprehensive analytics for a user."""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Missing user_id header")
        
        analytics = await storage_service.get_user_analytics(user_id)
        
        return UserAnalyticsResponse(**analytics)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"❌ Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )

# Legacy status endpoint for backward compatibility
@app.get("/api/status/{video_id}", response_model=StatusResponse)
async def get_video_status(
    video_id: str,
    user_id: Optional[str] = Header(None, alias="user-id")
):
    """Get video status (legacy endpoint for backward compatibility)."""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Missing user_id header")
        
        result = await storage_service.get_video(user_id, video_id)
        
        return StatusResponse(
            status=result["metadata"]["status"],
            video_url=result["video_url"],
            error=None
        )
        
    except HTTPException as he:
        if he.status_code == 404:
            return StatusResponse(
                status="not_found",
                video_url=None,
                error="Video not found"
            )
        raise he
    except Exception as e:
        logger.error(f"❌ Error getting status: {str(e)}")
        return StatusResponse(
            status="error",
            video_url=None,
            error=str(e)
        )

# Serve static files
if os.path.exists("media"):
    app.mount("/media", StaticFiles(directory="media"), name="media")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Animathic - AI Manim Generator API",
        "version": "2.0.0",
        "features": [
            "AI-powered video generation with Gemini 2.5 Flash",
            "Comprehensive database tracking and analytics",
            "User management and video organization",
            "Advanced logging and debugging",
            "Scalable storage with Supabase"
        ],
        "endpoints": {
            "generate": "POST /api/generate",
            "get_video": "GET /api/videos/{video_id}",
            "list_videos": "GET /api/videos",
            "delete_video": "DELETE /api/videos/{video_id}",
            "update_tags": "PUT /api/videos/{video_id}/tags",
            "analytics": "GET /api/analytics",
            "health": "GET /health"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
