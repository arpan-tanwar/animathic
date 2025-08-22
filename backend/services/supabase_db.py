"""
Supabase Database Service for Animathic Backend
Handles database operations using Supabase client instead of SQLAlchemy
"""

import os
import logging
from typing import Optional, List, Dict, Any
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseDBService:
    """Service for handling Supabase database operations"""
    
    def __init__(self):
        """Initialize the Supabase database service"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_service_key:
            logger.warning("Supabase credentials not set - database operations will be disabled")
            self.enabled = False
            self.client = None
        else:
            self.enabled = True
            try:
                self.client = create_client(self.supabase_url, self.supabase_service_key)
                logger.info("Supabase database service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.enabled = False
                self.client = None
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        if not self.enabled or not self.client:
            return False
        
        try:
            # Test connection and list available tables
            logger.info("Testing database connection...")
            
            # Try to access different tables to see what's available
            tables_to_test = ["videos", "generation_jobs", "generation_job", "video"]
            
            for table_name in tables_to_test:
                try:
                    result = self.client.table(table_name).select("id").limit(1).execute()
                    logger.info(f"Table '{table_name}' is accessible")
                except Exception as e:
                    logger.info(f"Table '{table_name}' is NOT accessible: {e}")
            
            # Simple query to test connection
            result = self.client.table("generation_jobs").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    async def get_generation_jobs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get generation jobs for a user"""
        if not self.enabled or not self.client:
            return []
        
        try:
            result = self.client.table("generation_jobs") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get generation jobs: {e}")
            return []
    
    async def get_generation_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific generation job"""
        if not self.enabled or not self.client:
            return None
        
        try:
            result = self.client.table("generation_jobs") \
                .select("*") \
                .eq("id", job_id) \
                .single() \
                .execute()
            
            return result.data if result.data else None
        except Exception as e:
            logger.error(f"Failed to get generation job {job_id}: {e}")
            return None
    
    async def create_generation_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Create a new generation job"""
        if not self.enabled or not self.client:
            return None
        
        try:
            result = self.client.table("generation_jobs") \
                .insert(job_data) \
                .execute()
            
            if result.data:
                return result.data[0].get("id")
            return None
        except Exception as e:
            logger.error(f"Failed to create generation job: {e}")
            return None
    
    async def update_generation_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update a generation job"""
        if not self.enabled or not self.client:
            return False
        
        try:
            result = self.client.table("generation_jobs") \
                .update(updates) \
                .eq("id", job_id) \
                .execute()
            
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to update generation job {job_id}: {e}")
            return False
    
    async def get_videos(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get videos for a user"""
        if not self.enabled or not self.client:
            return []
        
        try:
            logger.info(f"Querying videos for user: {user_id}")
            result = self.client.table("videos") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            logger.info(f"Database query result: {len(result.data) if result.data else 0} videos found")
            if result.data:
                for i, video in enumerate(result.data):
                    logger.info(f"Video {i+1}: ID={video.get('id')}, prompt={video.get('prompt')[:50]}...")
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get videos: {e}")
            return []
    
    async def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific video. Returns None if not found (avoids 406 single() coercion)."""
        if not self.enabled or not self.client:
            return None
        try:
            result = self.client.table("videos").select("*").eq("id", video_id).limit(1).execute()
            rows = result.data or []
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Failed to get video {video_id}: {e}")
            return None

    async def get_video_by_job(self, generation_job_id: str) -> Optional[Dict[str, Any]]:
        """Get a video by its generation_job_id. Returns None if not found."""
        if not self.enabled or not self.client:
            return None
        try:
            result = self.client.table("videos").select("*") \
                .eq("generation_job_id", generation_job_id).order("created_at", desc=True).limit(1).execute()
            rows = result.data or []
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Failed to get video by job {generation_job_id}: {e}")
            return None
    
    async def create_video(self, video_data: Dict[str, Any]) -> Optional[str]:
        """Create a new video record"""
        if not self.enabled or not self.client:
            return None
        
        try:
            result = self.client.table("videos") \
                .insert(video_data) \
                .execute()
            
            if result.data:
                return result.data[0].get("id")
            return None
        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            return None
    
    async def update_video(self, video_id: str, updates: Dict[str, Any]) -> bool:
        """Update a video record"""
        if not self.enabled or not self.client:
            return False
        
        try:
            result = self.client.table("videos") \
                .update(updates) \
                .eq("id", video_id) \
                .execute()
            
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to update video {video_id}: {e}")
            return False
    
    async def ensure_tables_exist(self) -> bool:
        """Ensure required tables exist (this is handled by Supabase automatically)"""
        if not self.enabled:
            return False
        
        try:
            # Test if we can access the tables
            await self.test_connection()
            return True
        except Exception as e:
            logger.error(f"Failed to ensure tables exist: {e}")
            return False

# Global instance
supabase_db = SupabaseDBService()
