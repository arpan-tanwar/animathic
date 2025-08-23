#!/usr/bin/env python3
"""
Test script to verify the new intelligent fade-out logic
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_intelligent_fade_logic():
    """Test the new intelligent fade-out logic"""
    print("🔍 Testing Intelligent Fade-Out Logic...")
    
    try:
        from services.ai_service_new import AIService
        
        # Initialize AI service
        ai_service = AIService()
        print(f"✅ AI service initialized")
        
        # Test the complex prompt that was having fade-out issues
        test_prompt = "Create a coordinate system with multiple function plots (sine, cosine, tangent, exponential), add geometric shapes at key points, include detailed text annotations, and animate the appearance of each element in sequence with proper timing"
        print(f"📝 Testing prompt: {test_prompt}")
        
        # Process the animation request
        result = await ai_service.process_animation_request(test_prompt)
        
        if 'error' in result:
            print(f"❌ Failed: {result['error']}")
            return False
        
        # Check workflow type
        workflow_type = result.get('workflow_type', 'unknown')
        print(f"📊 Workflow used: {workflow_type}")
        
        # Check animation spec
        animation_spec = result.get('animation_spec', {})
        objects = animation_spec.get('objects', [])
        print(f"📋 Objects generated: {len(objects)}")
        
        # Analyze the fade logic
        print(f"\n🔍 Analyzing Fade Logic:")
        
        persistent_objects = []
        transient_objects = []
        
        for i, obj in enumerate(objects):
            obj_type = obj.get('type', 'unknown')
            obj_id = obj.get('id', 'unknown')
            animations = obj.get('animations', [])
            
            if obj_type in ['axes', 'plot']:
                persistent_objects.append(obj)
                print(f"  🔒 {obj_id} ({obj_type}): PERSISTENT - should remain visible")
                
                # Check if it has fade-out (it shouldn't!)
                fade_out_anims = [anim for anim in animations if anim.get('type') == 'fade_out']
                if fade_out_anims:
                    print(f"    ⚠️ WARNING: {obj_id} has {len(fade_out_anims)} fade-out animations (shouldn't!)")
                else:
                    print(f"    ✅ No fade-out animations (correct!)")
            else:
                transient_objects.append(obj)
                print(f"  🔄 {obj_id} ({obj_type}): TRANSIENT - can fade in/out")
                
                # Check fade animations
                fade_in_count = len([anim for anim in animations if anim.get('type') == 'fade_in'])
                fade_out_count = len([anim for anim in animations if anim.get('type') == 'fade_out'])
                print(f"    📊 Animations: {fade_in_count} fade-in, {fade_out_count} fade-out")
        
        print(f"\n📊 Summary:")
        print(f"  🔒 Persistent objects: {len(persistent_objects)} (axes, plots)")
        print(f"  🔄 Transient objects: {len(transient_objects)} (shapes, text, dots)")
        
        # Check if the logic is working correctly
        persistent_with_fade_out = [obj for obj in persistent_objects 
                                  if any(anim.get('type') == 'fade_out' for anim in obj.get('animations', []))]
        
        if persistent_with_fade_out:
            print(f"  ❌ ISSUE: {len(persistent_with_fade_out)} persistent objects have fade-out (shouldn't!)")
            for obj in persistent_with_fade_out:
                print(f"    - {obj.get('id', 'unknown')} ({obj.get('type', 'unknown')})")
        else:
            print(f"  ✅ SUCCESS: No persistent objects have fade-out animations")
        
        # Check Manim code
        manim_code = result.get('manim_code', '')
        print(f"📏 Manim code length: {len(manim_code)} characters")
        
        # Check for enhancements
        enhancements = result.get('enhancements_applied', [])
        if enhancements:
            print(f"🔧 Enhancements applied: {len(enhancements)}")
            for enhancement in enhancements:
                print(f"  - {enhancement}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Intelligent Fade-Out Logic Test")
    print("=" * 60)
    
    success = await test_intelligent_fade_logic()
    
    if success:
        print(f"\n✅ Test completed successfully")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
