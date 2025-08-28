"""
AI Prompt Enhancement System for Animathic
Intelligently enhances AI prompts with context-aware improvements for better animation generation
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PromptEnhancementContext:
    """Context information for prompt enhancement"""
    prompt_complexity: str = 'simple'
    has_mathematical_content: bool = False
    has_multiple_objects: bool = False
    has_sequence_requirements: bool = False
    has_animation_effects: bool = False
    has_text_annotations: bool = False
    has_geometric_shapes: bool = False
    has_function_plots: bool = False
    has_typography_content: bool = False
    overlap_risk_level: str = 'low'
    performance_considerations: str = 'standard'


class AIPromptEnhancementSystem:
    """AI Prompt Enhancement System with intelligent context-aware improvements"""
    
    def __init__(self):
        """Initialize the AI prompt enhancement system"""
        self.enhancement_config = {
            'enable_context_analysis': True,
            'enable_overlap_prevention': True,
            'enable_sequence_optimization': True,
            'enable_performance_guidance': True,
            'enable_mathematical_optimization': True,
            'enhancement_level': 'comprehensive'  # 'minimal', 'standard', 'comprehensive'
        }
        
        # Enhancement templates for different content types
        self.enhancement_templates = {
            'typography_content': {
                'letter_positioning': """
CRITICAL FOR TYPOGRAPHY: When user asks for word/logo animations, ALWAYS create EACH LETTER as separate text object:
1. Create individual text objects: {"id": "letter_H", "type": "text", "properties": {"text": "H", "position": [-3.0, 0, 0]}}
2. Use consistent spacing: positions like [-3.0, 0, 0], [-1.8, 0, 0], [-0.6, 0, 0], [0.6, 0, 0], [1.8, 0, 0]
3. Each letter gets its own animation sequence
4. NO single text object containing entire word - this is WRONG!
5. Example for "HELLO": create letter_H, letter_E, letter_L, letter_L, letter_O as separate objects
""",
                'logo_transformation': """
FOR LOGO ANIMATIONS: Google, Facebook, etc.
1. Start with individual letters positioned horizontally
2. Use move animations to transform letters into final logo positions
3. Apply color changes during transformation (e.g., from white to brand colors)
4. Maintain smooth transitions between states
5. Use sequential timing for complex transformations
""",
                'typography_sequence': """
Typography animation sequence - ALWAYS FOLLOW THIS:
1. Individual letters appear first (fade_in or write animations)
2. Wait for all letters to appear before transformation begins
3. Apply transformation animations (move, color change) in logical sequence
4. End with final logo state clearly visible
5. NEVER put entire word in single text object!
""",
            },
            'mathematical_content': {
                'overlap_prevention': """
IMPORTANT: When creating multiple graphs or plots:
1. Each graph should appear sequentially, not simultaneously
2. Previous graphs must fade out before new ones appear
3. Use clear transitions between graphs
4. Ensure no visual overlap between different mathematical objects
5. If showing multiple functions, use a clear sequence: show first, fade out, show second, etc.
6. Position function plots at [0, 0, 0] for proper coordinate system layout
7. Use different colors for each function: sine=YELLOW, cosine=BLUE, tangent=GREEN, exponential=RED
""",
                'sequence_guidance': """
MATHEMATICAL SEQUENCE REQUIREMENTS:
- Show coordinate axes first
- Display functions one by one with clear transitions
- Use fade-out for previous functions when showing new ones
- Maintain mathematical precision and clarity
- Ensure all mathematical elements are clearly visible
"""
            },
            
            'geometric_shapes': {
                'overlap_prevention': """
GEOMETRIC SHAPE LAYOUT REQUIREMENTS:
- Position shapes with adequate spacing (minimum 1.5 units apart)
- Use sequential display for multiple shapes
- Avoid overlapping shapes unless specifically requested
- Ensure each shape is clearly visible and distinct
- Use different colors for different shapes when possible
""",
                'sequence_guidance': """
SHAPE DISPLAY SEQUENCE:
- Show shapes one at a time for clarity
- Use fade transitions between shapes
- Maintain visual hierarchy and organization
- Ensure smooth progression through the animation
"""
            },
            
            'text_annotations': {
                'overlap_prevention': """
TEXT ANNOTATION POSITIONING:
- Position text labels near but not overlapping with objects
- Use clear, readable positioning above or to the right of objects
- Ensure text is always visible and not obscured
- Use simple, short labels (A, B, C, etc.)
- Avoid text overlapping with other text or objects
""",
                'sequence_guidance': """
TEXT TIMING REQUIREMENTS:
- Show text labels after their corresponding objects appear
- Use brief fade-in animations for text
- Ensure text remains visible throughout the animation
- Position text for optimal readability
"""
            },
            
            'animation_effects': {
                'sequence_optimization': """
ANIMATION SEQUENCE REQUIREMENTS:
- Objects should appear in logical order
- Use fade transitions between different object types
- Maintain clear visual hierarchy
- Avoid cluttering the screen with too many objects at once
- Use appropriate timing for smooth visual flow
""",
                'performance_guidance': """
ANIMATION PERFORMANCE OPTIMIZATION:
- Limit simultaneous animations to 3-4 objects
- Use sequential display for complex scenes
- Implement fade-out for previous objects when showing new ones
- Maintain smooth frame rates and transitions
"""
            },
            
            'multiple_objects': {
                'overlap_prevention': """
MULTIPLE OBJECT LAYOUT:
- Use grid-based or systematic positioning
- Maintain clear spacing between objects
- Implement sequential display to prevent visual clutter
- Use fade transitions between object groups
- Ensure optimal camera positioning for all objects
""",
                'sequence_guidance': """
OBJECT DISPLAY SEQUENCE:
- Group related objects together
- Show objects in logical order
- Use batch transitions for object groups
- Maintain visual clarity throughout the sequence
"""
            }
        }
        
        # Performance guidance based on complexity
        self.performance_guidance = {
            'simple': """
PERFORMANCE GUIDANCE (Simple Scene):
- Use standard fade-in/fade-out animations
- Limit to 3-5 objects maximum
- Use simple color schemes
- Maintain standard timing (0.5-1.0s per animation)
""",
            'moderate': """
PERFORMANCE GUIDANCE (Moderate Scene):
- Use sequential display for multiple objects
- Implement fade-out for previous objects
- Limit simultaneous animations to 3-4 objects
- Use optimized timing (0.3-0.8s per animation)
- Consider camera adjustments for better viewing
""",
            'complex': """
PERFORMANCE GUIDANCE (Complex Scene):
- Use advanced sequence optimization
- Implement batch processing for object groups
- Use camera management for optimal viewing
- Limit simultaneous animations to 2-3 objects
- Use optimized timing (0.2-0.6s per animation)
- Consider performance monitoring and optimization
"""
        }
        
        logger.info("AIPromptEnhancementSystem initialized")
    
    def enhance_ai_prompt_with_context(self, original_prompt: str, animation_context: Optional[Dict[str, Any]] = None) -> str:
        """Enhance AI prompts with context-aware improvements"""
        try:
            enhanced_prompt = original_prompt
            
            # Analyze prompt context if not provided
            if animation_context is None:
                animation_context = self._analyze_prompt_context(original_prompt)
            
            logger.info(f"Enhancing prompt with context: {animation_context}")
            
            # Apply context-specific enhancements (typography first for priority)
            enhanced_prompt = self._apply_typography_enhancements(enhanced_prompt, animation_context)
            enhanced_prompt = self._apply_mathematical_enhancements(enhanced_prompt, animation_context)
            enhanced_prompt = self._apply_geometric_enhancements(enhanced_prompt, animation_context)
            enhanced_prompt = self._apply_text_enhancements(enhanced_prompt, animation_context)
            enhanced_prompt = self._apply_animation_enhancements(enhanced_prompt, animation_context)
            enhanced_prompt = self._apply_overlap_prevention(enhanced_prompt, animation_context)
            enhanced_prompt = self._apply_sequence_optimization(enhanced_prompt, animation_context)
            enhanced_prompt = self._apply_performance_guidance(enhanced_prompt, animation_context)
            
            # Add general enhancement guidelines
            enhanced_prompt = self._add_general_enhancement_guidelines(enhanced_prompt, animation_context)
            
            logger.info("Prompt enhancement completed successfully")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing AI prompt: {e}")
            return original_prompt
    
    def _analyze_prompt_context(self, prompt: str) -> PromptEnhancementContext:
        """Analyze prompt to determine enhancement context"""
        prompt_lower = prompt.lower()
        
        context = PromptEnhancementContext()
        
        # Analyze mathematical content (exclude typography keywords)
        math_keywords = ['function', 'plot', 'graph', 'equation', 'formula', 'sine', 'cosine', 'tangent', 'exponential', 'polynomial', 'math', 'calculate']
        typography_keywords_check = ['typography', 'logo', 'brand', 'letter', 'word', 'font', 'typeface', 'google', 'character', 'glyph', 'symbol', 'emblem', 'monogram', 'insignia']

        # Only mark as mathematical if math keywords are present AND typography keywords are NOT dominant
        has_math_keywords = any(keyword in prompt_lower for keyword in math_keywords)
        has_typography_keywords = any(keyword in prompt_lower for keyword in typography_keywords_check)

        # Prioritize typography over mathematical when both are detected
        if has_typography_keywords and has_math_keywords:
            context.has_mathematical_content = False  # Typography takes priority
        else:
            context.has_mathematical_content = has_math_keywords
        
        # Analyze geometric shapes
        shape_keywords = ['circle', 'square', 'triangle', 'diamond', 'star', 'hexagon', 'rectangle', 'ellipse', 'shape', 'geometric']
        context.has_geometric_shapes = any(keyword in prompt_lower for keyword in shape_keywords)
        
        # Analyze text annotations
        text_keywords = ['text', 'label', 'annotation', 'name', 'title', 'caption', 'description']
        context.has_text_annotations = any(keyword in prompt_lower for keyword in text_keywords)

        # Analyze typography content (logos, letters, branding) - MORE AGGRESSIVE DETECTION
        typography_keywords = [
            'typography', 'logo', 'brand', 'letter', 'word', 'font', 'typeface',
            'google', 'logo', 'brand', 'morph', 'transform', 'rearrange', 'evolve',
            'character', 'glyph', 'symbol', 'emblem', 'monogram', 'insignia',
            'each letter', 'individual letter', 'separate letter', 'letter by letter',
            'spelling', 'spell out', 'text animation', 'letter animation'
        ]
        context.has_typography_content = any(keyword in prompt_lower for keyword in typography_keywords)

        # Additional check for explicit typography patterns
        if not context.has_typography_content:
            # Check for patterns like "word X where each letter..."
            if 'word' in prompt_lower and ('letter' in prompt_lower or 'each' in prompt_lower):
                context.has_typography_content = True
            # Check for brand/logo names that are likely typography
            brand_names = ['google', 'facebook', 'apple', 'microsoft', 'amazon', 'netflix', 'youtube']
            if any(brand in prompt_lower for brand in brand_names):
                context.has_typography_content = True
        
        # Analyze animation effects
        animation_keywords = ['fade', 'appear', 'disappear', 'animate', 'transition', 'effect', 'morph', 'transform', 'sequence']
        context.has_animation_effects = any(keyword in prompt_lower for keyword in animation_keywords)
        
        # Analyze multiple objects
        multiple_keywords = ['multiple', 'several', 'many', 'various', 'both', 'and', 'with', 'together', 'group', 'collection']
        context.has_multiple_objects = any(keyword in prompt_lower for keyword in multiple_keywords)
        
        # Analyze sequence requirements
        sequence_keywords = ['sequence', 'step', 'progression', 'evolution', 'then', 'next', 'after', 'first', 'second', 'third', 'order']
        context.has_sequence_requirements = any(keyword in prompt_lower for keyword in sequence_keywords)
        
        # Determine complexity level
        complexity_score = sum([
            context.has_mathematical_content,
            context.has_geometric_shapes,
            context.has_text_annotations,
            context.has_animation_effects,
            context.has_multiple_objects,
            context.has_sequence_requirements
        ])
        
        if complexity_score <= 2:
            context.prompt_complexity = 'simple'
        elif complexity_score <= 4:
            context.prompt_complexity = 'moderate'
        else:
            context.prompt_complexity = 'complex'
        
        # Determine overlap risk level
        if context.has_multiple_objects and (context.has_mathematical_content or context.has_geometric_shapes):
            context.overlap_risk_level = 'high'
        elif context.has_multiple_objects:
            context.overlap_risk_level = 'medium'
        else:
            context.overlap_risk_level = 'low'
        
        # Determine performance considerations
        if context.prompt_complexity == 'complex':
            context.performance_considerations = 'high'
        elif context.prompt_complexity == 'moderate':
            context.performance_considerations = 'medium'
        else:
            context.performance_considerations = 'low'
        
        return context
    
    def _apply_typography_enhancements(self, prompt: str, context: PromptEnhancementContext) -> str:
        """Apply typography content enhancements"""
        if not context.has_typography_content:
            return prompt

        enhanced_prompt = prompt

        # Add typography letter positioning guidance
        enhanced_prompt += self.enhancement_templates['typography_content']['letter_positioning']

        # Add logo transformation guidance for complex typography
        if 'logo' in prompt.lower() or 'transform' in prompt.lower():
            enhanced_prompt += self.enhancement_templates['typography_content']['logo_transformation']

        # Add typography sequence guidance
        if context.has_sequence_requirements or context.has_animation_effects:
            enhanced_prompt += self.enhancement_templates['typography_content']['typography_sequence']

        logger.info("Applied typography content enhancements")
        return enhanced_prompt

    def _apply_mathematical_enhancements(self, prompt: str, context: PromptEnhancementContext) -> str:
        """Apply mathematical content enhancements"""
        if not context.has_mathematical_content:
            return prompt

        enhanced_prompt = prompt

        # Add mathematical overlap prevention
        if context.overlap_risk_level in ['medium', 'high']:
            enhanced_prompt += self.enhancement_templates['mathematical_content']['overlap_prevention']

        # Add mathematical sequence guidance
        if context.has_sequence_requirements:
            enhanced_prompt += self.enhancement_templates['mathematical_content']['sequence_guidance']

        logger.info("Applied mathematical content enhancements")
        return enhanced_prompt
    
    def _apply_geometric_enhancements(self, prompt: str, context: PromptEnhancementContext) -> str:
        """Apply geometric shape enhancements"""
        if not context.has_geometric_shapes:
            return prompt
        
        enhanced_prompt = prompt
        
        # Add geometric overlap prevention
        if context.overlap_risk_level in ['medium', 'high']:
            enhanced_prompt += self.enhancement_templates['geometric_shapes']['overlap_prevention']
        
        # Add geometric sequence guidance
        if context.has_sequence_requirements:
            enhanced_prompt += self.enhancement_templates['geometric_shapes']['sequence_guidance']
        
        logger.info("Applied geometric shape enhancements")
        return enhanced_prompt
    
    def _apply_text_enhancements(self, prompt: str, context: PromptEnhancementContext) -> str:
        """Apply text annotation enhancements"""
        if not context.has_text_annotations:
            return prompt
        
        enhanced_prompt = prompt
        
        # Add text overlap prevention
        if context.overlap_risk_level in ['medium', 'high']:
            enhanced_prompt += self.enhancement_templates['text_annotations']['overlap_prevention']
        
        # Add text sequence guidance
        if context.has_sequence_requirements:
            enhanced_prompt += self.enhancement_templates['text_annotations']['sequence_guidance']
        
        logger.info("Applied text annotation enhancements")
        return enhanced_prompt
    
    def _apply_animation_enhancements(self, prompt: str, context: PromptEnhancementContext) -> str:
        """Apply animation effect enhancements"""
        if not context.has_animation_effects:
            return prompt
        
        enhanced_prompt = prompt
        
        # Add animation sequence optimization
        if context.has_sequence_requirements:
            enhanced_prompt += self.enhancement_templates['animation_effects']['sequence_optimization']
        
        # Add animation performance guidance
        if context.performance_considerations in ['medium', 'high']:
            enhanced_prompt += self.enhancement_templates['animation_effects']['performance_guidance']
        
        logger.info("Applied animation effect enhancements")
        return enhanced_prompt
    
    def _apply_overlap_prevention(self, prompt: str, context: PromptEnhancementContext) -> str:
        """Apply general overlap prevention enhancements"""
        if context.overlap_risk_level == 'low':
            return prompt
        
        enhanced_prompt = prompt
        
        # Add general overlap prevention guidance
        if context.overlap_risk_level == 'high':
            enhanced_prompt += """
CRITICAL OVERLAP PREVENTION:
- Use sequential display for all objects
- Implement fade-out for previous objects before showing new ones
- Maintain clear spacing between all elements
- Use camera adjustments to provide optimal viewing space
- Consider using grid-based positioning for multiple objects
"""
        elif context.overlap_risk_level == 'medium':
            enhanced_prompt += """
OVERLAP PREVENTION GUIDELINES:
- Use sequential display for multiple objects
- Maintain adequate spacing between elements
- Use fade transitions to prevent visual clutter
- Ensure each object is clearly visible
"""
        
        logger.info("Applied overlap prevention enhancements")
        return enhanced_prompt
    
    def _apply_sequence_optimization(self, prompt: str, context: PromptEnhancementContext) -> str:
        """Apply sequence optimization enhancements"""
        if not context.has_sequence_requirements:
            return prompt
        
        enhanced_prompt = prompt
        
        # Add sequence optimization guidance
        enhanced_prompt += """
SEQUENCE OPTIMIZATION REQUIREMENTS:
- Show objects in logical, progressive order
- Use clear transitions between different object types
- Implement fade-out for previous objects when showing new ones
- Maintain visual hierarchy and organization
- Use appropriate timing for smooth visual flow
- Consider using batch transitions for object groups
"""
        
        logger.info("Applied sequence optimization enhancements")
        return enhanced_prompt
    
    def _apply_performance_guidance(self, prompt: str, context: PromptEnhancementContext) -> str:
        """Apply performance guidance enhancements"""
        enhanced_prompt = prompt
        
        # Add performance guidance based on complexity
        if context.prompt_complexity in self.performance_guidance:
            enhanced_prompt += self.performance_guidance[context.prompt_complexity]
        
        logger.info("Applied performance guidance enhancements")
        return enhanced_prompt
    
    def _add_general_enhancement_guidelines(self, prompt: str, context: PromptEnhancementContext) -> str:
        """Add general enhancement guidelines"""
        enhanced_prompt = prompt
        
        # Add general enhancement guidelines
        enhanced_prompt += """
GENERAL ENHANCEMENT GUIDELINES:
- Ensure all objects are clearly visible and distinct
- Use appropriate colors and contrast for better visibility
- Implement smooth transitions between animation phases
- Maintain consistent timing and pacing throughout
- Consider camera positioning for optimal viewing
- Use fade effects to prevent visual clutter
- Implement sequential display for complex scenes
"""
        
        # Add specific guidance based on context
        if context.has_mathematical_content and context.has_geometric_shapes:
            enhanced_prompt += """
MATHEMATICAL + GEOMETRIC INTEGRATION:
- Show mathematical content first (axes, plots)
- Then display geometric shapes at appropriate positions
- Use clear visual separation between mathematical and geometric elements
- Ensure geometric shapes complement mathematical content
"""
        
        if context.has_multiple_objects and context.has_text_annotations:
            enhanced_prompt += """
MULTIPLE OBJECTS + TEXT ANNOTATIONS:
- Show objects first, then their corresponding text labels
- Use sequential display to prevent text overlap
- Position text for optimal readability
- Maintain clear association between objects and labels
"""
        
        logger.info("Applied general enhancement guidelines")
        return enhanced_prompt
    
    def get_enhancement_summary(self, original_prompt: str, enhanced_prompt: str, context: PromptEnhancementContext) -> Dict[str, Any]:
        """Get a summary of applied enhancements"""
        try:
            # Calculate enhancement metrics
            original_length = len(original_prompt)
            enhanced_length = len(enhanced_prompt)
            enhancement_ratio = enhanced_length / original_length if original_length > 0 else 1.0
            
            # Identify applied enhancements
            applied_enhancements = []
            if context.has_mathematical_content:
                applied_enhancements.append('mathematical_optimization')
            if context.has_geometric_shapes:
                applied_enhancements.append('geometric_optimization')
            if context.has_text_annotations:
                applied_enhancements.append('text_optimization')
            if context.has_animation_effects:
                applied_enhancements.append('animation_optimization')
            if context.overlap_risk_level in ['medium', 'high']:
                applied_enhancements.append('overlap_prevention')
            if context.has_sequence_requirements:
                applied_enhancements.append('sequence_optimization')
            
            return {
                'enhancement_applied': True,
                'original_length': original_length,
                'enhanced_length': enhanced_length,
                'enhancement_ratio': enhancement_ratio,
                'prompt_complexity': context.prompt_complexity,
                'overlap_risk_level': context.overlap_risk_level,
                'performance_considerations': context.performance_considerations,
                'applied_enhancements': applied_enhancements,
                'enhancement_context': {
                    'has_mathematical_content': context.has_mathematical_content,
                    'has_geometric_shapes': context.has_geometric_shapes,
                    'has_text_annotations': context.has_text_annotations,
                    'has_animation_effects': context.has_animation_effects,
                    'has_multiple_objects': context.has_multiple_objects,
                    'has_sequence_requirements': context.has_sequence_requirements
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating enhancement summary: {e}")
            return {
                'enhancement_applied': False,
                'error': str(e)
            }
    
    def analyze_enhancement_effectiveness(self, original_prompt: str, enhanced_prompt: str, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the effectiveness of prompt enhancements"""
        try:
            effectiveness_metrics = {
                'enhancement_applied': True,
                'response_quality': 'unknown',
                'overlap_issues_resolved': False,
                'sequence_optimization_applied': False,
                'performance_improvements': False
            }
            
            # Analyze AI response for enhancement indicators
            if ai_response and isinstance(ai_response, dict):
                objects = ai_response.get('objects', [])
                
                # Check for overlap prevention
                if len(objects) > 1:
                    # Simple overlap check based on positioning
                    positions = []
                    for obj in objects:
                        pos = obj.get('properties', {}).get('position', [0, 0, 0])
                        if len(pos) >= 2:
                            positions.append((pos[0], pos[1]))
                    
                    # Check for overlapping positions
                    overlap_found = False
                    for i, pos1 in enumerate(positions):
                        for j, pos2 in enumerate(positions[i+1:], i+1):
                            distance = ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
                            if distance < 1.0:  # Overlap threshold
                                overlap_found = True
                                break
                        if overlap_found:
                            break
                    
                    effectiveness_metrics['overlap_issues_resolved'] = not overlap_found
                
                # Check for sequence optimization
                animations_count = sum(len(obj.get('animations', [])) for obj in objects)
                if animations_count > 0:
                    effectiveness_metrics['sequence_optimization_applied'] = True
                
                # Check for performance improvements
                if len(objects) <= 5:
                    effectiveness_metrics['performance_improvements'] = True
                
                # Assess overall response quality
                if objects and all(isinstance(obj, dict) and obj.get('type') for obj in objects):
                    effectiveness_metrics['response_quality'] = 'good'
                else:
                    effectiveness_metrics['response_quality'] = 'poor'
            
            return effectiveness_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing enhancement effectiveness: {e}")
            return {
                'enhancement_applied': False,
                'error': str(e)
            }


# Global instance
ai_prompt_enhancer = AIPromptEnhancementSystem()
