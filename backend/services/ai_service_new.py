"""
AI Service for Animathic - Modular Architecture
Main service class that orchestrates all modular components
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import numpy as np
import google.generativeai as genai
try:
    # Newer SDK (google-genai) optional types; fall back if unavailable
    from google.genai import types as genai_types  # type: ignore
except Exception:  # pragma: no cover
    genai_types = None  # type: ignore
from dotenv import load_dotenv
import httpx

# Import modular components
from .prompts import ANIMATION_PROMPT_TEMPLATE, GEMINI_SYSTEM_INSTRUCTION, DEFAULT_ANIMATION_SPEC
from .manim_code_generator import ManimCodeGenerator
from .object_tracking import ObjectTrackingSystem
from .animation_analysis import AnimationSequenceAnalyzer
from .camera_management import CameraManagementSystem
from .fade_out_system import FadeOutSystem
from .enhanced_workflow_orchestrator import EnhancedWorkflowOrchestrator
from .ai_prompt_enhancement import AIPromptEnhancementSystem
from .real_time_overlap_monitoring import RealTimeOverlapMonitor

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    """Enhanced AI service with intelligent workflow orchestration"""
    
    def __init__(self, api_key: str = None):
        """Initialize the AI service with enhanced capabilities"""
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY')
        self.gemini_client = None
        self.local_model_client = None
        self.enhanced_orchestrator = EnhancedWorkflowOrchestrator()
        self.code_generator = ManimCodeGenerator()
        self.object_tracker = ObjectTrackingSystem()
        self.camera_manager = CameraManagementSystem()
        self.fade_out_manager = FadeOutSystem()
        self.prompt_enhancer = AIPromptEnhancementSystem()
        self.real_time_monitor = RealTimeOverlapMonitor()
        
        # Set prompt enhancer in workflow orchestrator
        self.enhanced_orchestrator.set_prompt_enhancer(self.prompt_enhancer)
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_gemini_model(self):
        """Initialize Gemini model with appropriate configuration"""
        try:
            if genai_types is not None:
                try:
                    return genai.GenerativeModel(
                        'gemini-2.5-flash',
                        system_instruction=GEMINI_SYSTEM_INSTRUCTION,
                        config=genai_types.GenerateContentConfig(
                            thinking_config=genai_types.ThinkingConfig(thinking_budget=0)
                        ),
                    )
                except Exception:
                    pass
            
            # Fallback to basic configuration
            return genai.GenerativeModel(
                'gemini-2.5-flash',
                system_instruction=GEMINI_SYSTEM_INSTRUCTION,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    async def generate_animation_spec(self, prompt: str) -> Dict[str, Any]:
        """Generate animation specification using Gemini with enhanced prompts"""
        try:
            logger.info(f"Generating animation spec for prompt: {prompt}")
            
            # Enhance the prompt with context-aware improvements
            enhanced_prompt = self.prompt_enhancer.enhance_ai_prompt_with_context(prompt)
            logger.info(f"Prompt enhanced from {len(prompt)} to {len(enhanced_prompt)} characters")
            logger.info(f"Original prompt: {prompt}")
            logger.info(f"Enhanced prompt: {enhanced_prompt}")
            
            # Format the enhanced prompt
            formatted_prompt = ANIMATION_PROMPT_TEMPLATE.replace("{prompt}", enhanced_prompt)
            
            # Generate response from Gemini
            response = self.gemini_client.generate_content(
                formatted_prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.2,
                    "top_p": 0.8,
                },
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            # Parse JSON response robustly
            spec = self._parse_ai_response(response.text)
            
            # Normalize the specification
            normalized = self._normalize_animation_spec(spec, prompt)
            
            logger.info("Successfully generated and normalized animation specification")
            return normalized
                    
        except Exception as e:
            logger.error(f"Error generating animation spec: {e}")
            # Try local fallback generator if configured
            fallback = await self._try_local_fallback(prompt)
            if fallback is not None:
                return fallback
            raise
    
    def _parse_ai_response(self, raw_text: str) -> Dict[str, Any]:
        """Parse AI response with fallback strategies"""
        try:
            # Try direct JSON parsing first
            return json.loads(raw_text.strip())
        except Exception:
            import re
            # Try fenced code blocks
            m = re.search(r"```(?:json)?\s*\n(\{[\s\S]*?\})\s*```", raw_text)
            if m:
                return json.loads(m.group(1))
            
            # Try to find JSON object
            m2 = re.search(r"\{[\s\S]*\}", raw_text)
            if not m2:
                raise ValueError("Invalid JSON response from AI model")
            return json.loads(m2.group())
    
    def _normalize_animation_spec(self, spec: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Normalize animation specification with minimal intervention - only fix critical issues"""
        if not isinstance(spec, dict):
            # Sometimes the model returns a top-level list; wrap it
            spec = {"objects": spec}
        
        # Provide minimal safe defaults - don't add anything the user didn't request
        normalized: Dict[str, Any] = {
            "animation_type": spec.get("animation_type", "geometric"),
            "scene_description": spec.get("scene_description", f"Animation for: {prompt}"),
            "objects": spec.get("objects") or [],
            "camera_settings": spec.get("camera_settings") or {"position": [0, 0, 0], "zoom": 8},
            "duration": spec.get("duration", 5),
            "background_color": spec.get("background_color", "#000000"),
            "style": spec.get("style", "modern"),
        }
        
        # Ensure objects is a list - minimal validation only
        if not isinstance(normalized["objects"], list):
            try:
                normalized["objects"] = list(normalized["objects"])
            except Exception:
                normalized["objects"] = []
        
        # Check if this is a typography/logo animation and apply special handling
        is_typography_animation = self._is_typography_animation(prompt, normalized["objects"])

        # Only validate critical properties, don't add anything
        if normalized["objects"]:
            validated_objects = []
            for obj in normalized["objects"]:
                if isinstance(obj, dict) and obj.get("type"):
                    # Only ensure critical properties exist, don't add defaults
                    if "properties" not in obj:
                        obj["properties"] = {}
                    if "animations" not in obj:
                        obj["animations"] = []

                    # Only set position if it's completely missing (critical for rendering)
                    if "position" not in obj["properties"]:
                        obj["properties"]["position"] = [0, 0, 0]

                    # Coerce bracketed matrix-like text into matrix object if applicable
                    obj = self._maybe_coerce_matrix_text(obj)

                    validated_objects.append(obj)

            normalized["objects"] = validated_objects

            # Merge numeric text grids (2x2) into a single matrix object
            normalized["objects"] = self._merge_numeric_text_grid_to_matrix(normalized["objects"])

            # Apply typography positioning for typography animations
            if is_typography_animation:
                normalized["objects"] = self._apply_typography_positioning_to_all(normalized["objects"])
        
        return normalized

    def _maybe_coerce_matrix_text(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """If an object is a text/tex with bracketed matrix-like content, coerce to matrix type.

        Example: text="[[1, 2],[3, 4]]" -> {'type':'matrix','properties':{'data':[['1','2'],['3','4']]}}
        Preserves 'position','color','size' and 'animations' if present.
        """
        try:
            obj_type = str(obj.get('type', '')).lower()
            props = obj.get('properties', {}) or {}
            text_value = props.get('text')
            if obj_type in ('text', 'tex', 'mathtex') and isinstance(text_value, str):
                import re
                content = text_value.strip()
                # Compact whitespace/newlines so variants like "[ [1,2],\n [3,4] ]" are accepted
                compact = re.sub(r"\s+", "", content)
                # Must look like a 2D list e.g. [[...],[...]] regardless of internal whitespace
                if compact.startswith('[[') and compact.endswith(']]') and '],[' in compact:
                    inner = compact[1:-1]  # strip outer []
                    # Split rows by '],'
                    rows_compact = inner.split('],')
                    data = []
                    for row in rows_compact:
                        row = row.strip()
                        if not row.endswith(']'):
                            row = row + ']'
                        if row.startswith('[') and row.endswith(']'):
                            row = row[1:-1]
                        items = [itm for itm in row.split(',') if itm != '']
                        data.append(items)
                    coerced = {
                        'type': 'matrix',
                        'id': obj.get('id'),
                        'properties': {
                            'data': data,
                        }
                    }
                    for key in ('position', 'color', 'size'):
                        if key in props:
                            coerced['properties'][key] = props[key]
                    if 'animations' in obj:
                        coerced['animations'] = obj['animations']
                    return coerced
        except Exception:
            # Keep original if parsing fails
            return obj
        return obj

    def _is_typography_animation(self, prompt: str, objects: List[Dict]) -> bool:
        """Detect if this is a typography/logo animation that needs special handling"""
        prompt_lower = prompt.lower()

        # Check for typography keywords
        typography_keywords = [
            'typography', 'logo', 'text morph', 'letter', 'word', 'font', 'typeface',
            'google', 'logo', 'brand', 'morph', 'transform', 'rearrange', 'evolve'
        ]

        has_typography_keywords = any(keyword in prompt_lower for keyword in typography_keywords)

        # Check if we have multiple text objects that could be letters
        text_objects = [obj for obj in objects if str(obj.get('type', '')).lower() in ['text', 'letter']]
        has_multiple_text_objects = len(text_objects) >= 3

        # Check for objects with IDs that look like individual letters
        letter_like_ids = [obj for obj in objects if obj.get('id', '').startswith(('letter_', 'char_', 'google_', 'text_'))]
        has_letter_like_objects = len(letter_like_ids) >= 3

        result = has_typography_keywords or has_multiple_text_objects or has_letter_like_objects

        return result

    def _is_typography_context(self, obj: Dict[str, Any], existing_objects: List[Dict]) -> bool:
        """Check if the current object is part of a typography animation context"""
        # Count text objects with single characters (likely letters)
        single_char_texts = 0
        total_text_objects = 0

        for existing_obj in existing_objects:
            if str(existing_obj.get('type', '')).lower() in ['text', 'letter']:
                total_text_objects += 1
                text_content = str(existing_obj.get('properties', {}).get('text', ''))
                if len(text_content) <= 2:  # Single characters or short text
                    single_char_texts += 1

        # Check current object too
        current_text = str(obj.get('properties', {}).get('text', ''))
        if str(obj.get('type', '')).lower() in ['text', 'letter']:
            total_text_objects += 1
            if len(current_text) <= 2:
                single_char_texts += 1

        # Consider it typography if we have 3+ single character text objects
        return single_char_texts >= 3

    def _apply_typography_positioning(self, obj: Dict[str, Any], existing_objects: List[Dict]) -> Dict[str, Any]:
        """Apply special positioning for typography animations to prevent overlap"""
        if str(obj.get('type', '')).lower() not in ['text', 'letter']:
            return obj

        obj_id = obj.get('id', '')
        props = obj.get('properties', {})

        # Check if this is a typography animation by looking at existing objects
        # If we have multiple text objects with single characters, apply typography positioning
        is_typography_context = self._is_typography_context(obj, existing_objects)

        # If this looks like a letter in a word (e.g., google_G, google_o, text_G, letter_H, pagerank_text)
        if is_typography_context and ('google_' in obj_id or obj_id.startswith(('letter_', 'char_', 'text_')) or
                                      'pagerank' in obj_id.lower() or len(str(props.get('text', ''))) <= 2):
            # Extract letter index from ID to space them properly
            letter_index = 0
            if 'google_' in obj_id:
                letter_part = obj_id.split('google_')[-1]
                if letter_part.isdigit():
                    letter_index = int(letter_part)
                elif len(letter_part) == 1:
                    # Map letters to indices: G=0, o=1, o=2, g=3, l=4, e=5
                    letter_map = {'g': 0, 'o': 1, 'o2': 2, 'g2': 3, 'l': 4, 'e': 5}
                    letter_index = letter_map.get(letter_part, 0)
                else:
                    # Handle cases like "o1", "o2"
                    if letter_part.startswith('o') and letter_part[1:].isdigit():
                        letter_index = int(letter_part[1:])

            elif obj_id.startswith('letter_'):
                try:
                    letter_index = int(obj_id.split('_')[-1])
                except ValueError:
                    letter_index = len(existing_objects)

            elif obj_id.startswith('text_'):
                # Handle text_ prefixed IDs like text_G, text_o1, text_o2
                text_part = obj_id.split('text_')[-1]
                if text_part.isdigit():
                    letter_index = int(text_part)
                elif len(text_part) == 1:
                    # Single letter - use existing objects count as fallback
                    letter_index = len(existing_objects)
                else:
                    # Handle cases like "o1", "o2", "L1", "L2"
                    if text_part[0].isalpha() and text_part[1:].isdigit():
                        letter_index = int(text_part[1:])
                    else:
                        letter_index = len(existing_objects)

            elif 'pagerank' in obj_id.lower():
                # Handle pagerank_text - position it first (index 0)
                letter_index = 0

            elif len(str(props.get('text', ''))) <= 2:
                # For any short text (single characters), use existing objects count
                letter_index = len(existing_objects)

            else:
                # Fallback - use existing objects count
                letter_index = len(existing_objects)

            # Space letters horizontally with proper spacing
            base_x = -3.0  # Start position for Google logo
            letter_spacing = 1.2  # Space between letters
            x_position = base_x + (letter_index * letter_spacing)
            y_position = 0  # Center vertically

            # Force override the position regardless of what's already there
            props['position'] = [x_position, y_position, 0]
            obj['properties'] = props

            logger.info(f"Applied typography positioning for {obj_id}: position [{x_position}, {y_position}, 0] (letter_index: {letter_index})")

        return obj

    def _apply_typography_positioning_to_all(self, objects: List[Dict]) -> List[Dict]:
        """Apply typography positioning to all objects in a typography animation"""
        # Filter text objects that need typography positioning
        typography_objects = []
        for obj in objects:
            if str(obj.get('type', '')).lower() in ['text', 'letter']:
                obj_id = obj.get('id', '')
                # Check if this looks like a letter in typography
                if ('google_' in obj_id or obj_id.startswith(('letter_', 'char_', 'text_')) or
                    'pagerank' in obj_id.lower() or len(str(obj.get('properties', {}).get('text', ''))) <= 2):
                    typography_objects.append(obj)

        if len(typography_objects) < 3:
            return objects  # Not enough typography objects to position

        # Apply positioning to typography objects
        for i, obj in enumerate(typography_objects):
            obj_id = obj.get('id', '')

            # Extract letter index from ID
            letter_index = self._get_letter_index_from_id(obj_id, i)

            # Space letters horizontally with proper spacing
            base_x = -3.0  # Start position for Google logo
            letter_spacing = 1.2  # Space between letters
            x_position = base_x + (letter_index * letter_spacing)
            y_position = 0  # Center vertically

            # Apply the position
            if 'properties' not in obj:
                obj['properties'] = {}
            obj['properties']['position'] = [x_position, y_position, 0]

            logger.info(f"Applied typography positioning for {obj_id}: position [{x_position}, {y_position}, 0] (letter_index: {letter_index})")

        return objects

    def _get_letter_index_from_id(self, obj_id: str, fallback_index: int) -> int:
        """Extract letter index from object ID for typography positioning"""
        if 'google_' in obj_id:
            letter_part = obj_id.split('google_')[-1]
            if letter_part.isdigit():
                return int(letter_part)
            elif len(letter_part) == 1:
                # Map letters to indices: G=0, o=1, o=2, g=3, l=4, e=5
                letter_map = {'g': 0, 'o': 1, 'o2': 2, 'g2': 3, 'l': 4, 'e': 5}
                return letter_map.get(letter_part, fallback_index)

        elif obj_id.startswith('letter_'):
            try:
                return int(obj_id.split('_')[-1])
            except ValueError:
                return fallback_index

        elif obj_id.startswith('text_'):
            # Handle text_ prefixed IDs like text_G, text_o1, text_o2
            text_part = obj_id.split('text_')[-1]
            if text_part.isdigit():
                return int(text_part)
            elif len(text_part) == 1:
                # Single letter - use existing objects count as fallback
                return fallback_index
            else:
                # Handle cases like "o1", "o2", "L1", "L2"
                if text_part[0].isalpha() and text_part[1:].isdigit():
                    return int(text_part[1:])
                else:
                    return fallback_index

        elif 'pagerank' in obj_id.lower():
            # Handle pagerank_text - position it first (index 0)
            return 0

        elif len(obj_id) <= 2:
            # For any short IDs (single characters), use fallback
            return fallback_index

        else:
            # Fallback
            return fallback_index

    def _merge_numeric_text_grid_to_matrix(self, objects: list) -> list:
        """Detect a 2x2 grid of single-number Text objects and merge into a Matrix object.

        Heuristic:
        - Find groups of 4 Text objects whose text is numeric (int/float)
        - Their positions form two distinct Xs and two distinct Ys within small tolerances
        - Build data=[[a,b],[c,d]] in row-major (top-to-bottom, left-to-right)
        - Position the Matrix at the centroid of the four numbers; preserve color/size from first item if present
        """
        try:
            from math import isclose
            import re
            num_re = re.compile(r"^[-+]?\d+(?:\.\d+)?$")

            # Collect candidate numeric texts
            candidates = []
            for idx, obj in enumerate(objects):
                if not isinstance(obj, dict):
                    continue
                if str(obj.get('type','')).lower() != 'text':
                    continue
                props = obj.get('properties', {}) or {}
                text_val = props.get('text')
                pos = props.get('position') or obj.get('position')
                if not isinstance(text_val, str) or not isinstance(pos, (list, tuple)) or len(pos) < 2:
                    continue
                if not num_re.match(text_val.strip()):
                    continue
                candidates.append({'index': idx, 'obj': obj, 'x': float(pos[0]), 'y': float(pos[1]), 'text': text_val.strip()})

            if len(candidates) < 4:
                return objects

            # Simple approach: try to find best 2x2 by bucketing x and y values with tolerances
            xs = sorted({round(c['x'], 1) for c in candidates})
            ys = sorted({round(c['y'], 1) for c in candidates}, reverse=True)  # top row first (higher y)
            # Use tolerance to merge nearby values
            def cluster(values, tol=0.25):
                clusters = []
                for v in values:
                    placed = False
                    for cl in clusters:
                        if isclose(v, cl['rep'], abs_tol=tol):
                            cl['values'].append(v)
                            cl['rep'] = sum(cl['values']) / len(cl['values'])
                            placed = True
                            break
                    if not placed:
                        clusters.append({'rep': v, 'values': [v]})
                return [cl['rep'] for cl in clusters]

            x_bins = cluster(xs)
            y_bins = cluster(ys)
            if len(x_bins) != 2 or len(y_bins) != 2:
                return objects

            x_bins = sorted(x_bins)  # left to right
            y_bins = sorted(y_bins, reverse=True)  # top to bottom

            # Assign candidates to nearest bin
            def nearest_bin(val, bins):
                return min(bins, key=lambda b: abs(val - b))

            grid = {(0,0): None, (0,1): None, (1,0): None, (1,1): None}
            assigned = []
            for c in candidates:
                xb = nearest_bin(c['x'], x_bins)
                yb = nearest_bin(c['y'], y_bins)
                xi = 0 if isclose(xb, x_bins[0], abs_tol=0.3) else 1
                yi = 0 if isclose(yb, y_bins[0], abs_tol=0.3) else 1
                key = (yi, xi)  # (row, col)
                if grid[key] is None:
                    grid[key] = c
                    assigned.append(c)

            # Ensure full 2x2 grid assigned
            if any(grid[k] is None for k in grid):
                return objects

            # Build matrix data rows: row 0 is top (higher y), row 1 is bottom
            data = [
                [grid[(0,0)]['text'], grid[(0,1)]['text']],
                [grid[(1,0)]['text'], grid[(1,1)]['text']],
            ]

            # Compute centroid position
            cx = sum(cell['x'] for cell in grid.values()) / 4.0
            cy = sum(cell['y'] for cell in grid.values()) / 4.0
            cz = 0.0

            # Use first assigned object's style if available
            first_props = assigned[0]['obj'].get('properties', {}) or {}
            color = first_props.get('color')
            size = first_props.get('size')

            matrix_obj = {
                'id': 'matrix_auto_1',
                'type': 'matrix',
                'properties': {
                    'data': data,
                    'position': [cx, cy, cz],
                },
                'animations': [{'type': 'fade_in', 'duration': 1.0, 'parameters': {}}]
            }
            if color:
                matrix_obj['properties']['color'] = color
            if size:
                matrix_obj['properties']['size'] = size

            # Remove the four numeric text elements and insert matrix instead (at end)
            remove_indices = {c['index'] for c in assigned}
            new_objects = [o for i, o in enumerate(objects) if i not in remove_indices]
            new_objects.append(matrix_obj)
            return new_objects
        except Exception:
            # On any error, return original objects unchanged
            return objects
    
    def generate_manim_code(self, animation_spec: Dict[str, Any]) -> str:
        """Convert animation specification to Manim Python code using modular generator"""
        try:
            logger.info("Converting animation spec to Manim code")
            
            # Enhance animation spec with intelligent analysis
            enhanced_spec = self._enhance_animation_spec_with_analysis(animation_spec)
            
            # Generate Manim code using the modular generator
            manim_code = self.code_generator.generate_manim_code(enhanced_spec)
            
            logger.info("Successfully generated Manim code")
            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            raise
    
    def _enhance_animation_spec_with_analysis(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Minimal enhancement - only add what's absolutely necessary for rendering"""
        try:
            # Don't enhance unless absolutely necessary
            enhanced_spec = animation_spec.copy()
            
            # Only add minimal analysis for debugging purposes
            if animation_spec.get('objects'):
                enhanced_spec['debug_info'] = {
                    'object_count': len(animation_spec['objects']),
                    'object_types': [obj.get('type', 'unknown') for obj in animation_spec['objects']]
                }
            
            # Don't add positioning suggestions, camera strategies, or transitions
            # Let the user's original specification stand as-is
            
            return enhanced_spec
            
        except Exception as e:
            logger.error(f"Error in minimal enhancement: {e}")
            return animation_spec
    
    async def process_animation_request(self, prompt: str) -> Dict[str, Any]:
        """Process animation request with intelligent workflow selection - IMPROVED VERSION"""
        try:
            logger.info(f"Processing animation request: {prompt[:100]}...")
            
            # Phase 1: Generate initial animation specification
            logger.info("Phase 1: Generating animation specification")
            initial_spec = await self._generate_animation_specification(prompt)
            if not initial_spec:
                logger.error("Failed to generate animation specification")
                return {'error': 'Failed to generate animation specification'}
            
            logger.info(f"Initial spec generated with {len(initial_spec.get('objects', []))} objects")
            
            # Phase 2: Analyze prompt complexity and choose workflow
            logger.info("Phase 2: Analyzing prompt complexity")
            prompt_complexity = self._analyze_prompt_complexity(prompt)
            
            logger.info(f"Complexity analysis: {prompt_complexity['level']} (score: {prompt_complexity['score']})")
            
            if prompt_complexity['requires_enhancement']:
                logger.info("Using enhanced workflow for complex prompt")
                try:
                    # Use enhanced workflow for complex prompts
                    enhanced_result = self.enhanced_orchestrator.process_complex_animation_request(
                        initial_spec, prompt
                    )
                    
                    if 'error' in enhanced_result:
                        logger.warning(f"Enhanced workflow failed, falling back to basic: {enhanced_result['error']}")
                        # Fall back to basic workflow
                        final_spec = self._apply_basic_workflow(initial_spec, prompt)
                        workflow_type = 'enhanced_fallback'
                    else:
                        final_spec = enhanced_result['enhanced_animation_spec']
                        workflow_type = 'enhanced'
                        logger.info(f"Enhanced workflow applied {len(enhanced_result.get('enhancements_applied', []))} enhancements")
                        
                except Exception as e:
                    logger.warning(f"Enhanced workflow failed with exception, falling back to basic: {e}")
                    final_spec = self._apply_basic_workflow(initial_spec, prompt)
                    workflow_type = 'enhanced_fallback'
            else:
                logger.info("Using restrictive workflow for simple prompt")
                # Use restrictive workflow for simple prompts
                final_spec = self._apply_basic_workflow(initial_spec, prompt)
                workflow_type = 'restrictive'
            
            # Phase 3: Validate final specification
            logger.info("Phase 3: Validating final specification")
            if not self._validate_final_spec(final_spec):
                logger.error("Final specification validation failed")
                return {'error': 'Generated specification is invalid'}
            
            # Phase 4: Generate Manim code
            logger.info("Phase 4: Generating Manim code")
            manim_code = self._generate_manim_code(final_spec)
            if not manim_code:
                logger.error("Failed to generate Manim code")
                return {'error': 'Failed to generate Manim code'}
            
            logger.info("Manim code generated successfully")
            
            # Phase 5: Validate generated code
            logger.info("Phase 5: Validating generated code")
            if not self._validate_manim_code(manim_code):
                logger.error("Generated Manim code validation failed; dumping code snippet and spec for diagnosis")
                try:
                    snippet = (manim_code or "").splitlines()
                    snippet = "\n".join(snippet[:100])  # limit log size
                    logger.error("Invalid Manim code (first 100 lines):\n" + snippet)
                except Exception:
                    pass
                return {
                    'error': 'Generated Manim code is invalid',
                    'manim_code': manim_code,
                    'animation_spec': final_spec,
                }
            
            logger.info("All phases completed successfully")
            
            return {
                'animation_spec': final_spec,
                'manim_code': manim_code,
                'workflow_type': workflow_type,
                'complexity_analysis': prompt_complexity,
                'enhancements_applied': enhanced_result.get('enhancements_applied', []) if workflow_type == 'enhanced' else []
            }
            
        except Exception as e:
            logger.error(f"Error in animation request processing: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {'error': f'Animation processing failed: {str(e)}'}
    
    def _analyze_prompt_complexity(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt complexity to determine workflow selection - IMPROVED VERSION"""
        prompt_lower = prompt.lower()
        
        # Comprehensive complexity indicators with weighted scoring
        complexity_indicators = {
            # Mathematical content (high weight)
            'mathematical_functions': any(keyword in prompt_lower for keyword in
                ['sine', 'cosine', 'tangent', 'exponential', 'logarithmic', 'polynomial', 'parabola', 'hyperbola', 'function', 'plot', 'graph', 'equation', 'formula', 'calculus', 'derivative', 'integral']),
            'parametric_equations': any(keyword in prompt_lower for keyword in
                ['parametric', 'surface', '3d', 'three dimensional', 'rotation', 'spinning']),
            'matrices_vectors': any(keyword in prompt_lower for keyword in
                ['matrix', 'vector', 'linear algebra', 'transformation', 'eigenvalue']),

            # Animation complexity
            'multiple_objects': any(keyword in prompt_lower for keyword in
                ['multiple', 'several', 'many', 'various', 'both', 'and', 'with', 'together', 'group', 'collection', 'set of']),
            'complex_sequences': any(keyword in prompt_lower for keyword in
                ['sequence', 'step by step', 'progression', 'evolution', 'transition', 'morphing', 'transforming', 'then', 'next', 'after', 'before', 'first', 'second', 'third', 'finally']),
            'interaction_effects': any(keyword in prompt_lower for keyword in
                ['interact', 'connect', 'relate', 'combine', 'collide', 'bounce', 'between', 'among', 'link', 'join', 'merge', 'split']),

            # Visual complexity
            'color_schemes': any(keyword in prompt_lower for keyword in
                ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'cyan', 'magenta', 'rainbow', 'gradient', 'colorful', 'multicolor']),
            'text_typography': any(keyword in prompt_lower for keyword in
                ['text', 'letter', 'word', 'typography', 'font', 'write', 'type', 'label', 'annotation', 'caption']),
            'spatial_relationships': any(keyword in prompt_lower for keyword in
                ['above', 'below', 'left', 'right', 'near', 'far', 'inside', 'outside', 'around', 'through', 'along', 'position', 'location', 'place']),

            # Temporal aspects
            'timing_requirements': any(keyword in prompt_lower for keyword in
                ['slow', 'fast', 'quick', 'gradual', 'sudden', 'smooth', 'jerky', 'duration', 'seconds', 'minutes', 'timing', 'pace', 'rhythm']),
            'path_based_motion': any(keyword in prompt_lower for keyword in
                ['path', 'trajectory', 'orbit', 'circle around', 'follow', 'trace', 'curve', 'wave', 'oscillate']),

            # Advanced features
            'three_dimensional': any(keyword in prompt_lower for keyword in
                ['3d', 'three dimensional', 'depth', 'perspective', 'rotate', 'spin', 'cube', 'sphere', 'surface']),
            'particle_systems': any(keyword in prompt_lower for keyword in
                ['particle', 'particles', 'system', 'many objects', 'swarm', 'cloud', 'field']),
            'advanced_animations': any(keyword in prompt_lower for keyword in
                ['fade', 'appear', 'disappear', 'animate', 'transition', 'effect', 'morph', 'transform', 'grow', 'shrink', 'bounce', 'elastic', 'spring'])
        }
        
        # Calculate weighted complexity score
        weights = {
            'mathematical_functions': 3,
            'parametric_equations': 4,
            'matrices_vectors': 3,
            'multiple_objects': 2,
            'complex_sequences': 2,
            'interaction_effects': 3,
            'color_schemes': 1,
            'text_typography': 2,
            'spatial_relationships': 1,
            'timing_requirements': 1,
            'path_based_motion': 2,
            'three_dimensional': 4,
            'particle_systems': 3,
            'advanced_animations': 2
        }

        weighted_score = sum(weights[indicator] for indicator, present in complexity_indicators.items() if present)

        # Determine complexity level with refined thresholds
        if weighted_score <= 5:
            complexity_level = 'simple'
        elif weighted_score <= 12:
            complexity_level = 'moderate'
        elif weighted_score <= 20:
            complexity_level = 'complex'
        else:
            complexity_level = 'very_complex'

        # Enhanced workflow recommendation logic
        requires_enhancement = (
            weighted_score >= 10 or  # High complexity threshold
            complexity_indicators['parametric_equations'] or  # Always enhance 3D/parametric
            complexity_indicators['three_dimensional'] or  # Always enhance 3D content
            (complexity_indicators['mathematical_functions'] and complexity_indicators['multiple_objects']) or  # Math + multiple objects
            (complexity_indicators['complex_sequences'] and complexity_indicators['interaction_effects']) or  # Complex interactions
            complexity_indicators['particle_systems']  # Particle systems always need enhancement
        )

        # Determine scene type recommendation
        scene_type = 'Scene'  # default
        if complexity_indicators['three_dimensional']:
            scene_type = 'ThreeDScene'
        elif complexity_indicators['mathematical_functions'] and not complexity_indicators['parametric_equations']:
            scene_type = 'GraphScene'

        logger.info(f"Comprehensive complexity analysis: score={weighted_score}, level={complexity_level}, enhance={requires_enhancement}, scene_type={scene_type}")

        return {
            'level': complexity_level,
            'score': weighted_score,
            'indicators': complexity_indicators,
            'requires_enhancement': requires_enhancement,
            'workflow_recommendation': 'enhanced' if requires_enhancement else 'restrictive',
            'scene_type_recommendation': scene_type,
            'estimated_duration': self._estimate_animation_duration(weighted_score, complexity_indicators),
            'recommended_quality': 'high' if weighted_score > 15 else 'medium' if weighted_score > 8 else 'low'
        }

    def _estimate_animation_duration(self, score: int, indicators: Dict[str, bool]) -> float:
        """Estimate optimal animation duration based on complexity"""
        base_duration = 5.0

        # Add time for complex features
        if indicators['mathematical_functions']:
            base_duration += 3.0
        if indicators['parametric_equations']:
            base_duration += 4.0
        if indicators['complex_sequences']:
            base_duration += 2.0
        if indicators['three_dimensional']:
            base_duration += 3.0
        if indicators['particle_systems']:
            base_duration += 2.0

        # Adjust based on overall complexity
        if score > 20:
            base_duration *= 1.5
        elif score > 15:
            base_duration *= 1.3
        elif score < 5:
            base_duration *= 0.8

        return max(3.0, min(base_duration, 15.0))  # Clamp between 3-15 seconds
    
    def _apply_basic_workflow(self, animation_spec: Dict[str, Any], prompt: str = "") -> Dict[str, Any]:
        """Apply basic restrictive workflow (minimal intervention) - IMPROVED VERSION"""
        try:
            logger.info("Applying basic workflow with minimal intervention")
            
            # Apply minimal normalization
            normalized_spec = self._normalize_animation_spec(animation_spec, prompt)
            
            # For basic workflow, keep it simple - no complex enhancements
            # Only ensure the spec is valid for Manim rendering
            validated_spec = self._validate_basic_spec(normalized_spec)
            
            logger.info("Basic workflow completed successfully")
            return validated_spec
            
        except Exception as e:
            logger.error(f"Error in basic workflow: {e}")
            # Return the original spec if validation fails
            return animation_spec
    
    def _validate_basic_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate basic animation spec for Manim compatibility"""
        try:
            validated = spec.copy()
            
            # Ensure basic structure
            if 'objects' not in validated:
                validated['objects'] = []
            
            # Validate each object
            valid_objects = []
            for obj in validated['objects']:
                if isinstance(obj, dict) and obj.get('type'):
                    # Ensure basic properties exist
                    if 'properties' not in obj:
                        obj['properties'] = {}
                    
                    # Set safe defaults for critical properties
                    props = obj['properties']
                    if 'position' not in props:
                        props['position'] = [0, 0, 0]
                    if 'size' not in props and obj['type'] in ['circle', 'square']:
                        props['size'] = 1.0
                    if 'color' not in props:
                        props['color'] = 'WHITE'
                    
                    # Ensure animations array exists
                    if 'animations' not in obj:
                        obj['animations'] = []
                    
                    # Validate animations
                    valid_animations = []
                    for anim in obj['animations']:
                        if isinstance(anim, dict) and anim.get('type'):
                            # Ensure animation has required properties
                            if 'duration' not in anim:
                                anim['duration'] = 1.0
                            if 'parameters' not in anim:
                                anim['parameters'] = {}
                            valid_animations.append(anim)
                    
                    obj['animations'] = valid_animations
                    valid_objects.append(obj)
            
            validated['objects'] = valid_objects
            
            # Ensure camera settings are valid
            if 'camera_settings' not in validated:
                validated['camera_settings'] = {"position": [0, 0, 0], "zoom": 8}
            
            # Ensure duration is reasonable
            if 'duration' not in validated or not isinstance(validated['duration'], (int, float)):
                validated['duration'] = 5.0
            
            # Ensure background color is valid
            if 'background_color' not in validated:
                validated['background_color'] = "#000000"
            
            logger.info(f"Basic spec validation completed: {len(valid_objects)} valid objects")
            return validated
            
        except Exception as e:
            logger.error(f"Error in basic spec validation: {e}")
            return spec
    
    async def _try_local_fallback(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Attempt to generate a spec using a local inference service if available."""
        local_url = os.getenv("LOCAL_INFERENCE_URL")
        if not local_url:
            return None
        
        try:
            timeout = httpx.Timeout(20.0, connect=5.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(local_url, json={"prompt": prompt})
                if resp.status_code != 200:
                    logger.error(f"Local fallback returned {resp.status_code}")
                    return None
                
                data = resp.json()
                spec = data.get("animation_spec") or data
                if not isinstance(spec, dict):
                    return None
                
                # Normalize like primary path
                return self._normalize_animation_spec(spec, prompt)
                
        except Exception as ex:
            logger.error(f"Local fallback error: {ex}")
            return None
    
    # Utility methods for external access to modular components
    def get_object_tracking_status(self) -> Dict[str, Any]:
        """Get current status of the object tracking system"""
        return self.object_tracker.get_tracking_status()
    
    def get_camera_management_status(self) -> Dict[str, Any]:
        """Get current status of the camera management system"""
        return self.camera_manager.get_camera_management_status(self.object_tracker.object_registry)
    
    def get_fade_out_system_status(self) -> Dict[str, Any]:
        """Get current status of the fade-out system"""
        return self.fade_out_manager.get_fade_out_system_status(self.object_tracker.object_registry)
    
    def get_prompt_enhancement_status(self) -> Dict[str, Any]:
        """Get current status of the prompt enhancement system"""
        return {
            'system_active': True,
            'enhancement_config': self.prompt_enhancer.enhancement_config,
            'enhancement_templates_available': list(self.prompt_enhancer.enhancement_templates.keys()),
            'performance_guidance_levels': list(self.prompt_enhancer.performance_guidance.keys())
        }
    
    def get_real_time_overlap_monitoring_status(self) -> Dict[str, Any]:
        """Get current status of the real-time overlap monitoring system"""
        return {
            'system_active': True,
            'monitoring_status': self.real_time_monitor.get_monitoring_status(),
            'overlap_summary': self.real_time_monitor.get_overlap_summary(),
            'config': {
                'check_interval': self.real_time_monitor.config.check_interval,
                'overlap_threshold': self.real_time_monitor.config.overlap_threshold,
                'auto_correct': self.real_time_monitor.config.auto_correct,
                'max_concurrent_correction': self.real_time_monitor.config.max_concurrent_corrections
            }
        }
    
    def debug_object_state(self, obj_id: str) -> Dict[str, Any]:
        """Debug information for a specific object"""
        return self.object_tracker.debug_object_state(obj_id)
    
    def clear_tracking_data(self) -> Dict[str, Any]:
        """Clear all tracking data (useful for testing)"""
        return self.object_tracker.clear_tracking_data()

    def activate(self):
        """Activate the AI service - compatibility function"""
        try:
            # Initialize or re-initialize all subsystems
            self.object_tracker.init_object_registry()
            
            return {
                'status': 'activated',
                'subsystems': {
                    'object_tracker': 'ready',
                    'animation_analyzer': 'ready', 
                    'camera_manager': 'ready',
                    'fade_out_manager': 'ready',
                    'code_generator': 'ready'
                },
                'model_status': 'ready' if self.gemini_client else 'error'
            }
        except Exception as e:
            logger.error(f"Error in activate: {e}")
            return {'status': 'error', 'message': str(e)}

    def _initialize_clients(self):
        """Initialize AI model clients"""
        try:
            # Initialize Gemini client
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.gemini_client = self._initialize_gemini_model()
                logger.info("Gemini client initialized successfully")
            else:
                logger.warning("No Google API key found, Gemini client not initialized")
                raise RuntimeError("GOOGLE_AI_API_KEY is required for AI service")
            
            # Initialize local model client (placeholder for future implementation)
            self.local_model_client = None
            logger.info("AI service clients initialized")
            
        except Exception as e:
            logger.error(f"Error initializing AI clients: {e}")
            raise RuntimeError(f"Failed to initialize AI service: {e}")
    
    async def _generate_animation_specification(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate animation specification using available AI models"""
        try:
            # Try Gemini first
            if self.gemini_client:
                try:
                    return await self._generate_with_gemini(prompt)
                except Exception as e:
                    logger.warning(f"Gemini generation failed: {e}")
            
            # Try local model fallback
            if self.local_model_client:
                try:
                    return await self._generate_with_local_model(prompt)
                except Exception as e:
                    logger.warning(f"Local model generation failed: {e}")
            
            # Final fallback - smart specification based on prompt content
            logger.warning("Using smart fallback specification")
            return self._generate_smart_fallback_specification(prompt)
            
        except Exception as e:
            logger.error(f"Error generating animation specification: {e}")
            return None
    
    async def _generate_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Generate animation specification using Gemini"""
        try:
            # Use the existing Gemini generation logic
            return await self.generate_animation_spec(prompt)
        except Exception as e:
            logger.error(f"Error in Gemini generation: {e}")
            raise
    
    async def _generate_with_local_model(self, prompt: str) -> Dict[str, Any]:
        """Generate animation specification using local model"""
        # Placeholder for local model implementation
        raise NotImplementedError("Local model generation not yet implemented")
    
    def _generate_smart_fallback_specification(self, prompt: str) -> Dict[str, Any]:
        """Generate smart animation specification based on prompt content with enhanced prompts"""
        # Enhance the prompt for better fallback generation
        enhanced_prompt = self.prompt_enhancer.enhance_ai_prompt_with_context(prompt)
        prompt_lower = enhanced_prompt.lower()
        objects = []
        object_id_counter = 1
        
        # Detect if this is a complex mathematical prompt
        if any(keyword in prompt_lower for keyword in ['function', 'plot', 'sine', 'cosine', 'tangent', 'exponential']):
            logger.info("Detected mathematical prompt - generating function plots")
            
            # Add coordinate axes
            objects.append({
                'id': 'axes_1',
                'type': 'axes',
                'properties': {
                    'position': [0, 0, 0],
                    'color': 'WHITE',
                    'x_range': [-4, 4, 1],
                    'y_range': [-3, 3, 1],
                    'show_labels': True
                },
                'animations': [{
                    'type': 'fade_in',
                    'duration': 0.8,
                    'start_time': 'immediate'
                }]
            })
            
            # Add function plots based on what's mentioned
            function_keywords = {
                'sine': {'function': 'sine', 'color': 'YELLOW'},
                'cosine': {'function': 'cosine', 'color': 'BLUE'},
                'tangent': {'function': 'tangent', 'color': 'GREEN'},
                'exponential': {'function': 'exponential', 'color': 'RED'}
            }
            
            for func_name, func_props in function_keywords.items():
                if func_name in prompt_lower:
                    object_id_counter += 1
                    objects.append({
                        'id': f'plot_{func_name}',
                        'type': 'plot',
                        'properties': {
                            'position': [0, 0, 0],
                            'color': func_props['color'],
                            'function': func_props['function'],
                            'x_range_plot': [-4, 4]
                        },
                        'animations': [{
                            'type': 'fade_in',
                            'duration': 0.5,
                            'start_time': 'after_persistent_display'
                        }]
                    })
            
            # Add geometric shapes if mentioned
            shape_keywords = {
                'circle': {'type': 'circle', 'color': 'RED', 'position': [2, 1, 0]},
                'square': {'type': 'square', 'color': 'BLUE', 'position': [-2, 1, 0]},
                'triangle': {'type': 'triangle', 'color': 'GREEN', 'position': [0, 2, 0]},
                'diamond': {'type': 'diamond', 'color': 'PURPLE', 'position': [1, -1, 0]}
            }
            
            for shape_name, shape_props in shape_keywords.items():
                if shape_name in prompt_lower or 'geometric' in prompt_lower or 'shape' in prompt_lower:
                    object_id_counter += 1
                    objects.append({
                        'id': f'{shape_name}_{object_id_counter}',
                        'type': shape_props['type'],
                        'properties': {
                            'position': shape_props['position'],
                            'color': shape_props['color'],
                            'size': 0.5
                        },
                        'animations': [{
                            'type': 'fade_in',
                            'duration': 0.5,
                            'start_time': 'after_previous_transient_fade'
                        }]
                    })
            
            # Add text annotations if mentioned
            if any(keyword in prompt_lower for keyword in ['text', 'annotation', 'label']):
                annotations = ['A', 'B', 'C', 'f(x)', 'g(x)']
                positions = [[2.5, 1.5, 0], [-2.5, 1.5, 0], [0.5, 2.5, 0], [3, -1, 0], [-3, -1, 0]]
                
                for i, (annotation, pos) in enumerate(zip(annotations[:3], positions[:3])):
                    object_id_counter += 1
                    objects.append({
                        'id': f'text_{object_id_counter}',
                        'type': 'text',
                        'properties': {
                            'text': annotation,
                            'position': pos,
                            'color': 'WHITE',
                            'size': 0.6
                        },
                        'animations': [{
                            'type': 'fade_in',
                            'duration': 0.4,
                            'start_time': 'after_previous_transient_fade'
                        }]
                    })
            
        else:
            # Basic fallback for non-mathematical prompts
            objects.append({
                'id': 'text_1',
                'type': 'text',
                'properties': {
                    'text': prompt[:50] + '...' if len(prompt) > 50 else prompt,
                    'color': 'WHITE',
                    'size': 0.8,
                    'position': [0, 0, 0]
                },
                'animations': [{
                    'type': 'fade_in',
                    'duration': 1.0,
                    'start_time': 'immediate'
                }]
            })
        
        return {
            'animation_type': 'mathematical' if 'function' in prompt_lower else 'geometric',
            'scene_description': f"Smart fallback animation for: {prompt[:100]}...",
            'objects': objects,
            'camera_settings': {'position': [0, 0, 0], 'zoom': 8},
            'duration': 8.0 if len(objects) > 3 else 5.0,
            'background_color': '#000000',
            'style': 'modern'
        }
    
    def _generate_manim_code(self, animation_spec: Dict[str, Any]) -> Optional[str]:
        """Generate Manim code from animation specification"""
        try:
            # Use the enhanced code generator (supports move and move_along_path)
            return self.code_generator.generate_manim_code(animation_spec)
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            return None

    def _validate_final_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate final animation specification"""
        try:
            # Basic structure validation
            if not isinstance(spec, dict):
                logger.error("Spec is not a dictionary")
                return False
            
            if 'objects' not in spec:
                logger.error("Spec missing objects array")
                return False
            
            if not isinstance(spec['objects'], list):
                logger.error("Objects is not a list")
                return False
            
            # Object validation
            for i, obj in enumerate(spec['objects']):
                if not isinstance(obj, dict):
                    logger.error(f"Object {i} is not a dictionary")
                    return False
                
                if 'type' not in obj:
                    logger.error(f"Object {i} missing type")
                    return False
                
                if 'properties' not in obj:
                    logger.error(f"Object {i} missing properties")
                    return False
            
            logger.info("Final spec validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error in final spec validation: {e}")
            return False
    
    def _validate_manim_code(self, code: str) -> bool:
        """Validate generated Manim code"""
        try:
            # Basic syntax validation
            if not code or not isinstance(code, str):
                logger.error("Code is empty or not a string")
                return False
            
            # Check for required components
            required_components = [
                'from manim import',
                'class GeneratedScene',
                'def construct(self)'
            ]
            
            for component in required_components:
                if component not in code:
                    logger.error(f"Missing required component: {component}")
                    return False
            
            # Check for dangerous patterns
            dangerous_patterns = [
                'eval(', 'exec(', '__import__(', 'open(', 'file('
            ]
            
            for pattern in dangerous_patterns:
                if pattern in code:
                    # More intelligent detection - check if it's in a string literal or comment
                    lines = code.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line:
                            # Skip if it's a comment
                            stripped_line = line.strip()
                            if stripped_line.startswith('#'):
                                continue
                            
                            # Skip if it's in a string literal
                            if f"'{pattern}" in line or f'"{pattern}' in line:
                                continue
                            
                            # This is an actual dangerous pattern
                            logger.error(f"Dangerous pattern found on line {i+1}: {line.strip()}")
                            return False
            
            logger.info("Manim code validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error in Manim code validation: {e}")
            return False


# Singleton instance management
_ai_service_singleton: Optional[AIService] = None

def get_ai_service() -> AIService:
    """Get or create the AI service singleton instance"""
    global _ai_service_singleton
    if _ai_service_singleton is None:
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_AI_API_KEY is not set")
        _ai_service_singleton = AIService(api_key=api_key)
    return _ai_service_singleton
