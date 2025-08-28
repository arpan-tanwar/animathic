#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced Animathic workflow
Tests various animation types and complexity levels
"""

import asyncio
import logging
import os
import json
import re
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from services.ai_service_new import AIService
from services.manim_code_generator import ManimCodeGenerator

class EnhancedWorkflowTester:
    """Test class for comprehensive workflow validation"""

    def __init__(self):
        self.ai_service = None
        self.code_generator = ManimCodeGenerator()
        self.test_results = {}

    async def initialize(self):
        """Initialize the AI service"""
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            raise RuntimeError("GOOGLE_AI_API_KEY not found")

        self.ai_service = AIService(api_key=api_key)
        logger.info("Enhanced workflow tester initialized")

    def get_test_prompts(self) -> List[Dict[str, Any]]:
        """Get comprehensive test prompts covering various animation types"""
        return [
            # Simple animations
            {
                'name': 'simple_circle',
                'prompt': 'Create a simple blue circle that fades in',
                'expected_complexity': 'simple',
                'expected_types': ['circle'],
                'expected_animations': ['fade_in']
            },
            {
                'name': 'simple_text',
                'prompt': 'Show the text "Hello World" with white color',
                'expected_complexity': 'simple',
                'expected_types': ['text'],
                'expected_animations': ['fade_in']
            },

            # Mathematical animations
            {
                'name': 'sine_wave',
                'prompt': 'Plot a sine wave function with proper axes',
                'expected_complexity': 'moderate',
                'expected_types': ['axes', 'plot'],
                'expected_animations': ['create', 'write']
            },
            {
                'name': 'multiple_functions',
                'prompt': 'Plot sine, cosine, and tangent functions on the same graph with different colors',
                'expected_complexity': 'complex',
                'expected_types': ['axes', 'plot'],
                'expected_animations': ['create', 'write']
            },

            # Complex animations
            {
                'name': 'bouncing_ball',
                'prompt': 'Show a ball bouncing along a parabolic path with gravity effect',
                'expected_complexity': 'complex',
                'expected_types': ['circle'],
                'expected_animations': ['move_along_path']
            },
            {
                'name': 'text_morphing',
                'prompt': 'Create text that morphs from "Hello" to "World" with smooth transformation',
                'expected_complexity': 'complex',
                'expected_types': ['text'],
                'expected_animations': ['transform', 'replacement_transform']
            },

            # 3D animations
            {
                'name': 'rotating_cube',
                'prompt': 'Create a 3D cube that rotates in space',
                'expected_complexity': 'very_complex',
                'expected_types': ['surface'],
                'expected_animations': ['rotate']
            },

            # Interactive sequences
            {
                'name': 'step_by_step',
                'prompt': 'Show step-by-step mathematical derivation: 2x + 3 = 7, solve for x',
                'expected_complexity': 'complex',
                'expected_types': ['text', 'equation'],
                'expected_animations': ['write', 'transform', 'fade_out']
            },

            # Particle systems
            {
                'name': 'particle_cloud',
                'prompt': 'Create a cloud of moving particles that form a circle pattern',
                'expected_complexity': 'very_complex',
                'expected_types': ['dot'],
                'expected_animations': ['move', 'fade_in']
            }
        ]

    async def test_single_prompt(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single prompt through the complete workflow"""
        try:
            logger.info(f"Testing: {test_case['name']}")
            prompt = test_case['prompt']

            # Step 1: Process through AI service
            ai_result = await self.ai_service.process_animation_request(prompt)

            if 'error' in ai_result:
                return {
                    'name': test_case['name'],
                    'success': False,
                    'error': ai_result['error'],
                    'stage': 'ai_processing'
                }

            # Step 2: Extract animation spec
            animation_spec = ai_result.get('animation_spec', {})
            manim_code = ai_result.get('manim_code', '')

            if not animation_spec:
                return {
                    'name': test_case['name'],
                    'success': False,
                    'error': 'No animation spec generated',
                    'stage': 'spec_extraction'
                }

            # Step 3: Validate complexity analysis
            complexity = ai_result.get('complexity_analysis', {})
            logger.info(f"Complexity analysis: {complexity.get('level', 'unknown')} (score: {complexity.get('score', 0)})")

            # Step 4: Test Manim code generation (if not already generated by AI)
            if not manim_code:
                try:
                    manim_code = self.code_generator.generate_manim_code(animation_spec)
                except Exception as e:
                    return {
                        'name': test_case['name'],
                        'success': False,
                        'error': f'Manim code generation failed: {e}',
                        'stage': 'code_generation'
                    }

            # Step 5: Validate generated code structure
            validation_result = self._validate_generated_code(manim_code)
            if not validation_result['valid']:
                return {
                    'name': test_case['name'],
                    'success': False,
                    'error': f'Code validation failed: {validation_result["errors"]}',
                    'stage': 'code_validation'
                }

            # Step 6: Test code execution (syntax check)
            execution_result = self._test_code_execution(manim_code)
            if not execution_result['success']:
                return {
                    'name': test_case['name'],
                    'success': False,
                    'error': f'Code execution failed: {execution_result["error"]}',
                    'stage': 'code_execution'
                }

            # Success!
            return {
                'name': test_case['name'],
                'success': True,
                'complexity_level': complexity.get('level', 'unknown'),
                'complexity_score': complexity.get('score', 0),
                'workflow_type': ai_result.get('workflow_type', 'unknown'),
                'scene_type': complexity.get('scene_type_recommendation', 'Scene'),
                'object_count': len(animation_spec.get('objects', [])),
                'animation_types': self._extract_animation_types(animation_spec),
                'code_length': len(manim_code),
                'estimated_duration': complexity.get('estimated_duration', 5.0)
            }

        except Exception as e:
            logger.error(f"Test failed for {test_case['name']}: {e}")
            return {
                'name': test_case['name'],
                'success': False,
                'error': str(e),
                'stage': 'unexpected_error'
            }

    def _validate_generated_code(self, code: str) -> Dict[str, Any]:
        """Validate the structure of generated Manim code"""
        try:
            errors = []

            # Check for required components
            required_patterns = [
                r'import numpy as np',
                r'from manim import \*',
                r'class GeneratedScene\(Scene\):',
                r'def construct\(self\):',
            ]

            for pattern in required_patterns:
                if not re.search(pattern, code):
                    errors.append(f"Missing required pattern: {pattern}")

            # Check for balanced parentheses and brackets
            paren_count = code.count('(') - code.count(')')
            bracket_count = code.count('[') - code.count(']')
            brace_count = code.count('{') - code.count('}')

            if paren_count != 0:
                errors.append(f"Unbalanced parentheses: {paren_count}")
            if bracket_count != 0:
                errors.append(f"Unbalanced brackets: {bracket_count}")
            if brace_count != 0:
                errors.append(f"Unbalanced braces: {brace_count}")

            return {
                'valid': len(errors) == 0,
                'errors': errors
            }

        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {e}']
            }

    def _test_code_execution(self, code: str) -> Dict[str, Any]:
        """Test code execution (syntax check only)"""
        try:
            # Try to compile the code to check for syntax errors
            compile(code, '<string>', 'exec')
            return {'success': True}
        except SyntaxError as e:
            return {'success': False, 'error': f'Syntax error: {e}'}
        except Exception as e:
            return {'success': False, 'error': f'Compilation error: {e}'}

    def _extract_animation_types(self, spec: Dict[str, Any]) -> List[str]:
        """Extract animation types from animation spec"""
        animation_types = set()
        for obj in spec.get('objects', []):
            for anim in obj.get('animations', []):
                animation_types.add(anim.get('type', 'unknown'))
        return list(animation_types)

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests on all prompt types"""
        logger.info("Starting comprehensive workflow tests")

        test_prompts = self.get_test_prompts()
        results = []

        for test_case in test_prompts:
            result = await self.test_single_prompt(test_case)
            results.append(result)

            if result['success']:
                logger.info(f"✅ {result['name']}: PASSED ({result['complexity_level']}, score: {result['complexity_score']})")
            else:
                logger.error(f"❌ {result['name']}: FAILED at {result['stage']} - {result['error']}")

        # Summarize results
        successful_tests = [r for r in results if r['success']]
        failed_tests = [r for r in results if not r['success']]

        summary = {
            'total_tests': len(results),
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'success_rate': len(successful_tests) / len(results) * 100,
            'results': results,
            'complexity_breakdown': self._analyze_complexity_breakdown(results),
            'performance_metrics': self._calculate_performance_metrics(results)
        }

        logger.info(f"Test Summary: {summary['successful_tests']}/{summary['total_tests']} tests passed ({summary['success_rate']:.1f}%)")

        return summary

    def _analyze_complexity_breakdown(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze results by complexity level"""
        complexity_levels = {}
        for result in results:
            if result['success']:
                level = result.get('complexity_level', 'unknown')
                if level not in complexity_levels:
                    complexity_levels[level] = {'total': 0, 'successful': 0}
                complexity_levels[level]['total'] += 1
                complexity_levels[level]['successful'] += 1
            else:
                # Count failed tests in complexity breakdown too
                level = 'failed'
                if level not in complexity_levels:
                    complexity_levels[level] = {'total': 0, 'successful': 0}
                complexity_levels[level]['total'] += 1

        return complexity_levels

    def _calculate_performance_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics from test results"""
        successful_results = [r for r in results if r['success']]

        if not successful_results:
            return {'average_complexity_score': 0, 'average_object_count': 0, 'average_code_length': 0}

        avg_complexity = sum(r.get('complexity_score', 0) for r in successful_results) / len(successful_results)
        avg_objects = sum(r.get('object_count', 0) for r in successful_results) / len(successful_results)
        avg_code_length = sum(r.get('code_length', 0) for r in successful_results) / len(successful_results)

        return {
            'average_complexity_score': avg_complexity,
            'average_object_count': avg_objects,
            'average_code_length': avg_code_length
        }

async def main():
    """Main test function"""
    try:
        tester = EnhancedWorkflowTester()
        await tester.initialize()

        results = await tester.run_comprehensive_tests()

        # Save detailed results
        with open('/tmp/enhanced_workflow_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        logger.info("Test results saved to /tmp/enhanced_workflow_test_results.json")

        # Print summary
        print("\n" + "="*60)
        print("ENHANCED WORKFLOW TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful: {results['successful_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(".1f")
        print("\nComplexity Breakdown:")
        for level, stats in results['complexity_breakdown'].items():
            success_rate = stats['successful'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"  {level}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)")

        print("\nPerformance Metrics:")
        perf = results['performance_metrics']
        print(".2f")
        print(".1f")
        print(",")

    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
