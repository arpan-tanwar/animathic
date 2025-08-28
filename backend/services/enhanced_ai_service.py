"""
Enhanced AI Service for Animathic with Manim API Documentation Integration
Provides intelligent animation generation with comprehensive Manim knowledge
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional, List
import google.generativeai as genai
try:
    from google.genai import types as genai_types
except Exception:
    genai_types = None

from dotenv import load_dotenv
import httpx

# Import modular components
from .prompts import ANIMATION_PROMPT_TEMPLATE, GEMINI_SYSTEM_INSTRUCTION, DEFAULT_ANIMATION_SPEC
from .manim_code_generator import ManimCodeGenerator
from .manim_api_docs import ManimAPIDocumentationSystem, ManimDocResult
from .enhanced_workflow_orchestrator import EnhancedWorkflowOrchestrator
from .ai_prompt_enhancement import AIPromptEnhancementSystem

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedAIService:
    """Enhanced AI service with Manim API documentation integration"""
    
    def __init__(self, api_key: str = None):
        """Initialize the enhanced AI service"""
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY')
        self.gemini_client = None
        self.manim_docs = ManimAPIDocumentationSystem()
        self.enhanced_orchestrator = EnhancedWorkflowOrchestrator()
        self.code_generator = ManimCodeGenerator()
        self.prompt_enhancer = AIPromptEnhancementSystem()
        
        # Set prompt enhancer in workflow orchestrator
        self.enhanced_orchestrator.set_prompt_enhancer(self.prompt_enhancer)
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI clients"""
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.gemini_client = self._initialize_gemini_model()
                logger.info("Gemini client initialized successfully")
            else:
                logger.warning("No Google AI API key provided")
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
    
    def _initialize_gemini_model(self):
        """Initialize Gemini model with enhanced configuration"""
        try:
            if genai_types is not None:
                try:
                    return genai.GenerativeModel(
                        'gemini-2.5-flash',
                        system_instruction=self._get_enhanced_system_instruction(),
                        config=genai_types.GenerateContentConfig(
                            thinking_config=genai_types.ThinkingConfig(thinking_budget=0)
                        ),
                    )
                except Exception:
                    pass
            
            # Fallback to basic configuration
            return genai.GenerativeModel(
                'gemini-2.5-flash',
                system_instruction=self._get_enhanced_system_instruction(),
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    def _get_enhanced_system_instruction(self) -> str:
        """Get enhanced system instruction with Manim API knowledge"""
        base_instruction = GEMINI_SYSTEM_INSTRUCTION
        
        # Add Manim API documentation context
        manim_context = """
        
        IMPORTANT: You have access to comprehensive Manim API documentation. Before generating any animation specification:
        
        1. ALWAYS use the manim_doc() function to look up Manim symbols, classes, and functions
        2. Verify parameter names, types, and default values from the official documentation
        3. Use only valid Manim symbols and parameters
        4. Reference the canonical import paths and signatures
        
        Available Manim symbols include:
        - Geometric shapes: Circle, Square, Rectangle, Line, Arrow, etc.
        - Animations: Create, FadeIn, FadeOut, Transform, MoveToTarget, etc.
        - Colors: RED, BLUE, GREEN, WHITE, BLACK, etc.
        - Scenes: Scene, MovingCameraScene, etc.
        - Mathematical objects: MathTex, Tex, DecimalNumber, etc.
        
        When in doubt about a Manim feature, ALWAYS consult the documentation first.
        """
        
        return base_instruction + manim_context
    
    async def generate_animation_spec(self, prompt: str) -> Dict[str, Any]:
        """Generate animation specification using enhanced AI with Manim API knowledge"""
        try:
            logger.info(f"Generating animation spec for prompt: {prompt}")
            
            # Enhance the prompt with context-aware improvements
            enhanced_prompt = self.prompt_enhancer.enhance_ai_prompt_with_context(prompt)
            logger.info(f"Prompt enhanced from {len(prompt)} to {len(enhanced_prompt)} characters")
            
            # Analyze prompt for Manim symbols and validate them
            manim_analysis = self._analyze_prompt_for_manim_symbols(enhanced_prompt)
            
            # Format the enhanced prompt with Manim API context
            formatted_prompt = self._format_prompt_with_manim_context(enhanced_prompt, manim_analysis)
            
            if not self.gemini_client:
                raise Exception("Gemini client not available")
            
            # Generate response from Gemini
            response = self.gemini_client.generate_content(
                formatted_prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            
            # Parse and validate the response
            animation_spec = self._parse_and_validate_response(response, manim_analysis)
            
            logger.info(f"Successfully generated animation spec with {len(animation_spec.get('objects', []))} objects")
            return animation_spec
            
        except Exception as e:
            logger.error(f"Failed to generate animation spec: {e}")
            # Return enhanced default spec
            return self._get_enhanced_default_spec(prompt)
    
    def _analyze_prompt_for_manim_symbols(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt to identify potential Manim symbols and validate them"""
        analysis = {
            'identified_symbols': [],
            'validation_results': {},
            'suggestions': [],
            'required_imports': set()
        }
        
        # Common Manim symbol patterns
        manim_patterns = [
            r'\b(Circle|Square|Rectangle|Triangle|Line|Arrow|Dot|Point)\b',
            r'\b(Create|FadeIn|FadeOut|Transform|MoveToTarget|Scale|Rotate)\b',
            r'\b(RED|BLUE|GREEN|WHITE|BLACK|YELLOW|PURPLE|ORANGE)\b',
            r'\b(Scene|MovingCameraScene|ThreeDScene)\b',
            r'\b(MathTex|Tex|DecimalNumber|Integer|Variable)\b'
        ]
        
        for pattern in manim_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                # Look up in Manim documentation
                doc_result = self.manim_docs.manim_doc(match)
                if doc_result:
                    analysis['identified_symbols'].append({
                        'name': match,
                        'symbol': doc_result.symbol,
                        'relevance': doc_result.relevance_score,
                        'source': doc_result.source
                    })
                    
                    # Validate usage
                    is_valid, errors = self.manim_docs.validate_symbol_usage(match)
                    analysis['validation_results'][match] = {
                        'valid': is_valid,
                        'errors': errors
                    }
                    
                    # Add to required imports
                    if doc_result.symbol.canonical_path:
                        analysis['required_imports'].add(doc_result.symbol.canonical_path)
                else:
                    analysis['suggestions'].append(f"Consider using '{match}' - verify in Manim documentation")
        
        return analysis
    
    def _format_prompt_with_manim_context(self, enhanced_prompt: str, manim_analysis: Dict[str, Any]) -> str:
        """Format the prompt with Manim API context and validation results"""
        # Start with the base template
        formatted_prompt = ANIMATION_PROMPT_TEMPLATE.replace("{prompt}", enhanced_prompt)
        
        # Add Manim API context
        manim_context = "\n\nMANIM API CONTEXT:\n"
        manim_context += "The following Manim symbols have been identified and validated:\n"
        
        for symbol_info in manim_analysis['identified_symbols']:
            symbol = symbol_info['symbol']
            manim_context += f"\n- {symbol.name} ({symbol.symbol_type}): {symbol.description}\n"
            manim_context += f"  Signature: {symbol.signature}\n"
            manim_context += f"  Examples: {'; '.join(symbol.examples[:2])}\n"
            manim_context += f"  Import: {symbol.canonical_path}\n"
        
        if manim_analysis['suggestions']:
            manim_context += "\nSUGGESTIONS:\n"
            for suggestion in manim_analysis['suggestions']:
                manim_context += f"- {suggestion}\n"
        
        # Add validation requirements
        manim_context += "\nVALIDATION REQUIREMENTS:\n"
        manim_context += "1. Use only the validated Manim symbols listed above\n"
        manim_context += "2. Follow the exact parameter names and types from signatures\n"
        manim_context += "3. Include all required imports in the generated code\n"
        manim_context += "4. Ensure all object properties match Manim API specifications\n"
        
        return formatted_prompt + manim_context
    
    def _parse_and_validate_response(self, response, manim_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate the AI response against Manim API specifications"""
        try:
            # Extract text content
            if hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                response_text = response.candidates[0].content.parts[0].text
            else:
                raise Exception("Unexpected response format")
            
            # Parse JSON response
            animation_spec = json.loads(response_text)
            
            # Validate against Manim API
            validated_spec = self._validate_animation_spec(animation_spec, manim_analysis)
            
            return validated_spec
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            raise Exception("Invalid JSON response from AI model")
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            raise
    
    def _validate_animation_spec(self, animation_spec: Dict[str, Any], manim_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate animation specification against Manim API requirements"""
        validated_spec = animation_spec.copy()
        
        # Validate objects
        if 'objects' in validated_spec:
            validated_objects = []
            for obj in validated_spec['objects']:
                validated_obj = self._validate_object(obj, manim_analysis)
                if validated_obj:
                    validated_objects.append(validated_obj)
            
            validated_spec['objects'] = validated_objects
        
        # Validate animations
        if 'animations' in validated_spec:
            validated_animations = []
            for anim in validated_spec['animations']:
                validated_anim = self._validate_animation(anim, manim_analysis)
                if validated_anim:
                    validated_animations.append(validated_anim)
            
            validated_spec['animations'] = validated_animations
        
        # Add required imports
        if manim_analysis['required_imports']:
            validated_spec['required_imports'] = list(manim_analysis['required_imports'])
        
        return validated_spec
    
    def _validate_object(self, obj: Dict[str, Any], manim_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate a single object against Manim API"""
        # First, normalize known coercions (e.g., matrix-like text -> matrix)
        obj = self._maybe_coerce_matrix_text(obj)
        obj_type = obj.get('type', '')
        
        # Look up in Manim documentation
        doc_result = self.manim_docs.manim_doc(obj_type)
        if not doc_result:
            logger.warning(f"Unknown Manim object type: {obj_type}")
            return None
        
        symbol = doc_result.symbol
        
        # Validate properties
        validated_props = {}
        for prop_name, prop_value in obj.get('properties', {}).items():
            # Check if property is valid for this object type
            if self._is_valid_property(prop_name, prop_value, symbol):
                validated_props[prop_name] = prop_value
            else:
                logger.warning(f"Invalid property {prop_name}={prop_value} for {obj_type}")
        
        # Create validated object
        validated_obj = {
            'type': obj_type,
            'id': obj.get('id', f"{obj_type}_{len(manim_analysis['identified_symbols'])}"),
            'properties': validated_props,
            'manim_symbol': symbol.name,
            'canonical_path': symbol.canonical_path
        }
        
        return validated_obj

    def _maybe_coerce_matrix_text(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """If an object is a text object with bracketed matrix-like content, coerce to matrix type.

        Example: Text with text="[[a, b], [c, d]]" becomes a matrix object with data=[["a","b"],["c","d"]].
        Preserves common properties like position/color if present.
        """
        try:
            obj_type = str(obj.get('type', '')).lower()
            props = obj.get('properties', {}) or {}
            text_value = props.get('text')
            if obj_type in ('text', 'tex', 'mathtex') and isinstance(text_value, str):
                content = text_value.strip()
                # Quick shape check: starts with [[ and ends with ]]
                if content.startswith('[[') and content.endswith(']]') and '][' in content or '],[' in content:
                    # Normalize separators and tokenize rows
                    inner = content[1:-1]  # strip outer []
                    # Split rows on '],'
                    rows_raw = []
                    buf = ''
                    depth = 0
                    for ch in inner:
                        if ch == '[':
                            depth += 1
                        elif ch == ']':
                            depth -= 1
                        if ch == ',' and depth == 0:
                            rows_raw.append(buf)
                            buf = ''
                        else:
                            buf += ch
                    if buf:
                        rows_raw.append(buf)
                    # Each row like [a, b]
                    data: List[List[str]] = []
                    for row in rows_raw:
                        row = row.strip()
                        if row.startswith('[') and row.endswith(']'):
                            row = row[1:-1]
                        # split by commas at depth 0 (no nested structures expected)
                        items: List[str] = []
                        token = ''
                        depth2 = 0
                        for ch in row:
                            if ch in '([{':
                                depth2 += 1
                            elif ch in ')]}':
                                depth2 -= 1
                            if ch == ',' and depth2 == 0:
                                val = token.strip()
                                if val:
                                    items.append(val)
                                token = ''
                            else:
                                token += ch
                        last = token.strip()
                        if last:
                            items.append(last)
                        # Wrap tokens as strings suitable for Manim Matrix
                        data.append([str(it).strip() for it in items])
                    # Build coerced matrix object
                    coerced = {
                        'type': 'matrix',
                        'id': obj.get('id'),
                        'properties': {
                            'data': data,
                        }
                    }
                    # Preserve common layout/style props if present
                    for key in ('position', 'color', 'size'):
                        if key in props:
                            coerced['properties'][key] = props[key]
                    # Preserve animations if present
                    if 'animations' in obj:
                        coerced['animations'] = obj['animations']
                    return coerced
        except Exception as e:
            logger.warning(f"Matrix coercion skipped due to error: {e}")
        return obj
    
    def _validate_animation(self, anim: Dict[str, Any], manim_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate a single animation against Manim API"""
        anim_type = anim.get('type', '')
        
        # Look up in Manim documentation
        doc_result = self.manim_docs.manim_doc(anim_type)
        if not doc_result:
            logger.warning(f"Unknown Manim animation type: {anim_type}")
            return None
        
        symbol = doc_result.symbol
        
        # Validate animation parameters
        validated_params = {}
        for param_name, param_value in anim.get('parameters', {}).items():
            if self._is_valid_parameter(param_name, param_value, symbol):
                validated_params[param_name] = param_value
            else:
                logger.warning(f"Invalid parameter {param_name}={param_value} for {anim_type}")
        
        # Create validated animation
        validated_anim = {
            'type': anim_type,
            'target': anim.get('target', ''),
            'parameters': validated_params,
            'manim_symbol': symbol.name,
            'canonical_path': symbol.canonical_path
        }
        
        return validated_anim
    
    def _is_valid_property(self, prop_name: str, prop_value: Any, symbol) -> bool:
        """Check if a property is valid for a Manim symbol"""
        # Basic validation - could be enhanced with more sophisticated parsing
        if prop_name in ['color', 'fill_opacity', 'stroke_width', 'position', 'size']:
            return True
        
        # Check against symbol signature
        if symbol.signature and prop_name.lower() in symbol.signature.lower():
            return True
        
        return False
    
    def _is_valid_parameter(self, param_name: str, param_value: Any, symbol) -> bool:
        """Check if a parameter is valid for a Manim animation"""
        # Basic validation - could be enhanced
        if param_name in ['run_time', 'lag_ratio', 'shift', 'scale']:
            return True
        
        # Check against symbol signature
        if symbol.signature and param_name.lower() in symbol.signature.lower():
            return True
        
        return False
    
    def _get_enhanced_default_spec(self, prompt: str) -> Dict[str, Any]:
        """Get enhanced default animation specification when AI generation fails"""
        default_spec = DEFAULT_ANIMATION_SPEC.copy()
        
        # Enhance with Manim API knowledge
        manim_analysis = self._analyze_prompt_for_manim_symbols(prompt)
        
        # Add identified symbols to default spec
        if manim_analysis['identified_symbols']:
            default_spec['objects'] = []
            for symbol_info in manim_analysis['identified_symbols'][:3]:  # Limit to 3
                symbol = symbol_info['symbol']
                default_spec['objects'].append({
                    'type': symbol.name,
                    'id': f"{symbol.name.lower()}_1",
                    'properties': {
                        'color': 'WHITE',
                        'position': [0, 0, 0],
                        'size': 1
                    },
                    'manim_symbol': symbol.name,
                    'canonical_path': symbol.canonical_path
                })
        
        # Add required imports
        if manim_analysis['required_imports']:
            default_spec['required_imports'] = list(manim_analysis['required_imports'])
        
        return default_spec
    
    def get_manim_documentation(self, symbol_or_query: str) -> Optional[ManimDocResult]:
        """Get Manim documentation for a symbol or query"""
        return self.manim_docs.manim_doc(symbol_or_query)
    
    def search_manim_symbols(self, query: str, limit: int = 10) -> List[ManimDocResult]:
        """Search for Manim symbols matching a query"""
        return self.manim_docs.search_symbols(query, limit)
    
    def get_manim_statistics(self) -> Dict[str, Any]:
        """Get statistics about the Manim documentation system"""
        return self.manim_docs.get_statistics()
    
    def refresh_manim_documentation(self):
        """Refresh the Manim documentation"""
        self.manim_docs.refresh_documentation()
