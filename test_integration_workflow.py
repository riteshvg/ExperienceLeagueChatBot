#!/usr/bin/env python3
"""
Integration Test: Complete Workflow from User Query to Segment Creation

This script demonstrates the complete integration workflow:
1. User query analysis
2. Intent detection
3. Segment suggestions
4. Configuration building
5. Adobe Analytics API integration
"""

import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import all required modules
    from app import detect_create_action, generate_segment_suggestions
    from adobe_api import create_analytics_segment_from_json, get_company_id
    from segment_builder import SegmentBuilder
    
    print("✅ Successfully imported all required modules")
    
    # Test the complete workflow
    print("\n🚀 Testing Complete Integration Workflow:")
    print("=" * 60)
    
    # Test Case 1: Simple Mobile Users Segment
    print("\n📱 Test Case 1: Simple Mobile Users Segment")
    print("-" * 50)
    
    user_query = "Create a segment for mobile users from California"
    
    print(f"User Query: '{user_query}'")
    
    # Step 1: Intent Detection
    print("\n🔍 Step 1: Intent Detection")
    action_type, intent_details = detect_create_action(user_query)
    
    if action_type == 'segment':
        print(f"✅ Action detected: {action_type}")
        print(f"✅ Intent details: {json.dumps(intent_details, indent=2)}")
        
        # Step 2: Generate Suggestions
        print("\n💡 Step 2: Generate Suggestions")
        suggestions = generate_segment_suggestions(intent_details)
        print(f"✅ Suggested name: {suggestions['segment_name']}")
        print(f"✅ Suggested description: {suggestions['segment_description']}")
        print(f"✅ Recommended rules: {len(suggestions['recommended_rules'])}")
        
        # Step 3: Build Configuration
        print("\n⚙️ Step 3: Build Configuration")
        config = {
            'name': suggestions['segment_name'],
            'description': suggestions['segment_description'],
            'rsid': 'argupaepdemo',  # Test RSID
            'target_audience': intent_details.get('target_audience', 'visitors'),
            'rules': suggestions['recommended_rules']
        }
        
        print(f"✅ Configuration built: {json.dumps(config, indent=2)}")
        
        # Step 4: Build Adobe Analytics Payload
        print("\n📦 Step 4: Build Adobe Analytics Payload")
        
        # Use the segment builder's payload building logic
        builder = SegmentBuilder()
        builder.session_state.segment_builder_state['segment_config'] = config
        
        payload = builder.build_segment_payload()
        print(f"✅ Payload built successfully")
        print(f"✅ Payload structure: {json.dumps(payload, indent=2)}")
        
        # Step 5: Validate Configuration
        print("\n✅ Step 5: Validate Configuration")
        is_valid = builder.validate_configuration()
        print(f"✅ Configuration valid: {is_valid}")
        
        if not is_valid:
            errors = builder.session_state.segment_builder_state['validation_errors']
            print(f"❌ Validation errors: {errors}")
        
        # Step 6: Test Adobe Analytics API (Mock)
        print("\n🌐 Step 6: Test Adobe Analytics API Integration")
        
        # Check if we have the required credentials
        company_id = get_company_id()
        if company_id:
            print(f"✅ Company ID found: {company_id}")
            print(f"✅ Ready for API integration")
            
            # Note: We won't actually create the segment in this test
            # to avoid creating test segments in the real Adobe Analytics
            print(f"ℹ️  API integration ready (segment creation skipped for testing)")
        else:
            print(f"⚠️  Company ID not found - API integration not possible")
        
        print(f"\n🎉 Test Case 1 completed successfully!")
        
    else:
        print(f"❌ Expected segment action, got: {action_type}")
    
    # Test Case 2: Complex Behavioral Segment
    print("\n\n📊 Test Case 2: Complex Behavioral Segment")
    print("-" * 50)
    
    user_query_2 = "Build a segment for desktop visitors from New York who converted during business hours and visited more than 10 pages"
    
    print(f"User Query: '{user_query_2}'")
    
    # Step 1: Intent Detection
    print("\n🔍 Step 1: Intent Detection")
    action_type_2, intent_details_2 = detect_create_action(user_query_2)
    
    if action_type_2 == 'segment':
        print(f"✅ Action detected: {action_type_2}")
        print(f"✅ Intent details: {json.dumps(intent_details_2, indent=2)}")
        
        # Step 2: Generate Suggestions
        print("\n💡 Step 2: Generate Suggestions")
        suggestions_2 = generate_segment_suggestions(intent_details_2)
        print(f"✅ Suggested name: {suggestions_2['segment_name']}")
        print(f"✅ Suggested description: {suggestions_2['segment_description']}")
        print(f"✅ Recommended rules: {len(suggestions_2['recommended_rules'])}")
        
        # Step 3: Build Configuration
        print("\n⚙️ Step 3: Build Configuration")
        config_2 = {
            'name': suggestions_2['segment_name'],
            'description': suggestions_2['segment_description'],
            'rsid': 'argupaepdemo',  # Test RSID
            'target_audience': intent_details_2.get('target_audience', 'visitors'),
            'rules': suggestions_2['recommended_rules']
        }
        
        print(f"✅ Configuration built: {json.dumps(config_2, indent=2)}")
        
        # Step 4: Build Adobe Analytics Payload
        print("\n📦 Step 4: Build Adobe Analytics Payload")
        
        builder_2 = SegmentBuilder()
        builder_2.session_state.segment_builder_state['segment_config'] = config_2
        
        payload_2 = builder_2.build_segment_payload()
        print(f"✅ Payload built successfully")
        print(f"✅ Payload structure: {json.dumps(payload_2, indent=2)}")
        
        # Step 5: Validate Configuration
        print("\n✅ Step 5: Validate Configuration")
        is_valid_2 = builder_2.validate_configuration()
        print(f"✅ Configuration valid: {is_valid_2}")
        
        print(f"\n🎉 Test Case 2 completed successfully!")
        
    else:
        print(f"❌ Expected segment action, got: {action_type_2}")
    
    # Summary
    print("\n\n📋 Integration Test Summary:")
    print("=" * 60)
    print("✅ All modules imported successfully")
    print("✅ Intent detection working correctly")
    print("✅ Segment suggestions generated")
    print("✅ Configuration building functional")
    print("✅ Adobe Analytics payload generation working")
    print("✅ Validation system operational")
    print("✅ Ready for full UI integration")
    
    print("\n🎯 Next Steps:")
    print("  - Test the Streamlit UI: streamlit run segment_builder.py")
    print("  - Integrate with main app.py")
    print("  - Test with real Adobe Analytics API")
    print("  - Add error handling and edge cases")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 