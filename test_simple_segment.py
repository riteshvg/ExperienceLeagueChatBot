#!/usr/bin/env python3
"""
Simple Segment Test - Using the exact working structure
"""

import sys
import os
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from adobe_api import create_analytics_segment_from_json, get_company_id
    
    print("✅ Successfully imported Adobe API components")
    
    # Test the exact working structure from our previous successful tests
    test_payload = {
        "name": f"Simple Test Segment {datetime.now().strftime('%H:%M:%S')}",
        "description": "Simple test segment using working structure",
        "rsid": "argupaepdemo",
        "definition": {
            "version": [1, 0, 0],
            "func": "segment",
            "container": {
                "func": "container",
                "context": "visitors",
                "pred": {
                    "func": "streq",
                    "val": {
                        "func": "attr",
                        "name": "variables/page"
                    },
                    "str": "Homepage"
                }
            }
        }
    }
    
    print(f"\n🚀 Testing Simple Segment Creation")
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Test RSID: argupaepdemo")
    print("=" * 60)
    
    # Step 1: Validate Adobe Analytics Connection
    print("\n🔌 Step 1: Adobe Analytics Connection Validation")
    print("-" * 50)
    
    try:
        company_id = get_company_id()
        if company_id:
            print(f"✅ Company ID: {company_id}")
            print(f"✅ Adobe Analytics connection: SUCCESS")
        else:
            print(f"❌ Company ID not found")
            print(f"❌ Adobe Analytics connection: FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        sys.exit(1)
    
    # Step 2: Test Segment Creation
    print("\n⚙️ Step 2: Segment Creation Test")
    print("-" * 50)
    
    print(f"📱 Testing Segment: {test_payload['name']}")
    print(f"   Description: {test_payload['description']}")
    print(f"   Structure: Single rule with 'streq' function")
    
    # Display the payload structure
    print(f"\n📦 Payload Structure:")
    print(json.dumps(test_payload, indent=2))
    
    # Step 3: Execute Segment Creation
    print(f"\n🚀 Executing segment creation in Adobe Analytics...")
    
    result = create_analytics_segment_from_json(test_payload)
    
    if result.get('status') == 'success':
        segment_data = result.get('data', {})
        segment_id = segment_data.get('id', 'Unknown')
        print(f"   🎉 Segment created successfully!")
        print(f"   ✅ Segment ID: {segment_id}")
        print(f"   ✅ Segment Name: {test_payload['name']}")
        
        print(f"\n🎉 SUCCESS! Simple segment creation is working!")
        print(f"✅ This confirms the basic structure is correct")
        print(f"✅ We can now build upon this for more complex segments")
        
    else:
        print(f"   ❌ Segment creation failed: {result.get('message', 'Unknown error')}")
        print(f"\n❌ FAILED! Need to investigate the basic structure")
        print(f"❌ Error details: {result}")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 