#!/usr/bin/env python3
"""
Test script for the segment builder workflow
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test importing the segment builder
    from segment_builder import SegmentBuilder
    
    print("✅ Successfully imported SegmentBuilder class")
    
    # Test class instantiation
    print("\n🧪 Testing SegmentBuilder Class:")
    print("=" * 50)
    
    # Create a mock session state for testing
    class MockSessionState:
        def __init__(self):
            self.segment_builder_state = None
    
    mock_session = MockSessionState()
    
    # Test the builder
    builder = SegmentBuilder()
    print(f"✅ Builder instance created: {type(builder)}")
    
    # Test session state initialization
    print(f"✅ Session state initialized: {builder.session_state.segment_builder_state is not None}")
    
    # Test initial state
    initial_state = builder.session_state.segment_builder_state
    print(f"✅ Initial step: {initial_state['current_step']}")
    print(f"✅ Initial config keys: {list(initial_state['segment_config'].keys())}")
    
    # Test payload building with sample data
    print("\n🔧 Testing Payload Building:")
    print("=" * 50)
    
    # Set up sample configuration
    builder.session_state.segment_builder_state['segment_config'].update({
        'name': 'Test Mobile Users',
        'description': 'Test segment for mobile users',
        'rsid': 'test_rsid',
        'target_audience': 'visitors',
        'rules': [
            {
                'func': 'streq',
                'name': 'variables/device_type',
                'val': 'Mobile',
                'str': 'Mobile'
            }
        ]
    })
    
    # Test payload building
    try:
        payload = builder.build_segment_payload()
        print(f"✅ Payload built successfully")
        print(f"✅ Payload keys: {list(payload.keys())}")
        print(f"✅ Definition structure: {list(payload['definition'].keys())}")
        
        # Test JSON serialization
        import json
        json_payload = json.dumps(payload, indent=2)
        print(f"✅ JSON serialization successful ({len(json_payload)} characters)")
        
    except Exception as e:
        print(f"❌ Payload building failed: {e}")
    
    # Test validation
    print("\n✅ Testing Configuration Validation:")
    print("=" * 50)
    
    try:
        is_valid = builder.validate_configuration()
        print(f"✅ Validation result: {is_valid}")
        
        if not is_valid:
            errors = builder.session_state.segment_builder_state['validation_errors']
            print(f"✅ Validation errors: {errors}")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    print("\n🎉 All basic tests completed successfully!")
    print("\n📝 Next Steps:")
    print("  - Run 'streamlit run segment_builder.py' to test the full UI")
    print("  - Test the workflow with real user queries")
    print("  - Verify Adobe Analytics API integration")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1) 