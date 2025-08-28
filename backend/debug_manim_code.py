#!/usr/bin/env python3
"""
Debug script to examine the generated Manim code
"""

import asyncio
import logging
import os
import json
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def main():
    """Main function to get and examine Manim code"""
    logger.info("Getting AI-generated Manim code...")

    try:
        from services.ai_service_new import AIService

        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            logger.error("GOOGLE_AI_API_KEY not found")
            return

        ai_service = AIService(api_key=api_key)
        result = await ai_service.process_animation_request("Create a simple circle animation")

        if 'error' in result:
            logger.error(f"AI service failed: {result['error']}")
            return

        manim_code = result.get('manim_code', '')
        animation_spec = result.get('animation_spec', {})

        logger.info("=== GENERATED MANIM CODE ===")
        print(manim_code)
        print("\n=== ANIMATION SPEC ===")
        print(json.dumps(animation_spec, indent=2))

        # Save the code to a file for manual testing
        with open('/tmp/debug_manim_code.py', 'w', encoding='utf-8') as f:
            f.write(manim_code)

        logger.info("Code saved to /tmp/debug_manim_code.py")

        # Try to run it manually to get the full error
        import tempfile
        import subprocess
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            scene_file = temp_path / "debug_scene.py"
            scene_file.write_text(manim_code, encoding='utf-8')

            media_dir = temp_path / "media"
            media_dir.mkdir(parents=True, exist_ok=True)

            cmd = [
                "manim", "render",
                str(scene_file), "GeneratedScene",
                "-ql", "--fps", "15", "--format", "mp4",
                "--disable_caching", "--media_dir", str(media_dir),
                "--renderer", "cairo"
            ]

            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=temp_path,
                timeout=60
            )

            logger.info(f"Return code: {result.returncode}")
            logger.info("=== FULL STDOUT ===")
            print(result.stdout)
            logger.info("=== FULL STDERR ===")
            print(result.stderr)

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
