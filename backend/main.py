"""
Animathic - Consolidated AI Manim Generator API

This is the unified, optimized backend combining all best features:
- Enhanced security with input validation and rate limiting
- Performance monitoring and resource management  
- Memory leak prevention and automated cleanup
- Comprehensive error handling and logging
- Database integration with user tracking
- Health monitoring and metrics endpoints
"""

import os
import time
import logging
import traceback
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from collections import defaultdict, deque
from pathlib import Path
import uuid

from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from dotenv import load_dotenv
import psutil

# Load environment variables FIRST - before any imports that need them
load_dotenv()

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('animathic.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import services
try:
    from services.manim import get_manim_service, generate_video_from_prompt
    from services.storage import StorageService
    enhanced_features = True
    logger.info("✅ Using optimized Manim service")
except ImportError as e:
    logger.error(f"❌ Failed to import services: {e}")
    enhanced_features = False

# Try to initialize database if available
try:
    from models.database import init_database
    init_database()
    logger.info("✅ Enhanced database features enabled")
except ImportError:
    logger.info("📝 Using basic storage (enhanced database not available)")
except Exception as e:
    logger.warning(f"📝 Database initialization skipped: {e}")



# Environment variables already loaded above

class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self, max_requests: int = 10, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        client_requests = self.requests[client_id]
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True
        
        return False

class PerformanceMonitor:
    """Monitor application performance and resource usage"""
    
    def __init__(self):
        self.request_times = deque(maxlen=1000)
        self.error_count = 0
        self.total_requests = 0
    
    def log_request(self, duration: float, success: bool = True):
        """Log request performance"""
        self.request_times.append(duration)
        self.total_requests += 1
        if not success:
            self.error_count += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.request_times:
            return {"status": "no_data"}
        
        avg_time = sum(self.request_times) / len(self.request_times)
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        cpu_percent = psutil.cpu_percent()
        
        return {
            "avg_response_time": round(avg_time, 3),
            "total_requests": self.total_requests,
            "error_rate": round(self.error_count / self.total_requests * 100, 2) if self.total_requests > 0 else 0,
            "memory_usage_mb": round(memory_usage, 2),
            "cpu_percent": cpu_percent,
            "active_requests": len(self.request_times),
            "enhanced_features": enhanced_features
        }

# Initialize services
rate_limiter = RateLimiter(max_requests=5, window_minutes=1)
performance_monitor = PerformanceMonitor()

# In-memory video storage for status tracking
video_storage = {}

# Create FastAPI app
app = FastAPI(
    title="Animathic - AI Mathematical Animation Generator",
    description="Optimized AI-powered mathematical animation generator with enhanced security and performance",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers and performance monitoring"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Log performance
        duration = time.time() - start_time
        performance_monitor.log_request(duration, response.status_code < 400)
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        performance_monitor.log_request(duration, False)
        logger.error(f"Request failed: {e}")
        raise

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000", 
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "https://animathic.com",
    ],
    allow_origin_regex=r"https://.*\.animathic\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "user-id", "User-Id"],
    max_age=600,
)

# Mount static files
app.mount("/media", StaticFiles(directory="media"), name="media")

# Initialize services with error handling
try:
    if enhanced_features:
        storage_service = StorageService()
        logger.info("✅ Supabase storage service initialized successfully")
    else:
        storage_service = None
        logger.info("📝 Enhanced features disabled, using basic storage")
except Exception as e:
    logger.warning(f"⚠️ Supabase storage service failed to initialize: {e}")
    logger.info("📝 Falling back to local storage only")
    storage_service = None

logger.info("✅ All services initialized successfully")

# Pydantic models with validation
class GenerateRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Prompt must be at least 5 characters long')
        if len(v) > 500:
            raise ValueError('Prompt must be less than 500 characters')
        
        # Basic sanitization
        dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'exec', 'eval']
        v_lower = v.lower()
        for char in dangerous_chars:
            if char in v_lower:
                raise ValueError(f'Prompt contains potentially dangerous content: {char}')
        
        return v.strip()

class VideoResponse(BaseModel):
    id: str
    video_url: str
    metadata: Dict[str, Any]
    status: str = "completed"
    generation_time: Optional[float] = None

class StatusResponse(BaseModel):
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    performance: Dict[str, Any]

# Rate limiting dependency
async def check_rate_limit(request: Request):
    """Check rate limit for request"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    client_id = f"{client_ip}:{user_agent}"
    
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before making more requests."
        )

# Authentication dependency
async def verify_user(user_id: Optional[str] = Header(None)):
    """Verify user authentication"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user_id header")
    return user_id

# API Routes
@app.post("/api/generate", response_model=VideoResponse, dependencies=[Depends(check_rate_limit)])
async def generate_video(
    request: GenerateRequest,
    user_id: str = Depends(verify_user)
):
    """Generate a video with enhanced security and performance monitoring"""
    start_time = time.time()
    
    try:
        logger.info(f"Generating video for user {user_id}: {request.prompt}")
        
        # Generate video using new optimized service
        if enhanced_features:
            result = await generate_video_from_prompt(
                prompt=request.prompt,
                media_dir="./media"
            )
            
            generation_time = time.time() - start_time
            
            if result.success:
                try:
                    # Upload video to Supabase storage
                    if storage_service and result.video_path:
                        logger.info(f"Uploading video to Supabase: {result.video_path}")
                        
                        # Prepare metadata for Supabase
                        upload_metadata = {
                            "duration": result.duration,
                            "resolution": result.resolution,
                            "generation_time": round(generation_time, 2),
                            "code_used": result.code_used[:500] if result.code_used else None
                        }
                        
                        # Upload to Supabase
                        upload_result = await storage_service.upload_video(
                            user_id=user_id,
                            prompt=request.prompt,
                            video_path=result.video_path,
                            metadata=upload_metadata
                        )
                        
                        video_id = upload_result["metadata"]["id"]
                        video_url = upload_result["video_url"]
                        
                        logger.info(f"Video uploaded successfully. ID: {video_id}")
                        
                        # Clean up local file after successful upload
                        try:
                            if os.path.exists(result.video_path):
                                os.remove(result.video_path)
                                logger.info(f"Cleaned up local file: {result.video_path}")
                        except Exception as cleanup_error:
                            logger.warning(f"Failed to cleanup local file: {cleanup_error}")
                        
                        return VideoResponse(
                            id=video_id,
                            video_url=video_url,
                            metadata={
                                "duration": result.duration,
                                "resolution": result.resolution,
                                "prompt": request.prompt,
                                "generation_time": round(generation_time, 2),
                                "code_used": result.code_used[:500] if result.code_used else None
                            },
                            status="completed",
                            generation_time=round(generation_time, 2)
                        )
                    else:
                        # Fallback to local storage if Supabase unavailable
                        logger.warning("Supabase storage not available, using local storage")
                        
                        video_url = None
                        if result.video_path:
                            relative_path = os.path.relpath(result.video_path, "./media")
                            video_url = f"/media/{relative_path}"
                        
                        # Generate video ID and store metadata in memory
                        video_id = str(uuid.uuid4())
                        video_metadata = {
                            "id": video_id,
                            "user_id": user_id,
                            "video_url": video_url,
                            "video_path": result.video_path,
                            "status": "completed",
                            "prompt": request.prompt,
                            "duration": result.duration,
                            "resolution": result.resolution,
                            "generation_time": round(generation_time, 2),
                            "code_used": result.code_used[:500] if result.code_used else None,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        # Store in memory for status checking
                        video_storage[video_id] = video_metadata
                        
                        return VideoResponse(
                            id=video_id,
                            video_url=video_url,
                            metadata={
                                "duration": result.duration,
                                "resolution": result.resolution,
                                "prompt": request.prompt,
                                "generation_time": round(generation_time, 2),
                                "code_used": result.code_used[:500] if result.code_used else None
                            },
                            status="completed",
                            generation_time=round(generation_time, 2)
                        )
                        
                except Exception as upload_error:
                    logger.error(f"Failed to upload video to Supabase: {upload_error}")
                    # Fallback to local storage
                    video_url = None
                    if result.video_path:
                        relative_path = os.path.relpath(result.video_path, "./media")
                        video_url = f"/media/{relative_path}"
                    
                    # Generate video ID and store metadata in memory
                    video_id = str(uuid.uuid4())
                    video_metadata = {
                        "id": video_id,
                        "user_id": user_id,
                        "video_url": video_url,
                        "video_path": result.video_path,
                        "status": "completed",
                        "prompt": request.prompt,
                        "duration": result.duration,
                        "resolution": result.resolution,
                        "generation_time": round(generation_time, 2),
                        "code_used": result.code_used[:500] if result.code_used else None,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Store in memory for status checking
                    video_storage[video_id] = video_metadata
                    
                    return VideoResponse(
                        id=video_id,
                        video_url=video_url,
                        metadata={
                            "duration": result.duration,
                            "resolution": result.resolution,
                            "prompt": request.prompt,
                            "generation_time": round(generation_time, 2),
                            "code_used": result.code_used[:500] if result.code_used else None,
                            "upload_error": "Failed to upload to cloud storage, using local storage"
                        },
                        status="completed",
                        generation_time=round(generation_time, 2)
                    )
            else:
                # Handle different error types with appropriate status codes
                if "API key not found" in result.error or "GOOGLE_AI_API_KEY" in result.error:
                    raise HTTPException(
                        status_code=503, 
                        detail="Video generation service unavailable: Google AI API key not configured"
                    )
                elif "initialization failed" in result.error or "network connection" in result.error:
                    raise HTTPException(
                        status_code=503,
                        detail="Video generation service temporarily unavailable"
                    )
                else:
                    raise HTTPException(
                        status_code=422, 
                        detail=f"Video generation failed: {result.error}"
                    )
        else:
            raise HTTPException(status_code=503, detail="Video generation service not available")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.get("/api/status/{video_id}", response_model=StatusResponse)
async def get_video_status(video_id: str, user_id: str = Depends(verify_user)):
    """Get video generation status"""
    try:
        if not video_id or video_id == "undefined":
            raise HTTPException(status_code=400, detail="Invalid video ID")
        
        # Check in-memory storage first
        if video_id in video_storage:
            video = video_storage[video_id]
            # Verify user owns this video
            if video["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            return StatusResponse(
                status=video["status"],
                video_url=video["video_url"],
                error=None
            )
        
        # Fallback to storage service if available
        if storage_service:
            try:
                video = await storage_service.get_video(user_id, video_id)
                return StatusResponse(
                    status="completed",
                    video_url=video["video_url"],
                    error=None
                )
            except Exception:
                pass  # Continue to 404
        
        raise HTTPException(status_code=404, detail="Video not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video status: {e}")
        raise HTTPException(status_code=404, detail="Video not found")

@app.get("/api/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, user_id: str = Depends(verify_user)):
    """Get specific video by ID"""
    try:
        # Check in-memory storage first
        if video_id in video_storage:
            video = video_storage[video_id]
            # Verify user owns this video
            if video["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            return VideoResponse(
                id=video_id,
                video_url=video["video_url"],
                metadata={
                    "duration": video["duration"],
                    "resolution": video["resolution"],
                    "prompt": video["prompt"],
                    "generation_time": video["generation_time"],
                    "code_used": video["code_used"]
                },
                status=video["status"],
                generation_time=video["generation_time"]
            )
        
        # Fallback to storage service if available
        if storage_service:
            try:
                video = await storage_service.get_video(user_id, video_id)
                return VideoResponse(
                    id=video_id,
                    video_url=video["video_url"],
                    metadata=video["metadata"],
                    status="completed"
                )
            except Exception:
                pass  # Continue to 404
        
        raise HTTPException(status_code=404, detail="Video not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video: {e}")
        raise HTTPException(status_code=404, detail="Video not found")

@app.get("/api/service-status")
async def service_status():
    """Check service status and configuration"""
    try:
        # Check if AI service is available
        from services.manim import get_manim_service
        service = get_manim_service()
        
        ai_available = service.model is not None
        api_key_configured = bool(os.getenv('GOOGLE_AI_API_KEY'))
        
        return {
            "status": "healthy" if ai_available else "degraded",
            "ai_service": {
                "available": ai_available,
                "api_key_configured": api_key_configured,
                "message": "AI video generation ready" if ai_available else "API key required for AI features"
            },
            "storage_service": {
                "available": storage_service is not None,
                "message": "Storage service ready" if storage_service else "Storage service unavailable"
            }
        }
    except Exception as e:
        logger.error(f"Service status check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/api/videos")
async def list_videos(user_id: str = Depends(verify_user)):
    """List all videos for authenticated user"""
    try:
        # First check in-memory storage
        user_videos = []
        for video_id, video_data in video_storage.items():
            if video_data["user_id"] == user_id:
                user_videos.append({
                    "id": video_id,
                    "video_url": video_data["video_url"],
                    "prompt": video_data["prompt"],
                    "created_at": video_data["created_at"],
                    "status": video_data["status"],
                    "duration": video_data.get("duration"),
                    "resolution": video_data.get("resolution")
                })
        
        # If we have in-memory videos, return them
        if user_videos:
            return user_videos
        
        # Fallback to storage service if available and no videos in memory
        if storage_service:
            try:
                videos = await storage_service.list_user_videos(user_id)
                # Transform videos for frontend
                transformed_videos = []
                for video in videos:
                    try:
                        # Generate fresh signed URL
                        signed_url_response = storage_service.supabase.storage.from_(
                            storage_service.bucket_name
                        ).create_signed_url(video["file_path"], 3600)
                        
                        signed_url = signed_url_response.get('signedURL', '')
                        if signed_url:
                            transformed_videos.append({
                                "id": video["id"],
                                "video_url": signed_url,
                                "prompt": video["prompt"],
                                "created_at": video["created_at"],
                                "status": video.get("status", "completed")
                            })
                    except Exception as e:
                        logger.error(f"Error processing video {video.get('id')}: {e}")
                        continue
                return transformed_videos
            except Exception as e:
                logger.error(f"Storage service error: {e}")
        
        # Return empty list if no videos found
        return []
        
    except Exception as e:
        logger.error(f"Failed to list videos: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve videos")

@app.delete("/api/videos/{video_id}")
async def delete_video(video_id: str, user_id: str = Depends(verify_user)):
    """Delete video with proper authorization"""
    try:
        success = await storage_service.delete_video(user_id, video_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete video")
        
        return {"status": "success", "message": "Video deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete video: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete video")

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check with performance metrics"""
    try:
        # Test database connection
        await storage_service.list_user_videos("health_check")
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            version="3.0.0",
            performance=performance_monitor.get_metrics()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            version="3.0.0",
            performance=performance_monitor.get_metrics()
        )

@app.get("/api/metrics")
async def get_metrics():
    """Get detailed performance metrics"""
    return {
        "performance": performance_monitor.get_metrics(),
        "system": {
            "memory_usage": psutil.virtual_memory()._asdict(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "disk_usage": psutil.disk_usage('/')._asdict()
        },
        "features": {
            "enhanced_database": enhanced_features,
            "rate_limiting": True,
            "performance_monitoring": True,
            "security_headers": True,
            "automated_cleanup": True
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Animathic - AI Mathematical Animation Generator",
        "version": "3.0.0",
        "status": "operational",
        "features": {
            "enhanced_database": enhanced_features,
            "security": "enterprise-grade",
            "performance": "optimized"
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "metrics": "/api/metrics"
        }
    }

# Cleanup background task
async def cleanup_task():
    """Background task to clean up old files"""
    while True:
        try:
            # Clean up old media files (simple cleanup)
            media_dir = Path("./media")
            if media_dir.exists():
                # Remove files older than 24 hours
                cutoff_time = time.time() - (24 * 3600)
                for file_path in media_dir.glob("**/*"):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            logger.debug(f"Cleaned up old file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Failed to remove old file {file_path}: {e}")
            
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Cleanup task failed: {e}")
            await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("🚀 Starting Animathic API v3.0.0")
    logger.info(f"📊 Enhanced features: {'enabled' if enhanced_features else 'disabled'}")
    asyncio.create_task(cleanup_task())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("⏹️  Shutting down Animathic API")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
        access_log=True
    )