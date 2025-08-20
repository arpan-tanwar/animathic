"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Request schemas
class GenerateRequest(BaseModel):
    prompt: str
    user_id: str

class FeedbackRequest(BaseModel):
    rating: int
    feedback_text: Optional[str] = None

# Response schemas
class GenerateResponse(BaseModel):
    id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    id: str
    status: str
    current_step: int
    total_steps: int
    video_url: Optional[str] = None
    error: Optional[str] = None

class VideoResponse(BaseModel):
    id: str
    prompt: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    mime_type: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str
