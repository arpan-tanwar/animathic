from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ModelType(str, Enum):
    GEMINI_25_FLASH = "gemini-2.5-flash"
    LOCAL_TRAINED = "local-trained"
    HYBRID = "hybrid"


class GenerationQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAILED = "failed"


class UserFeedback(BaseModel):
    """User feedback on generated animations"""
    rating: int = Field(..., ge=1, le=5, description="1-5 star rating")
    quality: GenerationQuality = Field(..., description="Quality assessment")
    comments: Optional[str] = Field(None, description="User comments")
    animation_worked: bool = Field(..., description="Did the animation render successfully?")
    matched_intent: bool = Field(..., description="Did it match the user's intent?")


class GenerationRecord(BaseModel):
    """Complete record of a generation attempt"""
    id: str = Field(..., description="Unique generation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(..., description="User who requested the generation")
    prompt: str = Field(..., description="User's original prompt")
    
    # Model information
    primary_model: ModelType = Field(..., description="Which model was used")
    fallback_used: bool = Field(False, description="Was fallback model used?")
    fallback_model: Optional[ModelType] = Field(None, description="Fallback model if used")
    
    # Generation details
    generated_json: Dict[str, Any] = Field(..., description="Generated JSON schema")
    compiled_manim: str = Field(..., description="Compiled Manim code")
    render_success: bool = Field(..., description="Did Manim render succeed?")
    
    # Performance metrics
    generation_time: float = Field(..., description="Time to generate JSON (seconds)")
    compilation_time: float = Field(..., description="Time to compile to Manim (seconds)")
    render_time: float = Field(..., description="Time to render video (seconds)")
    total_time: float = Field(..., description="Total end-to-end time")
    
    # Output details
    video_path: Optional[str] = Field(None, description="Path to generated video")
    error_message: Optional[str] = Field(None, description="Error if generation failed")
    
    # Feedback
    user_feedback: Optional[UserFeedback] = Field(None, description="User feedback if provided")
    
    # Training data
    suitable_for_training: bool = Field(True, description="Is this generation suitable for training?")
    training_notes: Optional[str] = Field(None, description="Notes for training pipeline")


class TrainingDataset(BaseModel):
    """Dataset for training local models"""
    id: str = Field(..., description="Dataset ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(..., description="Source of training data")
    version: str = Field("1.0.0", description="Dataset version")
    
    # Training examples
    examples: List[Dict[str, Any]] = Field(..., description="Training examples")
    total_examples: int = Field(..., description="Total number of examples")
    
    # Quality metrics
    avg_rating: float = Field(..., description="Average user rating")
    success_rate: float = Field(..., description="Percentage of successful generations")
    
    # Metadata
    description: Optional[str] = Field(None, description="Dataset description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class ModelPerformance(BaseModel):
    """Performance metrics for each model"""
    model_type: ModelType = Field(..., description="Model identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Success metrics
    total_generations: int = Field(0, description="Total generation attempts")
    successful_generations: int = Field(0, description="Successful generations")
    success_rate: float = Field(0.0, description="Success rate percentage")
    
    # Quality metrics
    avg_user_rating: float = Field(0.0, description="Average user rating")
    avg_generation_time: float = Field(0.0, description="Average generation time")
    avg_total_time: float = Field(0.0, description="Average total time")
    
    # Error analysis
    common_errors: List[str] = Field(default_factory=list, description="Most common error types")
    error_counts: Dict[str, int] = Field(default_factory=dict, description="Error type counts")


class FeedbackAnalytics(BaseModel):
    """Analytics for improving model performance"""
    period_start: datetime = Field(..., description="Analysis period start")
    period_end: datetime = Field(..., description="Analysis period end")
    
    # Overall metrics
    total_generations: int = Field(0, description="Total generations in period")
    overall_success_rate: float = Field(0.0, description="Overall success rate")
    avg_user_satisfaction: float = Field(0.0, description="Average user satisfaction")
    
    # Model comparison
    model_performance: List[ModelPerformance] = Field(..., description="Performance by model")
    
    # Improvement opportunities
    top_improvement_areas: List[str] = Field(default_factory=list, description="Areas needing improvement")
    training_priorities: List[str] = Field(default_factory=list, description="Training priorities")
    
    # User behavior
    popular_prompts: List[str] = Field(default_factory=list, description="Most common prompt types")
    prompt_complexity_distribution: Dict[str, int] = Field(default_factory=dict, description="Prompt complexity breakdown")
