"""
Database models for Animathic video generation platform
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON, BigInteger, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.schema import CheckConstraint
import os

Base = declarative_base()

class User(Base):
    """User model for storing user information and statistics"""
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)  # Clerk user ID
    email = Column(String, nullable=True)
    name = Column(String, nullable=True)
    videos_count = Column(Integer, default=0)
    total_generation_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    # Relationships
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    generation_logs = relationship("GenerationLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', videos_count={self.videos_count})>"

class Video(Base):
    """Video model for storing video metadata and file information"""
    __tablename__ = 'videos'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    duration = Column(Float, nullable=True)  # Duration in seconds
    resolution_width = Column(Integer, default=1280)
    resolution_height = Column(Integer, default=720)
    status = Column(String, default='processing')  # processing, completed, failed, deleted
    generation_time = Column(Float, nullable=True)  # Time taken to generate in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})
    tags = Column(ARRAY(String), default=[])
    
    # Relationships
    user = relationship("User", back_populates="videos")
    generation_logs = relationship("GenerationLog", back_populates="video", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('file_size > 0', name='videos_file_size_positive'),
        CheckConstraint('duration > 0', name='videos_duration_positive'),
        CheckConstraint('generation_time > 0', name='videos_generation_time_positive'),
        CheckConstraint("status IN ('processing', 'completed', 'failed', 'deleted')", name='videos_status_check'),
        Index('idx_videos_user_id', 'user_id'),
        Index('idx_videos_created_at', 'created_at'),
        Index('idx_videos_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Video(id='{self.id}', user_id='{self.user_id}', status='{self.status}')>"

class GenerationLog(Base):
    """Generation log model for tracking video generation process and analytics"""
    __tablename__ = 'generation_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey('videos.id'), nullable=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    prompt = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # started, code_generated, rendering, completed, failed
    attempt_number = Column(Integer, default=1)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
    ai_model = Column(String, default='gemini-2.5-flash')
    generated_code = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    # Relationships
    video = relationship("Video", back_populates="generation_logs")
    user = relationship("User", back_populates="generation_logs")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('started', 'code_generated', 'rendering', 'completed', 'failed')", name='logs_status_check'),
        Index('idx_generation_logs_video_id', 'video_id'),
        Index('idx_generation_logs_user_id', 'user_id'),
        Index('idx_generation_logs_status', 'status'),
    )
    
    def __repr__(self):
        return f"<GenerationLog(id='{self.id}', video_id='{self.video_id}', status='{self.status}')>"

class DatabaseManager:
    """Database manager for handling connections and operations"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables from the database"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def get_user_by_id(self, session, user_id: str) -> Optional[User]:
        """Get a user by their ID"""
        return session.query(User).filter(User.id == user_id).first()
    
    def create_or_update_user(self, session, user_id: str, email: str = None, name: str = None) -> User:
        """Create a new user or update existing user"""
        user = self.get_user_by_id(session, user_id)
        if user:
            if email:
                user.email = email
            if name:
                user.name = name
            user.last_activity = datetime.utcnow()
        else:
            user = User(id=user_id, email=email, name=name)
            session.add(user)
        
        session.commit()
        session.refresh(user)
        return user
    
    def create_video(self, session, user_id: str, prompt: str, file_path: str, **kwargs) -> Video:
        """Create a new video record"""
        video = Video(
            user_id=user_id,
            prompt=prompt,
            file_path=file_path,
            **kwargs
        )
        session.add(video)
        session.commit()
        session.refresh(video)
        return video
    
    def update_video(self, session, video_id: str, **kwargs) -> Optional[Video]:
        """Update a video record"""
        video = session.query(Video).filter(Video.id == video_id).first()
        if video:
            for key, value in kwargs.items():
                if hasattr(video, key):
                    setattr(video, key, value)
            session.commit()
            session.refresh(video)
        return video
    
    def get_user_videos(self, session, user_id: str, status: Optional[str] = None, limit: int = 50) -> List[Video]:
        """Get videos for a user with optional status filter"""
        query = session.query(Video).filter(Video.user_id == user_id)
        if status:
            query = query.filter(Video.status == status)
        return query.order_by(Video.created_at.desc()).limit(limit).all()
    
    def get_video_by_id(self, session, video_id: str) -> Optional[Video]:
        """Get a video by its ID"""
        return session.query(Video).filter(Video.id == video_id).first()
    
    def delete_video(self, session, video_id: str) -> bool:
        """Delete a video and its associated logs"""
        video = session.query(Video).filter(Video.id == video_id).first()
        if video:
            session.delete(video)
            session.commit()
            return True
        return False
    
    def create_generation_log(self, session, user_id: str, prompt: str, status: str, **kwargs) -> GenerationLog:
        """Create a new generation log entry"""
        log = GenerationLog(
            user_id=user_id,
            prompt=prompt,
            status=status,
            **kwargs
        )
        session.add(log)
        session.commit()
        session.refresh(log)
        return log
    
    def update_generation_log(self, session, log_id: str, **kwargs) -> Optional[GenerationLog]:
        """Update a generation log entry"""
        log = session.query(GenerationLog).filter(GenerationLog.id == log_id).first()
        if log:
            for key, value in kwargs.items():
                if hasattr(log, key):
                    setattr(log, key, value)
            session.commit()
            session.refresh(log)
        return log
    
    def get_user_analytics(self, session, user_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a user"""
        user = self.get_user_by_id(session, user_id)
        if not user:
            return {}
        
        videos = session.query(Video).filter(Video.user_id == user_id).all()
        
        return {
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'member_since': user.created_at,
            'last_activity': user.last_activity,
            'total_videos': len(videos),
            'completed_videos': len([v for v in videos if v.status == 'completed']),
            'failed_videos': len([v for v in videos if v.status == 'failed']),
            'total_generation_time': sum(v.generation_time or 0 for v in videos),
            'avg_generation_time': sum(v.generation_time or 0 for v in videos) / len(videos) if videos else 0,
            'total_storage_used': sum(v.file_size or 0 for v in videos),
            'avg_video_duration': sum(v.duration or 0 for v in videos) / len(videos) if videos else 0,
        }

# Global database manager instance
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def init_database():
    """Initialize the database and create tables"""
    manager = get_db_manager()
    manager.create_tables()
    return manager
