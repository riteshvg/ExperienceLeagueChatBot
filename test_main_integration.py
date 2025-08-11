#!/usr/bin/env python3
"""
Test the main app integration with segment creation
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test importing the main functions
    from app import detect_create_action, generate_segment_suggestions
    
    print("✅ Successfully imported main app functions")
    
    # Test a simple segment creation query
    test_query = "Create a segment for mobile users from California"
    
    print(f"\n🧪 Testing: '{test_query}'")
    
    # Test intent detection
    action_type, action_details = detect_create_action(test_query)
    
    if action_type == 'segment':
        print(f"✅ Action detected: {action_type}")
        print(f"✅ Intent details: {action_details}")
        
        # Test suggestions generation
        suggestions = generate_segment_suggestions(action_details)
        print(f"✅ Suggestions generated: {suggestions['segment_name']}")
        
        print("\n🎉 Main app integration test successful!")
        print("✅ Ready for full integration testing")
        
    else:
        print(f"❌ Expected segment action, got: {action_type}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 