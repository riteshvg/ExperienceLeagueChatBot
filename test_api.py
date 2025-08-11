#!/usr/bin/env python3
"""
Adobe Analytics 2.0 API Test Script
Standalone script to test authentication and API access
"""

import requests
import os
import json

# ============================================================================
# CREDENTIALS - REPLACE THESE WITH YOUR ACTUAL VALUES
# ============================================================================
CLIENT_ID = "a415b62f8f2f4b39a17456772e3425f7"
CLIENT_SECRET = "p8e-N00YM7OXw5ZJrx7-FMVFEgk6ocZhsT9V"
COMPANY_ID = "adober1f"

# ============================================================================
# FUNCTIONS
# ============================================================================

def get_adobe_access_token(client_id, client_secret):
    """
    Get Adobe access token using client credentials flow.
    
    Args:
        client_id (str): Adobe client ID
        client_secret (str): Adobe client secret
        
    Returns:
        str: Access token if successful, None if failed
    """
    print("🔐 Getting Adobe access token...")
    
    # Adobe token endpoint URL
    token_endpoint = "https://ims-na1.adobelogin.com/ims/token/v3"
    
    # Required scopes for Adobe Analytics API
    scopes = "openid, AdobeID, additional_info.projectedProductContext"
    
    # Request payload
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scopes
    }
    
    # Request headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        print(f"📤 Making POST request to: {token_endpoint}")
        print(f"📤 Payload: {payload}")
        print(f"📤 Headers: {headers}")
        
        # Make POST request
        response = requests.post(
            token_endpoint,
            data=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                token_data = response.json()
                access_token = token_data.get('access_token')
                if access_token:
                    print(f"✅ Access token obtained successfully!")
                    print(f"✅ Token type: {token_data.get('token_type', 'Unknown')}")
                    print(f"✅ Expires in: {token_data.get('expires_in', 'Unknown')} seconds")
                    print(f"✅ Scope: {token_data.get('scope', 'Unknown')}")
                    return access_token
                else:
                    print(f"❌ No access_token in response")
                    print(f"📥 Response body: {response.text}")
                    return None
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"📥 Response text: {response.text}")
                return None
        else:
            print(f"❌ Token request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"📥 Error details: {error_data}")
            except:
                print(f"📥 Response text: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def get_adobe_segments(access_token, client_id, company_id):
    """
    Get Adobe Analytics segments using the access token.
    
    Args:
        access_token (str): Valid access token
        client_id (str): Adobe client ID
        company_id (str): Adobe company ID
        
    Returns:
        bool: True if successful, False if failed
    """
    print(f"\n📊 Getting Adobe Analytics segments for company: {company_id}")
    
    # Construct API endpoint URL
    segments_endpoint = f"https://analytics.adobe.io/api/{company_id}/segments"
    
    # Request headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-api-key': client_id,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        print(f"📤 Making GET request to: {segments_endpoint}")
        print(f"📤 Headers: {headers}")
        
        # Make GET request
        response = requests.get(
            segments_endpoint,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        # Check if request was successful
        if response.status_code == 200:
            print("✅ Successfully retrieved segments!")
            try:
                segments_data = response.json()
                print(f"📥 Response body: {json.dumps(segments_data, indent=2)}")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"📥 Response text: {response.text}")
                return False
        else:
            print(f"❌ Segments request failed with status {response.status_code}")
            
            # Print response headers (especially x-request-id)
            if 'x-request-id' in response.headers:
                print(f"📥 x-request-id: {response.headers['x-request-id']}")
            
            # Try to get error details
            try:
                error_data = response.json()
                print(f"📥 Error details: {error_data}")
            except:
                print(f"📥 Response text: {response.text}")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def create_adobe_segment(access_token, client_id, company_id, segment_name, segment_description):
    """
    Create Adobe Analytics segment using POST method.
    
    Args:
        access_token (str): Valid access token
        client_id (str): Adobe client ID
        company_id (str): Adobe company ID
        segment_name (str): Name of the segment to create
        segment_description (str): Description of the segment
        
    Returns:
        bool: True if successful, False if failed
    """
    print(f"\n🆕 Creating Adobe Analytics segment: {segment_name}")
    
    # Construct API endpoint URL for segment creation
    segments_endpoint = f"https://analytics.adobe.io/api/{company_id}/segments"
    
    # Request headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-api-key': client_id,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Sample segment definition for testing - using minimal format
    segment_definition = {
        "name": segment_name,
        "description": segment_description,
        "organization": "794867A5D7455CD67F000101@AdobeOrg",  # From the token response
        "rsid": "argupaepdemo",  # Report Suite ID
        "definition": {
            "func": "segment",
            "expr": {
                "func": "attr",
                "name": "evar1"
            },
            "comp": "eq",
            "val": "test_value"
        }
    }
    
    try:
        print(f"📤 Making POST request to: {segments_endpoint}")
        print(f"📤 Headers: {headers}")
        print(f"📤 Request body: {json.dumps(segment_definition, indent=2)}")
        
        # Make POST request to create segment
        response = requests.post(
            segments_endpoint,
            headers=headers,
            json=segment_definition,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        # Check if request was successful
        if response.status_code in [200, 201, 202]:
            print("✅ Successfully created segment!")
            try:
                response_data = response.json()
                print(f"📥 Response body: {json.dumps(response_data, indent=2)}")
                return True
            except json.JSONDecodeError as e:
                print(f"📥 Response text: {response.text}")
                return True  # Still consider it successful if we can't parse JSON
        else:
            print(f"❌ Segment creation failed with status {response.status_code}")
            
            # Print response headers (especially x-request-id)
            if 'x-request-id' in response.headers:
                print(f"📥 x-request-id: {response.headers['x-request-id']}")
            
            # Try to get error details
            try:
                error_data = response.json()
                print(f"📥 Error details: {error_data}")
            except:
                print(f"📥 Response text: {response.text}")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🚀 Adobe Analytics 2.0 API Test Script")
    print("=" * 50)
    
    # Check if credentials are set
    if CLIENT_ID == "YOUR_CLIENT_ID_HERE" or CLIENT_SECRET == "YOUR_CLIENT_SECRET_HERE" or COMPANY_ID == "YOUR_COMPANY_ID_HERE":
        print("❌ Please update the credentials at the top of this script!")
        print("   - CLIENT_ID")
        print("   - CLIENT_SECRET") 
        print("   - COMPANY_ID")
        exit(1)
    
    print(f"🔑 Using Client ID: {CLIENT_ID}")
    print(f"🏢 Using Company ID: {COMPANY_ID}")
    print(f"🔐 Client Secret: {'*' * len(CLIENT_SECRET)}")
    print()
    
    # Step 1: Get access token
    print("Step 1: Getting access token...")
    access_token = get_adobe_access_token(CLIENT_ID, CLIENT_SECRET)
    
    if access_token:
        print(f"✅ Access Token obtained successfully!")
        print(f"✅ Token: {access_token[:20]}...{access_token[-10:]}")
        print()
        
        # Step 2: Get segments
        print("Step 2: Getting segments...")
        success = get_adobe_segments(access_token, CLIENT_ID, COMPANY_ID)
        
        if success:
            print("✅ Successfully retrieved segments!")
            
            # Step 3: Create a test segment
            print("\n" + "="*50)
            print("Step 3: Creating test segment...")
            segment_created = create_adobe_segment(
                access_token, 
                CLIENT_ID, 
                COMPANY_ID, 
                "Test Segment from API", 
                "This is a test segment created via Adobe Analytics 2.0 API"
            )
            
            if segment_created:
                print("🎉 All tests passed successfully!")
            else:
                print("❌ Failed to create segment")
        else:
            print("❌ Failed to get segments")
    else:
        print("❌ Failed to get access token. Exiting.")
        exit(1)
    
    print("\n🏁 Test completed!") 