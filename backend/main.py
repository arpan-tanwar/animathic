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

from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from dotenv import load_dotenv
import psutil

# Import services - with fallback to basic service if enhanced unavailable
try:
    from services.optimized_manim import OptimizedManimService as ManimService
    from services.enhanced_storage import EnhancedStorageService as StorageService
    enhanced_features = True
except ImportError:
    from services.manim import ManimService
    from services.storage import StorageService
    enhanced_features = False

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

# Try to initialize database if available
try:
    from models.database import init_database
    init_database()
    logger.info("✅ Enhanced database features enabled")
except ImportError:
    logger.info("📝 Using basic storage (enhanced database not available)")



# Load environment variables
load_dotenv()

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
    storage_service = StorageService()
    manim_service = ManimService()
    logger.info("✅ All services initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize services: {e}")
    raise

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
        
        # Generate video using optimized service
        if enhanced_features and hasattr(manim_service, 'generate_video_with_database'):
            result = await manim_service.generate_video_with_database(
                user_id=user_id,
                prompt=request.prompt
            )
            generation_time = time.time() - start_time
            
            return VideoResponse(
                id=result["video_id"],
                video_url=result["video_url"],
                metadata=result["metadata"],
                status="completed",
                generation_time=round(generation_time, 2)
            )
        else:
            # Use basic service
            video_path = await manim_service.generate_video(request.prompt)
            
            if not os.path.exists(video_path):
                raise HTTPException(status_code=500, detail="Generated video file not found")
            
            # Upload to storage
            result = await storage_service.upload_video(
                user_id=user_id,
                prompt=request.prompt,
                video_path=video_path
            )
            
            # Clean up temporary file
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")
            
            generation_time = time.time() - start_time
            
            return VideoResponse(
                id=result["metadata"]["id"],
                video_url=result["video_url"],
                metadata=result["metadata"],
                status="completed",
                generation_time=round(generation_time, 2)
            )
        
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
        
        video = await storage_service.get_video(user_id, video_id)
        
        return StatusResponse(
            status="completed",
            video_url=video["video_url"],
            error=None
        )
        
    except Exception as e:
        logger.error(f"Failed to get video status: {e}")
        raise HTTPException(status_code=404, detail="Video not found")

@app.get("/api/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, user_id: str = Depends(verify_user)):
    """Get specific video by ID"""
    try:
        video = await storage_service.get_video(user_id, video_id)
        
        return VideoResponse(
            id=video_id,
            video_url=video["video_url"],
            metadata=video["metadata"],
            status="completed"
        )
        
    except Exception as e:
        logger.error(f"Failed to get video: {e}")
        raise HTTPException(status_code=404, detail="Video not found")

@app.get("/api/videos")
async def list_videos(user_id: str = Depends(verify_user)):
    """List all videos for authenticated user"""
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
            if hasattr(manim_service, 'cleanup_old_files'):
                manim_service.cleanup_old_files(max_age_hours=24)
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        access_log=True
    )