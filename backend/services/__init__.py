"""
Services package for Animathic backend
Contains all the core services for animation generation and processing
"""

# Core services - only import what we need for testing
from .manim_api_docs import ManimAPIDocumentationSystem, ManimSymbol, ManimDocResult
from .enhanced_manim_generator import EnhancedManimCodeGenerator

# For now, comment out other imports to avoid dependency issues
# from .ai_service_new import AIService
# from .enhanced_ai_service import EnhancedAIService
# from .manim_code_generator import ManimCodeGenerator
# from .enhanced_workflow_orchestrator import EnhancedWorkflowOrchestrator
# from .ai_prompt_enhancement import AIPromptEnhancementSystem
# from .enhanced_validation import EnhancedValidationService
# from .animation_analysis import AnimationSequenceAnalyzer
# from .advanced_positioning import AdvancedObjectPositioningSystem
# from .camera_management import CameraManagementSystem
# from .fade_out_system import FadeOutSystem
# from .object_tracking import ObjectTrackingSystem
# from .real_time_overlap_monitoring import RealTimeOverlapMonitor
# from .manim_utilities import *
# from .supabase_db import SupabaseDatabase
# from .supabase_storage import SupabaseStorage
# from .clerk_auth import ClerkAuthentication
# from .prompts import (
#     ANIMATION_PROMPT_TEMPLATE,
#     GEMINI_SYSTEM_INSTRUCTION,
#     DEFAULT_ANIMATION_SPEC
# )

__all__ = [
    # Core services - only what we need for testing
    'ManimAPIDocumentationSystem',
    'ManimSymbol',
    'ManimDocResult',
    'EnhancedManimCodeGenerator'
]
