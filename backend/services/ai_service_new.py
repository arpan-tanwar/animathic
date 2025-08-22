"""
AI Service for Animathic - Modular Architecture
Main service class that orchestrates all modular components
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import numpy as np
import google.generativeai as genai
try:
    # Newer SDK (google-genai) optional types; fall back if unavailable
    from google.genai import types as genai_types  # type: ignore
except Exception:  # pragma: no cover
    genai_types = None  # type: ignore
from dotenv import load_dotenv
import httpx

# Import modular components
from .prompts import ANIMATION_PROMPT_TEMPLATE, GEMINI_SYSTEM_INSTRUCTION, DEFAULT_ANIMATION_SPEC
from .manim_code_generator import ManimCodeGenerator
from .object_tracking import ObjectTrackingSystem
from .animation_analysis import AnimationSequenceAnalyzer
from .camera_management import CameraManagementSystem
from .fade_out_system import FadeOutSystem
from .enhanced_workflow_orchestrator import EnhancedWorkflowOrchestrator

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    """Enhanced AI service with intelligent workflow orchestration"""
    
    def __init__(self, api_key: str = None):
        """Initialize the AI service with enhanced capabilities"""
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY')
        self.gemini_client = None
        self.local_model_client = None
        self.enhanced_orchestrator = EnhancedWorkflowOrchestrator()
        self.code_generator = ManimCodeGenerator()
        self.object_tracker = ObjectTrackingSystem()
        self.camera_manager = CameraManagementSystem()
        self.fade_out_manager = FadeOutSystem()
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_gemini_model(self):
        """Initialize Gemini model with appropriate configuration"""
        try:
            if genai_types is not None:
                try:
                    return genai.GenerativeModel(
                        'gemini-2.5-flash',
                        system_instruction=GEMINI_SYSTEM_INSTRUCTION,
                        config=genai_types.GenerateContentConfig(
                            thinking_config=genai_types.ThinkingConfig(thinking_budget=0)
                        ),
                    )
                except Exception:
                    pass
            
            # Fallback to basic configuration
            return genai.GenerativeModel(
                'gemini-2.5-flash',
                system_instruction=GEMINI_SYSTEM_INSTRUCTION,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    async def generate_animation_spec(self, prompt: str) -> Dict[str, Any]:
        """Generate animation specification using Gemini"""
        try:
            logger.info(f"Generating animation spec for prompt: {prompt}")
            
            # Format the prompt
            formatted_prompt = ANIMATION_PROMPT_TEMPLATE.replace("{prompt}", prompt)
            
            # Generate response from Gemini
            response = self.gemini_client.generate_content(
                formatted_prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.2,
                    "top_p": 0.8,
                },
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            # Parse JSON response robustly
            spec = self._parse_ai_response(response.text)
            
            # Normalize the specification
            normalized = self._normalize_animation_spec(spec, prompt)
            
            logger.info("Successfully generated and normalized animation specification")
            return normalized
                    
        except Exception as e:
            logger.error(f"Error generating animation spec: {e}")
            # Try local fallback generator if configured
            fallback = await self._try_local_fallback(prompt)
            if fallback is not None:
                return fallback
            raise
    
    def _parse_ai_response(self, raw_text: str) -> Dict[str, Any]:
        """Parse AI response with fallback strategies"""
        try:
            # Try direct JSON parsing first
            return json.loads(raw_text.strip())
        except Exception:
            import re
            # Try fenced code blocks
            m = re.search(r"```(?:json)?\s*\n(\{[\s\S]*?\})\s*```", raw_text)
            if m:
                return json.loads(m.group(1))
            
            # Try to find JSON object
            m2 = re.search(r"\{[\s\S]*\}", raw_text)
            if not m2:
                raise ValueError("Invalid JSON response from AI model")
            return json.loads(m2.group())
    
    def _normalize_animation_spec(self, spec: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Normalize animation specification with minimal intervention - only fix critical issues"""
        if not isinstance(spec, dict):
            # Sometimes the model returns a top-level list; wrap it
            spec = {"objects": spec}
        
        # Provide minimal safe defaults - don't add anything the user didn't request
        normalized: Dict[str, Any] = {
            "animation_type": spec.get("animation_type", "geometric"),
            "scene_description": spec.get("scene_description", f"Animation for: {prompt}"),
            "objects": spec.get("objects") or [],
            "camera_settings": spec.get("camera_settings") or {"position": [0, 0, 0], "zoom": 8},
            "duration": spec.get("duration", 5),
            "background_color": spec.get("background_color", "#1a1a1a"),
            "style": spec.get("style", "modern"),
        }
        
        # Ensure objects is a list - minimal validation only
        if not isinstance(normalized["objects"], list):
            try:
                normalized["objects"] = list(normalized["objects"])
            except Exception:
                normalized["objects"] = []
        
        # Only validate critical properties, don't add anything
        if normalized["objects"]:
            validated_objects = []
            for obj in normalized["objects"]:
                if isinstance(obj, dict) and obj.get("type"):
                    # Only ensure critical properties exist, don't add defaults
                    if "properties" not in obj:
                        obj["properties"] = {}
                    if "animations" not in obj:
                        obj["animations"] = []
                    
                    # Only set position if it's completely missing (critical for rendering)
                    if "position" not in obj["properties"]:
                        obj["properties"]["position"] = [0, 0, 0]
                    
                    validated_objects.append(obj)
            
            normalized["objects"] = validated_objects
        
        return normalized
    
    def generate_manim_code(self, animation_spec: Dict[str, Any]) -> str:
        """Convert animation specification to Manim Python code using modular generator"""
        try:
            logger.info("Converting animation spec to Manim code")
            
            # Enhance animation spec with intelligent analysis
            enhanced_spec = self._enhance_animation_spec_with_analysis(animation_spec)
            
            # Generate Manim code using the modular generator
            manim_code = self.code_generator.generate_manim_code(enhanced_spec)
            
            logger.info("Successfully generated Manim code")
            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            raise
    
    def _enhance_animation_spec_with_analysis(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Minimal enhancement - only add what's absolutely necessary for rendering"""
        try:
            # Don't enhance unless absolutely necessary
            enhanced_spec = animation_spec.copy()
            
            # Only add minimal analysis for debugging purposes
            if animation_spec.get('objects'):
                enhanced_spec['debug_info'] = {
                    'object_count': len(animation_spec['objects']),
                    'object_types': [obj.get('type', 'unknown') for obj in animation_spec['objects']]
                }
            
            # Don't add positioning suggestions, camera strategies, or transitions
            # Let the user's original specification stand as-is
            
            return enhanced_spec
            
        except Exception as e:
            logger.error(f"Error in minimal enhancement: {e}")
            return animation_spec
    
    async def process_animation_request(self, prompt: str) -> Dict[str, Any]:
        """Process animation request with intelligent workflow selection"""
        try:
            logger.info(f"Processing animation request: {prompt[:100]}...")
            
            # Phase 1: Generate initial animation specification
            initial_spec = await self._generate_animation_specification(prompt)
            if not initial_spec:
                return {'error': 'Failed to generate animation specification'}
            
            # Phase 2: Analyze prompt complexity and choose workflow
            prompt_complexity = self._analyze_prompt_complexity(prompt)
            
            if prompt_complexity['requires_enhancement']:
                logger.info("Using enhanced workflow for complex prompt")
                # Use enhanced workflow for complex prompts
                enhanced_result = self.enhanced_orchestrator.process_complex_animation_request(
                    initial_spec, prompt
                )
                
                if 'error' in enhanced_result:
                    logger.warning(f"Enhanced workflow failed, falling back to basic: {enhanced_result['error']}")
                    # Fall back to basic workflow
                    final_spec = self._apply_basic_workflow(initial_spec, prompt)
                else:
                    final_spec = enhanced_result['enhanced_animation_spec']
                    logger.info(f"Enhanced workflow applied {len(enhanced_result.get('enhancements_applied', []))} enhancements")
            else:
                logger.info("Using restrictive workflow for simple prompt")
                # Use restrictive workflow for simple prompts
                final_spec = self._apply_basic_workflow(initial_spec, prompt)
            
            # Phase 3: Generate Manim code
            manim_code = self._generate_manim_code(final_spec)
            if not manim_code:
                return {'error': 'Failed to generate Manim code'}
            
            return {
                'animation_spec': final_spec,
                'manim_code': manim_code,
                'workflow_type': 'enhanced' if prompt_complexity['requires_enhancement'] else 'restrictive',
                'complexity_analysis': prompt_complexity,
                'enhancements_applied': enhanced_result.get('enhancements_applied', []) if prompt_complexity['requires_enhancement'] else []
            }
            
        except Exception as e:
            logger.error(f"Error in animation request processing: {e}")
            return {'error': str(e)}
    
    def _analyze_prompt_complexity(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt complexity to determine workflow selection"""
        complexity_indicators = {
            'mathematical_content': any(keyword in prompt.lower() for keyword in 
                ['function', 'plot', 'graph', 'equation', 'formula', 'sine', 'cosine', 'polynomial']),
            'multiple_objects': any(keyword in prompt.lower() for keyword in 
                ['multiple', 'several', 'many', 'various', 'both', 'and', 'with']),
            'sequence_requirements': any(keyword in prompt.lower() for keyword in 
                ['sequence', 'step', 'progression', 'evolution', 'then', 'next', 'after']),
            'interaction_requirements': any(keyword in prompt.lower() for keyword in 
                ['interact', 'connect', 'relate', 'combine', 'between', 'among']),
            'temporal_aspects': any(keyword in prompt.lower() for keyword in 
                ['time', 'duration', 'speed', 'timing', 'slow', 'fast']),
            'spatial_relationships': any(keyword in prompt.lower() for keyword in 
                ['above', 'below', 'left', 'right', 'near', 'far', 'position'])
        }
        
        complexity_score = sum(complexity_indicators.values())
        complexity_level = 'simple' if complexity_score <= 1 else 'moderate' if complexity_score <= 3 else 'complex'
        
        return {
            'level': complexity_level,
            'score': complexity_score,
            'indicators': complexity_indicators,
            'requires_enhancement': complexity_score >= 2,
            'workflow_recommendation': 'enhanced' if complexity_score >= 2 else 'restrictive'
        }
    
    def _apply_basic_workflow(self, animation_spec: Dict[str, Any], prompt: str = "") -> Dict[str, Any]:
        """Apply basic restrictive workflow (minimal intervention)"""
        try:
            # Apply minimal normalization
            normalized_spec = self._normalize_animation_spec(animation_spec, prompt)
            
            # Apply minimal enhancement (no automatic additions)
            enhanced_spec = self._enhance_animation_spec_with_analysis(normalized_spec)
            
            return enhanced_spec
            
        except Exception as e:
            logger.error(f"Error in basic workflow: {e}")
            return animation_spec
    
    async def _try_local_fallback(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Attempt to generate a spec using a local inference service if available."""
        local_url = os.getenv("LOCAL_INFERENCE_URL")
        if not local_url:
            return None
        
        try:
            timeout = httpx.Timeout(20.0, connect=5.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(local_url, json={"prompt": prompt})
                if resp.status_code != 200:
                    logger.error(f"Local fallback returned {resp.status_code}")
                    return None
                
                data = resp.json()
                spec = data.get("animation_spec") or data
                if not isinstance(spec, dict):
                    return None
                
                # Normalize like primary path
                return self._normalize_animation_spec(spec, prompt)
                
        except Exception as ex:
            logger.error(f"Local fallback error: {ex}")
            return None
    
    # Utility methods for external access to modular components
    def get_object_tracking_status(self) -> Dict[str, Any]:
        """Get current status of the object tracking system"""
        return self.object_tracker.get_tracking_status()
    
    def get_camera_management_status(self) -> Dict[str, Any]:
        """Get current status of the camera management system"""
        return self.camera_manager.get_camera_management_status(self.object_tracker.object_registry)
    
    def get_fade_out_system_status(self) -> Dict[str, Any]:
        """Get current status of the fade-out system"""
        return self.fade_out_manager.get_fade_out_system_status(self.object_tracker.object_registry)
    
    def debug_object_state(self, obj_id: str) -> Dict[str, Any]:
        """Debug information for a specific object"""
        return self.object_tracker.debug_object_state(obj_id)
    
    def clear_tracking_data(self) -> Dict[str, Any]:
        """Clear all tracking data (useful for testing)"""
        return self.object_tracker.clear_tracking_data()

    def activate(self):
        """Activate the AI service - compatibility function"""
        try:
            # Initialize or re-initialize all subsystems
            self.object_tracker.init_object_registry()
            
            return {
                'status': 'activated',
                'subsystems': {
                    'object_tracker': 'ready',
                    'animation_analyzer': 'ready', 
                    'camera_manager': 'ready',
                    'fade_out_manager': 'ready',
                    'code_generator': 'ready'
                },
                'model_status': 'ready' if self.gemini_client else 'error'
            }
        except Exception as e:
            logger.error(f"Error in activate: {e}")
            return {'status': 'error', 'message': str(e)}

    def _initialize_clients(self):
        """Initialize AI model clients"""
        try:
            # Initialize Gemini client
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.gemini_client = self._initialize_gemini_model()
                logger.info("Gemini client initialized successfully")
            else:
                logger.warning("No Google API key found, Gemini client not initialized")
                raise RuntimeError("GOOGLE_AI_API_KEY is required for AI service")
            
            # Initialize local model client (placeholder for future implementation)
            self.local_model_client = None
            logger.info("AI service clients initialized")
            
        except Exception as e:
            logger.error(f"Error initializing AI clients: {e}")
            raise RuntimeError(f"Failed to initialize AI service: {e}")
    
    async def _generate_animation_specification(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate animation specification using available AI models"""
        try:
            # Try Gemini first
            if self.gemini_client:
                try:
                    return await self._generate_with_gemini(prompt)
                except Exception as e:
                    logger.warning(f"Gemini generation failed: {e}")
            
            # Try local model fallback
            if self.local_model_client:
                try:
                    return await self._generate_with_local_model(prompt)
                except Exception as e:
                    logger.warning(f"Local model generation failed: {e}")
            
            # Final fallback - basic specification
            logger.warning("Using basic fallback specification")
            return self._generate_basic_specification(prompt)
            
        except Exception as e:
            logger.error(f"Error generating animation specification: {e}")
            return None
    
    async def _generate_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Generate animation specification using Gemini"""
        try:
            # Use the existing Gemini generation logic
            return await self.generate_animation_spec(prompt)
        except Exception as e:
            logger.error(f"Error in Gemini generation: {e}")
            raise
    
    async def _generate_with_local_model(self, prompt: str) -> Dict[str, Any]:
        """Generate animation specification using local model"""
        # Placeholder for local model implementation
        raise NotImplementedError("Local model generation not yet implemented")
    
    def _generate_basic_specification(self, prompt: str) -> Dict[str, Any]:
        """Generate basic animation specification as fallback"""
        return {
            'objects': [{
                'id': 'obj_1',
                'type': 'text',
                'properties': {
                    'text': prompt[:50] + '...' if len(prompt) > 50 else prompt,
                    'color': 'WHITE',
                    'size': 36,
                    'position': [0, 0, 0]
                },
                'animations': []
            }],
            'duration': 3.0,
            'background_color': 'BLACK'
        }
    
    def _generate_manim_code(self, animation_spec: Dict[str, Any]) -> Optional[str]:
        """Generate Manim code from animation specification"""
        try:
            # Use the existing code generator
            code_generator = ManimCodeGenerator()
            return code_generator.generate_manim_code(animation_spec)
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            return None


# Singleton instance management
_ai_service_singleton: Optional[AIService] = None

def get_ai_service() -> AIService:
    """Get or create the AI service singleton instance"""
    global _ai_service_singleton
    if _ai_service_singleton is None:
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_AI_API_KEY is not set")
        _ai_service_singleton = AIService(api_key=api_key)
    return _ai_service_singleton
