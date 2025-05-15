import os
from manim import Scene, config
from fastapi import HTTPException
import subprocess
from typing import Optional, Tuple
import sys
import google.generativeai as genai
import re

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
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def generate_video(self, prompt: str) -> str:
        """
        Generate a video using Manim based on the prompt.
        
        Args:
            prompt: The prompt describing the animation to generate
            
        Returns:
            Path to the generated video file
        """
        temp_file = None
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Generate the animation code
                gemini_prompt = f"""You are a Manim expert. Create a Manim animation for this prompt: {prompt}

                Analyze the prompt carefully and create an animation that EXACTLY matches the user's intent.
                Do not add any extra animations, color changes, or movements unless specifically requested.
                Keep the animation simple, clear, and focused on what the user asked for.
                
                Return the COMPLETE Python code including all necessary imports.
                The code must include a class named 'GeneratedScene' that inherits from Scene.
                The class must have a 'construct' method with animations using self.play() and self.wait().
                Do not include any explanations or markdown, just the Python code.

                Here are some examples of different animations:

                Example 1 - Transform circle to square (exactly as requested):
                from manim import *
                class GeneratedScene(Scene):
                    def construct(self):
                        circle = Circle(radius=2, color=BLUE)
                        self.play(Create(circle))
                        self.wait(1)
                        square = Square(side_length=3, color=RED)
                        self.play(Transform(circle, square))
                        self.wait(1)

                Example 2 - Rotate triangle (exactly as requested):
                from manim import *
                class GeneratedScene(Scene):
                    def construct(self):
                        triangle = Triangle(color=GREEN)
                        self.play(Create(triangle))
                        self.wait(1)
                        self.play(Rotate(triangle, angle=PI))
                        self.wait(1)

                Example 3 - Scale and move rectangle (exactly as requested):
                from manim import *
                class GeneratedScene(Scene):
                    def construct(self):
                        rect = Rectangle(height=2, width=4, color=YELLOW)
                        self.play(Create(rect))
                        self.wait(1)
                        self.play(rect.animate.scale(1.5).shift(RIGHT * 2))
                        self.wait(1)
                """
                
                # If this is a retry, include the previous error
                if last_error:
                    gemini_prompt += f"\n\nPrevious error: {last_error}\nPlease fix this error in your code."
                
                print(f"Generating animation code (attempt {retry_count + 1})")
                print(f"Using prompt: {gemini_prompt}")
                
                # Configure the model for better code generation
                generation_config = {
                    "temperature": 0.3,  # Lower temperature for more focused output
                    "top_p": 0.9,  # Higher top_p for more diverse output
                    "top_k": 50,  # Higher top_k for more diverse token selection
                    "max_output_tokens": 2048,  # Ensure we get enough tokens for the code
                }
                
                # Generate the code
                response = self.model.generate_content(
                    gemini_prompt,
                    generation_config=generation_config
                )
                
                print(f"Raw AI response: {response}")
                
                # Extract code from response
                if hasattr(response, 'text'):
                    scene_code = response.text
                    print(f"Response has text attribute: {scene_code}")
                else:
                    scene_code = str(response)
                    print(f"Response converted to string: {scene_code}")
                
                # Clean up the code - preserve newlines and indentation
                scene_code = re.sub(r'```python\n?', '', scene_code)
                scene_code = re.sub(r'```\n?', '', scene_code)
                scene_code = scene_code.strip()
                
                print(f"Cleaned scene code: {scene_code}")
                
                # Validate the code
                if not scene_code or not scene_code.strip():
                    print("Empty code received")
                    retry_count += 1
                    continue
                    
                if "class GeneratedScene" not in scene_code:
                    print("Missing GeneratedScene class")
                    retry_count += 1
                    continue
                    
                if "def construct" not in scene_code:
                    print("Missing construct method")
                    retry_count += 1
                    continue
                    
                if "from manim import" not in scene_code:
                    print("Missing Manim imports")
                    retry_count += 1
                    continue
                
                # Create a temporary Python file with the Manim code
                temp_file = os.path.join(self.media_dir, f"temp_scene_{retry_count}.py")
                
                # Write the code directly to file
                print(f"Writing code to file: {scene_code}")
                with open(temp_file, "w") as f:
                    f.write(scene_code)
                
                # Run Manim
                output_dir = os.path.join(self.media_dir, "videos", f"temp_scene_{retry_count}")
                os.makedirs(output_dir, exist_ok=True)
                
                # Run Manim with optimized settings
                try:
                    # First, verify Python path
                    python_path = sys.executable
                    print(f"Using Python at: {python_path}")
                    
                    # Run Manim with optimized settings
                    result = subprocess.run(
                        [
                            python_path, "-m", "manim",
                            "-qm",  # Medium quality
                            "--disable_caching",  # Disable caching
                            temp_file,
                            "GeneratedScene"
                        ],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print("Manim output:", result.stdout)
                    
                    # Find the generated video file
                    video_file = os.path.join(output_dir, "720p30", "GeneratedScene.mp4")
                    if not os.path.exists(video_file):
                        raise HTTPException(
                            status_code=500,
                            detail="Video file not found after generation"
                        )
                    
                    return video_file
                    
                except subprocess.CalledProcessError as e:
                    print(f"Manim command failed with error: {e.stderr}")
                    print(f"Command output: {e.stdout}")
                    last_error = e.stderr
                    retry_count += 1
                    continue
                
            except Exception as e:
                print(f"Error in generate_video: {str(e)}")
                last_error = str(e)
                retry_count += 1
                continue
            finally:
                # Clean up temporary files
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate valid video after {max_retries} attempts. Last error: {last_error}"
        )

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