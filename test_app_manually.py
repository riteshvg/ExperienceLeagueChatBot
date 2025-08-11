#!/usr/bin/env python3
"""
Manual Testing Script for Adobe Analytics ChatBot

This script allows you to test the application functionality step by step.
Run this to verify each component is working correctly.
"""

import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_intent_detection():
    """Test the intent detection system."""
    print("🔍 Testing Intent Detection System")
    print("=" * 50)
    
    try:
        from app import detect_create_action
        
        test_queries = [
            "Create a segment for mobile users from California",
            "Build a segment for desktop visitors with high page views",
            "Make a segment for users from New York who converted",
            "What is Adobe Analytics?",
            "How do I create a report?"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            action_type, action_details = detect_create_action(query)
            print(f"   Action: {action_type}")
            if action_details:
                print(f"   Details: {json.dumps(action_details, indent=6)}")
        
        print("\n✅ Intent detection test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Intent detection test failed: {e}")
        return False

def test_segment_suggestions():
    """Test the segment suggestions system."""
    print("\n💡 Testing Segment Suggestions System")
    print("=" * 50)
    
    try:
        from app import generate_segment_suggestions
        
        test_intents = [
            {
                'action_type': 'segment',
                'target_audience': 'visitors',
                'device': 'mobile',
                'geographic': 'country'
            },
            {
                'action_type': 'segment',
                'target_audience': 'visitors',
                'device': 'desktop',
                'behavioral': ['page_views']
            }
        ]
        
        for i, intent in enumerate(test_intents):
            print(f"\n📱 Test Intent {i+1}:")
            print(f"   Intent: {json.dumps(intent, indent=6)}")
            
            suggestions = generate_segment_suggestions(intent)
            print(f"   Name: {suggestions['segment_name']}")
            print(f"   Description: {suggestions['segment_description']}")
            print(f"   Rules: {len(suggestions['recommended_rules'])} rules")
            
            for j, rule in enumerate(suggestions['recommended_rules']):
                print(f"     Rule {j+1}: {rule['func']} on {rule['name']}")
        
        print("\n✅ Segment suggestions test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Segment suggestions test failed: {e}")
        return False

def test_adobe_api_connection():
    """Test the Adobe Analytics API connection."""
    print("\n🌐 Testing Adobe Analytics API Connection")
    print("=" * 50)
    
    try:
        from adobe_api import get_company_id, get_adobe_access_token
        
        # Test company ID
        print("🔍 Testing Company ID retrieval...")
        company_id = get_company_id()
        if company_id:
            print(f"   ✅ Company ID: {company_id}")
        else:
            print("   ❌ Company ID not found")
            return False
        
        # Test access token
        print("🔑 Testing Access Token retrieval...")
        access_token = get_adobe_access_token()
        if access_token:
            print(f"   ✅ Access Token: {access_token[:20]}...")
        else:
            print("   ❌ Access Token not found")
            return False
        
        print("\n✅ Adobe API connection test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Adobe API connection test failed: {e}")
        return False

def test_segment_builder():
    """Test the segment builder functionality."""
    print("\n⚙️ Testing Segment Builder")
    print("=" * 50)
    
    try:
        from segment_builder import SegmentBuilder
        
        # Create builder instance
        print("🔧 Creating Segment Builder instance...")
        builder = SegmentBuilder()
        print("   ✅ Builder instance created")
        
        # Test session state
        print("📊 Testing session state...")
        if hasattr(builder, 'session_state'):
            print("   ✅ Session state available")
        else:
            print("   ❌ Session state not available")
            return False
        
        # Test configuration building
        print("📦 Testing configuration building...")
        test_config = {
            'name': 'Test Segment',
            'description': 'Test segment for validation',
            'rsid': 'argupaepdemo',
            'target_audience': 'visitors',
            'rules': [
                {
                    'func': 'streq',
                    'name': 'variables/evar1',
                    'val': 'Mobile',
                    'str': 'Mobile'
                }
            ]
        }
        
        builder.session_state.segment_builder_state['segment_config'] = test_config
        
        # Test payload building
        payload = builder.build_segment_payload()
        print("   ✅ Payload built successfully")
        print(f"   📋 Payload keys: {list(payload.keys())}")
        
        print("\n✅ Segment builder test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Segment builder test failed: {e}")
        return False

def test_error_handling():
    """Test the error handling system."""
    print("\n🚨 Testing Error Handling System")
    print("=" * 50)
    
    try:
        from error_handling import handle_segment_creation_error, validate_segment_configuration
        
        # Test error handling
        print("🔧 Testing error handling...")
        test_error = ValueError("Test validation error")
        result = handle_segment_creation_error(test_error, "Test Context")
        print(f"   ✅ Error handled: {result['category']} - {result['severity']}")
        
        # Test validation
        print("✅ Testing validation...")
        is_valid, errors = validate_segment_configuration("Test", "valid123", [])
        print(f"   ✅ Validation result: {is_valid}")
        if errors:
            print(f"   📝 Errors: {errors}")
        
        print("\n✅ Error handling test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 MANUAL TESTING SCRIPT FOR ADOBE ANALYTICS CHATBOT")
    print("=" * 70)
    print("This script will test each component of the application.")
    print("Make sure all required services are running before starting.")
    print("\n📱 Required Services:")
    print("   - Main App: http://localhost:8503")
    print("   - Segment Builder: http://localhost:8502")
    print("   - Test Adobe API: http://localhost:8501")
    print("\n" + "=" * 70)
    
    # Run all tests
    tests = [
        ("Intent Detection", test_intent_detection),
        ("Segment Suggestions", test_segment_suggestions),
        ("Adobe API Connection", test_adobe_api_connection),
        ("Segment Builder", test_segment_builder),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The application is working correctly.")
        print("\n🚀 Next Steps:")
        print("   1. Open http://localhost:8503 in your browser")
        print("   2. Try asking: 'Create a segment for mobile users'")
        print("   3. Follow the workflow to create a real segment")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure all Streamlit apps are running")
        print("   2. Check your Adobe Analytics credentials")
        print("   3. Verify all dependencies are installed")
    
    print(f"\n📅 Testing completed at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 