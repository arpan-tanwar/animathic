import os
import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
except ImportError:
    genai = None
    GenerationConfig = None

from schemas.manim_schema import ManimScene
from schemas.feedback_schema import GenerationRecord, ModelType, GenerationQuality

logger = logging.getLogger(__name__)


class EnhancedGeminiService:
    """Enhanced Gemini service for generating structured Manim JSON with feedback collection"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_AI_API_KEY")
        self.model_name = os.getenv("GOOGLE_AI_MODEL", "gemini-2.0-flash-exp")
        self.temperature = float(os.getenv("GOOGLE_AI_TEMPERATURE", "0.1"))
        self.max_output_tokens = int(os.getenv("GOOGLE_AI_MAX_TOKENS", "4096"))
        self.top_p = float(os.getenv("GOOGLE_AI_TOP_P", "0.8"))
        self.top_k = int(os.getenv("GOOGLE_AI_TOP_K", "40"))
        
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY environment variable is required")
        
        if not genai:
            raise ImportError("google.generativeai library is not installed")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=GenerationConfig(
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                max_output_tokens=self.max_output_tokens,
            )
        )
        
        logger.info(f"✅ Enhanced Gemini service initialized with {self.model_name}")
    
    async def generate_structured_scene(self, prompt: str, user_id: str) -> Tuple[ManimScene, GenerationRecord]:
        """Generate structured Manim scene JSON using Gemini with comprehensive feedback tracking"""
        
        generation_start = time.time()
        generation_id = str(uuid.uuid4())
        
        try:
            # Build enhanced prompt for JSON generation
            enhanced_prompt = self._build_enhanced_prompt(prompt)
            
            # Generate with Gemini
            logger.info(f"🎯 Generating with Gemini {self.model_name} for prompt: {prompt[:100]}...")
            
            response = await self._generate_with_gemini(enhanced_prompt)
            
            # Extract and validate JSON
            json_str = self._extract_json_from_response(response)
            scene_obj = json.loads(json_str)
            
            # Validate with Pydantic
            manim_scene = ManimScene.model_validate(scene_obj)
            
            generation_time = time.time() - generation_start
            
            # Create generation record
            generation_record = GenerationRecord(
                id=generation_id,
                user_id=user_id,
                prompt=prompt,
                primary_model=ModelType.GEMINI_25_FLASH,
                fallback_used=False,
                generated_json=scene_obj,
                compiled_manim="",  # Will be filled by compiler
                render_success=False,  # Will be updated after render
                generation_time=generation_time,
                compilation_time=0.0,
                render_time=0.0,
                total_time=generation_time,
                suitable_for_training=True,
                training_notes="High-quality Gemini generation"
            )
            
            logger.info(f"✅ Gemini generated valid JSON in {generation_time:.2f}s")
            return manim_scene, generation_record
            
        except Exception as e:
            generation_time = time.time() - generation_start
            error_msg = str(e)
            
            logger.error(f"❌ Gemini generation failed: {error_msg}")
            
            # Create error record
            generation_record = GenerationRecord(
                id=generation_id,
                user_id=user_id,
                prompt=prompt,
                primary_model=ModelType.GEMINI_25_FLASH,
                fallback_used=False,
                generated_json={},
                compiled_manim="",
                render_success=False,
                generation_time=generation_time,
                compilation_time=0.0,
                render_time=0.0,
                total_time=generation_time,
                suitable_for_training=False,
                training_notes=f"Gemini generation failed: {error_msg}"
            )
            
            raise RuntimeError(f"Gemini generation failed: {error_msg}")
    
    def _build_enhanced_prompt(self, user_prompt: str) -> str:
        """Build an enhanced prompt that ensures structured JSON output"""
        
        enhanced_prompt = f"""
You are an expert at creating mathematical animations using Manim. Your task is to convert the user's request into a structured JSON representation that can be compiled into Manim code.

User Request: {user_prompt}

Please generate a JSON object with the following structure for a Manim scene:

{{
    "scene_name": "DescriptiveSceneName",
    "background_color": "BLACK",
    "imports": ["from manim import *"],
    "objects": [
        {{
            "name": "object_name",
            "type": "circle|square|rectangle|ellipse|triangle|text|line|dot|axes|number_line|graph",
            "props": {{
                "radius": 1.0,
                "color": "BLUE",
                "fill_opacity": 0.0,
                "side_length": 2.0,
                "width": 4.0,
                "height": 2.0,
                "text": "Hello",
                "start": "LEFT",
                "end": "RIGHT",
                "x_range": "[-3,3,1]",
                "y_range": "[-2,2,1]",
                "function": "lambda x: x**2",
                "axes": "axes"
            }}
        }}
    ],
    "animations": [
        {{
            "type": "create|transform|move|rotate|scale|fade_in|fade_out",
            "target": "object_name",
            "duration": 1.0,
            "props": {{
                "start_pos": "ORIGIN",
                "end_pos": "UP",
                "angle": 90,
                "scale_factor": 2.0
            }}
        }}
    ]
}}

Important guidelines:
1. Use descriptive names for objects and scenes
2. Choose appropriate colors (BLUE, RED, GREEN, YELLOW, WHITE, BLACK, etc.)
3. Use standard Manim positions (ORIGIN, UP, DOWN, LEFT, RIGHT, etc.)
4. Ensure all objects have valid properties for their type
5. Keep animations simple and logical
6. Return ONLY the JSON object, no additional text or explanations

Generate the JSON now:
"""
        
        return enhanced_prompt.strip()
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate response using Gemini API"""
        
        try:
            # Generate content
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise RuntimeError("Empty response from Gemini")
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Gemini API call failed: {e}")
            raise RuntimeError(f"Gemini API call failed: {str(e)}")
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from Gemini response"""
        
        try:
            # Try to find JSON in the response
            text = response_text.strip()
            
            # Look for JSON block markers
            json_start = text.find('{')
            json_end = text.rfind('}')
            
            if json_start == -1 or json_end == -1:
                raise ValueError("No JSON object found in response")
            
            # Extract the JSON part
            json_str = text[json_start:json_end + 1]
            
            # Validate JSON by parsing it
            json.loads(json_str)
            
            return json_str
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in response: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON in response: {str(e)}")
        except Exception as e:
            logger.error(f"❌ JSON extraction failed: {e}")
            raise ValueError(f"JSON extraction failed: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Test connection to Gemini API"""
        try:
            test_prompt = "Generate a simple JSON: {\"test\": true}"
            response = await self._generate_with_gemini(test_prompt)
            return "test" in response.lower()
        except Exception as e:
            logger.error(f"❌ Gemini connection test failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_output_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "api_key_configured": bool(self.api_key)
        }
