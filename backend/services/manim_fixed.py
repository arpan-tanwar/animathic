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
        # Use absolute path to avoid path conflicts
        self.media_dir = os.path.abspath(os.getenv("MEDIA_DIR", "media"))
        os.makedirs(self.media_dir, exist_ok=True)
        
        # Configure Manim for better performance
        config.media_dir = self.media_dir
        config.output_file = "animation"
        config.pixel_height = 720
        config.pixel_width = 1280
        config.frame_height = 8.0
        config.frame_width = 14.222222222222222
        config.disable_caching_warning = True
        config.quality = "medium_quality"
        config.preview = False
        config.write_to_movie = True
        config.write_still = False
        config.save_last_frame = False
        config.save_pngs = False
        config.save_as_gif = False
        config.save_sections = False
        config.save_frames = False
        config.disable_caching = True

        # Configure Gemini API
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Please set GOOGLE_API_KEY in your .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                top_p=0.8,
                top_k=20,
                max_output_tokens=8192,
                candidate_count=1,
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )

    async def generate_video(self, prompt: str) -> str:
        """Generate a video using Manim based on the prompt."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                print(f"=== ATTEMPT {attempt + 1} ===")
                scene_code = await self._generate_animation_code(prompt, attempt)
                
                if not self._validate_scene_code(scene_code):
                    print("Code validation failed, retrying...")
                    continue
                    
                video_file = await self._render_animation(scene_code, attempt)
                print("SUCCESS: Video generation complete!")
                return video_file
                
            except subprocess.CalledProcessError as e:
                print(f"Manim rendering failed (attempt {attempt + 1}): {e.stderr}")
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=500, detail=f"Failed to render video: {e.stderr}")
                    
            except Exception as e:
                print(f"Error during video generation (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")
                
        raise HTTPException(status_code=500, detail=f"Failed to generate video after {max_retries} attempts")

    async def _generate_animation_code(self, prompt: str, attempt: int = 0) -> str:
        """Generate Manim animation code using Gemini AI."""
        print(f"Generating animation code for: {prompt}")
        
        gemini_prompt = self._build_generation_prompt(prompt, attempt)
        
        try:
            response = self.model.generate_content(gemini_prompt)
            response_text = self._extract_response_text(response)
            
            if not response_text or len(response_text.strip()) < 50:
                raise Exception("Generated code too short or empty")
            
            cleaned_code = self._clean_code_response(response_text)
            print(f"Generated code length: {len(cleaned_code)} characters")
            return cleaned_code
            
        except Exception as e:
            print(f"Code generation failed: {str(e)}")
            raise

    def _build_generation_prompt(self, prompt: str, attempt: int = 0) -> str:
        """Build an optimized prompt for Gemini AI code generation."""
        attempt_context = ""
        if attempt > 0:
            attempt_context = f"\n\nThis is attempt {attempt + 1}. Please ensure the code is syntactically correct."
        
        return f"""You are an expert Manim developer. Generate Python code for this animation:

REQUEST: {prompt}

REQUIREMENTS:
1. Return ONLY executable Python code - no explanations
2. Use ONLY these objects: Text(), Rectangle(), Line(), Arrow(), Circle(), Square(), Triangle(), VGroup()
3. NEVER use MathTex, Tex, or LaTeX objects
4. Start with "from manim import *"
5. Create class "GeneratedScene" inheriting from Scene
6. Include "construct" method with animations
7. Use basic colors: RED, BLUE, GREEN, YELLOW, WHITE, ORANGE, PURPLE
8. Keep animations 5-15 seconds total

TEMPLATE:
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Create objects
        circle = Circle(radius=1, color=BLUE)
        
        # Add and animate
        self.play(Create(circle))
        self.wait(1)

Generate code for: {prompt}{attempt_context}"""

    def _extract_response_text(self, response) -> str:
        """Extract text from Gemini response."""
        try:
            if hasattr(response, 'text') and response.text:
                return response.text
        except Exception:
            pass
        
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts_text = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            parts_text.append(part.text)
                    if parts_text:
                        return ''.join(parts_text)
        except Exception:
            pass
        
        result = str(response)
        if len(result) < 10:
            raise Exception("Failed to extract text from response")
        return result

    def _clean_code_response(self, response: str) -> str:
        """Clean and format the AI response to extract pure Python code."""
        code = response.strip()
        
        # Remove markdown code blocks
        code = re.sub(r'```python\s*\n?', '', code, flags=re.IGNORECASE)
        code = re.sub(r'```\s*\n?', '', code)
        
        # Find the start of actual code
        lines = code.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('from manim'):
                start_idx = i
                break
        
        if start_idx > 0:
            code = '\n'.join(lines[start_idx:])
        
        # Clean up whitespace
        code = '\n'.join(line.rstrip() for line in code.split('\n'))
        code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
        
        return code.strip()

    def _validate_scene_code(self, scene_code: str) -> bool:
        """Validate the generated scene code."""
        if not scene_code or not scene_code.strip():
            print("ERROR: Empty code")
            return False
        
        required_elements = [
            "from manim import",
            "class GeneratedScene",
            "def construct",
            "Scene"
        ]
        
        for element in required_elements:
            if element not in scene_code:
                print(f"ERROR: Missing {element}")
                return False
        
        forbidden_elements = ["MathTex", "Tex(", "\\\\", "$$"]
        for element in forbidden_elements:
            if element in scene_code:
                print(f"ERROR: Contains forbidden {element}")
                return False
        
        if 'def construct(self' not in scene_code:
            print("ERROR: Invalid construct method signature")
            return False
        
        print("SUCCESS: Code validation passed")
        return True

    async def _render_animation(self, scene_code: str, attempt: int) -> str:
        """Render the animation from the generated code."""
        print(f"Starting animation rendering (attempt {attempt + 1})")
        
        # Use absolute paths throughout
        temp_file = os.path.abspath(os.path.join(self.media_dir, f"temp_scene_{attempt}.py"))
        output_dir = os.path.abspath(os.path.join(self.media_dir, "videos", f"temp_scene_{attempt}"))
        
        try:
            # Write code to file
            print(f"Writing scene code to: {temp_file}")
            with open(temp_file, "w", encoding='utf-8') as f:
                f.write(scene_code)
            
            if not os.path.exists(temp_file):
                raise Exception("Failed to create temporary Python file")
            
            # Setup output directory
            os.makedirs(output_dir, exist_ok=True)
            print(f"Output directory created: {output_dir}")
            
            # Run Manim with absolute paths
            manim_cmd = [
                sys.executable, "-m", "manim",
                "-qm", "--disable_caching",
                "--progress_bar", "none",
                "--media_dir", self.media_dir,  # Explicitly set media dir
                temp_file, "GeneratedScene"
            ]
            
            print(f"Running command: {' '.join(manim_cmd)}")
            
            result = subprocess.run(
                manim_cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300
            )
            
            print("Manim execution successful!")
            if result.stdout:
                print(f"Manim stdout: {result.stdout[-500:]}")  # Last 500 chars
            if result.stderr:
                print(f"Manim stderr: {result.stderr[-500:]}")  # Last 500 chars
            
            # Find generated video with multiple possible paths
            possible_paths = [
                os.path.join(output_dir, "720p30", "GeneratedScene.mp4"),
                os.path.join(self.media_dir, "videos", f"temp_scene_{attempt}", "720p30", "GeneratedScene.mp4"),
                os.path.join(os.getcwd(), "media", "videos", f"temp_scene_{attempt}", "720p30", "GeneratedScene.mp4"),
            ]
            
            print("Searching for generated video in:")
            for path in possible_paths:
                print(f"  - {path}")
                if os.path.exists(path):
                    print(f"  ✅ Found video at: {path}")
                    if os.path.getsize(path) > 0:
                        print(f"Animation rendering complete: {path}")
                        return path
                    else:
                        print("  ❌ Video file is empty")
            
            # List all mp4 files in media directory for debugging
            print("Searching for any MP4 files in media directory...")
            for root, dirs, files in os.walk(self.media_dir):
                for file in files:
                    if file.endswith('.mp4'):
                        full_path = os.path.join(root, file)
                        print(f"  Found MP4: {full_path}")
                        if f"temp_scene_{attempt}" in full_path and "GeneratedScene.mp4" in file:
                            print(f"  ✅ Using: {full_path}")
                            return full_path
            
            raise Exception("Generated video file not found in any expected location")
            
        except subprocess.CalledProcessError as e:
            print(f"Manim command failed with exit code {e.returncode}")
            print(f"Stderr: {e.stderr}")
            print(f"Stdout: {e.stdout}")
            raise Exception(f"Manim rendering failed: {e.stderr}")
        except Exception as e:
            print(f"Rendering failed: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"Cleaned up temporary file: {temp_file}")
            except Exception:
                pass

    def get_video_duration(self, video_path: str) -> float:
        """Get the duration of a video file in seconds."""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                 "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                capture_output=True, text=True, check=True
            )
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def get_video_resolution(self, video_path: str) -> Tuple[int, int]:
        """Get the resolution of a video file."""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0",
                 video_path],
                capture_output=True, text=True, check=True
            )
            width, height = map(int, result.stdout.strip().split("x"))
            return (width, height)
        except Exception:
            return (1280, 720)
