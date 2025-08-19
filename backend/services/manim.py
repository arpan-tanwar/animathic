import os
import re
import ast
import sys
import asyncio
import logging
import shutil
from pathlib import Path
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
        # Single Gemini model used as FALLBACK only
        self.model = None
        # Lazy imports to avoid heavy deps at module import
        try:
            from config import get_feature_flags, get_structured_backend  # noqa: F401
            from services.rag_service import RAGService  # noqa: F401
            from services.local_llm import LocalLLMService  # noqa: F401
            from services.manim_compiler import ManimCompiler  # noqa: F401
            from schemas.manim_schema import ManimScene  # noqa: F401
        except Exception:
            pass
        
        if genai:
            self._init_models()
        else:
            logger.warning("Google AI not available - API key missing or library not installed")

    def _init_models(self):
        # Gemini fallback disabled for local testing; keep code path in place but do not initialize
        self.model = None

    def _extract_response_text(self, response) -> str:
        """Extract text content from Gemini API response with multiple fallback methods"""
        try:
            # Check for truncated responses first
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    # Check if response was truncated
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason = str(candidate.finish_reason)
                        if 'MAX_TOKENS' in finish_reason:
                            logger.warning("⚠️ Response truncated due to MAX_TOKENS limit")
                            # Try to extract partial content anyway
                            if hasattr(candidate, 'content'):
                                content = candidate.content
                                if hasattr(content, 'parts') and content.parts:
                                    for part in content.parts:
                                        if hasattr(part, 'text'):
                                            text = str(part.text).strip()
                                            if text:
                                                logger.debug("✅ Extracted partial content from truncated response")
                                                return text
                    
                    # Method 1: Try candidates[0].content.parts[0].text (most common)
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
            
            code_candidate = None
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, response_str, re.IGNORECASE | re.DOTALL)
                if match:
                    code_candidate = match.group(1).strip()
                    if code_candidate and ('manim' in code_candidate or 'Scene' in code_candidate):
                        logger.debug(f"✅ Extracted using pattern {i+1}")
                        return code_candidate
            
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

    def _is_truncated_response(self, response) -> bool:
        """Check if the response was truncated due to token limits"""
        try:
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason = str(candidate.finish_reason)
                        if 'MAX_TOKENS' in finish_reason:
                            return True
            return False
        except Exception:
            return False



    def _fix_common_syntax_errors(self, code: str) -> str:
        """Fix common syntax errors in generated Manim code"""
        try:
            # Fix common indentation issues
            lines = code.split('\n')
            fixed_lines = []
            in_class = False
            in_method = False
            
            for line in lines:
                stripped = line.strip()
                
                # Skip empty lines
                if not stripped:
                    fixed_lines.append('')
                    continue
                
                # Handle class definition
                if stripped.startswith('class '):
                    in_class = True
                    in_method = False
                    fixed_lines.append(line)
                    continue
                
                # Handle method definition
                if stripped.startswith('def '):
                    in_method = True
                    fixed_lines.append('    ' + stripped)
                    continue
                
                # Handle content inside method
                if in_method and stripped and not stripped.startswith(('if ', 'for ', 'while ', 'try:', 'except:', 'finally:', 'with ')):
                    if not stripped.startswith('#'):  # Not a comment
                        fixed_lines.append('        ' + stripped)
                    else:
                        fixed_lines.append('    ' + stripped)
                    continue
                
                # Handle control structures
                if in_method and stripped.startswith(('if ', 'for ', 'while ', 'try:', 'except:', 'finally:', 'with ')):
                    fixed_lines.append('    ' + stripped)
                    continue
                
                # Handle else/elif
                if in_method and stripped.startswith(('else:', 'elif ')):
                    fixed_lines.append('    ' + stripped)
                    continue
                
                # Default case
                fixed_lines.append(line)
            
            fixed_code = '\n'.join(fixed_lines)
            
            # Fix common string issues
            fixed_code = fixed_code.replace('\\n', '\n')
            fixed_code = fixed_code.replace('\\t', '    ')
            
            # Ensure proper imports
            if 'from manim import *' not in fixed_code:
                fixed_code = 'from manim import *\n\n' + fixed_code
            
            return fixed_code
        
        except Exception as e:
            logger.warning(f"Failed to fix syntax errors: {e}")
            return code

    def _is_valid_python_content(self, content: str) -> bool:
        """Check if content contains valid Python code structure"""
        content_lower = content.lower()
        
        # Check for unwanted content types
        if any(unwanted in content_lower for unwanted in ['<html', '<svg', '<div', '```html', '```svg']):
            return False
        
        # Check for required Python keywords - be more flexible
        required_keywords = ['from manim import', 'class', 'def construct']
        if not all(keyword in content_lower for keyword in required_keywords):
            return False
        
        # Check that it's not just an explanation
        if content_lower.count('```') > 3:  # Allow more code blocks
            return False
            
        # Check for basic Python syntax
        if not ('(' in content and ')' in content and ':' in content):
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
        hint = f"\nFix: {previous_error}" if previous_error else ""
        return (
            "Generate working Python code for Manim. Return ONLY executable code.\n\n"
            "CRITICAL REQUIREMENTS:\n"
            "- from manim import *\n"
            "- class GeneratedScene(Scene):\n"
            "- def construct(self):\n"
            "- Use only: Text(), Circle(), Rectangle(), Axes(), Create(), Write(), FadeIn()\n"
            "- Use colors: RED, BLUE, GREEN, WHITE, BLACK\n"
            "- End with self.wait(2)\n"
            "- NO complex math, NO LaTeX, NO external libraries\n\n"
            f"Task: {user_prompt}{hint}\n\n"
            "Generate ONLY this structure:\n"
            "from manim import *\n\n"
            "class GeneratedScene(Scene):\n"
            "    def construct(self):\n"
            "        # Simple working code here\n"
            "        self.wait(2)"
        )
    
    def _aggressive_prompt(self, user_prompt: str, previous_error: Optional[str]) -> str:
        """More aggressive prompt for second attempt"""
        hint = f"\nFix: {previous_error}" if previous_error else ""
        return (
            "URGENT: Generate ONLY working Manim code. NO explanations.\n\n"
            "MANDATORY STRUCTURE:\n"
            "from manim import *\n\n"
            "class GeneratedScene(Scene):\n"
            "    def construct(self):\n"
            "        # Simple working animation\n"
            "        self.wait(2)\n\n"
            f"Task: {user_prompt}{hint}\n"
            "ONLY Python code, nothing else."
        )
    
    def _simple_prompt(self, user_prompt: str, previous_error: Optional[str]) -> str:
        """Simple fallback prompt for third attempt"""
        hint = f"\nFix: {previous_error}" if previous_error else ""
        return (
            f"Generate working Manim code for: {user_prompt}\n\n"
            "ONLY this exact structure:\n"
            "from manim import *\n\n"
            "class GeneratedScene(Scene):\n"
            "    def construct(self):\n"
            "        # Simple working code\n"
            "        self.wait(2)"
        )
    
    async def generate_animation(self, prompt: str, media_dir: str = './media') -> AnimationResult:
        # Structured local pipeline ONLY (Gemini fallback temporarily disabled for testing)
        try:
            res = await self._generate_via_structured_local(prompt, media_dir)
            return res
        except Exception as e:
            logger.error(f"Structured local pipeline error: {e}")
            return AnimationResult(success=False, error=str(e))

    async def _generate_via_structured_local(self, prompt: str, media_dir: str) -> Optional[AnimationResult]:
        try:
            from services.rag_service import RAGService
            from services.local_llm import LocalLLMService
            from services.manim_compiler import ManimCompiler
            from schemas.manim_schema import ManimScene

            enhanced = RAGService().enhance_prompt(prompt)
            scene: ManimScene = await LocalLLMService().generate_structured_scene(enhanced)
            code = ManimCompiler().compile_to_manim(scene)
            ast.parse(code)

            os.makedirs(media_dir, exist_ok=True)
            temp_dir = os.path.join(media_dir, 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            result = await self._render_manim_code(code, temp_dir, attempt=0)
            if result.success:
                result.code_used = code
                return result

            fixed = self._fix_common_syntax_errors(code)
            if fixed and fixed != code:
                retry = await self._render_manim_code(fixed, temp_dir, attempt=0)
                if retry.success:
                    retry.code_used = fixed
                    return retry
            return result
        except Exception as e:
            logger.error(f"Structured local generation failed: {e}")
            return AnimationResult(success=False, error=str(e))

    async def _render_manim_code(self, code: str, temp_dir: str, attempt: int) -> AnimationResult:
        scene_id = f"manim_scene_{hash(code) % 100000:08x}_attempt_{attempt}"
        temp_file = os.path.join(temp_dir, f"{scene_id}.py")
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            m = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\):', code)
            scene_name = m.group(1) if m else 'GeneratedScene'
            
            # Prefer using the project's virtualenv Python or its manim CLI
            python_exec = sys.executable

            # Resolve active or local venv
            venv_path = os.environ.get('VIRTUAL_ENV')
            backend_root = Path(__file__).resolve().parent.parent

            if venv_path:
                venv_python = Path(venv_path) / 'bin' / 'python'
                if venv_python.exists():
                    python_exec = str(venv_python)
            else:
                for candidate in [
                    backend_root / 'venv' / 'bin' / 'python3.12',
                    backend_root / 'venv' / 'bin' / 'python3',
                    backend_root / 'venv' / 'bin' / 'python',
                ]:
                    if candidate.exists():
                        python_exec = str(candidate)
                        break

            # Prefer venv CLI if present
            manim_cli_candidates = [
                Path(python_exec).parent / 'manim',
                Path(python_exec).parent / 'manimce',
            ]
            manim_cli = None
            for c in manim_cli_candidates:
                if c.exists():
                    try:
                        # Validate CLI script's interpreter exists to avoid broken shebang issues
                        with open(c, 'rb') as f:
                            first_line = f.readline().decode('utf-8', errors='ignore').strip()
                        if first_line.startswith('#!'):
                            interp = first_line[2:].strip()
                            # Some env shebangs like "/usr/bin/env python" are fine; otherwise check path exists
                            if interp.startswith('/'):  # absolute path
                                if not Path(interp).exists():
                                    continue
                        manim_cli = str(c)
                        break
                    except Exception:
                        continue

            # If still not found, try common absolute paths and PATH as extra fallback
            if manim_cli is None:
                absolute_cli_candidates = [
                    '/usr/local/bin/manim',
                    '/usr/bin/manim',
                    '/bin/manim',
                    '/usr/local/bin/manimce',
                    '/usr/bin/manimce',
                ]
                for p in absolute_cli_candidates:
                    if os.path.exists(p) and os.access(p, os.X_OK):
                        manim_cli = p
                        break
                if manim_cli is None:
                    for bin_name in ['manim', 'manimce']:
                        found = shutil.which(bin_name)
                        if found:
                            manim_cli = found
                            break

            # If no CLI, fallback to module invocation with chosen python
            if manim_cli is None:
                 logger.debug(f"Using module invocation: {python_exec} -m manim (sys.executable={sys.executable})")
                cmd = [
                    python_exec, '-m', 'manim',
                    '-q', 'm',
                    '-r', '1280,720',
                    '-v', 'WARNING',
                    '--renderer=cairo',
                    temp_file,
                    scene_name,
                    f'--media_dir={os.path.abspath(temp_dir)}/..',
                    '--disable_caching'
                ]
            else:
                logger.debug(f"Using CLI invocation: {manim_cli}")
                cmd = [
                    manim_cli,
                    '-q', 'm',
                    '-r', '1280,720',
                    '-v', 'WARNING',
                    '--renderer=cairo',
                    temp_file,
                    scene_name,
                    f'--media_dir={os.path.abspath(temp_dir)}/..',
                    '--disable_caching'
                ]

            # As absolute last resort, try global CLI if neither venv CLI nor module works
            
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
                stdout_text = (stdout or b'').decode('utf-8', errors='ignore')
                
                # Provide more detailed error information
                error_msg = f'Manim render failed: {err[:500]}'
                if stdout_text:
                    error_msg += f'\n\nStdout: {stdout_text[:200]}'
                
                logger.error(f"Manim render failed with return code {proc.returncode}")
                logger.error(f"Stderr: {err}")
                if stdout_text:
                    logger.error(f"Stdout: {stdout_text}")
                
                return AnimationResult(success=False, error=error_msg)
                
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