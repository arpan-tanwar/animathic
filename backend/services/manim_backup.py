import os
import sys
import re
import subprocess
from typing import Optional, Tuple
from fastapi import HTTPException
from manim import config
import google.generativeai as genai

class ManimService:
    def __init__(self):
        self.media_dir = os.getenv("MEDIA_DIR", "media")
        os.makedirs(self.media_dir, exist_ok=True)
        
        # Configure Manim for better performance
        config.media_dir = self.media_dir
        config.output_file = "animation"
        config.pixel_height = 720
        config.pixel_width = 1280
        config.frame_height = 8.0
        config.frame_width = 14.222222222222222
        config.disable_caching_warning = True
        config.quality = "medium_quality"  # Faster rendering
        config.preview = False  # Disable preview
        config.write_to_movie = True
        config.write_still = False  # Don't write still images
        config.save_last_frame = False  # Don't save last frame
        config.save_pngs = False  # Don't save PNGs
        config.save_as_gif = False  # Don't save as GIF
        config.save_sections = False  # Don't save sections
        config.save_frames = False  # Don't save individual frames
        config.disable_caching = True  # Disable caching completely

        # Configure Gemini API
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Please set GOOGLE_API_KEY in your .env file")
        
        genai.configure(api_key=self.api_key)
        # Use the latest Gemini 2.5 Flash free model for faster and cost-effective processing
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config=genai.GenerationConfig(
                temperature=0.1,  # Very low for consistent code generation
                top_p=0.8,
                top_k=20,
                max_output_tokens=8192,  # High limit for complex animations
                candidate_count=1,
            ),
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        )

    async def generate_video(self, prompt: str) -> str:
        """
        Generate a video using Manim based on the prompt.
        
        Args:
            prompt: The prompt describing the animation to generate
            
        Returns:
            Path to the generated video file
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                scene_code = await self._generate_animation_code(prompt, attempt)
                if not self._validate_scene_code(scene_code):
                    continue
                    
                video_file = await self._render_animation(scene_code, attempt)
                return video_file
                
            except subprocess.CalledProcessError as e:
                print(f"Manim command failed (attempt {attempt + 1}): {e.stderr}")
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to render video: {e.stderr}"
                    )
                    
            except Exception as e:
                print(f"Error during video generation (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to generate video: {str(e)}"
                    )
                
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video after {max_retries} attempts"
        )

    async def _generate_animation_code(self, prompt: str, attempt: int = 0) -> str:
        """Generate Manim animation code using Gemini AI with enhanced error handling."""
        print(f"🎬 Generating animation code (attempt {attempt + 1})")
        
        # Build optimized prompt
        gemini_prompt = self._build_generation_prompt(prompt, attempt)
        print(f"📝 Prompt length: {len(gemini_prompt)} characters")
        
        try:
            # Generate content with the pre-configured model
            print("🚀 Sending request to Gemini 2.5 Flash...")
            response = self.model.generate_content(gemini_prompt)
            
            print(f"✅ Received response: {type(response)}")
            
            # Extract text with robust handling
            response_text = self._extract_response_text(response)
            print(f"📄 Extracted text length: {len(response_text)}")
            
            if not response_text or len(response_text.strip()) == 0:
                raise Exception("Empty response text extracted from Gemini")
            
            # Clean and validate the code
            cleaned_code = self._clean_code_response(response_text)
            print(f"🧹 Cleaned code length: {len(cleaned_code)}")
            
            # Additional validation
            if len(cleaned_code.strip()) < 50:  # Too short to be valid code
                raise Exception("Generated code too short to be valid")
            
            print("✨ Code generation successful!")
            return cleaned_code
            
        except Exception as e:
            error_msg = f"❌ Code generation failed: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

    def _build_generation_prompt(self, prompt: str, attempt: int = 0) -> str:
        """Build an optimized prompt for Gemini AI code generation."""
        
        # Add context based on attempt number
        attempt_context = ""
        if attempt > 0:
            attempt_context = f"\n\nThis is attempt {attempt + 1}. Please ensure the code is syntactically correct and uses only basic Manim objects."
        
        return f"""You are an expert Manim developer. Generate Python code for this animation request:

USER REQUEST: {prompt}

STRICT REQUIREMENTS:
1. Return ONLY executable Python code - no explanations, no markdown
2. Use ONLY these Manim objects: Text(), Rectangle(), Line(), Arrow(), Circle(), Square(), Triangle(), VGroup(), NumberPlane(), Axes()
3. NEVER use MathTex, Tex, or any LaTeX objects
4. ALWAYS use "from manim import *" as the first line
5. Create a class named "GeneratedScene" that inherits from Scene
6. Include a "construct" method with the animation logic
7. Use self.play() for animations and self.wait() for pauses
8. Keep animations simple and clear
9. Use basic colors: RED, BLUE, GREEN, YELLOW, WHITE, ORANGE, PURPLE
10. Animation duration should be 5-15 seconds total

TEMPLATE:
```python
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Create objects
        
        # Add to scene
        
        # Animate
        
        # Wait
        self.wait(1)
```

EXAMPLES:

Example 1 - Circle to Square:
```python
                from manim import *

                class GeneratedScene(Scene):
                    def construct(self):
                        circle = Circle(radius=2, color=BLUE)
                        self.play(Create(circle))
                        self.wait(1)
        
                        square = Square(side_length=3, color=RED)
                        self.play(Transform(circle, square))
        self.wait(2)
```

Example 2 - Moving Text:
```python
                from manim import *

                class GeneratedScene(Scene):
                    def construct(self):
        text = Text("Hello Manim!", color=YELLOW)
        self.play(Write(text))
                        self.wait(1)

        self.play(text.animate.shift(UP * 2))
                        self.wait(1)

        self.play(text.animate.scale(1.5))
        self.wait(2)
```

Now generate the code for: {prompt}{attempt_context}

CODE:"""

    def _extract_response_text(self, response) -> str:
        """Extract text from Gemini 2.5 Flash response with robust error handling."""
        print(f"Analyzing response type: {type(response)}")
        
        # Method 1: Try simple text accessor
        try:
            if hasattr(response, 'text') and response.text:
                print(f"Method 1 success: {len(response.text)} chars")
                return response.text
        except Exception as e:
            print(f"Method 1 failed: {e}")
        
        # Method 2: Try candidates path
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts_text = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            parts_text.append(part.text)
                    if parts_text:
                        result = ''.join(parts_text)
                        print(f"Method 2 success: {len(result)} chars")
                        return result
        except Exception as e:
            print(f"Method 2 failed: {e}")
        
        # Method 3: Force resolve and retry
        try:
            if hasattr(response, 'resolve'):
                response.resolve()
                if hasattr(response, 'text') and response.text:
                    print(f"Method 3 success: {len(response.text)} chars")
                    return response.text
        except Exception as e:
            print(f"Method 3 failed: {e}")
        
        # Final fallback
        result = str(response)
        if len(result) < 10:
            raise Exception("All text extraction methods failed")
        
        print(f"Fallback success: {len(result)} chars")
        return result

    def _clean_code_response(self, response: str) -> str:
        """Clean and format the AI response to extract pure Python code."""
        print("🧹 Cleaning response text...")
        
        # Remove common prefixes/suffixes
        code = response.strip()
        
        # Remove markdown code blocks
        code = re.sub(r'```python\s*\n?', '', code, flags=re.IGNORECASE)
        code = re.sub(r'```\s*\n?', '', code)
        
        # Remove CODE: prefix if present
        code = re.sub(r'^CODE:\s*\n?', '', code, flags=re.MULTILINE)
        
        # Remove any leading explanation text before the code
        lines = code.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('from manim'):
                start_idx = i
                break
        
        if start_idx > 0:
            code = '\n'.join(lines[start_idx:])
            print(f"🔪 Removed {start_idx} explanation lines")
        
        # Clean up extra whitespace
        code = '\n'.join(line.rstrip() for line in code.split('\n'))
        code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)  # Max 2 consecutive newlines
        
        cleaned = code.strip()
        print(f"✨ Cleaned code: {len(cleaned)} chars")
        return cleaned

    def _validate_scene_code(self, scene_code: str) -> bool:
        """Validate the generated scene code with comprehensive checks."""
        print("Validating generated code...")
        
                if not scene_code or not scene_code.strip():
                    print("Empty code received")
            return False
        
        # Required elements check
        required_elements = [
            ("from manim import", "Missing Manim import"),
            ("class GeneratedScene", "Missing GeneratedScene class"),
            ("def construct", "Missing construct method"),
            ("Scene", "Class doesn't inherit from Scene")
        ]
        
        for element, error_msg in required_elements:
            if element not in scene_code:
                print(f"ERROR: {error_msg}")
                return False
        
        # Forbidden elements check
        forbidden_elements = [
            ("MathTex", "Contains forbidden MathTex"),
            ("Tex(", "Contains forbidden Tex"),
            ("\\\\", "Contains LaTeX commands"),
            ("$$", "Contains LaTeX math delimiters")
        ]
        
        for element, error_msg in forbidden_elements:
            if element in scene_code:
                print(f"ERROR: {error_msg}")
                return False
        
        # Basic syntax check
        lines = scene_code.split('\n')
        has_self_play = any('self.play(' in line for line in lines)
        
        if not has_self_play:
            print("WARNING: No self.play() found - animation might be static")
        
        # Check for common issues
        if scene_code.count('class ') > 1:
            print("ERROR: Multiple class definitions found")
            return False
        
        if 'def construct(self' not in scene_code:
            print("ERROR: Invalid construct method signature")
            return False
        
        print("SUCCESS: Code validation passed!")
        return True

    async def _render_animation(self, scene_code: str, attempt: int) -> str:
        """Render the animation from the generated code with enhanced error handling."""
        print(f"Starting animation rendering (attempt {attempt + 1})")
        
        # Create temporary file
        temp_file = os.path.join(self.media_dir, f"temp_scene_{attempt}.py")
        
        try:
            # Write code to file with error handling
            print(f"Writing code to: {temp_file}")
            with open(temp_file, "w", encoding='utf-8') as f:
                    f.write(scene_code)
            print("Code file written successfully")
            
            # Verify file was written correctly
            if not os.path.exists(temp_file):
                raise Exception("Failed to create temporary Python file")
                
            # Setup output directory
            output_dir = os.path.join(self.media_dir, "videos", f"temp_scene_{attempt}")
            os.makedirs(output_dir, exist_ok=True)
            print(f"Output directory: {output_dir}")
            
            # Prepare Manim command
            manim_cmd = [
                sys.executable, "-m", "manim",
                "-qm",  # Medium quality
                "--disable_caching",
                "--progress_bar", "none",  # Disable progress bar for cleaner logs
                temp_file,
                "GeneratedScene"
            ]
            
            print(f"🚀 Running Manim command: {' '.join(manim_cmd)}")
            
            # Run Manim with timeout
            try:
                result = subprocess.run(
                    manim_cmd,
                        capture_output=True,
                        text=True,
                    check=True,
                    cwd=self.media_dir,
                    timeout=300  # 5 minute timeout
                )
                
                print("✅ Manim execution successful")
                if result.stdout:
                    print(f"📋 Manim stdout: {result.stdout[:500]}...")
                if result.stderr:
                    print(f"⚠️ Manim stderr: {result.stderr[:500]}...")
                    
            except subprocess.TimeoutExpired:
                raise Exception("Manim rendering timed out after 5 minutes")
                except subprocess.CalledProcessError as e:
                error_details = f"Manim failed with code {e.returncode}"
                if e.stderr:
                    error_details += f"\nError: {e.stderr}"
                if e.stdout:
                    error_details += f"\nOutput: {e.stdout}"
                raise Exception(error_details)
            
            # Find generated video with multiple possible paths
            possible_paths = [
                os.path.join(output_dir, "720p30", "GeneratedScene.mp4"),
                os.path.join(self.media_dir, "videos", f"temp_scene_{attempt}", "720p30", "GeneratedScene.mp4"),
                os.path.join(self.media_dir, "videos", "temp_scene", "720p30", "GeneratedScene.mp4"),
            ]
            
            video_file = None
            for path in possible_paths:
                if os.path.exists(path):
                    video_file = path
                    print(f"🎥 Found video at: {path}")
                    break
            
            if not video_file:
                # List directory contents for debugging
                print("🔍 Searching for video files...")
                for root, dirs, files in os.walk(os.path.join(self.media_dir, "videos")):
                    for file in files:
                        if file.endswith('.mp4'):
                            print(f"  Found: {os.path.join(root, file)}")
                
                raise Exception("Generated video file not found in any expected location")
            
            # Verify video file is valid
            if os.path.getsize(video_file) == 0:
                raise Exception("Generated video file is empty")
            
            print(f"✨ Animation rendering complete: {video_file}")
            return video_file
            
        except Exception as e:
            print(f"❌ Rendering failed: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"🗑️ Cleaned up temporary file: {temp_file}")
            except Exception as cleanup_error:
                print(f"⚠️ Failed to cleanup {temp_file}: {cleanup_error}")

    def get_video_duration(self, video_path: str) -> float:
        """Get the duration of a video file in seconds."""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                 "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                capture_output=True,
                text=True,
                check=True
            )
            return float(result.stdout.strip())
        except Exception as e:
            print(f"Error getting video duration: {str(e)}")
            return 0.0

    def get_video_resolution(self, video_path: str) -> Tuple[int, int]:
        """Get the resolution of a video file."""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0",
                 video_path],
                capture_output=True,
                text=True,
                check=True
            )
            width, height = map(int, result.stdout.strip().split("x"))
            return (width, height)
        except Exception as e:
            print(f"Error getting video resolution: {str(e)}")
            return (1280, 720)  # Default resolution 