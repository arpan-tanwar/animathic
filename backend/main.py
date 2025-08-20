"""
Animathic - Production-Ready AI Manim Generator API

Complete workflow:
1. User provides prompt
2. Gemini generates structured JSON (local model as fallback)
3. JSON converts to Manim code
4. Code is compiled and provided to user
5. User feedback collected for fine-tuning and training
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

from fastapi import FastAPI, HTTPException, Header, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from dotenv import load_dotenv
import psutil

# Load environment variables FIRST - before any imports that need them
load_dotenv()

# Import configuration
from config import get_config, get_api_config, get_feature_flags, is_production, get_log_level, get_cors_origins, get_rate_limit_config

# Configure logging first
log_level = get_log_level()
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Cloud Run handles file logging
    ]
)
logger = logging.getLogger(__name__)

# Import services
try:
    from services.hybrid_orchestrator import HybridOrchestrator
    from services.feedback_collector import FeedbackCollector
    from services.manim_compiler import ManimCompiler
    from services.enhanced_gemini import EnhancedGeminiService
    from services.local_llm import LocalLLMService
    enhanced_features = True
    logger.info("✅ All services imported successfully")
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

# Initialize services
hybrid_orchestrator = None
feedback_collector = None
manim_compiler = None

if enhanced_features:
    try:
        hybrid_orchestrator = HybridOrchestrator()
        feedback_collector = FeedbackCollector()
        manim_compiler = ManimCompiler()
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        enhanced_features = False

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
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)
    
    def record_request(self, response_time: float, success: bool = True):
        """Record request metrics"""
        self.request_count += 1
        if not success:
            self.error_count += 1
        self.response_times.append(response_time)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = time.time() - self.start_time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "avg_response_time": avg_response_time,
            "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
            "cpu_percent": psutil.Process().cpu_percent()
        }

# Initialize monitoring
performance_monitor = PerformanceMonitor()

# Initialize rate limiter
rate_limit_config = get_rate_limit_config()
rate_limiter = RateLimiter(
    max_requests=rate_limit_config["max_requests"],
    window_minutes=rate_limit_config["window_minutes"]
)

# Create FastAPI app
app = FastAPI(**get_api_config())

# Add CORS middleware
cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/media", StaticFiles(directory="media"), name="media")

# Pydantic models for API
class AnimationRequest(BaseModel):
    """Request model for animation generation"""
    prompt: str
    user_id: Optional[str] = None
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Prompt must be at least 3 characters long')
        if len(v) > 1000:
            raise ValueError('Prompt must be less than 1000 characters')
        return v.strip()

class FeedbackRequest(BaseModel):
    """Request model for user feedback"""
    generation_id: str
    rating: int
    quality: str
    comments: Optional[str] = None
    animation_worked: bool
    matched_intent: bool
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    uptime: float
    services: Dict[str, str]
    performance: Dict[str, Any]

# Dependency for rate limiting
async def check_rate_limit(request: Request):
    """Check rate limit for request"""
    if not rate_limit_config["enabled"]:
        return
    
    client_id = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

# Background task for training
async def trigger_training(generation_id: str):
    """Trigger training pipeline in background"""
    try:
        if feedback_collector:
            # Collect training data
            training_data = await feedback_collector.get_training_data_for_generation(generation_id)
            if training_data:
                logger.info(f"🎯 Training data collected for generation {generation_id}")
                # Here you would trigger the actual training pipeline
                # For now, just log it
                logger.info(f"📚 Training pipeline would be triggered with {len(training_data)} examples")
    except Exception as e:
        logger.error(f"❌ Training trigger failed: {e}")

# API Endpoints

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Animathic API - AI-Powered Mathematical Animation Generation",
        "version": "1.0.0",
        "status": "operational",
        "workflow": [
            "1. User provides prompt",
            "2. Gemini generates structured JSON (local model as fallback)",
            "3. JSON converts to Manim code",
            "4. Code is compiled and provided to user",
            "5. User feedback collected for fine-tuning and training"
        ]
    }

@app.post("/api/generate-animation", response_class=JSONResponse)
async def generate_animation(
    request: AnimationRequest,
    background_tasks: BackgroundTasks,
    rate_limit_check: None = Depends(check_rate_limit)
):
    """
    Main endpoint for animation generation
    
    Complete workflow:
    1. User provides prompt
    2. Gemini generates structured JSON (local model as fallback)
    3. JSON converts to Manim code
    4. Code is compiled and provided to user
    """
    
    start_time = time.time()
    
    try:
        if not enhanced_features or not hybrid_orchestrator:
            raise HTTPException(
                status_code=503,
                detail="Animation service is currently unavailable"
            )
        
        logger.info(f"🎯 Generating animation for prompt: {request.prompt[:100]}...")
        
        # Step 1: Generate animation using hybrid orchestrator
        manim_scene, generation_record = await hybrid_orchestrator.generate_animation(
            request.prompt, 
            request.user_id or "anonymous"
        )
        
        # Step 2: Compile to Manim code
        compilation_start = time.time()
        compiled_manim = manim_compiler.compile_to_manim(manim_scene)
        compilation_time = time.time() - compilation_start
        
        # Update generation record with compilation info
        if feedback_collector:
            await feedback_collector.update_generation(generation_record.id, {
                "compiled_manim": compiled_manim,
                "compilation_time": compilation_time
            })
        
        # Step 3: Generate video (optional - can be done asynchronously)
        video_path = None
        try:
            # Here you would render the Manim code to video
            # For now, we'll just return the code
            logger.info("✅ Animation generation completed successfully")
        except Exception as e:
            logger.warning(f"⚠️ Video generation failed: {e}")
            # Continue without video - user can still see the code
        
        total_time = time.time() - start_time
        
        # Record performance metrics
        performance_monitor.record_request(total_time, True)
        
        # Prepare response
        response = {
            "success": True,
            "generation_id": generation_record.id,
            "prompt": request.prompt,
            "manim_code": compiled_manim,
            "video_path": video_path,
            "generation_time": generation_record.generation_time,
            "compilation_time": compilation_time,
            "total_time": total_time,
            "model_used": generation_record.primary_model.value,
            "fallback_used": generation_record.fallback_used
        }
        
        # Trigger training in background
        background_tasks.add_task(trigger_training, generation_record.id)
        
        return response
        
    except Exception as e:
        total_time = time.time() - start_time
        performance_monitor.record_request(total_time, False)
        
        logger.error(f"❌ Animation generation failed: {e}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Animation generation failed: {str(e)}"
        )

@app.post("/api/feedback", response_class=JSONResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    rate_limit_check: None = Depends(check_rate_limit)
):
    """Submit user feedback for animation generation"""
    
    try:
        if not feedback_collector:
            raise HTTPException(
                status_code=503,
                detail="Feedback service is currently unavailable"
            )
        
        # Create user feedback record
        user_feedback = await feedback_collector.create_user_feedback(
            generation_id=feedback.generation_id,
            rating=feedback.rating,
            quality=feedback.quality,
            comments=feedback.comments,
            animation_worked=feedback.animation_worked,
            matched_intent=feedback.matched_intent
        )
        
        logger.info(f"✅ Feedback submitted for generation {feedback.generation_id}")
        
        return {
            "success": True,
            "feedback_id": user_feedback.generation_id,
            "message": "Feedback submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Feedback submission failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Feedback submission failed: {str(e)}"
        )

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    # Check service status
    services = {}
    
    if hybrid_orchestrator:
        try:
            service_status = await hybrid_orchestrator.test_services()
            services["hybrid_orchestrator"] = "healthy" if service_status else "unhealthy"
        except:
            services["hybrid_orchestrator"] = "unhealthy"
    else:
        services["hybrid_orchestrator"] = "not_available"
    
    if feedback_collector:
        services["feedback_collector"] = "healthy"
    else:
        services["feedback_collector"] = "not_available"
    
    if manim_compiler:
        services["manim_compiler"] = "healthy"
    else:
        services["manim_compiler"] = "not_available"
    
    # Get performance metrics
    performance = performance_monitor.get_metrics()
    
    return HealthResponse(
        status="healthy" if all(s == "healthy" for s in services.values() if s != "not_available") else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        uptime=performance["uptime_seconds"],
        services=services,
        performance=performance
    )

@app.get("/api/metrics")
async def get_metrics():
    """Get performance metrics"""
    return performance_monitor.get_metrics()

@app.get("/api/status")
async def get_status():
    """Get detailed system status"""
    
    config = get_config()
    
    return {
        "environment": config.environment,
        "features_enabled": {
            "hybrid_ai": config.features.hybrid_ai,
            "feedback_collection": config.features.feedback_collection,
            "enhanced_database": config.features.enhanced_database,
            "ai_animations": config.features.ai_animations
        },
        "services": {
            "hybrid_orchestrator": enhanced_features and hybrid_orchestrator is not None,
            "feedback_collector": enhanced_features and feedback_collector is not None,
            "manim_compiler": enhanced_features and manim_compiler is not None
        },
        "configuration": {
            "google_ai_configured": bool(config.google_ai.api_key),
            "local_llm_enabled": config.local_llm.enabled,
            "rate_limiting_enabled": config.rate_limit.enabled
        }
    }

@app.get("/api/manim-code/{generation_id}")
async def get_manim_code(generation_id: str):
    """Get Manim code for a specific generation"""
    
    try:
        if not feedback_collector:
            raise HTTPException(
                status_code=503,
                detail="Service unavailable"
            )
        
        generation = await feedback_collector.get_generation(generation_id)
        if not generation:
            raise HTTPException(
                status_code=404,
                detail="Generation not found"
            )
        
        return {
            "generation_id": generation_id,
            "manim_code": generation.get("compiled_manim", ""),
            "prompt": generation.get("prompt", ""),
            "timestamp": generation.get("timestamp", "")
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve Manim code: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve Manim code: {str(e)}"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"❌ Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Animathic API starting up...")
    
    # Verify services
    if enhanced_features:
        logger.info("✅ Enhanced features enabled")
    else:
        logger.warning("⚠️ Enhanced features disabled - running in basic mode")
    
    logger.info("🎯 Ready to generate animations!")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 Animathic API shutting down...")
    
    # Cleanup resources
    if feedback_collector:
        try:
            await feedback_collector.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=not is_production(),
        log_level=log_level.lower()
    )