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

from fastapi import FastAPI, HTTPException, Request, Depends, Header, Query
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# SQLAlchemy removed in favor of Supabase client
# Removed SQLAlchemy usage; using Supabase client instead
import asyncio
from datetime import datetime as _dt, timezone
from slugify import slugify
import httpx
from urllib.parse import urlparse

from services.supabase_db import supabase_db
# Legacy ORM models not used; database operations now use Supabase client
from schemas import (
    GenerateRequest, GenerateResponse, StatusResponse, 
    VideoResponse, FeedbackRequest, HealthResponse
)
from services.ai_service_new import AIService
from services.clerk_auth import require_authentication, require_authentication_long_running, optional_authentication
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
    """Initialize Supabase database service only when needed"""
    global _database_initialized
    if _database_initialized:
        return
    
    try:
        # Test Supabase database connection
        if supabase_db.enabled:
            logger.info("Supabase database service is available and ready")
        else:
            logger.warning("Supabase database service not available - some features may not work")
        
        _database_initialized = True
        
    except Exception as e:
        logger.error(f"Supabase database service initialization failed: {e}")
        logger.warning("Continuing without database - some features may not work")

# Check if Supabase database service is available at startup
DATABASE_AVAILABLE_AT_STARTUP = supabase_db.enabled
if not DATABASE_AVAILABLE_AT_STARTUP:
    logger.warning("Supabase database service not available at startup - some endpoints may not work")
else:
    logger.info("Supabase database service is available and ready")

def is_database_available() -> bool:
    """Check if Supabase database service is available at runtime"""
    try:
        # Initialize database service if not already done
        initialize_database_lazy()
        return supabase_db.enabled
    except Exception:
        return False

# Ensure generation_jobs table exists (for cross-instance job status)
async def _ensure_generation_jobs_table() -> None:
    """Ensure generation_jobs table exists - called only when needed"""
    try:
        # Initialize database service if not already done
        initialize_database_lazy()
        
        if not supabase_db.enabled:
            logger.warning("Cannot ensure generation_jobs table - Supabase database service not available")
            return
            
        # Test if we can access the table
        await supabase_db.ensure_tables_exist()
        logger.info("Generation jobs table is accessible")
        
    except Exception as e:
        logger.error(f"Failed to ensure generation_jobs table: {e}")
        logger.warning("Continuing without table creation - some features may not work")

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
        "SUPABASE_URL": "Required for database and storage operations",
        "SUPABASE_SERVICE_KEY": "Required for database and storage operations",
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
    """Return a working URL for the given file_path, trying new bucket then old.
    Uses authenticated storage endpoint since buckets are private.
    """
    if not file_path:
        return None
    if not SUPABASE_SERVICE_KEY:
        logger.warning("SUPABASE_SERVICE_KEY missing; cannot check storage")
        return None
        
    path = file_path.lstrip("/")
    candidates = [
        f"{SUPABASE_URL}/storage/v1/object/{NEW_BUCKET}/{path}",
        f"{SUPABASE_URL}/storage/v1/object/{OLD_BUCKET}/{path}",
    ]
    timeout = httpx.Timeout(2.0, connect=2.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for url in candidates:
            try:
                headers = {
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "apikey": SUPABASE_SERVICE_KEY,
                }
                r = await client.head(url, headers=headers)
                if r.status_code == 200:
                    # Return the authenticated URL that can be used for streaming
                    return url
            except Exception as e:
                logger.debug(f"Failed to check {url}: {e}")
                continue
    return None


def build_https_base_url(request: Request) -> str:
    """Build a public https base URL using proxy headers.
    Ensures we never return http URLs to the browser (avoid mixed content).
    """
    try:
        xf_proto = request.headers.get("x-forwarded-proto") or request.headers.get("X-Forwarded-Proto")
        xf_host = request.headers.get("x-forwarded-host") or request.headers.get("X-Forwarded-Host")
        host = xf_host or request.headers.get("host") or urlparse(str(request.base_url)).netloc
        scheme = "https"
        return f"{scheme}://{host}"
    except Exception:
        # Fallback to request.base_url but force https scheme
        parsed = urlparse(str(request.base_url))
        netloc = parsed.netloc or ""
        return f"https://{netloc}"


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


async def ensure_placeholder_uploaded(db, dest_path: str) -> bool:
    """Ensure there is a file at dest_path in NEW_BUCKET by copying an existing video as placeholder."""
    try:
        # Find a recent existing file_path to clone
        row = None
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
    """Generate video from Manim code - IMPROVED VERSION"""
    try:
        logger.info(f"Starting video generation for job {job_id}")
        
        # Validate input code
        if not manim_code or not isinstance(manim_code, str):
            logger.error("Invalid Manim code provided")
            return None
        
        # Check for dangerous patterns
        dangerous_patterns = ['eval(', '__import__(', 'exec(', 'open(', 'file(']
        for pattern in dangerous_patterns:
            if pattern in manim_code:
                # More intelligent detection - check if it's in a string literal or comment
                lines = manim_code.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line:
                        # Skip if it's a comment
                        stripped_line = line.strip()
                        if stripped_line.startswith('#'):
                            continue
                        
                        # Skip if it's in a string literal
                        if f"'{pattern}" in line or f'"{pattern}' in line:
                            continue
                        
                        # This is an actual dangerous pattern
                        logger.error(f"Dangerous pattern found on line {i+1}: {line.strip()}")
                        return None
        
        # Create temporary directory for Manim execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            logger.info(f"Created temp directory: {temp_path}")
            
            # Create Manim scene file
            scene_file = temp_path / "animation_scene.py"
            scene_file.write_text(manim_code, encoding='utf-8')
            logger.info(f"Created scene file: {scene_file}")
            
            # Run Manim command in headless mode - FIXED 2025-08-21 for v0.19.0
            cmd = [
                "manim", "render", "-ql", str(scene_file), "GeneratedScene"
            ]
            
            logger.info(f"Running Manim command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=temp_path,
                timeout=300  # 5 minutes timeout
            )
            
            logger.info(f"Manim process completed with return code: {result.returncode}")
            
            if result.returncode != 0:
                logger.error(f"Manim execution failed with return code {result.returncode}")
                logger.error(f"Manim stdout: {result.stdout}")
                logger.error(f"Manim stderr: {result.stderr}")
                
                # Try to identify specific errors
                error_output = result.stderr or result.stdout or ""
                if "ImportError" in error_output:
                    logger.error("Import error detected - missing dependencies")
                elif "SyntaxError" in error_output:
                    logger.error("Syntax error detected - invalid Python code")
                elif "AttributeError" in error_output:
                    logger.error("Attribute error detected - invalid object usage")
                elif "NameError" in error_output:
                    logger.error("Name error detected - undefined variables")
                elif "TypeError" in error_output:
                    logger.error("Type error detected - invalid parameter types")
                elif "ValueError" in error_output:
                    logger.error("Value error detected - invalid parameter values")
                else:
                    logger.error("Unknown Manim execution error")
                
                return None
            
            # Add small delay to ensure file is fully written
            import time
            time.sleep(1)
            
            # Find generated video file - handle Manim v0.19.0 output structure
            media_dir = temp_path / "media"
            logger.info(f"Searching for video files in: {media_dir}")
            
            if not media_dir.exists():
                logger.error(f"Media directory does not exist: {media_dir}")
                return None
            
            # Search recursively for MP4 files
            video_files = list(media_dir.rglob("*.mp4"))
            logger.info(f"Found {len(video_files)} video files: {[str(f) for f in video_files]}")
            
            if not video_files:
                logger.error("No video files generated by Manim")
                # List all files in media directory for debugging
                all_files = list(media_dir.rglob("*"))
                logger.error(f"All files in media directory: {[str(f) for f in all_files]}")
                
                # Check if there are any error files
                error_files = list(media_dir.rglob("*.log"))
                if error_files:
                    for error_file in error_files:
                        try:
                            error_content = error_file.read_text(encoding='utf-8')
                            logger.error(f"Error log content from {error_file}: {error_content}")
                        except Exception as e:
                            logger.error(f"Could not read error log {error_file}: {e}")
                
                return None
            
            # Return path to the first video file
            video_path = str(video_files[0])
            logger.info(f"Selected video file: {video_path}")
            
            # Verify video file is valid
            if not Path(video_path).exists():
                logger.error(f"Selected video file does not exist: {video_path}")
                return None
            
            file_size = Path(video_path).stat().st_size
            if file_size == 0:
                logger.error(f"Video file is empty: {video_path}")
                return None
            
            logger.info(f"Video file size: {file_size} bytes")
            
            # Persist video to a stable temp path so it's available after context exits
            stable_path = Path("/tmp") / f"animathic_{job_id}.mp4"
            try:
                shutil.copy(video_path, stable_path)
                logger.info(f"Copied video to stable path: {stable_path}")
                return str(stable_path)
            except Exception as copy_err:
                logger.warning(f"Failed to copy video to stable path, returning original: {copy_err}")
                return video_path
            
    except subprocess.TimeoutExpired:
        logger.error(f"Manim execution timed out after 5 minutes for job {job_id}")
        return None
    except FileNotFoundError:
        logger.error("Manim command not found - Manim may not be installed")
        return None
    except PermissionError:
        logger.error("Permission denied when running Manim command")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating video from Manim: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

async def upload_video_to_supabase(video_path: str, job_id: str, user_id: str, prompt: str = "") -> Optional[Dict[str, str]]:
    """Upload video to Supabase storage.
    Returns {"url": public_url_or_none, "object_key": path_in_bucket}
    """
    try:
        logger.info(f"Uploading video {video_path} to Supabase for job {job_id}")
        
        # Use Supabase storage service
        upload_result = await supabase_storage.upload_video(video_path, job_id, user_id, prompt)
        
        if upload_result:
            # upload_result is a dict with url and object_key
            logger.info(f"Video uploaded successfully: {upload_result}")
            return upload_result
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
    try:
        # Check Supabase database connection
        if not supabase_db.enabled:
            return HealthResponse(
                status="unhealthy",
                timestamp=datetime.now(timezone.utc),
                version="1.0.0",
                database="unavailable",
                details="Supabase database service not configured"
            )
        
        # Test database connection with timeout
        try:
            db_healthy = await supabase_db.test_connection()
            if not db_healthy:
                return HealthResponse(
                    status="unhealthy",
                    timestamp=datetime.now(timezone.utc),
                    version="1.0.0",
                    database="connection_error",
                    details="Supabase database connection failed"
                )
        except Exception as db_error:
            logger.warning(f"Database health check failed: {db_error}")
            # Return unhealthy but don't crash the service
            return HealthResponse(
                status="unhealthy",
                timestamp=datetime.now(timezone.utc),
                version="1.0.0",
                database="connection_error",
                details=f"Database connection failed: {str(db_error)[:100]}"
            )
        
        # Check storage connectivity
        storage_status = "unknown"
        try:
            if SUPABASE_SERVICE_KEY:
                # Test storage access
                test_url = f"{SUPABASE_URL}/storage/v1/bucket/{NEW_BUCKET}"
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        test_url,
                        headers={"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}
                    )
                    if response.status_code == 200:
                        storage_status = "accessible"
                    else:
                        storage_status = f"error_{response.status_code}"
            else:
                storage_status = "no_key"
        except Exception as e:
            storage_status = f"error_{str(e)[:50]}"
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            version="1.0.0",
            database="supabase",
            details=f"Storage: {storage_status}"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(timezone.utc),
            version="1.0.0",
            database="error",
            details=str(e)
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
        
        # Check if token will expire soon and warn user
        if auth.get("_warn_refresh_soon"):
            logger.warning(f"User {user_id} starting long operation with token expiring soon")
            # Don't block the request, but log the warning
        
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
        
        # Try to insert job record in Supabase (optional)
        if is_database_available() and getattr(supabase_db, "client", None):
            try:
                pass
                # await _ensure_generation_jobs_table()
                supabase_db.client.table("generation_jobs").insert({
                    "id": job_id,
                    "user_id": user_id,
                    "prompt": request.prompt,
                    "status": "processing",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "ai_response": None,
                    "manim_code": None,
                }).execute()
                logger.info(f"Job {job_id} recorded in Supabase")
            except Exception as db_error:
                logger.warning(f"Failed to record job in Supabase: {db_error}")
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
            upload_result = await upload_video_to_supabase(video_path, job_id, user_id, prompt)
            
            if not upload_result:
                raise Exception("Failed to upload video to storage")
            
            generation_jobs[job_id]["current_step"] = 4
            generation_jobs[job_id]["file_path"] = upload_result.get("object_key")
            # Immediately set a stream-by-path URL so frontend can play even if DB insert is delayed
            try:
                from urllib.parse import quote as _quote
                key_q = _quote(str(generation_jobs[job_id]["file_path"]).lstrip("/"))
                generation_jobs[job_id]["video_url"] = f"/api/stream?bucket={NEW_BUCKET}&key={key_q}"
            except Exception:
                pass

            # Create video row in Supabase so it appears on the dashboard
            try:
                if supabase_db.enabled:
                    import uuid as _uuid
                    new_video_id = str(_uuid.uuid4())
                    vid_payload = {
                        "id": new_video_id,
                        "user_id": user_id,
                        "file_path": generation_jobs[job_id]["file_path"],
                        "prompt": prompt,
                        "status": "completed",
                        "mime_type": "video/mp4",
                        "generation_job_id": job_id,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                    vid_id = await supabase_db.create_video(vid_payload)
                    if not vid_id:
                        logger.warning(f"Supabase create_video returned no id for job {job_id}")
                    # Record result video id and stream URL for status endpoint
                    generation_jobs[job_id]["result_video_id"] = new_video_id
                    # Keep existing path URL; also set id-based URL as an alternative for clients that use it
                    generation_jobs[job_id]["video_url_id_based"] = f"/api/videos/{new_video_id}/stream"
            except Exception as _e:
                logger.warning(f"Failed to create video row: {_e}")
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
            
            # Try to update database (Supabase client)
            try:
                if supabase_db.enabled and getattr(supabase_db, "client", None):
                    update_payload = {
                        "status": "completed",
                        "current_step": 4,
                        "ai_response": json.dumps(animation_spec),
                        "manim_code": manim_code,
                        "video_url": generation_jobs[job_id].get("video_url"),
                    }
                    # Include result_video_id if available
                    if generation_jobs[job_id].get("result_video_id"):
                        update_payload["result_video_id"] = generation_jobs[job_id]["result_video_id"]
                    supabase_db.client.table("generation_jobs").update(update_payload).eq("id", job_id).execute()
                else:
                    logger.warning("Supabase DB not enabled; skipping job finalize DB update")
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
		upload_result = await upload_video_to_supabase(video_path, job_id, placeholder_user_id, request.prompt if hasattr(request, "prompt") else "")
		if not upload_result:
			return {"error": "Failed to upload video"}

		return {
			"job_id": job_id,
			"status": "completed",
			"video_url": upload_result.get("url"),
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
        db = None
        
        # Update job status
        generation_jobs[job_id]["status"] = "processing"
        generation_jobs[job_id]["current_step"] = 1
        try:
            pass
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
                    pass
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

                    # Create video DB row so it appears on the dashboard
                    try:
                        if supabase_db.enabled and getattr(supabase_db, "client", None):
                            await supabase_db.create_video({
                                "id": new_video_id,
                                "user_id": user_id,
                                "file_path": file_path,
                                "prompt": prompt,
                                "status": "completed",
                                "mime_type": "video/mp4",
                                "generation_job_id": job_id,
                                "created_at": datetime.now(timezone.utc).isoformat(),
                            })
                    except Exception as _e:
                        logger.warning(f"Failed to create video row (async path): {_e}")

                success = True
                break
            except Exception as attempt_err:
                last_error_summary = str(attempt_err)[:500]
                logger.error(f"Attempt {attempt} failed: {last_error_summary}")
                try:
                    pass
                except Exception:
                    pass

        if not success:
            raise Exception(f"All attempts failed. Last error: {last_error_summary}")

        # Insert DB row now that file exists
        try:
            pass
        except Exception:
            pass

        # Finalize job and point to streaming endpoint
        generation_jobs[job_id]["current_step"] = 4
        generation_jobs[job_id]["status"] = "completed"
        generation_jobs[job_id]["video_url"] = f"/api/videos/{new_video_id}/stream"
        try:
            pass
        except Exception as ue3:
            logger.warning(f"DB update failed (finalize job): {ue3}")
        
        logger.info(f"Generation job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing generation job {job_id}: {e}")
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = str(e)
        try:
            pass
        except Exception:
            pass
    finally:
        try:
            if db:
                db.close()
        except Exception:
            pass
        
        # No DB-side job/video updates needed on failure for minimal schema

@app.get("/api/auth/token-status")
async def check_token_status(
    auth: Dict[str, Any] = Depends(require_authentication)
):
    """Check the current token status and provide refresh guidance"""
    try:
        # Get token lifetime information
        from services.clerk_auth import clerk_auth
        token_info = auth
        
        # Get detailed token lifetime info
        lifetime_info = clerk_auth.get_token_lifetime_info(token_info)
        
        # Add user context
        response_data = {
            "user_id": auth.get("user_id"),
            "authenticated": True,
            "token_status": lifetime_info,
            "refresh_recommended": lifetime_info.get("refresh_recommended", False),
            "message": lifetime_info.get("message", "Token status unknown")
        }
        
        # Add specific guidance for long-running processes
        if lifetime_info.get("status") == "expiring_soon":
            response_data["long_running_warning"] = "Your session will expire soon. Consider refreshing before starting long operations like video generation."
        elif lifetime_info.get("status") == "expired":
            response_data["long_running_warning"] = "Your session has expired. You must refresh your authentication to continue."
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error checking token status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check token status")

@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_generation_status(
    job_id: str, 
    request: Request, 
    auth: Dict[str, Any] = Depends(require_authentication_long_running)
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
            # Get job from Supabase
            try:
                initialize_database_lazy()
                if not (supabase_db.enabled and getattr(supabase_db, "client", None)):
                    raise HTTPException(status_code=503, detail="Database not available")

                resp = supabase_db.client.table("generation_jobs").select(
                    "user_id,status,current_step,total_steps,result_video_id,error_message,ai_response,manim_code"
                ).eq("id", job_id).single().execute()

                row = (resp.data or {})
                if not row:
                    raise HTTPException(status_code=404, detail="Generation job not found")

                # Verify job belongs to authenticated user
                db_user_id = row.get("user_id")
                if db_user_id != user_id:
                    raise HTTPException(status_code=403, detail="Access denied - job belongs to different user")

                job = {
                    "user_id": db_user_id,
                    "status": row.get("status", "processing"),
                    "current_step": row.get("current_step", 0),
                    "total_steps": row.get("total_steps", 4),
                    "result_video_id": row.get("result_video_id"),
                    "error": row.get("error_message"),
                    "ai_response": row.get("ai_response"),
                    "manim_code": row.get("manim_code"),
                }
                logger.info(f"Found job {job_id} in Supabase: {job['status']}")

            except HTTPException:
                raise
            except Exception as db_error:
                logger.error(f"Supabase error when checking job {job_id}: {db_error}")
                raise HTTPException(status_code=500, detail="Failed to retrieve job status")
        
        # Ensure job was found
        if job is None:
            raise HTTPException(status_code=404, detail="Generation job not found")
        
        # Ensure video_url is absolute for frontend playback
        base = build_https_base_url(request)
        job_video_url = job.get("video_url")
        if not job_video_url and job.get("result_video_id"):
            # Prefer id-based link if present, otherwise fall back to path-based
            id_based = f"/api/videos/{job['result_video_id']}/stream"
            job_video_url = job.get("video_url_id_based") or job.get("video_url") or id_based
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
    """Get all videos for a user directly from storage buckets."""
    try:
        logger.info(f"Fetching videos for user {user_id}")

        # Initialize database service if not already done
        initialize_database_lazy()

        # Check if Supabase database service is available
        if not supabase_db.enabled:
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Get all videos directly from both storage buckets
        all_videos = []
        
        try:
            new_bucket_items = await supabase_storage.list_user_videos_in_bucket(NEW_BUCKET, user_id)
            logger.info(f"Found {len(new_bucket_items)} videos in {NEW_BUCKET} bucket for user {user_id}")
            all_videos.extend(new_bucket_items)
        except Exception as e:
            logger.warning(f"Failed to list videos from {NEW_BUCKET}: {e}")
        
        try:
            old_bucket_items = await supabase_storage.list_user_videos_in_bucket(OLD_BUCKET, user_id)
            logger.info(f"Found {len(old_bucket_items)} videos in {OLD_BUCKET} bucket for user {user_id}")
            all_videos.extend(old_bucket_items)
        except Exception as e:
            logger.warning(f"Failed to list videos from {OLD_BUCKET}: {e}")
        
        logger.info(f"Total videos found: {len(all_videos)}")

        # Convert storage items to VideoResponse objects
        def build_video_response(item):
            try:
                # Extract filename and create a meaningful prompt
                # Storage items have 'object_key' field with full path including user_id
                object_key = item.get('object_key', '')
                
                # Better title extraction
                prompt = "Video from storage"  # Default fallback
                if object_key:
                    try:
                        # Remove user_id prefix and file extension to get clean filename
                        # object_key format: "user_id/filename_timestamp_id.mp4"
                        clean_name = object_key.replace(f"{user_id}/", "").rsplit(".", 1)[0]
                        
                        # Remove timestamp and short ID if present (pattern: _YYYYMMDD_HHMMSS_abcdef12)
                        import re
                        match = re.match(r"^(.*)_\d{8}_\d{6}_[a-f0-9]{8}$", clean_name)
                        if match:
                            prompt = match.group(1).replace("-", " ").replace("_", " ").strip()
                        else:
                            prompt = clean_name.replace("-", " ").replace("_", " ").strip()
                        
                        if not prompt:
                            prompt = "Video from storage"
                    except Exception as e:
                        logger.warning(f"Error extracting title from {object_key}: {e}")
                        prompt = "Video from storage"
                
                # Generate a unique ID for storage items
                storage_id = f"storage_{hash(object_key) % 1000000}"
                
                # Create video URL with the FULL object key (including user_id prefix)
                video_url = f"{build_https_base_url(request)}/api/stream?bucket={item.get('_bucket', NEW_BUCKET)}&key={object_key}"
                
                return VideoResponse(
                    id=storage_id,
                    prompt=prompt,
                    video_url=video_url,
                    status="completed",
                    file_path=object_key,  # Store the full object key
                    created_at=item.get('created_at', datetime.now(timezone.utc)),
                    mime_type="video/mp4"
                )
            except Exception as e:
                logger.error(f"Error building video response for item {item}: {e}")
                # Return a fallback response
                return VideoResponse(
                    id=f"error_{hash(str(item)) % 1000000}",
                    prompt="Error loading video",
                    video_url="",
                    status="error",
                    file_path="",
                    created_at=datetime.now(timezone.utc),
                    mime_type="video/mp4"
                )
        
        # Build all video responses
        results = [build_video_response(item) for item in all_videos]
        logger.info(f"Returning {len(results)} total videos for user {user_id}")
        return results

    except Exception as e:
        logger.error(f"Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch videos")

@app.get("/api/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, request: Request = None):
    """Get a specific video by ID, compatible with existing Supabase schema."""
    try:
        # Initialize database service if not already done
        initialize_database_lazy()

        # Check if Supabase database service is available
        if not supabase_db.enabled:
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Get video from Supabase
        row_data = await supabase_db.get_video(video_id)
        if not row_data:
            raise HTTPException(status_code=404, detail="Video not found")

        # Extract data from the row
        rid = row_data.get('id')
        rprompt = row_data.get('prompt')
        rcreated = row_data.get('created_at') or datetime.now(timezone.utc)
        rfile = row_data.get('file_path')
        rstatus = row_data.get('status') or "completed"
        rmime_type = row_data.get('mime_type')

        # Check if the video file actually exists in storage
        file_exists = await resolve_public_video_url(rfile or "")

        # Serve via backend stream endpoint for reliability
        base = build_https_base_url(request)
        url = f"{base}/api/videos/{rid}/stream" if file_exists else None
        
        # Update status based on file existence
        if file_exists:
            final_status = "completed"
            error_msg = None
        else:
            final_status = "file_missing"
            error_msg = "Video file not found in storage"

        return VideoResponse(
            id=str(rid),
            prompt=rprompt or "",
            video_url=url,
            thumbnail_url=None,
            mime_type=rmime_type,
            status=final_status,
            error_message=error_msg,
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
        # Initialize database service if not already done
        initialize_database_lazy()

        # Check if Supabase database service is available
        if not supabase_db.enabled:
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Get video from Supabase
        row_data = await supabase_db.get_video(video_id)
        if not row_data:
            # Fallback 1: job row holds result_video_id
            try:
                job = await supabase_db.get_generation_job(video_id)
                if job and job.get("result_video_id"):
                    row_data = await supabase_db.get_video(job["result_video_id"])
            except Exception:
                pass
        if not row_data:
            # Fallback 2: video row references generation_job_id directly
            try:
                row_data = await supabase_db.get_video_by_job(video_id)
            except Exception:
                pass
        if not row_data:
            raise HTTPException(status_code=404, detail="Video not found")

        file_path = (row_data.get('file_path') or "").lstrip("/")
        mime_type = row_data.get('mime_type') or "video/mp4"

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
        
        # If video file not found, return a 404 with a helpful message
        logger.warning(f"Video file not found in buckets for video_id: {video_id}, file_path: {file_path}")
        raise HTTPException(status_code=404, detail="Video file not found in storage. The video may have been deleted or the file path is incorrect.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming video: {e}")
        raise HTTPException(status_code=500, detail="Failed to stream video")

@app.get("/api/stream")
async def stream_by_path(bucket: str, key: str, request: Request):
    """Stream a storage object directly by bucket and key (for storage-only items)."""
    try:
        if not SUPABASE_SERVICE_KEY:
            raise HTTPException(status_code=500, detail="Storage misconfigured")
        
        # Clean up the key - remove any leading slashes and ensure proper format
        file_path = key.lstrip("/")
        logger.info(f"Streaming request for bucket: {bucket}, key: {file_path}")
        
        # Try different Supabase storage endpoint formats
        # Format 1: Direct object access (for private buckets)
        url1 = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
        # Format 2: Public object access (for public buckets)
        url2 = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_path}"
        
        logger.info(f"Trying URL 1: {url1}")
        logger.info(f"Trying URL 2: {url2}")
        
        range_header = request.headers.get("range")
        timeout = httpx.Timeout(30.0, connect=10.0)
        
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            headers = {
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "apikey": SUPABASE_SERVICE_KEY
            }
            if range_header:
                headers["Range"] = range_header
            
            # Try the first URL (private bucket access)
            try:
                logger.info(f"Making request to Supabase with headers: {dict(headers)}")
                resp = await client.get(url1, headers=headers)
                logger.info(f"Supabase response status: {resp.status_code}")
                
                if resp.status_code in (200, 206):
                    stream = resp.aiter_bytes()
                    forward_headers = {}
                    for h in ("Content-Length", "Content-Range", "Accept-Ranges", "Cache-Control"):
                        if h in resp.headers:
                            forward_headers[h] = resp.headers[h]
                    
                    logger.info(f"Successfully streaming video from {bucket}/{file_path}")
                    return StreamingResponse(
                        stream, 
                        status_code=resp.status_code, 
                        media_type="video/mp4", 
                        headers=forward_headers
                    )
            except Exception as e:
                logger.warning(f"First URL failed: {e}")
            
            # Try the second URL (public bucket access)
            try:
                logger.info(f"Trying public URL: {url2}")
                resp = await client.get(url2, headers=headers)
                logger.info(f"Public URL response status: {resp.status_code}")
                
                if resp.status_code in (200, 206):
                    stream = resp.aiter_bytes()
                    forward_headers = {}
                    for h in ("Content-Length", "Content-Range", "Accept-Ranges", "Cache-Control"):
                        if h in resp.headers:
                            forward_headers[h] = resp.headers[h]
                    
                    logger.info(f"Successfully streaming video from public URL {bucket}/{file_path}")
                    return StreamingResponse(
                        stream, 
                        status_code=resp.status_code, 
                        media_type="video/mp4", 
                        headers=forward_headers
                    )
            except Exception as e:
                logger.warning(f"Public URL failed: {e}")
            
            # If both URLs fail, return detailed error
            logger.error(f"Both Supabase storage URLs failed for {bucket}/{file_path}")
            raise HTTPException(status_code=404, detail=f"Video file not found in storage: {bucket}/{file_path}")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming by path: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to stream video")

@app.delete("/api/videos/{video_id}")
async def delete_video(
    video_id: str,
    user_id: str = Header(..., alias="user-id"),
    object_key: str = Query(None, description="Object key for storage videos (required for storage videos)")
):
    """Delete a video"""
    try:
        # Initialize database service if not already done
        initialize_database_lazy()

        # Check if Supabase database service is available
        if not supabase_db.enabled:
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Handle storage-only videos (those with IDs starting with "storage_")
        if video_id.startswith("storage_"):
            # For storage-only videos, we need the object key to delete from storage
            # The frontend should provide this as a query parameter
            if not object_key:
                raise HTTPException(
                    status_code=400, 
                    detail="For storage videos, please provide the object_key as a query parameter. Example: DELETE /api/videos/storage_123?object_key=user_id/filename.mp4"
                )
            
            # Use the provided object key directly
            file_path = object_key
            logger.info(f"Deleting storage video with object key: {file_path}")
            
            # Delete from storage
            try:
                # Try both buckets
                success = False
                for bucket in [NEW_BUCKET, OLD_BUCKET]:
                    try:
                        if await supabase_delete_object(bucket, file_path):
                            success = True
                            logger.info(f"Successfully deleted video from bucket {bucket}: {file_path}")
                            break
                    except Exception as e:
                        logger.warning(f"Failed to delete from bucket {bucket}: {e}")
                        continue
                
                if not success:
                    logger.error(f"Failed to delete video from any bucket: {file_path}")
                    raise HTTPException(status_code=500, detail="Failed to delete video from storage")
                
            except Exception as e:
                logger.error(f"Error deleting storage video: {e}")
                raise HTTPException(status_code=500, detail="Failed to delete video from storage")
            
            return {"message": "Storage video deleted successfully"}
        
        # Handle database videos (existing logic)
        else:
            # Get video from Supabase to check ownership and get file path
            row_data = await supabase_db.get_video(video_id)
            if not row_data:
                raise HTTPException(status_code=404, detail="Video not found")

            # Check if user owns this video
            if row_data.get('user_id') != user_id:
                raise HTTPException(status_code=403, detail="Access denied")

            file_path = (row_data.get('file_path') or "").lstrip("/")

            # Delete from Supabase database
            success = await supabase_db.update_video(video_id, {"deleted_at": datetime.now(timezone.utc).isoformat()})
            if not success:
                # If update fails, try to delete the record
                try:
                    # Note: Supabase client doesn't have a direct delete method in the current version
                    # We'll mark it as deleted instead
                    logger.warning(f"Could not mark video {video_id} as deleted")
                except Exception as e:
                    logger.error(f"Failed to delete video record: {e}")

            # Best-effort delete from storage
            if file_path:
                try:
                    await supabase_delete_object(NEW_BUCKET, file_path)
                except Exception:
                    pass

            return {"message": "Database video deleted successfully"}
        
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
    """Submit feedback for a video (stub; persistence can be added via Supabase if desired)."""
    try:
        initialize_database_lazy()
        if not supabase_db.enabled:
            raise HTTPException(status_code=503, detail="Database not available")
        video = await supabase_db.get_video(video_id)
        if not video or video.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Video not found")
        logger.info(f"Feedback received for video {video_id}: rating={feedback.rating}")
        return {"message": "Feedback received"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/videos/{video_id}/download")
async def download_video(video_id: str):
    """Return basic metadata for download (placeholder)."""
    try:
        initialize_database_lazy()
        if not supabase_db.enabled:
            raise HTTPException(status_code=503, detail="Database not available")
        video = await supabase_db.get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return JSONResponse(content={"message": "OK", "video_id": video_id})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise HTTPException(status_code=500, detail=str(e))