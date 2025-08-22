"""
Database models for Animathic
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    videos = relationship("Video", back_populates="user")
    generation_jobs = relationship("GenerationJob", back_populates="user")

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    video_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    generation_job_id = Column(String, ForeignKey("generation_jobs.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="videos")
    generation_job = relationship("GenerationJob", back_populates="videos")

class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=4)
    ai_response = Column(Text, nullable=True)
    manim_code = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="generation_jobs")
    videos = relationship("Video", back_populates="generation_job")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 rating
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    video = relationship("Video")
