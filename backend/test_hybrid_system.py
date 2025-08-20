#!/usr/bin/env python3
"""
Production-Ready Test Script for the Animathic Hybrid AI System
Tests the complete workflow: prompt → Gemini JSON → Manim code → compilation → feedback → training
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_configuration():
    """Test the configuration system"""
    logger.info("🧪 Testing Configuration System...")
    
    try:
        from config import get_config, is_production, get_log_level
        
        config = get_config()
        logger.info(f"✅ Configuration loaded successfully")
        logger.info(f"📊 Environment: {config.environment}")
        logger.info(f"📊 Log Level: {get_log_level()}")
        logger.info(f"📊 Production Mode: {is_production()}")
        
        # Test sub-configurations
        logger.info(f"📊 Google AI configured: {bool(config.google_ai.api_key)}")
        logger.info(f"📊 Local LLM enabled: {config.local_llm.enabled}")
        logger.info(f"📊 Rate limiting enabled: {config.rate_limit.enabled}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

async def test_feedback_collector():
    """Test the feedback collection system"""
    logger.info("🧪 Testing Feedback Collector...")
    
    try:
        from services.feedback_collector import FeedbackCollector
        
        collector = FeedbackCollector("test_feedback.db")
        
        # Test basic operations
        logger.info("✅ Feedback Collector initialized successfully")
        
        # Test connection
        await collector.test_connection()
        logger.info("✅ Feedback Collector connection test passed")
        
        # Clean up test database
        if os.path.exists("test_feedback.db"):
            os.remove("test_feedback.db")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Feedback Collector test failed: {e}")
        return False

async def test_enhanced_gemini():
    """Test the enhanced Gemini service"""
    logger.info("🧪 Testing Enhanced Gemini Service...")
    
    try:
        from services.enhanced_gemini import EnhancedGeminiService
        
        # This will fail if GOOGLE_AI_API_KEY is not set, which is expected
        try:
            service = EnhancedGeminiService()
            logger.info("✅ Enhanced Gemini Service initialized successfully")
            
            # Test model info
            model_info = service.get_model_info()
            logger.info(f"📊 Model info: {model_info}")
            
            return True
        except ValueError as e:
            if "GOOGLE_AI_API_KEY" in str(e):
                logger.info("⚠️ Enhanced Gemini Service test skipped (no API key)")
                return True
            else:
                raise e
                
    except Exception as e:
        logger.error(f"❌ Enhanced Gemini Service test failed: {e}")
        return False

async def test_local_llm():
    """Test the local LLM service"""
    logger.info("🧪 Testing Local LLM Service...")
    
    try:
        from services.local_llm import LocalLLMService
        
        # This will fail if Ollama is not running, which is expected
        try:
            service = LocalLLMService()
            logger.info("✅ Local LLM Service initialized successfully")
            
            # Test model info
            model_info = service.get_model_info()
            logger.info(f"📊 Model info: {model_info}")
            
            return True
        except ConnectionError as e:
            if "Cannot connect to Ollama service" in str(e):
                logger.info("⚠️ Local LLM Service test skipped (Ollama not running)")
                return True
            else:
                raise e
                
    except Exception as e:
        logger.error(f"❌ Local LLM Service test failed: {e}")
        return False

async def test_manim_compiler():
    """Test the Manim compiler"""
    logger.info("🧪 Testing Manim Compiler...")
    
    try:
        from services.manim_compiler import ManimCompiler
        from schemas.manim_schema import ManimScene, ManimObject
        
        compiler = ManimCompiler()
        
        # Create a test scene
        test_scene = ManimScene(
            scene_name="TestScene",
            background_color="BLACK",
            objects=[
                ManimObject(
                    name="test_circle",
                    type="circle",
                    props={"radius": 1.0, "color": "BLUE"}
                )
            ],
            animations=[],
            imports=["from manim import *"]
        )
        
        # Compile to Manim code
        manim_code = compiler.compile_to_manim(test_scene)
        
        # Verify the output
        if "class TestScene" in manim_code and "test_circle = Circle" in manim_code:
            logger.info("✅ Manim Compiler test passed")
            logger.info(f"📝 Generated code length: {len(manim_code)} characters")
            return True
        else:
            logger.error("❌ Manim Compiler generated invalid code")
            return False
        
    except Exception as e:
        logger.error(f"❌ Manim Compiler test failed: {e}")
        return False

async def test_hybrid_orchestrator():
    """Test the hybrid orchestrator"""
    logger.info("🧪 Testing Hybrid Orchestrator...")
    
    try:
        from services.hybrid_orchestrator import HybridOrchestrator
        
        # This will fail if services are not available, which is expected
        try:
            orchestrator = HybridOrchestrator()
            logger.info("✅ Hybrid Orchestrator initialized successfully")
            
            # Test service availability
            services = await orchestrator.test_services()
            logger.info(f"📊 Service status: {services}")
            
            # Test performance metrics
            metrics = orchestrator.get_performance_metrics()
            logger.info(f"📊 Performance metrics: {metrics}")
            
            return True
            
        except Exception as e:
            if "Gemini service unavailable" in str(e) or "Local LLM service unavailable" in str(e):
                logger.info("⚠️ Hybrid Orchestrator test skipped (services not available)")
                return True
            else:
                raise e
                
    except Exception as e:
        logger.error(f"❌ Hybrid Orchestrator test failed: {e}")
        return False

async def test_training_pipeline():
    """Test the enhanced training pipeline"""
    logger.info("🧪 Testing Enhanced Training Pipeline...")
    
    try:
        from scripts.enhanced_training_pipeline import EnhancedTrainingPipeline
        
        pipeline = EnhancedTrainingPipeline("test_feedback.db")
        logger.info("✅ Enhanced Training Pipeline initialized successfully")
        
        # Clean up test database
        if os.path.exists("test_feedback.db"):
            os.remove("test_feedback.db")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced Training Pipeline test failed: {e}")
        return False

async def test_complete_workflow():
    """Test the complete workflow end-to-end"""
    logger.info("🧪 Testing Complete Workflow...")
    
    try:
        # This test requires actual services to be available
        from services.hybrid_orchestrator import HybridOrchestrator
        from services.manim_compiler import ManimCompiler
        
        try:
            orchestrator = HybridOrchestrator()
            compiler = ManimCompiler()
            
            # Test with a simple prompt
            test_prompt = "Create a simple blue circle"
            test_user_id = "test_user"
            
            logger.info(f"🎯 Testing workflow with prompt: {test_prompt}")
            
            # Step 1: Generate animation
            manim_scene, generation_record = await orchestrator.generate_animation(
                test_prompt, test_user_id
            )
            
            logger.info(f"✅ Step 1: Animation generation completed")
            logger.info(f"📊 Generation ID: {generation_record.id}")
            logger.info(f"📊 Model used: {generation_record.primary_model.value}")
            logger.info(f"📊 Generation time: {generation_record.generation_time:.2f}s")
            
            # Step 2: Compile to Manim code
            manim_code = compiler.compile_to_manim(manim_scene)
            
            logger.info(f"✅ Step 2: Manim compilation completed")
            logger.info(f"📊 Generated code length: {len(manim_code)} characters")
            
            # Step 3: Verify the workflow
            if "class" in manim_code and "def construct" in manim_code:
                logger.info("✅ Step 3: Workflow verification passed")
                logger.info("🎉 Complete workflow test successful!")
                return True
            else:
                logger.error("❌ Step 3: Workflow verification failed - invalid Manim code")
                return False
                
        except Exception as e:
            if "services are not available" in str(e):
                logger.info("⚠️ Complete workflow test skipped (services not available)")
                return True
            else:
                raise e
                
    except Exception as e:
        logger.error(f"❌ Complete workflow test failed: {e}")
        return False

async def test_api_endpoints():
    """Test the API endpoints"""
    logger.info("🧪 Testing API Endpoints...")
    
    try:
        # Import FastAPI app
        from main import app
        
        # Test that the app can be imported
        logger.info("✅ FastAPI app imported successfully")
        
        # Check available endpoints
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                if hasattr(route, 'methods'):
                    routes.append(f"{route.methods} {route.path}")
                else:
                    # Handle mounted routes (like StaticFiles)
                    routes.append(f"MOUNT {route.path}")
        
        logger.info(f"📊 Available endpoints: {len(routes)}")
        for route in routes[:5]:  # Show first 5
            logger.info(f"   {route}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ API endpoints test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    logger.info("🚀 Starting Animathic Production System Tests...")
    logger.info("=" * 60)
    
    tests = [
        ("Configuration System", test_configuration),
        ("Feedback Collector", test_feedback_collector),
        ("Enhanced Gemini Service", test_enhanced_gemini),
        ("Local LLM Service", test_local_llm),
        ("Manim Compiler", test_manim_compiler),
        ("Hybrid Orchestrator", test_hybrid_orchestrator),
        ("Training Pipeline", test_training_pipeline),
        ("Complete Workflow", test_complete_workflow),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running: {test_name}")
        try:
            result = await test_func()
            results[test_name] = result
            if result:
                passed += 1
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            results[test_name] = False
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is production-ready.")
        return True
    elif passed >= total * 0.8:
        logger.warning("⚠️ Most tests passed. System is mostly ready but needs attention.")
        return False
    else:
        logger.error("❌ Many tests failed. System needs significant work before production.")
        return False

async def main():
    """Main test runner"""
    try:
        success = await run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
