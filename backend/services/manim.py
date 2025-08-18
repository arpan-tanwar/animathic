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
        try:
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content'):
                        content = candidate.content
                        if hasattr(content, 'parts') and content.parts:
                            for part in content.parts:
                                if hasattr(part, 'text'):
                                    text = str(part.text).strip()
                                    if text:
                                        return text
            
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'text'):
                        text = str(part.text).strip()
                        if text:
                            return text
            
            try:
                if hasattr(response, 'text'):
                    text = str(response.text).strip()
                    if text:
                        return text
            except Exception:
                pass
            
            response_str = str(response)
            patterns = [
                r"```python\s*([\s\S]*?)```",
                r"```\s*(from\s+manim[\s\S]*?)```", 
                r"(from\s+manim\s+import[\s\S]*?self\.wait\([^)]*\))",
                r"```(?:python)?\s*([\s\S]*?)```"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response_str, re.IGNORECASE | re.DOTALL)
                if match:
                    code = match.group(1).strip()
                    if code and 'manim' in code:
                        return code
            
            if 'from manim import' in response_str:
                return response_str
            
            raise ValueError("No extractable text content found in response")
            
        except Exception as e:
            logger.error(f"Failed to extract response: {e}")
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
            "Return ONLY valid Python code for Manim 0.19. No explanations, no markdown formatting.\n\n"
            "REQUIREMENTS:\n"
            "- Start exactly with: from manim import *\n"
            "- Define: class GeneratedScene(Scene):\n"
            "- Include: def construct(self):\n"
            "- Use Text() instead of MathTex/Tex for safety\n"
            "- Use Axes() for coordinate systems\n"
            "- Use simple colors like RED, BLUE, GREEN\n"
            "- Keep animations simple with Create(), Write(), FadeIn()\n"
            "- End with self.wait(2)\n"
            "- Avoid complex LaTeX, subscripts, or special formatting\n"
            "- Use basic Python math functions (no external libraries)\n\n"
            f"Task: {user_prompt}{hint}\n\n"
            "Example format:\n"
            "from manim import *\n\n"
            "class GeneratedScene(Scene):\n"
            "    def construct(self):\n"
            "        # Your animation code here\n"
            "        self.wait(2)\n"
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
                prompt_txt = self._force_format_prompt(prompt, feedback)
                model_to_use = self.model if attempt == 0 and self.model else (self.model_secondary or self.model)
                
                response = await asyncio.get_event_loop().run_in_executor(None, model_to_use.generate_content, prompt_txt)
                raw = self._extract_response_text(response)
                code = self._ensure_code_prereqs(self._sanitize_code(raw))
                
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