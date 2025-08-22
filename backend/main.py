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
import json
import time
import logging
import tempfile
import subprocess
import uuid
import shutil
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
import asyncio
from datetime import datetime as _dt, timezone
from slugify import slugify
import httpx

from database import init_database, SessionLocal, engine, async_engine
from models.database import User, Video, GenerationJob, Feedback
from schemas import (
    GenerateRequest, GenerateResponse, StatusResponse, 
    VideoResponse, FeedbackRequest, HealthResponse
)
from services.ai_service_new import AIService
from services.clerk_auth import require_authentication, optional_authentication
from services.supabase_storage import supabase_storage

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get logger first
logger = logging.getLogger(__name__)

# Production logging configuration
try:
    from production_config import LOG_LEVEL, LOG_FORMAT, LOG_FILE
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Configure logging with file handler for production
    handlers = [logging.StreamHandler()]  # Always log to console
    
    # Add file handler if LOG_FILE is specified and writable
    if LOG_FILE and LOG_FILE != "-":
        try:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(LOG_FILE)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            handlers.append(logging.FileHandler(LOG_FILE))
        except Exception as e:
            logger.warning(f"Could not create log file {LOG_FILE}: {e}")
    
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=handlers
    )
except ImportError:
    # Fallback to basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Initialize FastAPI app
app = FastAPI(
    title="Animathic API",
    description="AI-powered animation generation using Gemini and Manim",
    version="1.0.0"
)

# Production configuration
try:
    from production_config import ALLOWED_ORIGINS, DEBUG
except ImportError:
    ALLOWED_ORIGINS = ["*"]
    DEBUG = False

# CORS middleware with production settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global variables for lazy initialization
_database_initialized = False
_ai_service = None

def initialize_database_lazy():
    """Initialize database only when needed"""
    global _database_initialized
    if _database_initialized:
        return
    
    try:
        # Initialize database with production configuration
        try:
            from production_config import DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW, DATABASE_POOL_TIMEOUT, DATABASE_POOL_RECYCLE
            
            # Update database engine with production settings
            if engine:
                engine.pool_size = DATABASE_POOL_SIZE
                engine.max_overflow = DATABASE_MAX_OVERFLOW
                engine.pool_timeout = DATABASE_POOL_TIMEOUT
                engine.pool_recycle = DATABASE_POOL_RECYCLE
                logger.info(f"Database engine configured with pool_size={DATABASE_POOL_SIZE}, max_overflow={DATABASE_MAX_OVERFLOW}")
            
            init_database()
            logger.info("Database initialized successfully with production settings")
        except ImportError:
            # Fallback to basic database initialization
            try:
                init_database()
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                logger.warning("Continuing without database - some features may not work")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            logger.warning("Continuing without database - some features may not work")
        
        _database_initialized = True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("Continuing without database - some features may not work")

# Check if database is available at startup (but don't initialize yet)
DATABASE_AVAILABLE_AT_STARTUP = engine is not None and async_engine is not None
if not DATABASE_AVAILABLE_AT_STARTUP:
    logger.warning("Database not available at startup - some endpoints may not work")
else:
    logger.info("Database is available and ready")

def is_database_available() -> bool:
    """Check if database is available at runtime"""
    try:
        # Initialize database if not already done
        initialize_database_lazy()
        return (engine is not None and 
                async_engine is not None and 
                SessionLocal is not None)
    except Exception:
        return False

# Ensure generation_jobs table exists (for cross-instance job status)
async def _ensure_generation_jobs_table() -> None:
    """Ensure generation_jobs table exists - called only when needed"""
    try:
        # Initialize database if not already done
        initialize_database_lazy()
        
        if not SessionLocal:
            logger.warning("Cannot ensure generation_jobs table - SessionLocal not available")
            return
            
        with SessionLocal() as _db:
            # Create table if it doesn't exist
            _db.execute(text(
                """
                CREATE TABLE IF NOT EXISTS generation_jobs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    current_step INTEGER DEFAULT 0,
                    total_steps INTEGER DEFAULT 4,
                    ai_response TEXT,
                    manim_code TEXT,
                    error_message TEXT,
                    result_video_id TEXT,
                    video_url TEXT,
                    created_at TIMESTAMPTZ DEFAULT now(),
                    updated_at TIMESTAMPTZ DEFAULT now()
                );
                """
            ))
            
            # Add missing columns if they don't exist
            try:
                _db.execute(text("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS ai_response TEXT;"))
            except Exception:
                pass  # Column might already exist
                
            try:
                _db.execute(text("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS manim_code TEXT;"))
            except Exception:
                pass  # Column might already exist
                
            try:
                _db.execute(text("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS video_url TEXT;"))
            except Exception:
                pass  # Column might already exist
            
            _db.commit()
            logger.info("Generation jobs table ensured successfully")
    except Exception as _e:
        logger.warning(f"generation_jobs table ensure failed (continuing): {_e}")

# In-memory storage for generation jobs (in production, use Redis or database)
generation_jobs = {}

def get_ai_service():
    """Get or create the AI service instance"""
    global _ai_service
    if _ai_service is None:
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            logger.error("GOOGLE_AI_API_KEY is not set")
            raise RuntimeError("GOOGLE_AI_API_KEY is not set")
        try:
            _ai_service = AIService(api_key=api_key)
            logger.info("AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise
    return _ai_service

# Supabase public URL base (for public buckets)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cclnoqiorysuciutdera.supabase.co").rstrip("/")
SUPABASE_PUBLIC_BASE = f"{SUPABASE_URL}/storage/v1/object/public"
NEW_BUCKET = os.getenv("SUPABASE_NEW_BUCKET", "animathic-media")
OLD_BUCKET = os.getenv("SUPABASE_OLD_BUCKET", "manim-videos")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Check if required environment variables are set
def check_environment():
    """Check if required environment variables are set"""
    required_vars = {
        "GOOGLE_AI_API_KEY": "Required for AI animation generation",
        "DATABASE_URL": "Required for database operations",
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        logger.warning("Missing environment variables:")
        for var in missing_vars:
            logger.warning(f"  - {var}")
        logger.warning("Some features may not work properly")
    else:
        logger.info("All required environment variables are set")

# Check environment on startup
check_environment()


async def resolve_public_video_url(file_path: str) -> Optional[str]:
    """Return a working public URL for the given file_path, trying new bucket then old.
    Assumes buckets are public. Falls back to None if both not accessible.
    """
    if not file_path:
        return None
    path = file_path.lstrip("/")
    candidates = [
        f"{SUPABASE_PUBLIC_BASE}/{NEW_BUCKET}/{path}",
        f"{SUPABASE_PUBLIC_BASE}/{OLD_BUCKET}/{path}",
    ]
    timeout = httpx.Timeout(2.0, connect=2.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for url in candidates:
            try:
                r = await client.head(url)
                if r.status_code == 200:
                    return url
            except Exception:
                continue
    return None


async def supabase_copy_object(source_bucket: str, source_key: str, dest_bucket: str, dest_key: str) -> bool:
    """Use Supabase Storage copy API to duplicate an object."""
    if not SUPABASE_SERVICE_KEY:
        return False
    url = f"{SUPABASE_URL}/storage/v1/object/copy"
    payload = {
        "bucketId": source_bucket,
        "sourceKey": source_key,
        "destinationBucket": dest_bucket,
        "destinationKey": dest_key,
        "upsert": True,
    }
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "apikey": SUPABASE_SERVICE_KEY,
    }
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(url, json=payload, headers=headers)
        return r.status_code in (200, 201)


async def ensure_placeholder_uploaded(db: Session, dest_path: str) -> bool:
    """Ensure there is a file at dest_path in NEW_BUCKET by copying an existing video as placeholder."""
    try:
        # Find a recent existing file_path to clone
        row = db.execute(
            text("""
                SELECT file_path
                FROM videos
                WHERE file_path IS NOT NULL AND file_path <> ''
                ORDER BY created_at DESC NULLS LAST
                LIMIT 1
            """),
        ).fetchone()
        if not row:
            return False
        source_key = (getattr(row, "file_path", None) or row[0]).lstrip("/")

        # Detect which bucket has the source
        # Try new bucket URL
        source_new = f"{SUPABASE_PUBLIC_BASE}/{NEW_BUCKET}/{source_key}"
        source_old = f"{SUPABASE_PUBLIC_BASE}/{OLD_BUCKET}/{source_key}"
        timeout = httpx.Timeout(3.0, connect=2.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            src_bucket = None
            try:
                h = await client.head(source_new)
                if h.status_code == 200:
                    src_bucket = NEW_BUCKET
            except Exception:
                pass
            if not src_bucket:
                try:
                    h2 = await client.head(source_old)
                    if h2.status_code == 200:
                        src_bucket = OLD_BUCKET
                except Exception:
                    pass
        if not src_bucket:
            return False

        # Copy to destination in NEW_BUCKET
        ok = await supabase_copy_object(src_bucket, source_key, NEW_BUCKET, dest_path)
        return ok
    except Exception as e:
        logger.error(f"ensure_placeholder_uploaded error: {e}")
        return False


async def supabase_delete_object(bucket: str, key: str) -> bool:
    """Delete an object from Supabase Storage."""
    if not SUPABASE_SERVICE_KEY:
        return False
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{key}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
    }
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.delete(url, headers=headers)
        return r.status_code in (200, 204)

async def generate_video_from_manim(manim_code: str, job_id: str) -> Optional[str]:
    """Generate video from Manim code"""
    try:
        # Create temporary directory for Manim execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create Manim scene file
            scene_file = temp_path / "animation_scene.py"
            scene_file.write_text(manim_code)
            
            # Run Manim command in headless mode - FIXED 2025-08-21 for v0.19.0
            cmd = [
                "manim", "render", "-ql", str(scene_file), "GeneratedScene"
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=temp_path,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Manim execution failed: {result.stderr}")
                return None
            
            # Add small delay to ensure file is fully written
            import time
            time.sleep(1)
            
            # Find generated video file - handle Manim v0.19.0 output structure
            media_dir = temp_path / "media"
            logger.info(f"Searching for video files in: {media_dir}")
            
            # Search recursively for MP4 files
            video_files = list(media_dir.rglob("*.mp4"))
            logger.info(f"Found {len(video_files)} video files: {[str(f) for f in video_files]}")
            
            if not video_files:
                logger.error("No video files generated by Manim")
                # List all files in media directory for debugging
                all_files = list(media_dir.rglob("*"))
                logger.error(f"All files in media directory: {[str(f) for f in all_files]}")
                return None
            
            # Return path to the first video file
            video_path = str(video_files[0])
            logger.info(f"Selected video file: {video_path}")
            
            # Persist video to a stable temp path so it's available after context exits
            stable_path = Path("/tmp") / f"animathic_{job_id}.mp4"
            try:
                shutil.copy(video_path, stable_path)
                logger.info(f"Copied video to stable path: {stable_path}")
                return str(stable_path)
            except Exception as copy_err:
                logger.warning(f"Failed to copy video to stable path, returning original: {copy_err}")
                return video_path
            
    except Exception as e:
        logger.error(f"Error generating video from Manim: {e}")
        return None

async def upload_video_to_supabase(video_path: str, job_id: str, user_id: str) -> Optional[str]:
    """Upload video to Supabase storage"""
    try:
        logger.info(f"Uploading video {video_path} to Supabase for job {job_id}")
        
        # Use Supabase storage service
        video_url = await supabase_storage.upload_video(video_path, job_id, user_id)
        
        if video_url:
            logger.info(f"Video uploaded successfully: {video_url}")
            return video_url
        else:
            logger.error("Failed to upload video to Supabase")
            return None
        
    except Exception as e:
        logger.error(f"Error uploading video to Supabase: {e}")
        return None

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
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
        database="supabase"
    )

@app.post("/api/generate")
async def generate_animation(
    request: GenerateRequest,
    auth: Dict[str, Any] = Depends(require_authentication)
):
    """Generate animation based on prompt"""
    try:
        # Validate request
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Use authenticated user ID
        user_id = auth.get("user_id")
        if not user_id or user_id == "anonymous":
            raise HTTPException(status_code=401, detail="Authentication required")
        
        logger.info(f"Starting animation generation for user {user_id} with prompt: {request.prompt[:100]}...")
        
        # Create job record
        job_id = str(uuid.uuid4())
        
        # Store job in memory for immediate access
        generation_jobs[job_id] = {
            'id': job_id,
            'user_id': user_id,
            'prompt': request.prompt,
            'status': 'processing',
            'current_step': 1,
            'total_steps': 4,
            'created_at': datetime.now(timezone.utc),
            'ai_response': None,
            'manim_code': None
        }
        
        # Try to insert job record in database (optional)
        if is_database_available():
            try:
                await _ensure_generation_jobs_table()
                async with async_engine.begin() as conn:
                    await conn.execute(
                        text("""
                            INSERT INTO generation_jobs (id, user_id, prompt, status, created_at, ai_response, manim_code)
                            VALUES (:id, :user_id, :prompt, :status, :created_at, :ai_response, :manim_code)
                        """),
                        {"id": job_id, "user_id": user_id, "prompt": request.prompt, "status": "processing", "created_at": datetime.now(timezone.utc), "ai_response": None, "manim_code": None}
                    )
                logger.info(f"Job {job_id} recorded in database")
            except Exception as db_error:
                logger.warning(f"Failed to record job in database: {db_error}")
                # Continue with in-memory storage
        else:
            logger.info(f"Database not available - job {job_id} stored in memory only")
        
        # Process animation request asynchronously
        asyncio.create_task(process_generation_job_async(job_id, request.prompt, user_id))
        
        # Return immediate response with job ID
        return {
            "id": job_id,
            "status": "processing",
            "message": "Animation generation started",
            "current_step": 1,
            "total_steps": 4
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def process_generation_job_async(job_id: str, prompt: str, user_id: str):
    """Process animation generation asynchronously"""
    try:
        logger.info(f"Processing generation job {job_id}")
        
        # Update job status
        generation_jobs[job_id]["status"] = "processing"
        generation_jobs[job_id]["current_step"] = 1
        
        # Step 1: Generate animation specification using AI
        try:
            logger.info(f"Step 1: Generating animation spec for job {job_id}")
            ai_service = get_ai_service()
            result = await ai_service.process_animation_request(prompt)
            
            if 'error' in result:
                raise Exception(f"AI generation failed: {result['error']}")
            
            # Extract results
            animation_spec = result.get('animation_spec', {})
            manim_code = result.get('manim_code', '')
            
            # Update job with AI response
            generation_jobs[job_id]["current_step"] = 2
            generation_jobs[job_id]["ai_response"] = animation_spec
            generation_jobs[job_id]["manim_code"] = manim_code
            
            logger.info(f"Step 1 completed for job {job_id}")
            
        except Exception as ai_error:
            logger.error(f"AI generation failed for job {job_id}: {ai_error}")
            generation_jobs[job_id]["status"] = "failed"
            generation_jobs[job_id]["error"] = str(ai_error)
            return
        
        # Step 2: Generate video using Manim
        try:
            logger.info(f"Step 2: Generating video for job {job_id}")
            video_path = await generate_video_from_manim(manim_code, job_id)
            
            if not video_path:
                raise Exception("Failed to generate video from Manim code")
            
            generation_jobs[job_id]["current_step"] = 3
            logger.info(f"Step 2 completed for job {job_id}")
            
        except Exception as manim_error:
            logger.error(f"Manim generation failed for job {job_id}: {manim_error}")
            generation_jobs[job_id]["status"] = "failed"
            generation_jobs[job_id]["error"] = str(manim_error)
            return
        
        # Step 3: Upload video to storage
        try:
            logger.info(f"Step 3: Uploading video for job {job_id}")
            video_url = await upload_video_to_supabase(video_path, job_id, user_id)
            
            if not video_url:
                raise Exception("Failed to upload video to storage")
            
            generation_jobs[job_id]["current_step"] = 4
            generation_jobs[job_id]["video_url"] = video_url
            logger.info(f"Step 3 completed for job {job_id}")
            
        except Exception as upload_error:
            logger.error(f"Video upload failed for job {job_id}: {upload_error}")
            generation_jobs[job_id]["status"] = "failed"
            generation_jobs[job_id]["error"] = str(upload_error)
            return
        
        # Step 4: Finalize job
        try:
            logger.info(f"Step 4: Finalizing job {job_id}")
            generation_jobs[job_id]["status"] = "completed"
            generation_jobs[job_id]["current_step"] = 4
            
            # Try to update database
            try:
                async with async_engine.begin() as conn:
                    await conn.execute(
                        text("""
                            UPDATE generation_jobs 
                            SET status = :status, current_step = :current_step, 
                                ai_response = :ai_response, manim_code = :manim_code,
                                video_url = :video_url, updated_at = now()
                            WHERE id = :id
                        """),
                        {
                            "status": "completed",
                            "current_step": 4,
                            "ai_response": json.dumps(animation_spec),
                            "manim_code": manim_code,
                            "video_url": video_url,
                            "id": job_id
                        }
                    )
            except Exception as db_error:
                logger.warning(f"Failed to update database for completed job: {db_error}")
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as finalize_error:
            logger.error(f"Job finalization failed for job {job_id}: {finalize_error}")
            generation_jobs[job_id]["status"] = "failed"
            generation_jobs[job_id]["error"] = str(finalize_error)
            return
            
    except Exception as e:
        logger.error(f"Unexpected error processing generation job {job_id}: {e}")
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = str(e)


@app.post("/api/generate_direct")
async def generate_animation_direct(request: GenerateRequest):
	"""Stateless generation that bypasses database operations entirely.
	Returns video_url, ai_response, and manim_code directly.
	"""
	try:
		job_id = str(uuid.uuid4())

		# 1) Run AI workflow
		result = await get_ai_service().process_animation_request(request.prompt)
		if not result or (isinstance(result, dict) and result.get("status") == "failed"):
			return {"error": (result or {}).get("error", "AI generation failed")}

		animation_spec = result.get("animation_spec", {})
		manim_code = result.get("manim_code", "")
		workflow_type = result.get("workflow_type", "unknown")
		complexity_analysis = result.get("complexity_analysis", {})
		enhancements_applied = result.get("enhancements_applied", [])

		# 2) Render Manim video
		video_path = await generate_video_from_manim(manim_code, job_id)
		if not video_path:
			return {"error": "Failed to generate video (Manim)"}

		# 3) Upload to Supabase storage (no DB rows)
		# Use a placeholder user_id since this is a direct endpoint
		placeholder_user_id = "direct_user"
		video_url = await upload_video_to_supabase(video_path, job_id, placeholder_user_id)
		if not video_url:
			return {"error": "Failed to upload video"}

		return {
			"job_id": job_id,
			"status": "completed",
			"video_url": video_url,
			"workflow_type": workflow_type,
			"complexity_level": complexity_analysis.get("level", "unknown"),
			"enhancements_applied": len(enhancements_applied),
			"ai_response": animation_spec,
			"manim_code": manim_code,
		}
	except Exception as e:
		logger.error(f"Error in generate_direct endpoint: {e}")
		return {"error": str(e)}

async def process_generation_job(job_id: str, prompt: str, user_id: str):
    """Process animation generation asynchronously"""
    try:
        logger.info(f"Processing generation job {job_id}")
        # Open a fresh DB session for background work
        db = SessionLocal()
        
        # Update job status
        generation_jobs[job_id]["status"] = "processing"
        generation_jobs[job_id]["current_step"] = 1
        try:
            db.execute(
                text("UPDATE generation_jobs SET status='processing', current_step=1, updated_at=now() WHERE id=:id"),
                {"id": job_id},
            )
            db.commit()
        except Exception as ue:
            logger.warning(f"DB update failed (processing step 1): {ue}")
        
        # Steps 1-2 with retry: generate -> render -> upload
        last_error_summary = ""
        success = False
        new_video_id = None
        for attempt in range(1, 4):
            try:
                logger.info(f"Attempt {attempt}/3: Generating animation spec for job {job_id}")
                augmented_prompt = prompt if attempt == 1 else (
                    f"{prompt}\n\nConstraints: The previous attempt failed with error: {last_error_summary}. "
                    "Regenerate a corrected JSON spec that avoids this issue and remains compatible with Manim v0.19, "
                    "ensuring safe numeric types (no float steps in Python range) and robust axes numbering."
                )
                ai_result = await get_ai_service().process_animation_request(augmented_prompt)
                if ai_result["status"] == "failed":
                    raise Exception(f"AI generation failed: {ai_result.get('error', 'Unknown error')}")

                # Update job with AI response
                generation_jobs[job_id]["current_step"] = 2
                generation_jobs[job_id]["ai_response"] = ai_result["animation_spec"]
                generation_jobs[job_id]["manim_code"] = ai_result["manim_code"]
                try:
                    db.execute(
                        text(
                            "UPDATE generation_jobs SET current_step=2, ai_response=:ar, manim_code=:mc, updated_at=now() WHERE id=:id"
                        ),
                        {
                            "id": job_id,
                            "ar": json.dumps(ai_result["animation_spec"])[:50000],
                            "mc": ai_result["manim_code"][:50000],
                        },
                    )
                    db.commit()
                except Exception as ue2:
                    logger.warning(f"DB update failed (after AI result): {ue2}")

                # Render and upload
                logger.info(f"Attempt {attempt}/3: Rendering video for job {job_id}")
                import uuid
                new_video_id = str(uuid.uuid4())
                ts = _dt.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                safe_prompt = slugify(prompt)[:80] or "animation"
                file_path = f"{user_id}/{safe_prompt}_{ts}_{new_video_id[:8]}.mp4"
                import tempfile, subprocess
                with tempfile.TemporaryDirectory() as tmpdir:
                    scene_file = Path(tmpdir) / "generated_scene.py"
                    scene_file.write_text(generation_jobs[job_id]["manim_code"], encoding="utf-8")
                    cmd = [
                        "manim", "render",
                        str(scene_file),
                        "GeneratedScene",
                        "-ql",
                        "--renderer=cairo",
                        "--format=mp4",
                        "--media_dir",
                        tmpdir,
                    ]
                    logger.info(f"Running render: {' '.join(cmd)}")
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=420)
                    if proc.returncode != 0:
                        logger.error(proc.stdout)
                        logger.error(proc.stderr)
                        err_out = (proc.stderr or proc.stdout or "Manim render failed").strip()
                        raise Exception(err_out)
                    out = next(Path(tmpdir).rglob("*.mp4"), None)
                    if not out or not out.exists():
                        raise Exception("Rendered MP4 not found")
                    if not SUPABASE_SERVICE_KEY:
                        raise Exception("Storage misconfigured")
                    upload_url = f"{SUPABASE_URL}/storage/v1/object/{NEW_BUCKET}/{file_path}"
                    headers = {"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "apikey": SUPABASE_SERVICE_KEY, "Content-Type": "video/mp4"}
                    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=5.0)) as client:
                        resp = await client.post(upload_url, headers=headers, content=out.read_bytes())
                        if resp.status_code not in (200, 201):
                            raise Exception(f"Upload failed: {resp.status_code} {resp.text}")

                success = True
                break
            except Exception as attempt_err:
                last_error_summary = str(attempt_err)[:500]
                logger.error(f"Attempt {attempt} failed: {last_error_summary}")
                try:
                    db.execute(
                        text("UPDATE generation_jobs SET error_message=:err, updated_at=now() WHERE id=:id"),
                        {"id": job_id, "err": f"Attempt {attempt} failed: {last_error_summary}"[:1000]},
                    )
                    db.commit()
                except Exception:
                    pass

        if not success:
            raise Exception(f"All attempts failed. Last error: {last_error_summary}")

        # Insert DB row now that file exists
        try:
            db.execute(
                text(
                    """
                    INSERT INTO videos (id, user_id, file_path, prompt, status, mime_type, created_at, generation_job_id)
                    VALUES (:id, :uid, :file_path, :prompt, :status, :mime_type, now(), :gjid)
                    """
                ),
                {
                    "id": new_video_id,
                    "uid": user_id,
                    "file_path": file_path,
                    "prompt": prompt,
                    "status": "completed",
                    "mime_type": "video/mp4",
                    "gjid": job_id,
                },
            )
            db.commit()
        except Exception:
            # Fallback if generation_job_id column doesn't exist
            db.rollback()
            db.execute(
                text(
                    """
                    INSERT INTO videos (id, user_id, file_path, prompt, status, mime_type, created_at)
                    VALUES (:id, :uid, :file_path, :prompt, :status, :mime_type, now())
                    """
                ),
                {
                    "id": new_video_id,
                    "uid": user_id,
                    "file_path": file_path,
            "prompt": prompt,
                    "status": "completed",
                    "mime_type": "video/mp4",
                },
            )
            db.commit()

        # Finalize job and point to streaming endpoint
        generation_jobs[job_id]["current_step"] = 4
        generation_jobs[job_id]["status"] = "completed"
        generation_jobs[job_id]["video_url"] = f"/api/videos/{new_video_id}/stream"
        try:
            db.execute(
                text(
                    "UPDATE generation_jobs SET status='completed', current_step=4, result_video_id=:vid, updated_at=now() WHERE id=:id"
                ),
                {"id": job_id, "vid": new_video_id},
            )
            db.commit()
        except Exception as ue3:
            logger.warning(f"DB update failed (finalize job): {ue3}")
        
        logger.info(f"Generation job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing generation job {job_id}: {e}")
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = str(e)
        try:
            with SessionLocal() as _db2:
                _db2.execute(
                    text("UPDATE generation_jobs SET status='failed', error_message=:err, updated_at=now() WHERE id=:id"),
                    {"id": job_id, "err": str(e)[:1000]},
                )
                _db2.commit()
        except Exception:
            pass
    finally:
        try:
            db.close()
        except Exception:
            pass
        
        # No DB-side job/video updates needed on failure for minimal schema

@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_generation_status(
    job_id: str, 
    request: Request, 
    auth: Dict[str, Any] = Depends(require_authentication)
):
    """Get the status of a generation job"""
    try:
        # Get authenticated user ID
        user_id = auth.get("user_id")
        if not user_id or user_id == "anonymous":
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Initialize job variable
        job = None
        
        # Check in-memory storage first
        if job_id in generation_jobs:
            job = generation_jobs[job_id]
            # Verify job belongs to authenticated user
            if job.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="Access denied - job belongs to different user")
            logger.info(f"Found job {job_id} in memory: {job['status']}")
        else:
            # Get job from database
            try:
                # Initialize database if not already done
                initialize_database_lazy()
                
                # Create database session manually
                if not SessionLocal:
                    raise HTTPException(status_code=503, detail="Database not available")
                
                db = SessionLocal()
                
                row = db.execute(
                    text(
                        "SELECT user_id, status, current_step, total_steps, result_video_id, error_message, ai_response, manim_code FROM generation_jobs WHERE id = :id LIMIT 1"
                    ),
                    {"id": job_id},
                ).fetchone()
                
                if not row:
                    raise HTTPException(status_code=404, detail="Generation job not found")
                
                # Verify job belongs to authenticated user
                db_user_id = getattr(row, "user_id", None) or row[0]
                if db_user_id != user_id:
                    raise HTTPException(status_code=403, detail="Access denied - job belongs to different user")
                
                job = {
                    "user_id": db_user_id,
                    "status": getattr(row, "status", None) or (len(row) > 1 and row[1]) or "processing",
                    "current_step": getattr(row, "current_step", None) or (len(row) > 2 and row[2]) or 0,
                    "total_steps": getattr(row, "total_steps", None) or (len(row) > 3 and row[3]) or 4,
                    "result_video_id": getattr(row, "result_video_id", None) or (len(row) > 4 and row[4]) or None,
                    "error": getattr(row, "error_message", None) or (len(row) > 5 and row[5]) or None,
                    "ai_response": getattr(row, "ai_response", None) or (len(row) > 6 and row[6]) or None,
                    "manim_code": getattr(row, "manim_code", None) or (len(row) > 7 and row[7]) or None,
                }
                logger.info(f"Found job {job_id} in database: {job['status']}")
                
            except Exception as db_error:
                logger.error(f"Database error when checking job {job_id}: {db_error}")
                raise HTTPException(status_code=500, detail="Failed to retrieve job status")
            finally:
                try:
                    db.close()
                except Exception:
                    pass
        
        # Ensure job was found
        if job is None:
            raise HTTPException(status_code=404, detail="Generation job not found")
        
        # Ensure video_url is absolute for frontend playback
        base = str(request.base_url).rstrip("/")
        job_video_url = job.get("video_url")
        if not job_video_url and job.get("result_video_id"):
            job_video_url = f"/api/videos/{job['result_video_id']}/stream"
        if job_video_url:
            if job_video_url.startswith("http://") or job_video_url.startswith("https://"):
                absolute_url = job_video_url
            else:
                # Guarantee single slash between base and path
                absolute_url = f"{base}{job_video_url if job_video_url.startswith('/') else '/' + job_video_url}"
        else:
            absolute_url = None

        # Convert ai_response and manim_code to strings if they are JSON objects
        ai_response = job.get("ai_response")
        manim_code = job.get("manim_code")
        
        if ai_response and not isinstance(ai_response, str):
            import json
            ai_response = json.dumps(ai_response)
        
        if manim_code and not isinstance(manim_code, str):
            import json
            manim_code = json.dumps(manim_code)
        
        return StatusResponse(
            id=job_id,
            status=job["status"],
            current_step=job["current_step"],
            total_steps=job["total_steps"],
            video_url=absolute_url,
            error=job.get("error"),
            ai_response=ai_response,
            manim_code=manim_code
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/videos", response_model=List[VideoResponse])
async def get_user_videos(
    user_id: str = Header(..., alias="user-id"),
    request: Request = None,
):
    """Get all videos for a user, compatible with existing Supabase schema."""
    try:
        logger.info(f"Fetching videos for user {user_id}")

        # Initialize database if not already done
        initialize_database_lazy()

        # Create database session
        if not SessionLocal:
            raise HTTPException(status_code=503, detail="Database not available")
        
        with SessionLocal() as db:
            # Use resilient select limited to commonly existing columns
            rows = db.execute(
                text("""
                    SELECT id, prompt, created_at, file_path, status, mime_type
                    FROM videos
                    WHERE user_id = :uid
                    ORDER BY created_at DESC NULLS LAST
                """),
                {"uid": user_id},
            ).fetchall()

            results: List[VideoResponse] = []
            # Resolve URLs concurrently
            async def build_response(r):
                # Row may be a RowMapping or tuple depending on driver
                rid = getattr(r, "id", None) or r[0]
                rprompt = getattr(r, "prompt", None) or r[1]
                rcreated = getattr(r, "created_at", None) or (len(r) > 2 and r[2]) or datetime.now(timezone.utc)
                rfile = getattr(r, "file_path", None) or (len(r) > 3 and r[3]) or None
                rstatus = getattr(r, "status", None) or (len(r) > 4 and r[4]) or "completed"
                url = await resolve_public_video_url(rfile or "")
                return VideoResponse(
                    id=str(rid),
                    prompt=rprompt or "",
                    video_url=url,
                    thumbnail_url=None,
                    mime_type=(getattr(r, "mime_type", None) or (len(r) > 5 and r[5]) or None),
                    status=rstatus or "completed",
                    error_message=None,
                    created_at=rcreated,
                )

            # For reliable playback (CORS/range), serve via backend stream endpoint
            base = str(request.base_url).rstrip("/") if request else ""
            async def build_with_stream(r):
                vr = await build_response(r)
                vr.video_url = f"{base}/api/videos/{vr.id}/stream"
                return vr

            results = await asyncio.gather(*(build_with_stream(r) for r in rows))
            return results

    except Exception as e:
        logger.error(f"Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch videos")

@app.get("/api/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, request: Request = None):
    """Get a specific video by ID, compatible with existing Supabase schema."""
    try:
        # Initialize database if not already done
        initialize_database_lazy()

        # Create database session
        if not SessionLocal:
            raise HTTPException(status_code=503, detail="Database not available")
        
        with SessionLocal() as db:
            row = db.execute(
                text("""
                    SELECT id, prompt, created_at, file_path, status, mime_type
                    FROM videos
                    WHERE id = :vid
                    LIMIT 1
                """),
                {"vid": video_id},
            ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Video not found")

            rid = getattr(row, "id", None) or row[0]
            rprompt = getattr(row, "prompt", None) or row[1]
            rcreated = getattr(row, "created_at", None) or (len(row) > 2 and row[2]) or datetime.now(timezone.utc)
            rfile = getattr(row, "file_path", None) or (len(row) > 3 and row[3]) or None
            rstatus = getattr(row, "status", None) or (len(row) > 4 and row[4]) or "completed"

            # Serve via backend stream endpoint for reliability
            base = str(request.base_url).rstrip("/") if request else ""
            url = f"{base}/api/videos/{rid}/stream"

            return VideoResponse(
                id=str(rid),
                prompt=rprompt or "",
                video_url=url,
                thumbnail_url=None,
                mime_type=(getattr(row, "mime_type", None) or (len(row) > 5 and row[5]) or None),
                status=rstatus or "completed",
                error_message=None,
                created_at=rcreated,
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching video: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch video")

@app.get("/api/videos/{video_id}/stream")
async def stream_video(video_id: str, request: Request):
    """Proxy stream the video from Supabase storage (new bucket first, then old) with Range support.
    Uses service key for private buckets.
    """
    try:
        # Initialize database if not already done
        initialize_database_lazy()

        # Create database session
        if not SessionLocal:
            raise HTTPException(status_code=503, detail="Database not available")
        
        with SessionLocal() as db:
            row = db.execute(
                text("""
                    SELECT file_path, mime_type
                    FROM videos
                    WHERE id = :vid
                    LIMIT 1
                """),
                {"vid": video_id},
            ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Video not found")

            file_path = (getattr(row, "file_path", None) or (len(row) > 0 and row[0]) or "").lstrip("/")
            mime_type = getattr(row, "mime_type", None) or (len(row) > 1 and row[1]) or "video/mp4"

            if not SUPABASE_SERVICE_KEY:
                logger.error("SUPABASE_SERVICE_KEY missing; cannot stream from private storage")
                raise HTTPException(status_code=500, detail="Storage misconfigured")

            # Private storage endpoints (authorized with service key)
            candidates = [
                f"{SUPABASE_URL}/storage/v1/object/{NEW_BUCKET}/{file_path}",
                f"{SUPABASE_URL}/storage/v1/object/{OLD_BUCKET}/{file_path}",
            ]

            range_header = request.headers.get("range")
            timeout = httpx.Timeout(10.0, connect=5.0)
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                for url in candidates:
                    try:
                        headers = {"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}
                        if range_header:
                            headers["Range"] = range_header
                        resp = await client.get(url, headers=headers)
                        if resp.status_code in (200, 206):
                            stream = resp.aiter_bytes()
                            forward_headers = {}
                            for h in ("Content-Length", "Content-Range", "Accept-Ranges", "Cache-Control"):
                                if h in resp.headers:
                                    forward_headers[h] = resp.headers[h]
                            return StreamingResponse(stream, status_code=resp.status_code, media_type=mime_type, headers=forward_headers)
                    except Exception:
                        continue
            raise HTTPException(status_code=404, detail="Video file not found in buckets")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming video: {e}")
        raise HTTPException(status_code=500, detail="Failed to stream video")

@app.delete("/api/videos/{video_id}")
async def delete_video(
    video_id: str,
    user_id: str = Header(..., alias="user-id")
):
    """Delete a video"""
    try:
        # Initialize database if not already done
        initialize_database_lazy()

        # Create database session
        if not SessionLocal:
            raise HTTPException(status_code=503, detail="Database not available")
        
        with SessionLocal() as db:
            # Resolve file_path first (raw SQL since ORM tables may differ)
            row = db.execute(
                text(
                    """
                    SELECT file_path
                    FROM videos
                    WHERE id = :vid AND user_id = :uid
                    LIMIT 1
                    """
                ),
                {"vid": video_id, "uid": user_id},
            ).fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Video not found")

            file_path = (getattr(row, "file_path", None) or row[0] or "").lstrip("/")

            # Delete DB row
            db.execute(
                text("DELETE FROM videos WHERE id = :vid AND user_id = :uid"),
                {"vid": video_id, "uid": user_id},
            )
            db.commit()

            # Best-effort delete from storage
            if file_path:
                try:
                    await supabase_delete_object(NEW_BUCKET, file_path)
                except Exception:
                    pass

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
    user_id: str = Header(..., alias="user-id")
):
    """Submit feedback for a video"""
    try:
        # Initialize database if not already done
        initialize_database_lazy()

        # Create database session
        if not SessionLocal:
            raise HTTPException(status_code=503, detail="Database not available")
        
        with SessionLocal() as db:
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
async def download_video(video_id: str):
    """Download a video file"""
    try:
        # Initialize database if not already done
        initialize_database_lazy()

        # Create database session
        if not SessionLocal:
            raise HTTPException(status_code=503, detail="Database not available")
        
        with SessionLocal() as db:
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