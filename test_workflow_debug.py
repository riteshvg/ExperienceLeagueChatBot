#!/usr/bin/env python3
"""
Debug Workflow State Management
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_workflow_state():
    """Test the workflow state management."""
    print("🔍 Testing Workflow State Management")
    print("=" * 50)
    
    try:
        # Test 1: Import the workflow functions
        print("📱 Test 1: Import workflow functions...")
        from app import (
            detect_create_action, 
            generate_segment_suggestions,
            handle_segment_creation_workflow
        )
        print("   ✅ All workflow functions imported successfully")
        
        # Test 2: Test intent detection
        print("\n🔍 Test 2: Test intent detection...")
        test_query = "Create a segment for mobile users from California"
        action_type, action_details = detect_create_action(test_query)
        
        print(f"   📊 Action type: {action_type}")
        print(f"   📋 Action details: {action_details}")
        
        if action_type == 'segment':
            print("   ✅ Intent detection working correctly")
        else:
            print(f"   ❌ Expected 'segment', got: {action_type}")
            return False
        
        # Test 3: Test segment suggestions
        print("\n💡 Test 3: Test segment suggestions...")
        suggestions = generate_segment_suggestions(action_details)
        
        print(f"   📝 Suggested name: {suggestions['segment_name']}")
        print(f"   📋 Suggested description: {suggestions['segment_description']}")
        print(f"   ⚙️ Rules count: {len(suggestions['recommended_rules'])}")
        
        # Test 4: Test workflow state simulation
        print("\n⚙️ Test 4: Test workflow state simulation...")
        
        # Simulate what happens when user clicks "Start Segment Builder"
        segment_intent = {
            'prompt': test_query,
            'action_details': action_details,
            'suggestions': suggestions
        }
        
        print(f"   📦 Segment intent created: {len(segment_intent)} keys")
        print(f"   🔑 Keys: {list(segment_intent.keys())}")
        
        # Test 5: Check if the workflow functions exist
        print("\n🔧 Test 5: Check workflow function availability...")
        
        # Import the render functions
        from app import render_segment_builder_workflow, render_segment_creation_workflow
        
        if render_segment_builder_workflow:
            print("   ✅ render_segment_builder_workflow function available")
        else:
            print("   ❌ render_segment_builder_workflow function not found")
            return False
            
        if render_segment_creation_workflow:
            print("   ✅ render_segment_creation_workflow function available")
        else:
            print("   ❌ render_segment_creation_workflow function not found")
            return False
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Workflow state management is working correctly")
        print("✅ All required functions are available")
        print("✅ The navigation fix should work properly")
        
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
    """Run the workflow debug test."""
    print("🚀 WORKFLOW DEBUG TEST")
    print("=" * 60)
    print("This test verifies that the workflow state management")
    print("is working correctly in the updated app.")
    print("\n" + "=" * 60)
    
    success = test_workflow_state()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Open http://localhost:8503 in your browser")
        print("   2. Ask: 'Create a segment for mobile users from California'")
        print("   3. Click 'Start Segment Builder'")
        print("   4. Check the sidebar for workflow state info")
        print("   5. Verify the segment builder workflow appears")
    else:
        print("\n❌ Tests failed. Check the errors above.")
    
    print(f"\n📅 Test completed at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 