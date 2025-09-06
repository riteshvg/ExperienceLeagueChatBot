#!/usr/bin/env python3
"""
Real Adobe Analytics Segment Creation Test

This test uses actual Adobe Analytics API credentials to create a real segment
for mobile users from India using the provided parameters.
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_real_segment_creation():
    """
    Test real segment creation with Adobe Analytics API
    """
    print("🧪 Real Adobe Analytics Segment Creation Test")
    print("=" * 60)
    
    # Test credentials from secrets.toml
    test_credentials = {
        "client_id": "a415b62f8f2f4b39a17456772e3425f7",
        "client_secret": "p8e-N00YM7OXw5ZJrx7-FMVFEgk6ocZhsT9V",
        "org_id": "0103FFA9573F6FF77F000101@AdobeOrg"
    }
    
    # Test parameters
    test_rsid = "argupAEPdemo"
    test_variables = ["eVar1", "eVar2"]
    
    print(f"📋 Test Parameters:")
    print(f"   RSID: {test_rsid}")
    print(f"   Variables: {', '.join(test_variables)}")
    print(f"   Target: Mobile users from India")
    print()
    
    try:
        # Step 1: Import required modules
        print("1️⃣ Importing modules...")
        from adobe_api_client import AdobeAnalyticsClient
        from segment_parser import detect_segment_request, parse_segment_components
        from variable_mapper import map_variable, get_missing_mappings, suggest_context
        from segment_builder import build_segment_definition, format_segment_summary
        print("   ✅ All modules imported successfully")
        
        # Step 2: Test segment detection and parsing
        print("\n2️⃣ Testing segment detection and parsing...")
        test_message = "Create a segment for mobile users from India"
        
        # Test detection
        is_segment = detect_segment_request(test_message)
        print(f"   Detection: {'✅ Segment detected' if is_segment else '❌ Not detected'}")
        
        # Test parsing
        components = parse_segment_components(test_message)
        print(f"   Parsed components: {len(components.get('conditions', []))} conditions")
        print(f"   Logic: {components.get('logic', 'unknown')}")
        print(f"   Context: {components.get('context', 'unknown')}")
        
        # Display parsed conditions
        for i, condition in enumerate(components.get('conditions', []), 1):
            print(f"   Condition {i}: {condition}")
        
        # Step 3: Test variable mapping
        print("\n3️⃣ Testing variable mapping...")
        mapped_components = []
        missing_mappings = []
        
        for condition in components.get('conditions', []):
            mapped = map_variable(condition)
            if mapped.get('name'):
                mapped_components.append(mapped)
                print(f"   Mapped: {condition['variable']} -> {mapped['name']}")
            else:
                missing_mappings.append(condition)
                print(f"   Missing mapping: {condition['variable']}")
        
        # Step 4: Handle missing mappings for eVar1 and eVar2
        print("\n4️⃣ Handling missing mappings...")
        user_inputs = {}
        
        # Map device to eVar1 (mobile device type)
        if any(c['variable'] == 'device' for c in components.get('conditions', [])):
            user_inputs['device'] = {
                "name": "variables/evar1",
                "operator": "streq",
                "value": "Mobile Phone"
            }
            print("   ✅ Mapped device to eVar1")
        
        # Map geography to eVar2 (country) - override the parsed value
        if any(c['variable'] == 'geography' for c in components.get('conditions', [])):
            user_inputs['geography'] = {
                "name": "variables/evar2", 
                "operator": "streq",
                "value": "India"  # Override the parsed value
            }
            print("   ✅ Mapped geography to eVar2 (India)")
        
        # Also add a custom condition for India if not detected
        if not any(c['variable'] == 'geography' for c in components.get('conditions', [])):
            user_inputs['custom_geography'] = {
                "name": "variables/evar2",
                "operator": "streq", 
                "value": "India"
            }
            print("   ✅ Added custom geography condition for India (eVar2)")
        
        # Step 5: Build segment definition
        print("\n5️⃣ Building segment definition...")
        segment_definition = build_segment_definition(
            components.get('conditions', []),
            mapped_components,
            user_inputs
        )
        
        # Update with test parameters
        segment_definition['rsid'] = test_rsid
        segment_definition['name'] = f"Mobile Users from India - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        segment_definition['description'] = "Test segment for mobile users from India created via API"
        
        print(f"   Segment Name: {segment_definition['name']}")
        print(f"   RSID: {segment_definition['rsid']}")
        
        # Step 6: Format segment summary
        print("\n6️⃣ Formatting segment summary...")
        summary = format_segment_summary(segment_definition)
        print("   Segment Summary:")
        for line in summary.split('\n'):
            if line.strip():
                print(f"     {line}")
        
        # Step 7: Initialize Adobe Analytics client
        print("\n7️⃣ Initializing Adobe Analytics client...")
        client = AdobeAnalyticsClient(
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"],
            org_id=test_credentials["org_id"]
        )
        print("   ✅ Client initialized successfully")
        print(f"   Access Token: {client.access_token[:20]}..." if client.access_token else "   No access token")
        print(f"   Company ID: {client.company_id}")
        print(f"   Base URL: {client.base_url}")
        
        # Step 8: Test connection
        print("\n8️⃣ Testing API connection...")
        connection_test = client.test_connection()
        if connection_test.get('success'):
            print("   ✅ API connection successful")
            print(f"   Company ID: {client.company_id}")
            print(f"   Base URL: {client.base_url}")
        else:
            print(f"   ❌ API connection failed: {connection_test.get('message', 'Unknown error')}")
            return False
        
        # Step 9: Validate segment
        print("\n9️⃣ Validating segment definition...")
        validation_result = client.validate_segment(segment_definition['definition'], test_rsid)
        
        if validation_result.get('success'):
            print("   ✅ Segment validation successful")
            print(f"   Validation response: {validation_result.get('message', 'Valid')}")
        else:
            print(f"   ❌ Segment validation failed: {validation_result.get('message', 'Unknown error')}")
            if 'error' in validation_result:
                print(f"   Error details: {validation_result['error']}")
            return False
        
        # Step 10: Create segment
        print("\n🔟 Creating segment in Adobe Analytics...")
        creation_result = client.create_segment(segment_definition)
        
        if creation_result.get('success'):
            print("   🎉 Segment created successfully!")
            print(f"   Status Code: {creation_result.get('status_code')}")
            print(f"   Message: {creation_result.get('message')}")
            
            # Display segment details
            if 'data' in creation_result:
                segment_data = creation_result['data']
                print(f"   Segment ID: {segment_data.get('id', 'N/A')}")
                print(f"   Segment Name: {segment_data.get('name', 'N/A')}")
                print(f"   Created: {segment_data.get('created', 'N/A')}")
                print(f"   Modified: {segment_data.get('modified', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ Segment creation failed: {creation_result.get('message', 'Unknown error')}")
            if 'error' in creation_result:
                print(f"   Error details: {creation_result['error']}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_segment_retrieval():
    """
    Test retrieving the created segment
    """
    print("\n🔍 Testing Segment Retrieval")
    print("=" * 40)
    
    try:
        from adobe_api_client import AdobeAnalyticsClient
        
        # Initialize client
        client = AdobeAnalyticsClient(
            client_id="a415b62f8f2f4b39a17456772e3425f7",
            client_secret="p8e-N00YM7OXw5ZJrx7-FMVFEgk6ocZhsT9V",
            org_id="0103FFA9573F6FF77F000101@AdobeOrg"
        )
        
        # List segments
        print("📋 Listing segments...")
        segments_result = client.list_segments("argupAEPdemo", limit=10)
        
        if segments_result.get('success'):
            segments = segments_result.get('data', {}).get('content', [])
            print(f"   Found {len(segments)} segments")
            
            # Look for our test segment
            test_segments = [s for s in segments if 'Mobile Users from India' in s.get('name', '')]
            if test_segments:
                print("   ✅ Found our test segment:")
                for segment in test_segments:
                    print(f"     - {segment.get('name')} (ID: {segment.get('id')})")
            else:
                print("   ℹ️ Test segment not found in recent segments")
        else:
            print(f"   ❌ Failed to list segments: {segments_result.get('message')}")
            
    except Exception as e:
        print(f"   ❌ Segment retrieval test failed: {str(e)}")

def main():
    """
    Main test function
    """
    print("🚀 Starting Real Adobe Analytics Segment Creation Test")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run the main test
    success = test_real_segment_creation()
    
    # Run retrieval test
    test_segment_retrieval()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ Real segment created in Adobe Analytics")
    else:
        print("❌ Test failed - check error messages above")
    
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
