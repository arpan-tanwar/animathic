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
        self.model = genai.GenerativeModel('gemini-2.5-flash')

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
        """Generate Manim animation code using Gemini AI."""
        gemini_prompt = self._build_generation_prompt(prompt)
        
        print(f"Generating animation code (attempt {attempt + 1})")
        
        # Optimized generation config for 2.5 Flash
        generation_config = genai.GenerationConfig(
            temperature=0.3,  # Slightly higher for better generation
            top_p=0.9,
            top_k=40,
            max_output_tokens=4096,  # Increase token limit
            candidate_count=1,  # Ensure single candidate
        )
        
        try:
            response = self.model.generate_content(
                gemini_prompt,
                generation_config=generation_config
            )
            
            print(f"Raw AI response type: {type(response)}")
            
            # Check if response is valid
            if not response:
                raise Exception("Empty response from Gemini API")
            
            # Handle the new Gemini 2.5 Flash response structure
            response_text = self._extract_response_text(response)
            print(f"Extracted response text length: {len(response_text)}")
            
            if not response_text or len(response_text.strip()) == 0:
                print("Got empty response text, trying alternative extraction...")
                # Try resolving the response first
                if hasattr(response, 'resolve'):
                    response.resolve()
                    response_text = self._extract_response_text(response)
                    print(f"After resolve - extracted text length: {len(response_text)}")
            
            if not response_text or len(response_text.strip()) == 0:
                raise Exception("Failed to extract any text content from Gemini response")
            
            return self._clean_code_response(response_text)
            
        except Exception as e:
            print(f"Error in generate_content: {str(e)}")
            raise

    def _build_generation_prompt(self, prompt: str) -> str:
        """Build the prompt for Gemini AI code generation."""
        return f"""You are a Manim expert. Create a Manim animation for this prompt: {prompt}

        Requirements:
        - Create an animation that EXACTLY matches the user's intent
        - Keep it simple, clear, and focused
        - Use basic Manim objects: Text(), Rectangle(), Line(), Arrow(), Circle(), Square(), Triangle(), VGroup()
        - DO NOT use MathTex or LaTeX-based objects
        
        Return ONLY the complete Python code with:
        - All necessary imports
        - A class named 'GeneratedScene' inheriting from Scene
        - A 'construct' method with animations using self.play() and self.wait()
        
        Example structure:
        from manim import *
        class GeneratedScene(Scene):
            def construct(self):
                # Your animation code here
                pass
        """

    def _extract_response_text(self, response) -> str:
        """Extract text from Gemini 2.5 Flash response, handling different response structures."""
        print(f"Response attributes: {dir(response)}")
        
        try:
            # Try the simple text accessor first
            if hasattr(response, 'text'):
                print("Using response.text accessor")
                return response.text
        except Exception as e:
            print(f"Failed to use response.text: {str(e)}")
        
        try:
            # Use the parts accessor for complex responses
            if hasattr(response, 'parts') and response.parts:
                print("Using response.parts accessor")
                print(f"Response.parts length: {len(response.parts)}")
                text_content = ""
                for i, part in enumerate(response.parts):
                    print(f"Part {i} attributes: {dir(part)}")
                    if hasattr(part, 'text'):
                        print(f"Part {i} text length: {len(part.text)}")
                        text_content += part.text
                return text_content
        except Exception as e:
            print(f"Failed to use response.parts: {str(e)}")
        
        try:
            # Use the full candidates accessor as fallback
            if (hasattr(response, 'candidates') and 
                response.candidates and 
                len(response.candidates) > 0):
                
                print(f"Number of candidates: {len(response.candidates)}")
                candidate = response.candidates[0]
                print(f"Candidate attributes: {dir(candidate)}")
                
                if hasattr(candidate, 'content'):
                    content = candidate.content
                    print(f"Content attributes: {dir(content)}")
                    
                    if hasattr(content, 'parts') and content.parts:
                        print(f"Content.parts length: {len(content.parts)}")
                        text_parts = []
                        
                        for i, part in enumerate(content.parts):
                            print(f"Content part {i} attributes: {dir(part)}")
                            print(f"Content part {i} type: {type(part)}")
                            
                            # Try different ways to access text
                            if hasattr(part, 'text') and part.text:
                                print(f"Found text in part {i}, length: {len(part.text)}")
                                text_parts.append(part.text)
                            elif hasattr(part, '_pb') and hasattr(part._pb, 'text'):
                                print(f"Found _pb.text in part {i}")
                                text_parts.append(part._pb.text)
                            else:
                                print(f"Part {i} content: {str(part)}")
                        
                        result = ''.join(text_parts)
                        print(f"Final extracted text length: {len(result)}")
                        return result
                        
        except Exception as e:
            print(f"Failed to use response.candidates: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
        
        # Final fallback - convert to string
        print("Using string conversion fallback")
        result = str(response)
        print(f"String conversion result length: {len(result)}")
        return result

    def _clean_code_response(self, response: str) -> str:
        """Clean and format the AI response to extract pure Python code."""
        # Remove markdown code blocks
        code = re.sub(r'```python\n?', '', response)
        code = re.sub(r'```\n?', '', code)
        return code.strip()

    def _validate_scene_code(self, scene_code: str) -> bool:
        """Validate the generated scene code."""
        required_elements = [
            "class GeneratedScene",
            "def construct",
            "from manim import"
        ]
        
        if not scene_code or not scene_code.strip():
            print("Empty code received")
            return False
            
        for element in required_elements:
            if element not in scene_code:
                print(f"Missing required element: {element}")
                return False
                
        return True

    async def _render_animation(self, scene_code: str, attempt: int) -> str:
        """Render the animation from the generated code."""
        # Create temporary file
        temp_file = os.path.join(self.media_dir, f"temp_scene_{attempt}.py")
        
        with open(temp_file, "w", encoding='utf-8') as f:
            f.write(scene_code)
        
        # Setup output directory
        output_dir = os.path.join(self.media_dir, "videos", f"temp_scene_{attempt}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Run Manim
        result = subprocess.run(
            [
                sys.executable, "-m", "manim",
                "-qm", "--disable_caching",
                temp_file, "GeneratedScene"
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=self.media_dir
        )
        
        print("Manim output:", result.stdout)
        
        # Find generated video
        video_file = os.path.join(output_dir, "720p30", "GeneratedScene.mp4")
        if not os.path.exists(video_file):
            raise HTTPException(
                status_code=500,
                detail="Generated video file not found"
            )
        
        return video_file

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