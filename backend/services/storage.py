import os
from datetime import datetime
from typing import Optional, Dict, Any
from supabase import create_client, Client
from fastapi import HTTPException
import uuid
from slugify import slugify
from dotenv import load_dotenv

load_dotenv()

class StorageService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials in environment variables")
            
        self.supabase: Client = create_client(
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
        self.bucket_name = "manim-videos"

    async def ensure_bucket_exists(self):
        """Ensure the storage bucket exists, create if it doesn't."""
        try:
            # Try to get bucket info
            self.supabase.storage.get_bucket(self.bucket_name)
        except Exception as e:
            print(f"Bucket not found, creating new bucket: {self.bucket_name}")
            try:
                # Create bucket with proper options
                self.supabase.storage.create_bucket(
                    id=self.bucket_name,
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

            # Upload file
            with open(video_path, "rb") as f:
                file_data = f.read()
                self.supabase.storage.from_(self.bucket_name).upload(
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
                "status": "completed"
            }

            # Add any additional metadata if provided
            if metadata:
                video_data.update(metadata)

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
            
            # Generate signed URL
            signed_url_response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                video["file_path"],
                3600  # URL valid for 1 hour
            )
            
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
            
            # Delete from storage
            self.supabase.storage.from_(self.bucket_name).remove([video["file_path"]])
            
            # Delete metadata
            self.supabase.table("videos").delete().eq("id", video_id).execute()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete video: {str(e)}"
            ) 