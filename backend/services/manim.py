"""
Consolidated Manim Video Generation Service

This unified service combines the best features from all variants:
- Enhanced security with input validation and sanitization
- Memory leak prevention with proper resource management  
- Improved AI prompts for better video generation
- Performance optimizations and automated cleanup
- Comprehensive error handling and logging
"""

import os
import sys
import re
import subprocess
import tempfile
import shutil
import gc
import resource
import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

import google.generativeai as genai
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VideoGenerationConfig:
    """Configuration for video generation with security and performance settings"""
    max_prompt_length: int = 500
    max_code_length: int = 8192
    max_execution_time: int = 300  # 5 minutes
    max_memory_mb: int = 2048      # 2GB (more reasonable default)
    max_retries: int = 3
    quality: str = "medium_quality"
    resolution: tuple = (1280, 720)
    frame_rate: int = 30
    max_animation_duration: int = 30  # seconds
    enable_resource_limits: bool = True  # Can be disabled if limits cause issues
    
    def __post_init__(self):
        """Load configuration from config module if available"""
        try:
            from config import config
            self.max_prompt_length = config.security.max_prompt_length
            self.max_code_length = config.security.max_code_length
            self.max_execution_time = config.performance.max_execution_time_seconds
            self.max_memory_mb = config.performance.max_memory_mb
            self.max_retries = config.ai.max_retries
            self.quality = config.performance.video_quality
            self.resolution = config.performance.video_resolution
            self.frame_rate = config.performance.video_frame_rate
        except ImportError:
            logger.warning("Config module not available, using default values")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using default values")
        
        # Check environment variable to disable resource limits
        if os.getenv("DISABLE_RESOURCE_LIMITS", "").lower() in ("true", "1", "yes"):
            self.enable_resource_limits = False
            logger.info("Resource limits disabled via environment variable")

class SecurityValidator:
    """Security validation for user inputs and generated code"""
    
    # Dangerous patterns that should never appear in generated code
    DANGEROUS_PATTERNS = [
        r'import\s+os',
        r'import\s+sys',
        r'import\s+subprocess',
        r'import\s+shutil',
        r'exec\s*\(',
        r'eval\s*\(',
        r'__import__',
        r'open\s*\(',
        r'file\s*\(',
        r'input\s*\(',
        r'raw_input\s*\(',
        r'compile\s*\(',
        r'globals\s*\(',
        r'locals\s*\(',
    ]
    
    # Required patterns for valid Manim code
    REQUIRED_PATTERNS = [
        r'from\s+manim\s+import\s+\*',
        r'class\s+\w+\s*\(\s*Scene\s*\)',
        r'def\s+construct\s*\(',
    ]
    
    # Allowed Manim objects and methods
    ALLOWED_MANIM_OBJECTS = {
        'Text', 'Circle', 'Square', 'Rectangle', 'Triangle', 'Line', 'Arrow',
        'VGroup', 'Dot', 'Point', 'Arc', 'Polygon', 'NumberLine',
        'Create', 'Transform', 'FadeIn', 'FadeOut', 'Write', 'DrawBorderThenFill',
        'ShowCreation', 'GrowFromCenter', 'ReplacementTransform', 'MoveToTarget',
        'Rotate', 'Scale', 'Shift', 'AnimationGroup', 'Succession',
        'RED', 'BLUE', 'GREEN', 'YELLOW', 'WHITE', 'BLACK', 'ORANGE', 'PURPLE',
        'PINK', 'GRAY', 'GREY', 'DARK_BLUE', 'LIGHT_BLUE', 'UP', 'DOWN', 'LEFT', 'RIGHT',
        'ORIGIN', 'PI', 'TAU', 'Scene', 'wait', 'play', 'add', 'remove'
    }
    
    @classmethod
    def validate_prompt(cls, prompt: str) -> bool:
        """Validate user prompt for security and length"""
        if not prompt or len(prompt.strip()) < 5:
            raise ValueError("Prompt is too short")
        
        if len(prompt) > 500:
            raise ValueError("Prompt is too long (max 500 characters)")
        
        # Check for potential injection attempts
        dangerous_keywords = ['import', 'exec', 'eval', 'open', 'file', 'os.', 'sys.']
        prompt_lower = prompt.lower()
        for keyword in dangerous_keywords:
            if keyword in prompt_lower:
                raise ValueError(f"Prompt contains potentially dangerous keyword: {keyword}")
        
        return True
    
    @classmethod
    def validate_generated_code(cls, code: str) -> bool:
        """Validate generated code for security and correctness"""
        if not code or len(code.strip()) < 50:
            raise ValueError("Generated code is too short")
        
        if len(code) > 8192:
            raise ValueError("Generated code is too long")
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                raise ValueError(f"Code contains dangerous pattern: {pattern}")
        
        # Check for required patterns
        for pattern in cls.REQUIRED_PATTERNS:
            if not re.search(pattern, code, re.IGNORECASE):
                raise ValueError(f"Code missing required pattern: {pattern}")
        
        return True

class ResourceManager:
    """Manage system resources to prevent memory leaks and overconsumption"""
    
    def __init__(self, config: VideoGenerationConfig):
        self.config = config
        self.initial_memory = None
        
    def __enter__(self):
        """Set resource limits when entering context"""
        if PSUTIL_AVAILABLE:
            self.initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Skip resource limits if disabled or if they cause issues
        if not self.config.enable_resource_limits:
            logger.debug("Resource limits disabled")
            return self
        
        try:
            # Get current limits to avoid setting limits lower than current usage
            current_mem_soft, current_mem_hard = resource.getrlimit(resource.RLIMIT_AS)
            current_cpu_soft, current_cpu_hard = resource.getrlimit(resource.RLIMIT_CPU)
            
            # Set memory limit (only if higher than current or current is unlimited)
            new_memory_limit = self.config.max_memory_mb * 1024 * 1024
            if current_mem_soft == resource.RLIM_INFINITY or new_memory_limit > current_mem_soft:
                resource.setrlimit(resource.RLIMIT_AS, (
                    new_memory_limit,  # soft limit
                    max(new_memory_limit, current_mem_hard) if current_mem_hard != resource.RLIM_INFINITY else new_memory_limit   # hard limit
                ))
                logger.debug(f"Set memory limit to {self.config.max_memory_mb}MB")
            else:
                logger.debug(f"Memory limit not set (current: {current_mem_soft // 1024 // 1024}MB, requested: {self.config.max_memory_mb}MB)")
            
            # Set CPU time limit (only if higher than current or current is unlimited)
            new_cpu_limit = self.config.max_execution_time
            if current_cpu_soft == resource.RLIM_INFINITY or new_cpu_limit > current_cpu_soft:
                resource.setrlimit(resource.RLIMIT_CPU, (
                    new_cpu_limit,  # soft limit
                    max(new_cpu_limit + 30, current_cpu_hard) if current_cpu_hard != resource.RLIM_INFINITY else new_cpu_limit + 30  # hard limit
                ))
                logger.debug(f"Set CPU time limit to {new_cpu_limit}s")
            else:
                logger.debug(f"CPU time limit not set (current: {current_cpu_soft}s, requested: {new_cpu_limit}s)")
                
        except (ImportError, OSError, ValueError) as e:
            logger.warning(f"Could not set resource limits: {e} - disabling resource limits for this session")
            # Disable resource limits for future calls if they're causing issues
            self.config.enable_resource_limits = False
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context"""
        try:
            # Force garbage collection
            gc.collect()
            
            # Check for memory leaks
            if PSUTIL_AVAILABLE and self.initial_memory:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_increase = current_memory - self.initial_memory
                
                if memory_increase > 100:  # More than 100MB increase
                    logger.warning(f"Potential memory leak detected: {memory_increase:.2f}MB increase")
            
        except Exception as e:
            logger.error(f"Error during resource cleanup: {e}")

class ManimService:
    """Consolidated Manim service with all optimizations and security features"""
    
    def __init__(self):
        self.config = VideoGenerationConfig()
        self.config.__post_init__()  # Initialize configuration
        self.validator = SecurityValidator()
        
        # Setup directories with proper permissions
        self.media_dir = os.path.abspath(os.getenv("MEDIA_DIR", "media"))
        self.temp_dir = os.path.join(self.media_dir, "temp")
        os.makedirs(self.media_dir, mode=0o755, exist_ok=True)
        os.makedirs(self.temp_dir, mode=0o755, exist_ok=True)
        
        # Configure Gemini AI
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config=genai.GenerationConfig(
                temperature=0.05,  # Lower temperature for more consistent code
                top_p=0.7,
                top_k=15,
                max_output_tokens=4096,
                candidate_count=1,
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
        )
        
        # Process pool for isolated execution
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        
        logger.info("ManimService initialized successfully")
    
    async def generate_video(self, prompt: str, user_id: str = None) -> str:
        """Generate video with comprehensive security and performance optimization"""
        
        # Validate input
        self.validator.validate_prompt(prompt)
        
        with ResourceManager(self.config) as resource_mgr:
            for attempt in range(self.config.max_retries):
                temp_file = None
                try:
                    logger.info(f"Generating video (attempt {attempt + 1}/{self.config.max_retries})")
                    
                    # Generate animation code
                    scene_code = await self._generate_animation_code(prompt, attempt)

                    # Ensure required imports and normalize code
                    scene_code = self._ensure_code_prereqs(scene_code)

                    # Detect scene class name (fallback to GeneratedScene)
                    scene_name = self._detect_scene_class_name(scene_code) or "GeneratedScene"
                    
                    # Validate generated code
                    self.validator.validate_generated_code(scene_code)
                    
                    # Create secure temporary file
                    temp_file = self._create_secure_temp_file(scene_code, attempt)
                    
                    # Render animation
                    video_path = await self._render_animation(temp_file, attempt, scene_name)
                    
                    logger.info("Video generation successful")
                    return video_path
                    
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.config.max_retries - 1:
                        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
                    
                finally:
                    # Clean up temporary file
                    if temp_file and os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except Exception as e:
                            logger.warning(f"Failed to clean up temp file: {e}")
        
        raise HTTPException(status_code=500, detail="Video generation failed after all attempts")
    
    async def _generate_animation_code(self, prompt: str, attempt: int = 0) -> str:
        """Generate optimized Manim code using enhanced AI prompts"""
        
        enhanced_prompt = self._build_enhanced_prompt(prompt, attempt)
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, 
                enhanced_prompt
            )
            
            # Extract and clean response
            code = self._extract_and_clean_response(response)
            
            if not code or len(code.strip()) < 50:
                raise ValueError("Generated code is too short or empty")
            
            return code
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise
    
    def _build_enhanced_prompt(self, prompt: str, attempt: int = 0) -> str:
        """Build an enhanced prompt with better instructions and examples"""
        
        retry_context = ""
        if attempt > 0:
            retry_context = f"""
IMPORTANT: This is retry attempt {attempt + 1}. The previous code had issues.
- Ensure perfect Python syntax
- Use only allowed Manim objects
- Keep animations simple and clear
- Verify all parentheses and indentation
"""
        
        mathematical_examples = """
MATHEMATICAL EXAMPLES:

For "show quadratic function":
```python
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Create parabola using points
        points = [np.array([x, x**2 * 0.5, 0]) for x in np.linspace(-3, 3, 50)]
        parabola = VGroup(*[Dot(point, radius=0.02) for point in points])
        parabola.set_color(BLUE)
        
        # Create axes
        x_axis = Line(LEFT * 4, RIGHT * 4).set_color(WHITE)
        y_axis = Line(DOWN * 2, UP * 4).set_color(WHITE)
        
        self.play(Create(x_axis), Create(y_axis))
        self.play(Create(parabola), run_time=2)
        self.wait(1)
```

For "visualize circle":
```python
                from manim import *

                class GeneratedScene(Scene):
                    def construct(self):
                        circle = Circle(radius=2, color=BLUE)
                        self.play(Create(circle))
                        self.wait(1)
```
"""
        
        return f"""You are an expert Manim animator specializing in mathematical visualizations. Create clean, educational Python code.

USER REQUEST: {prompt}

{mathematical_examples}

STRICT REQUIREMENTS:
1. ONLY return executable Python code - NO explanations or markdown
2. Start with "from manim import *" and numpy import if needed
3. Create class "GeneratedScene(Scene)" with "construct(self)" method
4. Use ONLY these safe objects:
   - Shapes: Circle, Square, Rectangle, Triangle, Line, Arrow, Dot, Arc, Polygon
   - Text: Text (NO MathTex, NO Tex, NO LaTeX)
   - Groups: VGroup
   - Animations: Create, Transform, FadeIn, FadeOut, Write, GrowFromCenter
   - Colors: RED, BLUE, GREEN, YELLOW, WHITE, BLACK, ORANGE, PURPLE
   - Directions: UP, DOWN, LEFT, RIGHT, ORIGIN
5. Keep animations 5-20 seconds total
6. Use simple mathematical relationships (no complex functions)
7. Ensure perfect Python syntax and indentation
8. NO imports except "from manim import *" and "import numpy as np"

ANIMATION GUIDELINES:
- Start simple, build complexity gradually
- Use clear colors and positioning
- Add appropriate wait() calls
- Use run_time parameter for smooth animations
- Position objects clearly (use shift(), move_to())

{retry_context}

Generate clean, working code for: {prompt}

Remember: Return ONLY the Python code, no explanations."""
    
    def _extract_and_clean_response(self, response) -> str:
        """Extract and clean the response from Gemini AI"""
        try:
            # Try different ways to extract text
            if hasattr(response, 'text') and response.text:
                text = response.text
            elif hasattr(response, 'parts') and response.parts:
                text = ''.join(part.text for part in response.parts if hasattr(part, 'text'))
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    text = ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                else:
                    text = str(candidate)
            else:
                text = str(response)
            
            if not text:
                raise ValueError("No text content in response")
            
            # Clean the response
            text = self._clean_code_response(text)
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract response: {e}")
            raise ValueError(f"Could not extract code from AI response: {e}")
    
    def _clean_code_response(self, response_text: str) -> str:
        """Clean and validate the code response"""
        # Remove markdown code blocks
        response_text = re.sub(r'```python\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        
        # Remove explanatory text before the code
        lines = response_text.split('\n')
        code_started = False
        cleaned_lines = []
        
        for line in lines:
            if line.strip().startswith('from manim import'):
                code_started = True
            
            if code_started:
                cleaned_lines.append(line)
        
        if not cleaned_lines:
            # Fallback: try to find code block
            code_match = re.search(r'(from manim import.*)', response_text, re.DOTALL | re.IGNORECASE)
            if code_match:
                cleaned_lines = code_match.group(1).split('\n')
        
        # Join and clean up
        code = '\n'.join(cleaned_lines)
        code = re.sub(r'\n{3,}', '\n\n', code)  # Remove excessive newlines
        code = code.strip()
        
        return code

    def _ensure_code_prereqs(self, code: str) -> str:
        """Ensure the generated code has required imports and sane defaults."""
        lines = code.split("\n")
        # Ensure numpy import if np. is used
        uses_np = any("np." in line for line in lines)
        has_np_import = any(line.strip().startswith("import numpy as np") for line in lines)
        if uses_np and not has_np_import:
            # Insert after the manim import
            for idx, line in enumerate(lines):
                if line.strip().startswith("from manim import"):
                    lines.insert(idx + 1, "import numpy as np")
                    break
        # Ensure class name exists; if not, wrap minimal Scene
        if not re.search(r"class\s+\w+\s*\(\s*Scene\s*\)", code):
            lines.append("")
            lines.append("class GeneratedScene(Scene):")
            lines.append("    def construct(self):")
            lines.append("        self.wait(1)")
        return "\n".join(lines)

    def _detect_scene_class_name(self, code: str) -> Optional[str]:
        """Find the Scene subclass name in the code."""
        match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)", code)
        if match:
            return match.group(1)
        return None
    
    def _create_secure_temp_file(self, code: str, attempt: int) -> str:
        """Create a secure temporary file for the animation code"""
        # Create secure temporary file
        fd, temp_path = tempfile.mkstemp(
            suffix=f'_attempt_{attempt}.py',
            prefix='manim_scene_',
            dir=self.temp_dir,
            text=True
        )
        
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(code)
            
            # Set restrictive permissions
            os.chmod(temp_path, 0o600)
            
            return temp_path
        
        except Exception as e:
            os.close(fd)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
    
    async def _render_animation(self, code_file: str, attempt: int, scene_name: str) -> str:
        """Render animation with resource limits"""
        
        module_name = os.path.splitext(os.path.basename(code_file))[0]
        output_dir = os.path.join(self.media_dir, "videos", module_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # Manim command with safer CLI flags compatible with manim 0.19
        width, height = self.config.resolution
        cmd = [
            sys.executable, "-m", "manim",
            "-q", "m",  # medium quality
            "-r", f"{width},{height}",
            "-v", "WARNING",
            "--renderer=cairo",
            code_file,
            scene_name,
            f"--media_dir={self.media_dir}",
            "--disable_caching",
        ]
        
        try:
            # Run with timeout
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=dict(os.environ, PYTHONPATH=os.pathsep.join(sys.path))
                ),
                timeout=self.config.max_execution_time
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                decoded_err = stderr.decode(errors="ignore") if stderr else "Unknown rendering error"
                logger.error("Manim stderr:\n" + decoded_err)
                raise subprocess.CalledProcessError(result.returncode, cmd, stderr=decoded_err)
            
            # Find the generated video file
            video_file = self._find_generated_video(output_dir, scene_name)
            
            if not video_file or not os.path.exists(video_file):
                raise FileNotFoundError("Generated video file not found")
            
            return video_file
            
        except asyncio.TimeoutError:
            raise HTTPException(status_code=500, detail="Video rendering timed out")
        except Exception as e:
            logger.error(f"Rendering failed: {e}")
            raise
    
    def _find_generated_video(self, output_dir: str, scene_name: str) -> Optional[str]:
        """Find the generated video file in the output directory"""
        filename = f"{scene_name}.mp4"
        possible_paths = [
            os.path.join(output_dir, "720p30", filename),
            os.path.join(output_dir, "1080p60", filename),
            os.path.join(output_dir, "480p15", filename),
            os.path.join(output_dir, filename),
        ]
        
        # Also search recursively
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.mp4') and scene_name in file:
                    possible_paths.append(os.path.join(root, file))
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.getsize(path) > 1000:  # At least 1KB
                return path
        
        return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old temporary files to prevent disk space issues"""
        import time
        current_time = time.time()
        
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if current_time - os.path.getctime(file_path) > max_age_hours * 3600:
                        os.remove(file_path)
                        logger.info(f"Cleaned up old file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {file_path}: {e}")
    
    def __del__(self):
        """Cleanup resources when service is destroyed"""
        try:
            if hasattr(self, 'process_pool'):
                self.process_pool.shutdown(wait=True)
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

# Legacy class names for compatibility
OptimizedManimService = ManimService
EnhancedManimService = ManimService