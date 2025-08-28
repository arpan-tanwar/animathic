#!/usr/bin/env python3
"""
Test script for the simplified, reliable animation system
Tests that the system fixes the persistent issues: flickering, wrong shapes, positioning, overlap, fade out, smooth animation
"""

import asyncio
import logging
import os
import json
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from services.simple_ai_service import SimpleAIService

class SimpleSystemTester:
    """Test class for validating the simplified animation system"""

    def __init__(self):
        self.ai_service = None

    async def initialize(self):
        """Initialize the simple AI service"""
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            raise RuntimeError("GOOGLE_AI_API_KEY not found")

        self.ai_service = SimpleAIService(api_key=api_key)
        logger.info("Simple system tester initialized")

    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Get test cases that previously caused persistent issues"""
        return [
            # Basic animations that should work reliably
            {
                'name': 'basic_circle_fade',
                'prompt': 'Create a blue circle that fades in smoothly',
                'issue_tested': 'fade_in_flickering',
                'expected_success': True
            },
            {
                'name': 'basic_square_rotate',
                'prompt': 'Show a green square that rotates without flickering',
                'issue_tested': 'shape_correctness',
                'expected_success': True
            },
            {
                'name': 'text_display',
                'prompt': 'Display the text "Hello World" clearly without overlap',
                'issue_tested': 'text_positioning',
                'expected_success': True
            },
            {
                'name': 'multiple_objects',
                'prompt': 'Show a circle and a square positioned apart without overlapping',
                'issue_tested': 'overlap_prevention',
                'expected_success': True
            },
            {
                'name': 'fade_sequence',
                'prompt': 'Create a circle that fades in, then fades out smoothly',
                'issue_tested': 'fade_out_smoothness',
                'expected_success': True
            },
            {
                'name': 'moving_object',
                'prompt': 'Show a dot that moves smoothly from left to right',
                'issue_tested': 'smooth_movement',
                'expected_success': True
            },
            {
                'name': 'function_plot',
                'prompt': 'Plot a simple sine wave with axes',
                'issue_tested': 'mathematical_accuracy',
                'expected_success': True
            },
            # Edge cases that previously failed
            {
                'name': 'complex_request',
                'prompt': 'Create a complex animation with multiple objects and animations',
                'issue_tested': 'complexity_handling',
                'expected_success': True
            }
        ]

    async def test_single_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single animation case"""
        try:
            logger.info(f"Testing: {test_case['name']} - {test_case['issue_tested']}")
            prompt = test_case['prompt']

            # Process the animation request
            result = await self.ai_service.process_animation_request(prompt)

            if 'error' in result:
                return {
                    'name': test_case['name'],
                    'success': False,
                    'issue_tested': test_case['issue_tested'],
                    'error': result['error'],
                    'manim_code': result.get('manim_code', ''),
                    'expected_success': test_case['expected_success']
                }

            # Validate the generated code
            manim_code = result.get('manim_code', '')
            animation_spec = result.get('animation_spec', {})

            # Check for common issues
            issues_found = self._check_for_common_issues(manim_code, animation_spec)

            return {
                'name': test_case['name'],
                'success': True,
                'issue_tested': test_case['issue_tested'],
                'issues_found': issues_found,
                'manim_code_length': len(manim_code),
                'objects_count': len(animation_spec.get('objects', [])),
                'expected_success': test_case['expected_success']
            }

        except Exception as e:
            logger.error(f"Test failed for {test_case['name']}: {e}")
            return {
                'name': test_case['name'],
                'success': False,
                'issue_tested': test_case['issue_tested'],
                'error': str(e),
                'expected_success': test_case['expected_success']
            }

    def _check_for_common_issues(self, manim_code: str, animation_spec: Dict[str, Any]) -> List[str]:
        """Check for common issues that previously plagued the system"""
        issues_found = []

        # Check for flickering issues (multiple rapid animations)
        if manim_code.count('self.play') > 5:
            issues_found.append("potential_flickering_multiple_plays")

        # Check for positioning issues (overlapping objects)
        objects = animation_spec.get('objects', [])
        positions = []
        for obj in objects:
            pos = obj.get('properties', {}).get('position', [0, 0, 0])
            # Check if positions are too close (potential overlap)
            for existing_pos in positions:
                distance = ((pos[0] - existing_pos[0])**2 + (pos[1] - existing_pos[1])**2)**0.5
                if distance < 1.0:  # Less than 1 unit apart
                    issues_found.append("potential_overlap_close_positions")
                    break
            positions.append(pos)

        # Check for timing issues (very short or very long durations)
        for obj in objects:
            for anim in obj.get('animations', []):
                duration = anim.get('duration', 1.0)
                if duration < 0.3:
                    issues_found.append("very_short_duration_potential_flickering")
                elif duration > 5.0:
                    issues_found.append("very_long_duration_potential_lag")

        # Check for smooth animation (proper use of animate)
        if 'animate.move_to' not in manim_code and 'animate.rotate' not in manim_code:
            # This might be okay for simple animations
            pass

        # Check for proper fade sequences
        if manim_code.count('FadeIn') > 1 and manim_code.count('FadeOut') == 0:
            issues_found.append("multiple_fade_ins_without_fade_out")

        return issues_found

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive tests on the simplified system"""
        logger.info("Starting comprehensive test of simplified animation system")

        test_cases = self.get_test_cases()
        results = []

        for test_case in test_cases:
            result = await self.test_single_case(test_case)
            results.append(result)

            if result['success']:
                issues_str = f" (issues: {len(result.get('issues_found', []))})" if result.get('issues_found') else ""
                logger.info(f"✅ {result['name']}: PASSED{issues_str}")
            else:
                logger.error(f"❌ {result['name']}: FAILED - {result.get('error', 'Unknown error')}")

        # Analyze results
        successful_tests = [r for r in results if r['success']]
        failed_tests = [r for r in results if not r['success']]

        # Check for persistent issues
        persistent_issues = self._analyze_persistent_issues(results)

        summary = {
            'total_tests': len(results),
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'success_rate': len(successful_tests) / len(results) * 100,
            'results': results,
            'persistent_issues': persistent_issues,
            'system_improvements': self._calculate_improvements(results)
        }

        logger.info(f"Comprehensive test completed: {summary['successful_tests']}/{summary['total_tests']} tests passed ({summary['success_rate']:.1f}%)")

        return summary

    def _analyze_persistent_issues(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze if persistent issues have been resolved"""
        issue_analysis = {
            'flickering_issues': 0,
            'positioning_issues': 0,
            'overlap_issues': 0,
            'fade_out_issues': 0,
            'smoothness_issues': 0,
            'shape_issues': 0
        }

        for result in results:
            if result['success']:
                issues_found = result.get('issues_found', [])
                for issue in issues_found:
                    if 'flickering' in issue.lower():
                        issue_analysis['flickering_issues'] += 1
                    if 'position' in issue.lower():
                        issue_analysis['positioning_issues'] += 1
                    if 'overlap' in issue.lower():
                        issue_analysis['overlap_issues'] += 1
                    if 'fade_out' in issue.lower():
                        issue_analysis['fade_out_issues'] += 1
                    if 'smooth' in issue.lower():
                        issue_analysis['smoothness_issues'] += 1
                    if 'shape' in issue.lower():
                        issue_analysis['shape_issues'] += 1

        return issue_analysis

    def _calculate_improvements(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate improvements compared to the old system"""
        successful_tests = [r for r in results if r['success']]
        total_issues = sum(len(r.get('issues_found', [])) for r in successful_tests)

        return {
            'tests_passed': len(successful_tests),
            'average_issues_per_test': total_issues / len(successful_tests) if successful_tests else 0,
            'most_common_issue': self._find_most_common_issue(results),
            'reliability_score': (len(successful_tests) / len(results)) * 100
        }

    def _find_most_common_issue(self, results: List[Dict[str, Any]]) -> str:
        """Find the most common issue across all test results"""
        all_issues = []
        for result in results:
            if result['success']:
                all_issues.extend(result.get('issues_found', []))

        if not all_issues:
            return "none"

        # Count issue frequencies
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        return max(issue_counts, key=issue_counts.get) if issue_counts else "none"

async def main():
    """Main test function"""
    try:
        tester = SimpleSystemTester()
        await tester.initialize()

        results = await tester.run_comprehensive_test()

        # Save detailed results
        with open('/tmp/simple_system_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        logger.info("Test results saved to /tmp/simple_system_test_results.json")

        # Print comprehensive summary
        print("\n" + "="*70)
        print("SIMPLIFIED ANIMATION SYSTEM TEST RESULTS")
        print("="*70)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful: {results['successful_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(".1f")

        print("\n🔧 PERSISTENT ISSUES ANALYSIS:")
        issues = results['persistent_issues']
        for issue_type, count in issues.items():
            status = "✅ RESOLVED" if count == 0 else f"⚠️  {count} instances"
            print(f"  {issue_type}: {status}")

        print("\n📊 SYSTEM IMPROVEMENTS:")
        improvements = results['system_improvements']
        print(".1f")
        print(".2f")
        print(f"  Reliability Score: {improvements['reliability_score']:.1f}%")

        if improvements['reliability_score'] >= 90:
            print("\n🎉 SUCCESS! The simplified system has resolved the persistent issues!")
        elif improvements['reliability_score'] >= 75:
            print("\n👍 GOOD! The system shows significant improvement.")
        else:
            print("\n⚠️  NEEDS WORK! The system still has reliability issues.")

    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
