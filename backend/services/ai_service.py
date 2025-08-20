"""
AI Service for Animathic - Gemini 2.5 Flash Integration
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, api_key: str):
        """Initialize AI service with Gemini"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Animation generation prompt template
        self.animation_prompt_template = """
You are an expert animation creator using Manim (Mathematical Animation Engine). 
Create a detailed animation specification based on the user's prompt.

User Prompt: {prompt}

Generate a JSON response with the following structure:
{
    "animation_type": "string (e.g., 'geometric', 'mathematical', 'text', 'object')",
    "scene_description": "string (detailed description of what the animation shows)",
    "objects": [
        {
            "type": "string (e.g., 'circle', 'square', 'text', 'line')",
            "properties": {
                "position": [x, y, z],
                "color": "string",
                "size": "number",
                "other_properties": "as needed"
            },
            "animations": [
                {
                    "type": "string (e.g., 'move', 'scale', 'rotate', 'fade')",
                    "duration": "number (seconds)",
                    "easing": "string (e.g., 'linear', 'ease_in', 'ease_out')",
                    "parameters": {}
                }
            ]
        }
    ],
    "camera_settings": {
        "position": [x, y, z],
        "zoom": "number"
    },
    "duration": "number (total animation duration in seconds)",
    "background_color": "string",
    "style": "string (e.g., 'modern', 'classic', 'minimal')"
}

Make the animation engaging and visually appealing. Ensure all coordinates and properties are realistic for a mathematical animation.
"""

    async def generate_animation_spec(self, prompt: str) -> Dict[str, Any]:
        """
        Generate animation specification using Gemini
        """
        try:
            logger.info(f"Generating animation spec for prompt: {prompt}")
            
            # Format the prompt
            formatted_prompt = self.animation_prompt_template.format(prompt=prompt)
            
            # Generate response from Gemini
            response = self.model.generate_content(formatted_prompt)
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            # Parse JSON response
            try:
                animation_spec = json.loads(response.text)
                logger.info("Successfully generated animation specification")
                return animation_spec
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    raise ValueError("Invalid JSON response from AI model")
                    
        except Exception as e:
            logger.error(f"Error generating animation spec: {e}")
            raise

    def generate_manim_code(self, animation_spec: Dict[str, Any]) -> str:
        """
        Convert animation specification to Manim Python code
        """
        try:
            logger.info("Converting animation spec to Manim code")
            
            # Basic Manim scene template
            manim_code = f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Animation: {animation_spec.get('scene_description', 'Generated animation')}
        
        # Set background color
        self.camera.background_color = "{animation_spec.get('background_color', '#000000')}"
        
        # Camera settings
        self.camera.frame.set_width({animation_spec.get('camera_settings', {}).get('zoom', 8)})
        
        # Create objects and animations
'''
            
            # Generate objects and animations
            for obj in animation_spec.get('objects', []):
                obj_type = obj.get('type', 'circle')
                props = obj.get('properties', {})
                animations = obj.get('animations', [])
                
                # Create object
                if obj_type == 'circle':
                    manim_code += f'''
        # Create {obj_type}
        {obj_type}_obj = Circle(
            radius={props.get('size', 1)},
            color="{props.get('color', 'WHITE')}",
            fill_opacity=0.8
        )
        {obj_type}_obj.move_to([{', '.join(map(str, props.get('position', [0, 0, 0])))}])
        self.play(Create({obj_type}_obj))
'''
                elif obj_type == 'square':
                    manim_code += f'''
        # Create {obj_type}
        {obj_type}_obj = Square(
            side_length={props.get('size', 2)},
            color="{props.get('color', 'BLUE')}",
            fill_opacity=0.8
        )
        {obj_type}_obj.move_to([{', '.join(map(str, props.get('position', [0, 0, 0])))}])
        self.play(Create({obj_type}_obj))
'''
                elif obj_type == 'text':
                    manim_code += f'''
        # Create {obj_type}
        {obj_type}_obj = Text(
            "{props.get('text', 'Hello')}",
            color="{props.get('color', 'WHITE')}",
            font_size={props.get('size', 36)}
        )
        {obj_type}_obj.move_to([{', '.join(map(str, props.get('position', [0, 0, 0])))}])
        self.play(Write({obj_type}_obj))
'''
                
                # Add animations
                for i, anim in enumerate(animations):
                    anim_type = anim.get('type', 'move')
                    duration = anim.get('duration', 1)
                    
                    if anim_type == 'move':
                        target_pos = anim.get('parameters', {}).get('target_position', [1, 1, 0])
                        manim_code += f'''
        # Animate {obj_type} {anim_type}
        self.play(
            {obj_type}_obj.animate.move_to([{', '.join(map(str, target_pos))}]),
            run_time={duration}
        )
'''
                    elif anim_type == 'scale':
                        scale_factor = anim.get('parameters', {}).get('scale_factor', 1.5)
                        manim_code += f'''
        # Animate {obj_type} {anim_type}
        self.play(
            {obj_type}_obj.animate.scale({scale_factor}),
            run_time={duration}
        )
'''
                    elif anim_type == 'rotate':
                        angle = anim.get('parameters', {}).get('angle', PI/2)
                        manim_code += f'''
        # Animate {obj_type} {anim_type}
        self.play(
            Rotate({obj_type}_obj, angle={angle}),
            run_time={duration}
        )
'''
            
            # Add final wait
            manim_code += '''
        # Final pause
        self.wait(2)
'''
            
            logger.info("Successfully generated Manim code")
            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            raise

    async def process_animation_request(self, prompt: str) -> Dict[str, Any]:
        """
        Complete animation processing workflow
        """
        try:
            # Step 1: Generate animation specification
            animation_spec = await self.generate_animation_spec(prompt)
            
            # Step 2: Convert to Manim code
            manim_code = self.generate_manim_code(animation_spec)
            
            return {
                "animation_spec": animation_spec,
                "manim_code": manim_code,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in animation processing workflow: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


_ai_service_singleton: Optional[AIService] = None

def get_ai_service() -> AIService:
    global _ai_service_singleton
    if _ai_service_singleton is None:
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_AI_API_KEY is not set")
        _ai_service_singleton = AIService(api_key=api_key)
    return _ai_service_singleton
