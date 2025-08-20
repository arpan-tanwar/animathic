import os
import time
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import uuid

from schemas.manim_schema import ManimScene
from schemas.feedback_schema import (
    GenerationRecord, ModelType, UserFeedback, GenerationQuality
)
from services.enhanced_gemini import EnhancedGeminiService
from services.local_llm import LocalLLMService
from services.feedback_collector import FeedbackCollector
from services.manim_compiler import ManimCompiler

logger = logging.getLogger(__name__)


class HybridOrchestrator:
    """Intelligently orchestrates between Gemini (primary) and local model (fallback)"""
    
    def __init__(self):
        self.feedback_collector = FeedbackCollector()
        self.manim_compiler = ManimCompiler()
        
        # Initialize services
        try:
            self.gemini_service = EnhancedGeminiService()
            self.gemini_available = True
            logger.info("✅ Gemini service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Gemini service unavailable: {e}")
            self.gemini_available = False
            self.gemini_service = None
        
        try:
            self.local_service = LocalLLMService()
            self.local_available = True
            logger.info("✅ Local LLM service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Local LLM service unavailable: {e}")
            self.local_available = False
            self.local_service = None
        
        # Configuration
        self.gemini_confidence_threshold = float(os.getenv("GEMINI_CONFIDENCE_THRESHOLD", "0.7"))
        self.local_fallback_enabled = os.getenv("LOCAL_FALLBACK_ENABLED", "true").lower() == "true"
        self.quality_assessment_enabled = os.getenv("QUALITY_ASSESSMENT_ENABLED", "true").lower() == "true"
        
        # Performance tracking
        self.model_performance = {
            ModelType.GEMINI_25_FLASH: {"success_count": 0, "total_count": 0, "avg_time": 0},
            ModelType.LOCAL_TRAINED: {"success_count": 0, "total_count": 0, "avg_time": 0}
        }
        
        logger.info(f"🎯 Hybrid orchestrator initialized - Gemini: {self.gemini_available}, Local: {self.local_available}")
    
    async def generate_animation(self, prompt: str, user_id: str) -> Tuple[ManimScene, GenerationRecord]:
        """
        Complete workflow: Generate animation using intelligent model routing with fallback
        
        Steps:
        1. User provides prompt
        2. Gemini generates structured JSON (local model as fallback)
        3. JSON converts to Manim code
        4. Code is compiled and provided to user
        5. User feedback collected for fine-tuning and training
        """
        
        generation_start = time.time()
        generation_id = str(uuid.uuid4())
        
        # Determine primary model based on prompt complexity and performance
        primary_model = self._select_primary_model(prompt)
        logger.info(f"🎯 Selected {primary_model.value} as primary model for prompt: {prompt[:100]}...")
        
        try:
            # Step 1: Attempt generation with primary model
            if primary_model == ModelType.GEMINI_25_FLASH and self.gemini_available:
                manim_scene, generation_record = await self._generate_with_gemini(prompt, user_id, generation_id)
            elif primary_model == ModelType.LOCAL_TRAINED and self.local_available:
                manim_scene, generation_record = await self._generate_with_local(prompt, user_id, generation_id)
            else:
                raise RuntimeError(f"Selected primary model {primary_model.value} is not available")
            
            # Step 2: Validate the generated scene
            if not self._validate_scene(manim_scene):
                raise ValueError("Generated scene failed validation")
            
            # Step 3: Compile to Manim code
            compilation_start = time.time()
            try:
                compiled_manim = self.manim_compiler.compile_to_manim(manim_scene)
                compilation_time = time.time() - compilation_start
                
                # Update generation record
                await self.feedback_collector.update_generation(generation_id, {
                    "compiled_manim": compiled_manim,
                    "compilation_time": compilation_time
                })
                
                logger.info(f"✅ Compiled to Manim code in {compilation_time:.2f}s")
                
            except Exception as e:
                compilation_time = time.time() - compilation_start
                logger.error(f"❌ Compilation failed: {e}")
                
                # Update generation record with error
                await self.feedback_collector.update_generation(generation_id, {
                    "compilation_time": compilation_time,
                    "error_message": f"Compilation failed: {str(e)}"
                })
                
                # Try fallback if compilation fails
                if self.local_fallback_enabled and self.local_available and primary_model == ModelType.GEMINI_25_FLASH:
                    logger.info("🔄 Attempting fallback to local model due to compilation failure")
                    manim_scene, generation_record = await self._generate_with_local(prompt, user_id, generation_id)
                    
                    # Try compilation again
                    compilation_start = time.time()
                    try:
                        compiled_manim = self.manim_compiler.compile_to_manim(manim_scene)
                        compilation_time = time.time() - compilation_start
                        
                        await self.feedback_collector.update_generation(generation_id, {
                            "compiled_manim": compiled_manim,
                            "compilation_time": compilation_time,
                            "fallback_used": True,
                            "fallback_reason": "Compilation failure with primary model"
                        })
                        
                        logger.info(f"✅ Fallback compilation successful in {compilation_time:.2f}s")
                        
                    except Exception as fallback_e:
                        compilation_time = time.time() - compilation_start
                        logger.error(f"❌ Fallback compilation also failed: {fallback_e}")
                        
                        await self.feedback_collector.update_generation(generation_id, {
                            "compilation_time": compilation_time,
                            "error_message": f"Both primary and fallback compilation failed: {str(fallback_e)}"
                        })
                        
                        raise RuntimeError(f"All compilation attempts failed: {str(e)}, fallback: {str(fallback_e)}")
                else:
                    raise RuntimeError(f"Compilation failed and no fallback available: {str(e)}")
            
            # Step 4: Assess quality and prepare for training
            if self.quality_assessment_enabled:
                quality_score = await self._assess_generation_quality(manim_scene, prompt)
                generation_record.suitable_for_training = quality_score >= 0.7
                generation_record.training_notes = f"Quality score: {quality_score:.2f}"
                
                await self.feedback_collector.update_generation(generation_id, {
                    "suitable_for_training": generation_record.suitable_for_training,
                    "training_notes": generation_record.training_notes
                })
            
            # Step 5: Update final metrics
            total_time = time.time() - generation_start
            generation_record.total_time = total_time
            
            await self.feedback_collector.update_generation(generation_id, {
                "total_time": total_time
            })
            
            # Update performance tracking
            self._update_model_performance(primary_model, total_time, True)
            
            logger.info(f"✅ Complete animation generation workflow completed in {total_time:.2f}s")
            return manim_scene, generation_record
            
        except Exception as e:
            total_time = time.time() - generation_start
            error_msg = str(e)
            
            # Create error record
            generation_record = GenerationRecord(
                id=generation_id,
                user_id=user_id,
                prompt=prompt,
                primary_model=primary_model,
                fallback_used=False,
                generated_json={},
                compiled_manim="",
                render_success=False,
                generation_time=total_time,
                compilation_time=0.0,
                render_time=0.0,
                total_time=total_time,
                suitable_for_training=False,
                training_notes=f"Generation failed: {error_msg}"
            )
            
            # Update performance tracking
            self._update_model_performance(primary_model, total_time, False)
            
            # Store error record
            await self.feedback_collector.create_generation_record(generation_record)
            
            logger.error(f"❌ Animation generation workflow failed: {error_msg}")
            raise RuntimeError(f"Animation generation failed: {error_msg}")
    
    def _validate_scene(self, scene: ManimScene) -> bool:
        """Validate the generated Manim scene"""
        try:
            # Basic validation
            if not scene.scene_name:
                return False
            
            if not scene.objects:
                logger.warning("⚠️ Scene has no objects")
                return False
            
            # Check for required properties
            for obj in scene.objects:
                if not obj.name or not obj.type:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Scene validation failed: {e}")
            return False
    
    async def _assess_generation_quality(self, scene: ManimScene, prompt: str) -> float:
        """Assess the quality of the generated scene for training suitability"""
        try:
            # Simple quality heuristics
            quality_score = 0.5  # Base score
            
            # Object count bonus
            if len(scene.objects) >= 3:
                quality_score += 0.2
            
            # Animation steps bonus
            if len(scene.animations) >= 2:
                quality_score += 0.2
            
            # Scene complexity bonus
            if len(scene.imports) > 2:
                quality_score += 0.1
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.warning(f"⚠️ Quality assessment failed: {e}")
            return 0.5  # Default to neutral
    
    def _select_primary_model(self, prompt: str) -> ModelType:
        """Select the primary model based on prompt complexity and performance"""
        
        # Check if Gemini is available
        if not self.gemini_available:
            if self.local_available:
                return ModelType.LOCAL_TRAINED
            else:
                raise RuntimeError("No models available")
        
        # Check if local model is available
        if not self.local_available:
            return ModelType.GEMINI_25_FLASH
        
        # Simple heuristics for model selection
        prompt_length = len(prompt)
        prompt_complexity = self._assess_prompt_complexity(prompt)
        
        # Use Gemini for complex prompts or when local model performance is poor
        if prompt_complexity > 0.7 or prompt_length > 200:
            return ModelType.GEMINI_25_FLASH
        
        # Check local model performance
        local_perf = self.model_performance[ModelType.LOCAL_TRAINED]
        if local_perf["total_count"] > 0:
            local_success_rate = local_perf["success_count"] / local_perf["total_count"]
            if local_success_rate > 0.8:
                return ModelType.LOCAL_TRAINED
        
        # Default to Gemini for reliability
        return ModelType.GEMINI_25_FLASH
    
    def _assess_prompt_complexity(self, prompt: str) -> float:
        """Assess the complexity of a prompt"""
        complexity = 0.0
        
        # Length complexity
        if len(prompt) > 100:
            complexity += 0.3
        
        # Mathematical complexity indicators
        math_keywords = ["function", "equation", "graph", "plot", "animation", "transform", "rotate", "scale"]
        for keyword in math_keywords:
            if keyword.lower() in prompt.lower():
                complexity += 0.1
        
        # Animation complexity indicators
        animation_keywords = ["sequence", "timeline", "keyframe", "interpolation", "easing"]
        for keyword in animation_keywords:
            if keyword.lower() in prompt.lower():
                complexity += 0.15
        
        return min(complexity, 1.0)
    
    async def _generate_with_gemini(self, prompt: str, user_id: str, generation_id: str) -> Tuple[ManimScene, GenerationRecord]:
        """Generate animation using Gemini service"""
        
        generation_start = time.time()
        
        try:
            manim_scene, generation_record = await self.gemini_service.generate_structured_scene(prompt, user_id)
            
            # Update generation ID
            generation_record.id = generation_id
            
            generation_time = time.time() - generation_start
            generation_record.generation_time = generation_time
            
            logger.info(f"✅ Gemini generation completed in {generation_time:.2f}s")
            return manim_scene, generation_record
            
        except Exception as e:
            generation_time = time.time() - generation_start
            logger.error(f"❌ Gemini generation failed: {e}")
            
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
                training_notes=f"Gemini generation failed: {str(e)}"
            )
            
            raise RuntimeError(f"Gemini generation failed: {str(e)}")
    
    async def _generate_with_local(self, prompt: str, user_id: str, generation_id: str) -> Tuple[ManimScene, GenerationRecord]:
        """Generate animation using local LLM service"""
        
        generation_start = time.time()
        
        try:
            manim_scene, generation_record = await self.local_service.generate_structured_scene(prompt, user_id)
            
            # Update generation ID
            generation_record.id = generation_id
            
            generation_time = time.time() - generation_start
            generation_record.generation_time = generation_time
            
            logger.info(f"✅ Local LLM generation completed in {generation_time:.2f}s")
            return manim_scene, generation_record
            
        except Exception as e:
            generation_time = time.time() - generation_start
            logger.error(f"❌ Local LLM generation failed: {e}")
            
            # Create error record
            generation_record = GenerationRecord(
                id=generation_id,
                user_id=user_id,
                prompt=prompt,
                primary_model=ModelType.LOCAL_TRAINED,
                fallback_used=False,
                generated_json={},
                compiled_manim="",
                render_success=False,
                generation_time=generation_time,
                compilation_time=0.0,
                render_time=0.0,
                total_time=generation_time,
                suitable_for_training=False,
                training_notes=f"Local LLM generation failed: {str(e)}"
            )
            
            raise RuntimeError(f"Local LLM generation failed: {str(e)}")
    
    def _update_model_performance(self, model_type: ModelType, response_time: float, success: bool):
        """Update model performance metrics"""
        if model_type not in self.model_performance:
            return
        
        perf = self.model_performance[model_type]
        perf["total_count"] += 1
        
        if success:
            perf["success_count"] += 1
        
        # Update average response time
        if perf["total_count"] == 1:
            perf["avg_time"] = response_time
        else:
            perf["avg_time"] = (perf["avg_time"] * (perf["total_count"] - 1) + response_time) / perf["total_count"]
    
    async def test_services(self) -> Dict[str, bool]:
        """Test all available services"""
        services_status = {}
        
        # Test Gemini
        if self.gemini_available:
            try:
                # Simple test prompt
                test_prompt = "Create a simple circle"
                await self.gemini_service.generate_structured_scene(test_prompt, "test_user")
                services_status["gemini"] = True
            except Exception as e:
                logger.warning(f"⚠️ Gemini service test failed: {e}")
                services_status["gemini"] = False
        else:
            services_status["gemini"] = False
        
        # Test Local LLM
        if self.local_available:
            try:
                # Simple test prompt
                test_prompt = "Create a simple circle"
                await self.local_service.generate_structured_scene(test_prompt, "test_user")
                services_status["local_llm"] = True
            except Exception as e:
                logger.warning(f"⚠️ Local LLM service test failed: {e}")
                services_status["local_llm"] = False
        else:
            services_status["local_llm"] = False
        
        # Test Manim Compiler
        try:
            from schemas.manim_schema import ManimScene, ManimObject
            test_scene = ManimScene(
                scene_name="TestScene",
                background_color="BLACK",
                objects=[ManimObject(name="test_circle", type="circle", props={"radius": 1.0})],
                animations=[],
                imports=["from manim import *"]
            )
            self.manim_compiler.compile_to_manim(test_scene)
            services_status["manim_compiler"] = True
        except Exception as e:
            logger.warning(f"⚠️ Manim compiler test failed: {e}")
            services_status["manim_compiler"] = False
        
        # Test Feedback Collector
        try:
            await self.feedback_collector.test_connection()
            services_status["feedback_collector"] = True
        except Exception as e:
            logger.warning(f"⚠️ Feedback collector test failed: {e}")
            services_status["feedback_collector"] = False
        
        return services_status
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "model_performance": self.model_performance,
            "service_availability": {
                "gemini": self.gemini_available,
                "local_llm": self.local_available
            },
            "configuration": {
                "gemini_confidence_threshold": self.gemini_confidence_threshold,
                "local_fallback_enabled": self.local_fallback_enabled,
                "quality_assessment_enabled": self.quality_assessment_enabled
            }
        }
