import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import HTTPException
from slugify import slugify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class StorageService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        # Prefer service role key; fallback to legacy env name if present
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials in environment variables")
            
        self.supabase: Client = create_client(
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
        # Configure buckets - new videos go to animathic-media, old videos are read from manim-videos
        self.new_bucket_name = os.getenv("SUPABASE_BUCKET_NAME", "animathic-media")
        self.legacy_bucket_name = "manim-videos"  # Old bucket for backward compatibility

    async def ensure_bucket_exists(self):
        """Ensure both storage buckets exist, create if they don't."""
        for bucket_name in [self.new_bucket_name, self.legacy_bucket_name]:
            try:
                # Try to get bucket info
                self.supabase.storage.get_bucket(bucket_name)
            except Exception as e:
                print(f"Bucket not found, creating new bucket: {bucket_name}")
                try:
                    # Create bucket with proper options
                    self.supabase.storage.create_bucket(
                        id=bucket_name,
                        options={"public": False}
                    )
                except Exception as create_error:
                    print(f"Error creating bucket: {str(create_error)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to create storage bucket: {str(create_error)}"
                    )

    def _generate_file_path(self, user_id: str, prompt: str) -> str:
        """Generate a unique file path for the video."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        slug = slugify(prompt)[:50]  # Limit slug length
        return f"{user_id}/{slug}_{timestamp}_{unique_id}.mp4"

    async def upload_video(
        self,
        user_id: str,
        prompt: str,
        video_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload a video file to Supabase Storage and store metadata.
        
        Args:
            user_id: The Clerk user ID
            prompt: The original prompt used to generate the video
            video_path: Path to the video file on disk
            metadata: Additional metadata to store
            
        Returns:
            Dict containing the video URL and metadata
        """
        try:
            # Ensure bucket exists
            await self.ensure_bucket_exists()

            # Generate file path
            file_path = self._generate_file_path(user_id, prompt)

            # Upload file to new bucket
            with open(video_path, "rb") as f:
                file_data = f.read()
                file_size = len(file_data)
                self.supabase.storage.from_(self.new_bucket_name).upload(
                    path=file_path,
                    file=file_data,
                    file_options={"content-type": "video/mp4"}
                )

            # Store metadata in PostgreSQL
            video_data = {
                "user_id": user_id,
                "file_path": file_path,
                "prompt": prompt,
                "created_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "mime_type": "video/mp4"
            }

            # Add any additional metadata if provided, mapping to correct column names
            if metadata:
                # Map common metadata fields to database columns
                if "duration" in metadata:
                    video_data["duration"] = metadata["duration"]
                if "resolution" in metadata and metadata["resolution"]:
                    # Parse resolution like "1280x720" into separate width/height
                    try:
                        width, height = metadata["resolution"].split("x")
                        video_data["resolution_width"] = int(width)
                        video_data["resolution_height"] = int(height)
                    except (ValueError, AttributeError):
                        pass  # Skip if resolution format is invalid
                
                # Add file size if available
                if "file_size" in metadata:
                    video_data["file_size"] = metadata["file_size"]
            
            # Always add file size from upload
            video_data["file_size"] = file_size
                
                # Note: Custom fields like generation_time, code_used are not stored in DB
                # They can be returned in the response metadata but not persisted

            try:
                result = self.supabase.table("videos").insert(video_data).execute()
                
                if not result.data:
                    raise HTTPException(status_code=500, detail="Failed to store video metadata")

                # Get the video ID from the result
                video_id = result.data[0].get('id')
                if not video_id:
                    raise HTTPException(status_code=500, detail="Failed to get video ID from database")

                # Generate signed URL for immediate access
                signed_url_response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                    file_path,
                    3600  # URL valid for 1 hour
                )
                
                # Extract the signed URL from the response
                signed_url = signed_url_response.get('signedURL', '')
                if not signed_url:
                    raise HTTPException(status_code=500, detail="Failed to generate signed URL")

                # Update video_data with the ID
                video_data['id'] = video_id

                return {
                    "video_url": signed_url,
                    "metadata": video_data
                }
            except Exception as db_error:
                print(f"Database error: {str(db_error)}")
                # If database insert fails, try to delete the uploaded file
                try:
                    self.supabase.storage.from_(self.bucket_name).remove([file_path])
                except Exception as cleanup_error:
                    print(f"Failed to cleanup uploaded file: {str(cleanup_error)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to store video metadata: {str(db_error)}"
                )

        except Exception as e:
            print(f"Error uploading video: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload video: {str(e)}"
            )

    async def get_video(self, user_id: str, video_id: str) -> Dict[str, Any]:
        """
        Retrieve video metadata and generate a signed URL.
        
        Args:
            user_id: The Clerk user ID
            video_id: The ID of the video to retrieve
            
        Returns:
            Dict containing the video URL and metadata
        """
        try:
            # Get video metadata
            result = self.supabase.table("videos").select("*").eq("id", video_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Video not found")
            
            video = result.data[0]
            
            # Verify ownership
            if video["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to access this video")
            
            # Try to generate signed URL from new bucket first, then legacy bucket
            signed_url = None
            try:
                signed_url_response = self.supabase.storage.from_(self.new_bucket_name).create_signed_url(
                    video["file_path"],
                    3600  # URL valid for 1 hour
                )
                signed_url = signed_url_response.get('signedURL', '')
            except Exception:
                # If new bucket fails, try legacy bucket
                try:
                    signed_url_response = self.supabase.storage.from_(self.legacy_bucket_name).create_signed_url(
                        video["file_path"],
                        3600  # URL valid for 1 hour
                    )
                    signed_url = signed_url_response.get('signedURL', '')
                except Exception as legacy_error:
                    print(f"Failed to generate signed URL from both buckets: {legacy_error}")
                    raise HTTPException(status_code=500, detail="Failed to generate signed URL from storage")
            
            # Extract the signed URL from the response
            signed_url = signed_url_response.get('signedURL', '')
            if not signed_url:
                raise HTTPException(status_code=500, detail="Failed to generate signed URL")
            
            return {
                "video_url": signed_url,
                "metadata": video
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve video: {str(e)}"
            )

    async def list_user_videos(self, user_id: str) -> list:
        """
        List all videos for a user.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            List of video metadata
        """
        try:
            result = self.supabase.table("videos").select("*").eq("user_id", user_id).execute()
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list videos: {str(e)}"
            )

    async def delete_video(self, user_id: str, video_id: str) -> bool:
        """
        Delete a video and its metadata.
        
        Args:
            user_id: The Clerk user ID
            video_id: The ID of the video to delete
            
        Returns:
            True if successful
        """
        try:
            # Get video metadata first
            result = self.supabase.table("videos").select("*").eq("id", video_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Video not found")
            
            video = result.data[0]
            
            # Verify ownership
            if video["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to delete this video")
            
            # Try to delete from both buckets (in case file exists in either)
            try:
                self.supabase.storage.from_(self.new_bucket_name).remove([video["file_path"]])
            except Exception:
                pass  # Ignore if file doesn't exist in new bucket
                
            try:
                self.supabase.storage.from_(self.legacy_bucket_name).remove([video["file_path"]])
            except Exception:
                pass  # Ignore if file doesn't exist in legacy bucket
            
            # Delete metadata
            self.supabase.table("videos").delete().eq("id", video_id).execute()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete video: {str(e)}"
            )

    async def migrate_legacy_videos(self, user_id: str) -> Dict[str, Any]:
        """
        Migrate videos from legacy bucket to new bucket for a user.
        This is optional and can be called to consolidate storage.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            Dict containing migration results
        """
        try:
            # Get all videos for the user
            videos = await self.list_user_videos(user_id)
            migrated_count = 0
            failed_count = 0
            
            for video in videos:
                try:
                    # Try to get file from legacy bucket
                    legacy_file = self.supabase.storage.from_(self.legacy_bucket_name).download(video["file_path"])
                    
                    # Upload to new bucket
                    self.supabase.storage.from_(self.new_bucket_name).upload(
                        path=video["file_path"],
                        file=legacy_file,
                        file_options={"content-type": "video/mp4"}
                    )
                    
                    migrated_count += 1
                    print(f"Migrated video {video['id']} to new bucket")
                    
                except Exception as e:
                    print(f"Failed to migrate video {video['id']}: {str(e)}")
                    failed_count += 1
            
            return {
                "migrated_count": migrated_count,
                "failed_count": failed_count,
                "total_count": len(videos)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to migrate legacy videos: {str(e)}"
            ) 