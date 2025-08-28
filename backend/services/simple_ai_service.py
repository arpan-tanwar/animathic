"""
Simple, Reliable AI Service for Animathic
A streamlined service that creates consistent animations without complex workflows
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from services.simple_animation_generator import SimpleAnimationGenerator, AnimationConfig
from services.simple_workflow_orchestrator import SimpleWorkflowOrchestrator

logger = logging.getLogger(__name__)


class SimpleAIService:
    """
    A simple, reliable AI service that creates consistent animations.
    This service focuses on understanding basic animation requests and
    generating clean, predictable results.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the simple AI service"""
        self.api_key = api_key
        self.generator = SimpleAnimationGenerator()
        self.orchestrator = SimpleWorkflowOrchestrator()

        # Simple configuration that works reliably
        self.config = AnimationConfig(
            default_duration=1.0,
            default_color="WHITE",
            camera_width=14.0,
            camera_height=10.0,
            background_color="#000000"
        )

        logger.info("Simple AI service initialized")

    async def process_animation_request(self, prompt: str) -> Dict[str, Any]:
        """
        Process animation request with simple, reliable workflow.
        This method focuses on creating working animations rather than complex analysis.
        """
        try:
            logger.info(f"Processing simple animation request: {prompt[:100]}...")

            # Step 1: Generate basic animation spec
            basic_result = self.generator.generate_animation(prompt)
            animation_spec = basic_result.get('animation_spec', {})

            # Step 2: Apply simple workflow orchestration
            workflow_result = self.orchestrator.process_simple_animation_request(
                animation_spec, prompt
            )

            enhanced_spec = workflow_result.get('enhanced_animation_spec', animation_spec)

            # Step 3: Generate final code with enhanced spec
            final_result = self.generator.generate_animation_from_spec(enhanced_spec)

            logger.info("Simple animation request processed successfully")

            return final_result

        except Exception as e:
            logger.error(f"Simple animation processing failed: {e}")
            # Return the generator's fallback
            return self.generator._generate_minimal_fallback(prompt)

    async def generate_animation_spec(self, prompt: str) -> Dict[str, Any]:
        """
        Generate animation specification using simple approach.
        This is a direct interface to the simple generator.
        """
        try:
            result = self.generator.generate_animation(prompt)
            return result
        except Exception as e:
            logger.error(f"Animation spec generation failed: {e}")
            return self.generator._generate_minimal_fallback(prompt)

    def get_supported_animations(self) -> Dict[str, str]:
        """Get list of supported animation types"""
        return {
            'fade_in': 'Object appears with fade effect',
            'fade_out': 'Object disappears with fade effect',
            'move': 'Object moves to a new position',
            'rotate': 'Object rotates around its center',
            'scale': 'Object changes size',
        }

    def get_supported_objects(self) -> Dict[str, str]:
        """Get list of supported object types"""
        return {
            'circle': 'Circular shape',
            'square': 'Square/rectangle shape',
            'triangle': 'Triangular shape',
            'text': 'Text label',
            'axes': 'Coordinate axes',
            'plot': 'Mathematical function plot',
        }

    def validate_prompt(self, prompt: str) -> Dict[str, bool]:
        """Simple prompt validation"""
        prompt_lower = prompt.lower()

        return {
            'has_animation_keywords': any(word in prompt_lower for word in [
                'fade', 'appear', 'move', 'rotate', 'scale', 'animate', 'show', 'display'
            ]),
            'has_object_keywords': any(word in prompt_lower for word in [
                'circle', 'square', 'triangle', 'text', 'plot', 'graph', 'axes', 'shape'
            ]),
            'is_likely_animation_request': len(prompt.strip()) > 5
        }
