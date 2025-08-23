"""
Services package for Animathic
Contains all modular service components
"""

from .ai_service_new import AIService, get_ai_service
from .object_tracking import ObjectTrackingSystem
from .animation_analysis import AnimationSequenceAnalyzer
from .camera_management import CameraManagementSystem
from .fade_out_system import FadeOutSystem
from .enhanced_validation import EnhancedValidationService
from .ai_prompt_enhancement import AIPromptEnhancementSystem
from .real_time_overlap_monitoring import RealTimeOverlapMonitor
from .manim_code_generator import ManimCodeGenerator
from .manim_utilities import *
from .prompts import *

__all__ = [
    'AIService',
    'get_ai_service',
    'ObjectTrackingSystem',
    'AnimationSequenceAnalyzer',
    'CameraManagementSystem',
    'FadeOutSystem',
    'EnhancedValidationService',
    'AIPromptEnhancementSystem',
    'RealTimeOverlapMonitor',
    'ManimCodeGenerator',
]
