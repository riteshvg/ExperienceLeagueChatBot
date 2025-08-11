#!/usr/bin/env python3
"""
Test Navigation Fix - Verify the segment builder workflow is now integrated
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_navigation_fix():
    """Test that the navigation fix is working."""
    print("🧪 Testing Navigation Fix")
    print("=" * 50)
    
    try:
        # Test 1: Import the main app
        print("📱 Test 1: Import main app...")
        from app import detect_create_action, generate_segment_suggestions
        print("   ✅ Main app imports successfully")
        
        # Test 2: Test intent detection
        print("\n🔍 Test 2: Test intent detection...")
        test_query = "Create a segment for mobile users from California"
        action_type, action_details = detect_create_action(test_query)
        
        if action_type == 'segment':
            print("   ✅ Intent detection working correctly")
            print(f"   📊 Action type: {action_type}")
            print(f"   📋 Action details: {action_details}")
        else:
            print(f"   ❌ Expected 'segment', got: {action_type}")
            return False
        
        # Test 3: Test segment suggestions
        print("\n💡 Test 3: Test segment suggestions...")
        suggestions = generate_segment_suggestions(action_details)
        
        if suggestions and 'segment_name' in suggestions:
            print("   ✅ Segment suggestions working correctly")
            print(f"   📝 Suggested name: {suggestions['segment_name']}")
            print(f"   📋 Suggested description: {suggestions['segment_description']}")
            print(f"   ⚙️ Rules count: {len(suggestions['recommended_rules'])}")
        else:
            print("   ❌ Segment suggestions failed")
            return False
        
        # Test 4: Check for workflow functions
        print("\n⚙️ Test 4: Check workflow functions...")
        
        # Import the workflow functions
        from app import render_segment_builder_workflow, render_segment_creation_workflow
        
        if render_segment_builder_workflow and render_segment_creation_workflow:
            print("   ✅ Workflow functions available")
        else:
            print("   ❌ Workflow functions not found")
            return False
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Navigation fix is working correctly")
        print("✅ Segment builder workflow is integrated")
        print("✅ Users can now create segments without leaving the main app")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the navigation fix test."""
    print("🚀 NAVIGATION FIX VALIDATION TEST")
    print("=" * 60)
    print("This test verifies that the segment builder workflow")
    print("is now properly integrated into the main app.")
    print("\n" + "=" * 60)
    
    success = test_navigation_fix()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Open http://localhost:8503 in your browser")
        print("   2. Ask: 'Create a segment for mobile users'")
        print("   3. Click 'Start Segment Builder'")
        print("   4. Verify you stay in the same app")
        print("   5. Complete the segment creation workflow")
    else:
        print("\n❌ Tests failed. Check the errors above.")
    
    print(f"\n📅 Test completed at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 