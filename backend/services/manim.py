import os
import re
import ast
import sys
import asyncio
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        logger.info("Google AI configured successfully")
    else:
        logger.warning("GOOGLE_AI_API_KEY not found in environment variables")
        genai = None
except Exception as e:
    logger.warning(f"Google Generative AI not available: {e}")
    genai = None

@dataclass
class AnimationResult:
    success: bool
    video_path: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    resolution: Optional[str] = None
    code_used: Optional[str] = None

class SecurityValidator:
    ALLOWED_MANIM_OBJECTS = {
        'Text', 'MathTex', 'Tex', 'Circle', 'Square', 'Rectangle', 'Triangle', 'Line', 'Arrow',
        'VGroup', 'Dot', 'Point', 'Arc', 'Polygon', 'NumberLine', 'Axes',
        'DashedVMobject', 'Scene', 'GeneratedScene',
        'Create', 'Transform', 'FadeIn', 'FadeOut', 'Write', 'DrawBorderThenFill',
        'ShowCreation', 'GrowFromCenter', 'ReplacementTransform', 'MoveToTarget',
        'Rotate', 'Scale', 'Shift', 'AnimationGroup', 'Succession',
        'RED', 'BLUE', 'GREEN', 'YELLOW', 'WHITE', 'BLACK', 'ORANGE', 'PURPLE',
        'PINK', 'GRAY', 'GREY', 'DARK_BLUE', 'LIGHT_BLUE',
        'UP', 'DOWN', 'LEFT', 'RIGHT', 'ORIGIN', 'PI', 'TAU',
        'wait', 'play', 'add', 'remove', 'construct',
        'np', 'numpy', 'array', 'linspace', 'sin', 'cos', 'tan', 'sqrt', 'abs',
        'range', 'len', 'enumerate', 'zip', 'min', 'max', 'sum', 'int', 'float',
        'list', 'dict', 'tuple', 'str', 'bool', 'type', 'isinstance', 'hasattr',
        'self', 'run_time', 'radius', 'color', 'width', 'height', 'scale', 'shift',
        'next_to', 'move_to', 'set_color', 'animate', 'stroke_width', 'fill_opacity'
    }
    DANGEROUS_PATTERNS = [
        r'\b(exec|eval|__import__|open|file)\b',
        r'\b(os\.|sys\.|subprocess\.|shutil\.)',
        r'\b(socket|urllib|http|requests)\b',
        r'__[a-zA-Z_][a-zA-Z0-9_]*__',
    ]
    
    def validate_code(self, code: str) -> bool:
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                logger.error(f"Dangerous pattern found: {pattern}")
                return False
        if 'import' in code:
            allowed = ['from manim import', 'import numpy as np', 'import manim']
            for line in code.split('\n'):
                t = line.strip()
                if t.startswith('import ') or t.startswith('from '):
                    if not any(a in t for a in allowed):
                        logger.error(f"Disallowed import: {line}")
                        return False
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if node.id not in self.ALLOWED_MANIM_OBJECTS and not node.id.startswith('_'):
                        if node.id in ['eval', 'exec', 'compile', '__import__', 'globals', 'locals', 'vars']:
                            logger.error(f"Dangerous identifier: {node.id}")
                            return False
        except SyntaxError as e:
            logger.error(f"Syntax error during validation: {e}")
            return False
        return True

class OptimizedManimService:
    def __init__(self):
        self.validator = SecurityValidator()
        self.max_attempts = 3
        self.timeout = 120
        self.model = None
        self.model_secondary = None
        
        if genai:
            self._init_models()
        else:
            logger.warning("Google AI not available - API key missing or library not installed")

    def _init_models(self):
        try:
            self.model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=20,
                    max_output_tokens=2048,
                    candidate_count=1
                )
            )
            logger.info("✅ Gemini primary model initialized (gemini-2.5-flash)")
        except Exception as e:
            logger.warning(f"Primary model init failed: {e}")
            self.model = None
            
        try:
            self.model_secondary = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config=genai.GenerationConfig(
                    temperature=0.05,
                    top_p=0.8,
                    top_k=20,
                    max_output_tokens=2048,
                    candidate_count=1
                )
            )
            logger.info("✅ Gemini secondary model initialized (gemini-2.0-flash)")
        except Exception as e:
            logger.warning(f"Secondary model init failed: {e}")
            self.model_secondary = None

    def _extract_response_text(self, response) -> str:
        """Extract text content from Gemini API response with multiple fallback methods"""
        try:
            # Method 1: Try candidates[0].content.parts[0].text (most common)
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content'):
                        content = candidate.content
                        if hasattr(content, 'parts') and content.parts:
                            for part in content.parts:
                                if hasattr(part, 'text'):
                                    text = str(part.text).strip()
                                    if text:
                                        logger.debug("✅ Extracted from candidates[].content.parts[].text")
                                        return text
                        
                        # Also try direct text access on content
                        if hasattr(content, 'text'):
                            text = str(content.text).strip()
                            if text:
                                logger.debug("✅ Extracted from candidates[].content.text")
                                return text
                        
                        # Try to access text as a property
                        try:
                            if hasattr(content, 'text'):
                                text = content.text.strip()
                                if text:
                                    logger.debug("✅ Extracted from content.text property")
                                    return text
                        except Exception:
                            pass
            
            # Method 2: Try response.parts directly
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'text'):
                        text = str(part.text).strip()
                        if text:
                            logger.debug("✅ Extracted from response.parts[].text")
                            return text
            
            # Method 3: Try response.text (simple responses)
            try:
                if hasattr(response, 'text'):
                    text = str(response.text).strip()
                    if text:
                        logger.debug("✅ Extracted from response.text")
                        return text
            except Exception:
                pass
            
            # Method 3.5: Try response.text() method call (Google Generative AI)
            try:
                if hasattr(response, 'text') and callable(getattr(response, 'text', None)):
                    text = response.text().strip()
                    if text:
                        logger.debug("✅ Extracted from response.text() method call")
                        return text
            except Exception:
                pass
            
            # Method 3.6: Try to access text as a property on the response object
            try:
                if hasattr(response, 'text'):
                    text = response.text.strip()
                    if text:
                        logger.debug("✅ Extracted from response.text property")
                        return text
            except Exception:
                pass
            
            # Method 3.7: Try to get text from the response object directly
            try:
                text = getattr(response, 'text', None)
                if text:
                    text_str = str(text).strip()
                    if text_str and text_str != str(response):
                        logger.debug("✅ Extracted from response.text direct access")
                        return text_str
            except Exception:
                pass
            
            # Method 4: Convert to string and use regex patterns
            response_str = str(response)
            logger.debug(f"🔍 Response string length: {len(response_str)}")
            logger.debug(f"🔍 Response preview: {response_str[:200]}...")
            
            # Enhanced patterns for code extraction
            patterns = [
                r"```python\s*([\s\S]*?)```",
                r"```\s*(from\s+manim[\s\S]*?)```", 
                r"(from\s+manim\s+import[\s\S]*?self\.wait\([^)]*\))",
                r"```(?:python)?\s*([\s\S]*?)```",
                r"(from\s+manim[\s\S]*?class\s+\w+\s*\(\s*Scene\s*\)[\s\S]*?def\s+construct[\s\S]*?self\.wait)",
                r"(class\s+\w+\s*\(\s*Scene\s*\)[\s\S]*?def\s+construct[\s\S]*?self\.wait)"
            ]
            
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, response_str, re.IGNORECASE | re.DOTALL)
                if match:
                    code = match.group(1).strip()
                    if code and ('manim' in code or 'Scene' in code):
                        logger.debug(f"✅ Extracted using pattern {i+1}")
                        return code
            
            # Method 5: Look for any Python code structure
            if 'from manim import' in response_str or 'class' in response_str or 'def construct' in response_str:
                logger.debug("✅ Extracted from response string (contains key keywords)")
                return response_str
            
            # Method 6: Last resort - return the full response string if it looks like code
            if any(keyword in response_str.lower() for keyword in ['import', 'class', 'def', 'self.', 'manim']):
                logger.debug("✅ Extracted from response string (contains Python keywords)")
                return response_str
            
            # Method 7: Try to extract Python code from explanations using regex
            python_code_patterns = [
                r'(from manim import[\s\S]*?class[\s\S]*?def construct[\s\S]*?self\.wait)',
                r'(class[\s\S]*?Scene[\s\S]*?def construct[\s\S]*?self\.wait)',
                r'(from manim[\s\S]*?self\.wait)',
                r'(class[\s\S]*?Scene[\s\S]*?self\.wait)'
            ]
            
            for i, pattern in enumerate(python_code_patterns):
                match = re.search(pattern, response_str, re.IGNORECASE | re.DOTALL)
                if match:
                    code = match.group(1).strip()
                    if code and len(code) > 50:  # Ensure it's substantial code
                        logger.debug(f"✅ Extracted Python code from explanation using pattern {i+1}")
                        return code
            
            # If we get here, we couldn't extract anything useful
            logger.error(f"❌ No extractable content found. Response type: {type(response)}")
            logger.error(f"❌ Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
            logger.error(f"❌ Response string preview: {response_str[:500]}...")
            
            raise ValueError("No extractable text content found in response")
            
        except Exception as e:
            logger.error(f"❌ Failed to extract response: {e}")
            logger.error(f"❌ Response type: {type(response)}")
            logger.error(f"❌ Response string: {str(response)[:500]}...")
            raise ValueError(f"Could not extract code from AI response: {e}")
    
    def _ensure_code_prereqs(self, code: str) -> str:
        lines = code.split('\n')
        out = []
        
        if not any(l.strip().startswith('from manim import') for l in lines):
            out.append('from manim import *')
            
        uses_np = any('np.' in l for l in lines)
        if uses_np and not any(l.strip().startswith('import numpy as np') for l in lines):
            out.append('import numpy as np')
            
        for l in lines:
            if l.strip() and not (l.strip().startswith('from manim import') or l.strip().startswith('import numpy as np')):
                out.append(l)
                
        code2 = '\n'.join(out)
        
        if not re.search(r'class\s+\w+\s*\(\s*Scene\s*\):', code2):
            wrap = ['from manim import *', '']
            if uses_np:
                wrap.insert(-1, 'import numpy as np')
            wrap.extend(['class GeneratedScene(Scene):', '    def construct(self):'])
            for l in out:
                if l.strip() and not l.strip().startswith(('from manim import', 'import numpy as np')):
                    wrap.append('        ' + l.lstrip())
            wrap.append('        self.wait(1)')
            return '\n'.join(wrap)
        else:
            final_lines = []
            if not any(l.strip().startswith('from manim import') for l in out):
                final_lines.append('from manim import *')
            if uses_np and not any(l.strip().startswith('import numpy as np') for l in out):
                final_lines.append('import numpy as np')
            if final_lines:
                final_lines.append('')
            final_lines.extend(out)
            return '\n'.join(final_lines)

    def _sanitize_code(self, raw: str) -> str:
        raw = re.sub(r'```python\s*', '', raw)
        raw = re.sub(r'```\s*', '', raw)
        lines = raw.split('\n')
        started = False
        collected = []
        for line in lines:
            if line.strip().startswith('from manim import'):
                started = True
            if started:
                if '\\' in line and not ('"' in line or "'" in line):
                    line = line.replace('\\', '')
                collected.append(line)
        code = '\n'.join(collected).strip() or raw.strip()
        return code

    def _is_valid_python_content(self, content: str) -> bool:
        """Check if content contains valid Python code structure, not HTML/SVG"""
        content_lower = content.lower()
        
        # Check for unwanted content types
        if any(unwanted in content_lower for unwanted in ['<html', '<svg', '<div', '```html', '```svg']):
            return False
        
        # Check for required Python keywords
        required_keywords = ['from manim import', 'class', 'def construct', 'self.']
        if not all(keyword in content_lower for keyword in required_keywords):
            return False
        
        # Check that it's not just an explanation
        if content_lower.count('```') > 2:  # Too many code blocks
            return False
            
        return True

    def _validate_syntax_thoroughly(self, code: str) -> Tuple[bool, Optional[str]]:
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"SyntaxError at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def _force_format_prompt(self, user_prompt: str, previous_error: Optional[str]) -> str:
        hint = f"\nPrevious error to fix: {previous_error}" if previous_error else ""
        return (
            "SYSTEM: You are a Python code generator for Manim animations. You MUST return ONLY Python code.\n\n"
            "CRITICAL RULES:\n"
            "1. Return ONLY Python code - no explanations, no markdown, no HTML, no SVG\n"
            "2. Start EXACTLY with: from manim import *\n"
            "3. Define: class GeneratedScene(Scene):\n"
            "4. Include: def construct(self):\n"
            "5. Use Text() instead of MathTex/Tex for safety\n"
            "6. Use Axes() for coordinate systems\n"
            "7. Use simple colors like RED, BLUE, GREEN\n"
            "8. Keep animations simple with Create(), Write(), FadeIn()\n"
            "9. End with self.wait(2)\n"
            "10. Avoid complex LaTeX, subscripts, or special formatting\n"
            "11. Use basic Python math functions (no external libraries)\n"
            "12. NO explanations, NO markdown, NO HTML, NO SVG, NO comments outside the code\n\n"
            f"TASK: {user_prompt}{hint}\n\n"
            "RESPONSE FORMAT (Python code only):\n"
            "from manim import *\n\n"
            "class GeneratedScene(Scene):\n"
            "    def construct(self):\n"
            "        title = Text('Hello World', color=BLUE)\n"
            "        self.play(Write(title))\n"
            "        self.wait(2)\n"
                )
    
    def _aggressive_prompt(self, user_prompt: str, previous_error: Optional[str]) -> str:
        """More aggressive prompt for second attempt"""
        hint = f"\nPrevious error to fix: {previous_error}" if previous_error else ""
        return (
            "URGENT: You are a Python code generator. Return ONLY Python code for Manim.\n\n"
            "MANDATORY: Return ONLY this Python code structure:\n"
            "from manim import *\n\n"
            "class GeneratedScene(Scene):\n"
            "    def construct(self):\n"
            "        # Animation code here\n"
            "        self.wait(2)\n\n"
            f"Task: {user_prompt}{hint}\n"
            "NO explanations, NO markdown, ONLY Python code."
        )
    
    def _simple_prompt(self, user_prompt: str, previous_error: Optional[str]) -> str:
        """Simple fallback prompt for third attempt"""
        hint = f"\nPrevious error to fix: {previous_error}" if previous_error else ""
        return (
            f"Write Python code for Manim to {user_prompt}. Return ONLY:\n"
            "from manim import *\n\n"
            "class GeneratedScene(Scene):\n"
            "    def construct(self):\n"
            "        # Code here\n"
            "        self.wait(2)"
        )
    
    async def generate_animation(self, prompt: str, media_dir: str = './media') -> AnimationResult:
        if not self.model and not self.model_secondary:
            return AnimationResult(success=False, error='AI model not available')
            
        os.makedirs(media_dir, exist_ok=True)
        temp_dir = os.path.join(media_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        last_error = None
        for attempt in range(self.max_attempts):
            logger.info(f"Generating animation (attempt {attempt+1}/{self.max_attempts})")
            try:
                feedback = last_error if attempt > 0 else None
                
                # Use different prompt strategies for different attempts
                if attempt == 0:
                    prompt_txt = self._force_format_prompt(prompt, feedback)
                elif attempt == 1:
                    # Second attempt: More aggressive prompt
                    prompt_txt = self._aggressive_prompt(prompt, feedback)
                else:
                    # Third attempt: Fallback to secondary model with simple prompt
                    prompt_txt = self._simple_prompt(prompt, feedback)
                
                model_to_use = self.model if attempt == 0 and self.model else (self.model_secondary or self.model)
                
                response = await asyncio.get_event_loop().run_in_executor(None, model_to_use.generate_content, prompt_txt)
                
                # Log response details for debugging
                logger.debug(f"🔍 Response type: {type(response)}")
                logger.debug(f"🔍 Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
                
                raw = self._extract_response_text(response)
                logger.debug(f"📝 Extracted raw text length: {len(raw)}")
                logger.debug(f"📝 Raw text preview: {raw[:200]}...")
                
                # Validate that we got Python code, not HTML/SVG
                if self._is_valid_python_content(raw):
                    logger.debug("✅ Content validation passed - contains Python code")
                else:
                    logger.warning("⚠️ Content validation failed - may contain HTML/SVG, retrying...")
                    last_error = "AI returned HTML/SVG instead of Python code"
                    continue
                
                code = self._ensure_code_prereqs(self._sanitize_code(raw))
                logger.debug(f"🔧 Processed code length: {len(code)}")
                logger.debug(f"🔧 Code preview: {code[:200]}...")
                
                ok, err = self._validate_syntax_thoroughly(code)
                if not ok:
                    last_error = err
                    logger.error(f"Attempt {attempt+1} failed: {err}")
                    continue
                    
                if not self.validator.validate_code(code):
                    last_error = 'Code failed security validation'
                    logger.error(f"Attempt {attempt+1} failed: security validation")
                    continue
                    
                result = await self._render_manim_code(code, temp_dir, attempt)
                if result.success:
                    result.code_used = code
                    return result
                    
                last_error = result.error
                logger.error(f"Attempt {attempt+1} failed: {result.error}")
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Attempt {attempt+1} failed with exception: {e}")
                
        return AnimationResult(success=False, error=f"Failed after {self.max_attempts} attempts: {last_error}")

    async def _render_manim_code(self, code: str, temp_dir: str, attempt: int) -> AnimationResult:
        scene_id = f"manim_scene_{hash(code) % 100000:08x}_attempt_{attempt}"
        temp_file = os.path.join(temp_dir, f"{scene_id}.py")
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            m = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\):', code)
            scene_name = m.group(1) if m else 'GeneratedScene'
            
            cmd = [
                sys.executable, '-m', 'manim',
                '-q', 'm',
                '-r', '1280,720',
                '-v', 'WARNING',
                '--renderer=cairo',
                temp_file,
            scene_name,
                f'--media_dir={os.path.abspath(temp_dir)}/..',
                '--disable_caching'
            ]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return AnimationResult(success=False, error='Rendering timeout')
                
            if proc.returncode == 0:
                media_root = os.path.abspath(os.path.join(temp_dir, '..'))
                videos_root = os.path.join(media_root, 'videos')
                latest_mp4 = None
                latest_mtime = -1
                
                if os.path.isdir(videos_root):
                    for root, _, files in os.walk(videos_root):
                        for fname in files:
                            if fname.lower().endswith('.mp4'):
                                fpath = os.path.join(root, fname)
                                try:
                                    mtime = os.path.getmtime(fpath)
                                    if mtime > latest_mtime:
                                        latest_mtime = mtime
                                        latest_mp4 = fpath
                                except Exception:
                                    continue
                                    
                if latest_mp4:
                    return AnimationResult(success=True, video_path=latest_mp4, resolution='1280x720', duration=None)
                return AnimationResult(success=False, error='Video file not found after successful render')
            else:
                err = (stderr or b'').decode('utf-8', errors='ignore')
                return AnimationResult(success=False, error=f'Manim render failed: {err[:300]}')
                
        except Exception as e:
            return AnimationResult(success=False, error=f'Rendering exception: {str(e)}')
        finally:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass

_service_instance: Optional[OptimizedManimService] = None

def get_manim_service() -> OptimizedManimService:
    global _service_instance
    if _service_instance is None:
        _service_instance = OptimizedManimService()
    return _service_instance

async def generate_video_from_prompt(prompt: str, media_dir: str = './media') -> AnimationResult:
    svc = get_manim_service()
    return await svc.generate_animation(prompt, media_dir)