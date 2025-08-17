"""
Enhanced storage service with comprehensive database integration
"""
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import HTTPException
from slugify import slugify
from supabase import create_client, Client
from dotenv import load_dotenv

from models.database import get_db_manager, Video, User, GenerationLog

load_dotenv()

class EnhancedStorageService:
    """Enhanced storage service with database integration and analytics"""
    
    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials in environment variables")
            
        self.supabase: Client = create_client(
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
        self.bucket_name = "manim-videos"
        
        # Initialize database manager
        self.db_manager = get_db_manager()
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the storage bucket exists, create if it doesn't."""
        try:
            self.supabase.storage.get_bucket(self.bucket_name)
            print(f"✅ Storage bucket '{self.bucket_name}' found")
        except Exception:
            print(f"📦 Creating storage bucket: {self.bucket_name}")
            try:
                self.supabase.storage.create_bucket(
                    id=self.bucket_name,
                    options={"public": False}
                )
                print(f"✅ Storage bucket '{self.bucket_name}' created successfully")
            except Exception as create_error:
                print(f"❌ Error creating bucket: {str(create_error)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create storage bucket: {str(create_error)}"
                )
    
    def _generate_file_path(self, user_id: str, prompt: str, video_id: Optional[str] = None) -> str:
        """Generate a unique file path for the video."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = video_id or str(uuid.uuid4())[:8]
        slug = slugify(prompt)[:30]  # Shorter slug for better paths
        return f"users/{user_id}/videos/{slug}_{timestamp}_{unique_id}.mp4"
    
    def _get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract metadata from video file using ffprobe."""
        try:
            import subprocess
            
            # Get file size
            file_size = os.path.getsize(video_path)
            
            # Get video duration and resolution using ffprobe
            duration_cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", video_path
            ]
            
            resolution_cmd = [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0",
                video_path
            ]
            
            try:
                duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
                duration = float(duration_result.stdout.strip())
            except Exception:
                duration = None
            
            try:
                resolution_result = subprocess.run(resolution_cmd, capture_output=True, text=True, check=True)
                width, height = map(int, resolution_result.stdout.strip().split("x"))
            except Exception:
                width, height = 1280, 720  # Default resolution
            
            return {
                "file_size": file_size,
                "duration": duration,
                "resolution_width": width,
                "resolution_height": height
            }
            
        except Exception as e:
            print(f"⚠️ Warning: Could not extract video metadata: {str(e)}")
            return {
                "file_size": os.path.getsize(video_path) if os.path.exists(video_path) else 0,
                "duration": None,
                "resolution_width": 1280,
                "resolution_height": 720
            }
    
    async def create_user_if_not_exists(self, user_id: str, email: str = None, name: str = None) -> User:
        """Create or update user record in database."""
        with self.db_manager.get_session() as session:
            return self.db_manager.create_or_update_user(session, user_id, email, name)
    
    async def start_video_generation(
        self,
        user_id: str,
        prompt: str,
        title: Optional[str] = None,
        email: str = None,
        name: str = None
    ) -> Dict[str, Any]:
        """Start video generation process and create database records."""
        try:
            # Ensure user exists
            await self.create_user_if_not_exists(user_id, email, name)
            
            # Create video record with processing status
            with self.db_manager.get_session() as session:
                video = self.db_manager.create_video(
                    session=session,
                    user_id=user_id,
                    prompt=prompt,
                    title=title or f"Animation: {prompt[:50]}...",
                    file_path="",  # Will be updated when upload completes
                    status="processing"
                )
                
                # Create initial generation log
                log = self.db_manager.create_generation_log(
                    session=session,
                    user_id=user_id,
                    video_id=video.id,
                    prompt=prompt,
                    status="started",
                    attempt_number=1,
                    metadata={"started_at": datetime.utcnow().isoformat()}
                )
                
                return {
                    "video_id": str(video.id),
                    "log_id": str(log.id),
                    "status": "processing"
                }
                
        except Exception as e:
            print(f"❌ Error starting video generation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start video generation: {str(e)}"
            )
    
    async def update_generation_progress(
        self,
        video_id: str,
        log_id: str,
        status: str,
        error_message: Optional[str] = None,
        generated_code: Optional[str] = None,
        execution_time: Optional[float] = None,
        attempt_number: Optional[int] = None
    ):
        """Update generation progress in the database."""
        try:
            with self.db_manager.get_session() as session:
                # Update generation log
                update_data = {"status": status}
                if error_message:
                    update_data["error_message"] = error_message
                if generated_code:
                    update_data["generated_code"] = generated_code
                if execution_time:
                    update_data["execution_time"] = execution_time
                if attempt_number:
                    update_data["attempt_number"] = attempt_number
                
                self.db_manager.update_generation_log(session, log_id, **update_data)
                
                # Update video status if final
                if status in ["completed", "failed"]:
                    self.db_manager.update_video(session, video_id, status=status)
                    
        except Exception as e:
            print(f"⚠️ Warning: Could not update generation progress: {str(e)}")
    
    async def complete_video_upload(
        self,
        video_id: str,
        user_id: str,
        prompt: str,
        video_path: str,
        generation_time: Optional[float] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete video upload process with file storage and database updates."""
        try:
            # Extract video metadata
            video_metadata = self._get_video_metadata(video_path)
            
            # Generate file path
            file_path = self._generate_file_path(user_id, prompt, video_id)
            
            # Upload file to Supabase Storage
            print(f"📤 Uploading video to: {file_path}")
            with open(video_path, "rb") as f:
                file_data = f.read()
                self.supabase.storage.from_(self.bucket_name).upload(
                    path=file_path,
                    file=file_data,
                    file_options={"content-type": "video/mp4"}
                )
            
            # Update video record in database
            with self.db_manager.get_session() as session:
                video_update_data = {
                    "file_path": file_path,
                    "status": "completed",
                    "generation_time": generation_time,
                    **video_metadata
                }
                
                if title:
                    video_update_data["title"] = title
                
                video = self.db_manager.update_video(session, video_id, **video_update_data)
                
                if not video:
                    raise HTTPException(status_code=404, detail="Video not found")
                
                # Generate signed URL for immediate access
                signed_url_response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                    file_path,
                    3600  # URL valid for 1 hour
                )
                
                signed_url = signed_url_response.get('signedURL', '')
                if not signed_url:
                    raise HTTPException(status_code=500, detail="Failed to generate signed URL")
                
                return {
                    "video_id": str(video.id),
                    "video_url": signed_url,
                    "metadata": {
                        "id": str(video.id),
                        "user_id": video.user_id,
                        "title": video.title,
                        "prompt": video.prompt,
                        "file_path": video.file_path,
                        "file_size": video.file_size,
                        "duration": video.duration,
                        "resolution_width": video.resolution_width,
                        "resolution_height": video.resolution_height,
                        "status": video.status,
                        "generation_time": video.generation_time,
                        "created_at": video.created_at.isoformat() if video.created_at else None,
                        "tags": video.tags or []
                    }
                }
                
        except Exception as e:
            print(f"❌ Error completing video upload: {str(e)}")
            # Mark video as failed in database
            try:
                with self.db_manager.get_session() as session:
                    self.db_manager.update_video(session, video_id, status="failed")
            except Exception:
                pass
            
            raise HTTPException(
                status_code=500,
                detail=f"Failed to complete video upload: {str(e)}"
            )
    
    async def get_video(self, user_id: str, video_id: str) -> Dict[str, Any]:
        """Retrieve video metadata and generate a signed URL."""
        try:
            with self.db_manager.get_session() as session:
                video = self.db_manager.get_video_by_id(session, video_id)
                
                if not video:
                    raise HTTPException(status_code=404, detail="Video not found")
                
                # Verify ownership
                if video.user_id != user_id:
                    raise HTTPException(status_code=403, detail="Not authorized to access this video")
                
                # Generate signed URL if video is completed
                video_url = None
                if video.status == "completed" and video.file_path:
                    signed_url_response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                        video.file_path,
                        3600  # URL valid for 1 hour
                    )
                    video_url = signed_url_response.get('signedURL', '')
                
                return {
                    "video_id": str(video.id),
                    "video_url": video_url,
                    "metadata": {
                        "id": str(video.id),
                        "user_id": video.user_id,
                        "title": video.title,
                        "prompt": video.prompt,
                        "file_size": video.file_size,
                        "duration": video.duration,
                        "resolution_width": video.resolution_width,
                        "resolution_height": video.resolution_height,
                        "status": video.status,
                        "generation_time": video.generation_time,
                        "created_at": video.created_at.isoformat() if video.created_at else None,
                        "updated_at": video.updated_at.isoformat() if video.updated_at else None,
                        "tags": video.tags or []
                    }
                }
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve video: {str(e)}"
            )
    
    async def list_user_videos(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List all videos for a user with optional filtering."""
        try:
            with self.db_manager.get_session() as session:
                videos = self.db_manager.get_user_videos(session, user_id, status, limit)
                
                result = []
                for video in videos:
                    video_data = {
                        "id": str(video.id),
                        "user_id": video.user_id,
                        "title": video.title,
                        "prompt": video.prompt,
                        "file_size": video.file_size,
                        "duration": video.duration,
                        "resolution_width": video.resolution_width,
                        "resolution_height": video.resolution_height,
                        "status": video.status,
                        "generation_time": video.generation_time,
                        "created_at": video.created_at.isoformat() if video.created_at else None,
                        "updated_at": video.updated_at.isoformat() if video.updated_at else None,
                        "tags": video.tags or []
                    }
                    
                    # Generate signed URL for completed videos
                    if video.status == "completed" and video.file_path:
                        try:
                            signed_url_response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                                video.file_path,
                                3600  # URL valid for 1 hour
                            )
                            video_data["video_url"] = signed_url_response.get('signedURL', '')
                        except Exception:
                            video_data["video_url"] = None
                    else:
                        video_data["video_url"] = None
                    
                    result.append(video_data)
                
                return result
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list videos: {str(e)}"
            )
    
    async def delete_video(self, user_id: str, video_id: str) -> bool:
        """Delete a video and its metadata."""
        try:
            with self.db_manager.get_session() as session:
                video = self.db_manager.get_video_by_id(session, video_id)
                
                if not video:
                    raise HTTPException(status_code=404, detail="Video not found")
                
                # Verify ownership
                if video.user_id != user_id:
                    raise HTTPException(status_code=403, detail="Not authorized to delete this video")
                
                # Delete from storage if file exists
                if video.file_path:
                    try:
                        self.supabase.storage.from_(self.bucket_name).remove([video.file_path])
                        print(f"🗑️ Deleted file from storage: {video.file_path}")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not delete file from storage: {str(e)}")
                
                # Delete from database (cascade will handle logs)
                success = self.db_manager.delete_video(session, video_id)
                
                if success:
                    print(f"🗑️ Deleted video from database: {video_id}")
                
                return success
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete video: {str(e)}"
            )
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a user."""
        try:
            with self.db_manager.get_session() as session:
                return self.db_manager.get_user_analytics(session, user_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get user analytics: {str(e)}"
            )
    
    async def update_video_tags(self, user_id: str, video_id: str, tags: List[str]) -> bool:
        """Update tags for a video."""
        try:
            with self.db_manager.get_session() as session:
                video = self.db_manager.get_video_by_id(session, video_id)
                
                if not video:
                    raise HTTPException(status_code=404, detail="Video not found")
                
                if video.user_id != user_id:
                    raise HTTPException(status_code=403, detail="Not authorized to update this video")
                
                self.db_manager.update_video(session, video_id, tags=tags)
                return True
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update video tags: {str(e)}"
            )
