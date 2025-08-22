"""
Supabase Storage Service for Animathic Backend
Handles video uploads and storage management
"""

import os
import logging
import httpx
from datetime import datetime, timezone
from slugify import slugify
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    """Service for handling Supabase storage operations"""
    
    def __init__(self):
        """Initialize the Supabase storage service"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.bucket_name = os.getenv("SUPABASE_NEW_BUCKET", "animathic-media")
        
        if not self.supabase_url or not self.supabase_service_key:
            logger.warning("Supabase credentials not set - storage operations will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"Supabase storage service initialized with bucket: {self.bucket_name}")
    
    async def upload_video(self, file_path: str, job_id: str, user_id: str, prompt: str = "") -> Optional[str]:
        """Upload a video file to Supabase storage using a descriptive filename.
        Returns {"url": public_url, "object_key": object_key}
        """
        if not self.enabled:
            logger.warning("Supabase storage disabled - cannot upload video")
            return None
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"Video file not found: {file_path}")
                return None
            
            # Generate descriptive object key under user-specific folder
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            short_id = job_id.split("-")[0]
            safe_prompt = (slugify(prompt)[:80] or "animation")
            filename = f"{safe_prompt}_{ts}_{short_id}.mp4"
            object_key = f"{user_id}/{filename}"
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to Supabase storage
            headers = {
                "Authorization": f"Bearer {self.supabase_service_key}",
                "apikey": self.supabase_service_key,
                "Content-Type": "video/mp4"
            }
            
            upload_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{object_key}"
            logger.info(f"Attempting upload to: {upload_url}")
            logger.info(f"File size: {len(file_content)} bytes")
            logger.info(f"Headers: {headers}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    upload_url,
                    headers=headers,
                    data=file_content
                )
                
                if response.status_code in (200, 201):
                    # Get public URL (if bucket is public, else backend streams)
                    public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{object_key}"
                    logger.info(f"Video uploaded successfully: {public_url}")
                    # Return both URL and object key for DB persistence
                    return {"url": public_url, "object_key": object_key}
                else:
                    logger.error(f"Failed to upload video: {response.status_code} - {response.text}")
                    logger.error(f"Response headers: {dict(response.headers)}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error uploading video: {e}", exc_info=True)
            return None
    
    async def delete_video(self, filename: str) -> bool:
        """Delete a video file from Supabase storage"""
        if not self.enabled:
            logger.warning("Supabase storage disabled - cannot delete video")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.supabase_service_key}"
            }
            
            # filename can be a full object key like "<user_id>/<name>.mp4"
            delete_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(delete_url, headers=headers)
                
                if response.status_code == 200:
                    logger.info(f"Video deleted successfully: {filename}")
                    return True
                else:
                    logger.error(f"Failed to delete video: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False
    
    async def get_video_url(self, filename: str) -> Optional[str]:
        """Get the public URL for a video file"""
        if not self.enabled:
            return None
        
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
    
    async def list_user_videos(self, user_id: str) -> list:
        """List all videos for a specific user"""
        if not self.enabled:
            logger.warning("Supabase storage disabled - cannot list videos")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.supabase_service_key}"
            }
            
            list_url = f"{self.supabase_url}/storage/v1/object/list/{self.bucket_name}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Filter objects by prefix (user folder)
                response = await client.post(list_url, headers=headers, json={"prefix": f"{user_id}/"})
                
                if response.status_code == 200:
                    data = response.json()
                    videos = []
                    
                    for item in data.get('data', []):
                        # item['name'] is already relative to the prefix when provided
                        object_key = f"{user_id}/{item['name']}"
                        videos.append({
                            'name': object_key,
                            'size': item.get('metadata', {}).get('size', 0),
                            'created_at': item.get('created_at'),
                            'url': await self.get_video_url(object_key)
                        })
                    
                    logger.info(f"Found {len(videos)} videos for user {user_id}")
                    return videos
                else:
                    logger.error(f"Failed to list videos: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error listing videos: {e}")
            return []

    async def list_user_videos_in_bucket(self, bucket: str, user_id: str) -> list:
        """List all videos for a specific user in a given bucket"""
        if not self.enabled:
            return []
        try:
            headers = {"Authorization": f"Bearer {self.supabase_service_key}"}
            list_url = f"{self.supabase_url}/storage/v1/object/list/{bucket}"
            prefix = f"{user_id}/"
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(list_url, headers=headers, json={"prefix": prefix})
                if response.status_code != 200:
                    return []
                data = response.json()
                items = []
                for item in data.get('data', []):
                    object_key = f"{user_id}/{item['name']}"
                    items.append({
                        'bucket': bucket,
                        'object_key': object_key,
                        'size': item.get('metadata', {}).get('size', 0),
                        'created_at': item.get('created_at'),
                    })
                return items
        except Exception:
            return []

# Global instance
supabase_storage = SupabaseStorageService()
