#!/usr/bin/env python3
"""
Debug script to test video generation and identify failure points
"""

import asyncio
import logging
import os
import tempfile
import subprocess
import json
from pathlib import Path
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_ai_service():
    """Test the AI service to generate animation spec"""
    try:
        logger.info("Testing AI service...")
        from services.ai_service_new import AIService

        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            logger.error("GOOGLE_AI_API_KEY not found")
            return None

        ai_service = AIService(api_key=api_key)
        result = await ai_service.process_animation_request("Create a simple circle animation")

        if 'error' in result:
            logger.error(f"AI service failed: {result['error']}")
            return None

        logger.info("AI service test passed")
        return result

    except Exception as e:
        logger.error(f"AI service test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def test_manim_code_generation(ai_result):
    """Test Manim code generation from AI result"""
    try:
        logger.info("Testing Manim code generation...")

        if not ai_result or 'manim_code' not in ai_result:
            logger.error("No Manim code in AI result")
            return None

        manim_code = ai_result['manim_code']
        logger.info(f"Generated Manim code length: {len(manim_code)}")

        # Validate the code
        if not manim_code or not isinstance(manim_code, str):
            logger.error("Invalid Manim code")
            return None

        # Check for required components
        required_components = [
            'from manim import',
            'class GeneratedScene',
            'def construct(self)'
        ]

        for component in required_components:
            if component not in manim_code:
                logger.error(f"Missing required component: {component}")
                return None

        logger.info("Manim code generation test passed")
        return manim_code

    except Exception as e:
        logger.error(f"Manim code generation test failed: {e}")
        return None

def test_video_generation(manim_code: str) -> Optional[str]:
    """Test video generation from Manim code"""
    try:
        logger.info("Testing video generation...")

        # Validate input code
        if not manim_code or not isinstance(manim_code, str):
            logger.error("Invalid Manim code provided")
            return None

        # Check for dangerous patterns
        dangerous_patterns = ['eval(', '__import__(', 'exec(', 'open(', 'file(']
        for pattern in dangerous_patterns:
            if pattern in manim_code:
                logger.error(f"Dangerous pattern found: {pattern}")
                return None

        # Create temporary directory for Manim execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            logger.info(f"Created temp directory: {temp_path}")

            # Create Manim scene file
            scene_file = temp_path / "animation_scene.py"
            scene_file.write_text(manim_code, encoding='utf-8')
            logger.info(f"Created scene file: {scene_file}")

            # Set up environment for headless Manim rendering
            env = os.environ.copy()
            env.update({
                'DISPLAY': ':99',
                'MPLBACKEND': 'Agg',
                'PYTHONPATH': '/usr/local/lib/python3.10/site-packages',
                'MANIM_CONFIG_FILE': '',
            })

            # Create media directory explicitly
            media_dir = temp_path / "media"
            media_dir.mkdir(parents=True, exist_ok=True)

            # Test if Manim is working
            logger.info("Testing Manim installation...")
            test_cmd = ["python3", "-c", "import manim; print('Manim import successful')"]
            test_result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )

            if test_result.returncode != 0:
                logger.error("Manim import test failed")
                logger.error(f"Test stderr: {test_result.stderr}")
                logger.error(f"Test stdout: {test_result.stdout}")
                return None
            else:
                logger.info("Manim import test passed")

            # Run Manim command
            cmd = [
                "manim", "render",
                str(scene_file), "GeneratedScene",
                "-ql",
                "--fps", "15",
                "--format", "mp4",
                "--disable_caching",
                "--media_dir", str(media_dir),
                "--renderer", "cairo",
            ]

            logger.info(f"Running Manim command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=temp_path,
                env=env,
                timeout=120
            )

            logger.info(f"Manim process completed with return code: {result.returncode}")

            # Log output
            if result.stdout:
                logger.info(f"Manim stdout: {result.stdout[:500]}...")
            if result.stderr:
                logger.info(f"Manim stderr: {result.stderr[:500]}...")

            if result.returncode != 0:
                logger.error(f"Manim execution failed with return code {result.returncode}")
                return None

            # Find generated video file
            video_files = list(media_dir.rglob("*.mp4"))
            logger.info(f"Found {len(video_files)} video files: {[str(f) for f in video_files]}")

            if not video_files:
                logger.error("No video files generated by Manim")
                return None

            # Return path to the first video file
            video_path = str(video_files[0])
            logger.info(f"Selected video file: {video_path}")

            # Verify video file is valid
            if not Path(video_path).exists():
                logger.error(f"Selected video file does not exist: {video_path}")
                return None

            file_size = Path(video_path).stat().st_size
            if file_size == 0:
                logger.error(f"Video file is empty: {video_path}")
                return None

            logger.info(f"Video file size: {file_size} bytes")
            logger.info("Video generation test passed")
            return video_path

    except subprocess.TimeoutExpired:
        logger.error("Manim execution timed out")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in video generation test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

async def main():
    """Main test function"""
    logger.info("Starting comprehensive debug test...")

    # Step 1: Test AI service
    ai_result = await test_ai_service()
    if not ai_result:
        logger.error("AI service test failed - stopping")
        return

    # Step 2: Test Manim code generation
    manim_code = test_manim_code_generation(ai_result)
    if not manim_code:
        logger.error("Manim code generation test failed - stopping")
        return

    # Step 3: Test video generation
    video_path = test_video_generation(manim_code)
    if not video_path:
        logger.error("Video generation test failed")
        return

    logger.info("All tests passed successfully!")
    logger.info(f"Generated video at: {video_path}")

if __name__ == "__main__":
    asyncio.run(main())
