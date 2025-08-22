"""
Supabase Storage Service for Animathic Backend
Handles video uploads and storage management
"""

import os
import logging
import httpx
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
    
    async def upload_video(self, file_path: str, job_id: str, user_id: str) -> Optional[str]:
        """Upload a video file to Supabase storage"""
        if not self.enabled:
            logger.warning("Supabase storage disabled - cannot upload video")
            return None
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"Video file not found: {file_path}")
                return None
            
            # Generate unique filename
            filename = f"{job_id}_{file_path_obj.name}"
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to Supabase storage
            headers = {
                "Authorization": f"Bearer {self.supabase_service_key}",
                "apikey": self.supabase_service_key,
                "Content-Type": "video/mp4"
            }
            
            upload_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
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
                    # Get public URL
                    public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
                    logger.info(f"Video uploaded successfully: {public_url}")
                    return public_url
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
                response = await client.get(list_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    videos = []
                    
                    for item in data.get('data', []):
                        if item.get('name', '').startswith(f"{user_id}_"):
                            videos.append({
                                'name': item['name'],
                                'size': item.get('metadata', {}).get('size', 0),
                                'created_at': item.get('created_at'),
                                'url': await self.get_video_url(item['name'])
                            })
                    
                    logger.info(f"Found {len(videos)} videos for user {user_id}")
                    return videos
                else:
                    logger.error(f"Failed to list videos: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error listing videos: {e}")
            return []

# Global instance
supabase_storage = SupabaseStorageService()
