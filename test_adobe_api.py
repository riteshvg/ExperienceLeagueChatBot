#!/usr/bin/env python3
"""
Test script for Adobe Analytics 2.0 API functionality.
This script demonstrates how to use the adobe_api.py module with enhanced testing capabilities.
"""

import streamlit as st
import requests
import json
from adobe_api import (
    test_api_connection, 
    create_sample_segment, 
    validate_oauth_secrets,
    validate_api_secrets,
    get_company_id,
    get_adobe_access_token
)

def get_adobe_segments_enhanced(access_token, client_id, company_id):
    """
    Enhanced function to get Adobe Analytics segments using the access token.
    
    Args:
        access_token (str): Valid access token
        client_id (str): Adobe client ID
        company_id (str): Adobe company ID
        
    Returns:
        bool: True if successful, False if failed
    """
    st.info(f"📊 Getting Adobe Analytics segments for company: {company_id}")
    
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
        st.info(f"📤 Making GET request to: {segments_endpoint}")
        
        # Make GET request
        response = requests.get(
            segments_endpoint,
            headers=headers,
            timeout=30
        )
        
        st.info(f"📥 Response status: {response.status_code}")
        
        # Check if request was successful
        if response.status_code == 200:
            st.success("✅ Successfully retrieved segments!")
            try:
                segments_data = response.json()
                st.json(segments_data)
                return True
            except json.JSONDecodeError as e:
                st.error(f"❌ Failed to parse JSON response: {e}")
                st.text(f"📥 Response text: {response.text}")
                return False
        else:
            st.error(f"❌ Segments request failed with status {response.status_code}")
            
            # Print response headers (especially x-request-id)
            if 'x-request-id' in response.headers:
                st.info(f"📥 x-request-id: {response.headers['x-request-id']}")
            
            # Try to get error details
            try:
                error_data = response.json()
                st.error(f"📥 Error details: {error_data}")
            except:
                st.error(f"📥 Response text: {response.text}")
            
            return False
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None

def create_analytics_segment_from_json(segment_payload):
    """
    Function to create Adobe Analytics segment using a JSON payload.
    
    This function takes a complete segment definition JSON and sends it directly to the API.
    
    Args:
        segment_payload (dict): Complete segment definition JSON object
        
    Returns:
        dict: Response dictionary with status and data/error information
        
    Example payload structure:
        {
            "name": "Segment Name",
            "description": "Segment Description",
            "rsid": "your_rsid",
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
    """
    st.info("🔍 DEBUG: Starting create_analytics_segment_from_json function")
    st.info(f"🔍 DEBUG: Input payload: {json.dumps(segment_payload, indent=2)}")
    
    # 1. Authentication and Setup - Get access token, client ID, and company ID
    st.info("🔍 DEBUG: Step 1 - Getting access token...")
    access_token = get_adobe_access_token()
    if not access_token:
        st.error("🔍 DEBUG: Failed to get access token")
        return {'status': 'error', 'message': 'Failed to authenticate with Adobe.'}
    
    st.info("🔍 DEBUG: ✅ Access token obtained successfully")
    st.info(f"🔍 DEBUG: Access token (first 20 chars): {access_token[:20]}...")
    
    try:
        st.info("🔍 DEBUG: Step 2 - Reading credentials from Streamlit secrets...")
        client_id = st.secrets.get("ADOBE_CLIENT_ID")
        company_id = st.secrets.get("ADOBE_COMPANY_ID")
        
        st.info(f"🔍 DEBUG: Client ID: {client_id}")
        st.info(f"🔍 DEBUG: Company ID: {company_id}")
        
        if not client_id or not company_id:
            st.error("🔍 DEBUG: Missing credentials")
            return {'status': 'error', 'message': 'Missing required credentials (ADOBE_CLIENT_ID or ADOBE_COMPANY_ID)'}
    except Exception as e:
        st.error(f"🔍 DEBUG: Exception reading credentials: {str(e)}")
        return {'status': 'error', 'message': f'Failed to read credentials: {str(e)}'}
    
    # 2. Validate the input payload
    st.info("🔍 DEBUG: Step 3 - Validating input payload...")
    required_fields = ['name', 'description', 'rsid', 'definition']
    for field in required_fields:
        if field not in segment_payload:
            st.error(f"🔍 DEBUG: Missing required field: {field}")
            return {'status': 'error', 'message': f'Missing required field: {field}'}
    
    st.info("🔍 DEBUG: ✅ Payload validation passed")
    
    # 3. Use the provided payload directly
    st.info("🔍 DEBUG: Step 4 - Using provided payload...")
    body = segment_payload.copy()
    
    st.info("🔍 DEBUG: ✅ Payload body constructed")
    st.info(f"🔍 DEBUG: Full payload body: {json.dumps(body, indent=2)}")
    
    # 4. Construct URL and headers
    st.info("🔍 DEBUG: Step 5 - Constructing URL and headers...")
    url = f"https://analytics.adobe.io/api/{company_id}/segments"
    headers = {
        'Authorization': f"Bearer {access_token}",
        'x-api-key': client_id,
        'Content-Type': 'application/json'
    }
    
    st.info(f"🔍 DEBUG: URL: {url}")
    st.info(f"🔍 DEBUG: Headers: {json.dumps(headers, indent=2)}")
    
    try:
        # 5. Make the API POST request
        st.info("🔍 DEBUG: Step 6 - Making API POST request...")
        st.info(f"🔍 DEBUG: Request details:")
        st.info(f"  - URL: {url}")
        st.info(f"  - Method: POST")
        st.info(f"  - Headers: {json.dumps(headers, indent=2)}")
        st.info(f"  - Body (JSON): {json.dumps(body, indent=2)}")
        
        # Convert body to JSON string for logging
        json_body = json.dumps(body)
        st.info(f"🔍 DEBUG: Body length: {len(json_body)} characters")
        st.info(f"🔍 DEBUG: Body as string: {json_body}")
        
        response = requests.post(
            url,
            headers=headers,
            data=json_body,
            timeout=30
        )
        
        st.info(f"🔍 DEBUG: ✅ API request completed")
        st.info(f"🔍 DEBUG: Response status code: {response.status_code}")
        st.info(f"🔍 DEBUG: Response headers: {dict(response.headers)}")
        
        # 6. Handle the response
        if response.status_code == 201:
            st.info("🔍 DEBUG: ✅ Success response (201)")
            response_data = response.json()
            st.info(f"🔍 DEBUG: Response data: {json.dumps(response_data, indent=2)}")
            return {'status': 'success', 'data': response_data}
        else:
            st.error(f"🔍 DEBUG: ❌ Error response (status {response.status_code})")
            st.error(f"🔍 DEBUG: Response text: {response.text}")
            
            # Try to parse error response as JSON
            try:
                error_json = response.json()
                st.error(f"🔍 DEBUG: Error response as JSON: {json.dumps(error_json, indent=2)}")
            except:
                st.error("🔍 DEBUG: Could not parse error response as JSON")
            
            return {'status': 'error', 'code': response.status_code, 'message': response.text}
            
    except requests.exceptions.RequestException as e:
        st.error(f"🔍 DEBUG: ❌ Request exception: {str(e)}")
        return {'status': 'error', 'message': f'Request failed: {str(e)}'}
    except Exception as e:
        st.error(f"🔍 DEBUG: ❌ Unexpected exception: {str(e)}")
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}

def main():
    st.set_page_config(
        page_title="Adobe Analytics API Test",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🔐 Adobe Analytics 2.0 API Test Suite")
    st.markdown("---")
    
    # Check secrets status
    st.header("🔑 Secrets Configuration")
    
    # Check OAuth secrets (required for API connection)
    if validate_oauth_secrets():
        st.success("✅ OAuth secrets configured - can test API connection")
        
        # Check if we can also make API calls
        if validate_api_secrets():
            st.success("✅ All secrets configured - can test full functionality")
        else:
            st.warning("⚠️ Company ID missing - can only test OAuth connection")
        
        # Display company ID (this is safe to show)
        company_id = get_company_id()
        if company_id:
            st.info(f"🏢 Company ID: {company_id}")
    else:
        st.error("❌ OAuth secrets missing - cannot test API connection")
        st.markdown("""
        **Required OAuth Secrets:**
        - `ADOBE_CLIENT_ID` - Your Adobe Client ID
        - `ADOBE_CLIENT_SECRET` - Your Adobe Client Secret  
        - `ADOBE_ORG_ID` - Your Adobe Organization ID
        - `ADOBE_TECH_ID` - Your Adobe Technical Account ID
        
        **Optional for API calls:**
        - `ADOBE_COMPANY_ID` - Your Adobe Analytics Company ID
        
        Configure these in your `.streamlit/secrets.toml` file or environment variables.
        """)
        return
    
    st.markdown("---")
    
    # Test API Connection
    st.header("🌐 API Connection Test")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔗 Test API Connection", type="primary"):
            with st.spinner("Testing connection..."):
                success = test_api_connection()
                if success:
                    st.balloons()
    
    with col2:
        st.info("""
        This will test your Adobe API credentials by:
        1. Reading secrets from Streamlit
        2. Making a JWT token request
        3. Validating the response
        """)
    
    st.markdown("---")
    
    # Enhanced API Testing Section
    st.header("🚀 Enhanced API Testing")
    
    if validate_api_secrets():
        company_id = get_company_id()
        client_id = st.secrets.get("ADOBE_CLIENT_ID")
        
        # Dynamic JSON Input Section
        st.subheader("📝 Dynamic Segment Creation")
        st.info("""
        **Create Custom Segments:**
        Enter your segment definition JSON below and click 'Create Segment' to send it directly to the Adobe Analytics API.
        """)
        
        # JSON input text area
        default_json = '''{
  "name": "Custom Segment",
  "description": "Your custom segment description",
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
}'''
        
        json_input = st.text_area(
            "Segment Definition JSON:",
            value=default_json,
            height=300,
            help="Enter your complete segment definition JSON here"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Create Custom Segment", type="primary"):
                try:
                    # Parse JSON input
                    segment_payload = json.loads(json_input)
                    st.success("✅ JSON parsed successfully!")
                    
                    with st.spinner("Creating custom segment..."):
                        result = create_analytics_segment_from_json(segment_payload)
                        
                        if result['status'] == 'success':
                            st.success("🎉 Custom segment created successfully!")
                            st.json(result['data'])
                            st.balloons()
                        else:
                            st.error(f"❌ Failed to create custom segment: {result['message']}")
                            if 'code' in result:
                                st.error(f"Status Code: {result['code']}")
                                
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON format: {str(e)}")
                    st.info("Please check your JSON syntax and try again.")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
        
        with col2:
            st.info("""
            **JSON Input Guidelines:**
            
            **Required Fields:**
            - `name`: Segment name
            - `description`: Segment description  
            - `rsid`: Report Suite ID
            - `definition`: Segment definition object
            
            **Definition Structure:**
            - `version`: [1, 0, 0]
            - `func`: "segment"
            - `container`: Container configuration
            - `context`: "visitors", "visits", or "hits"
            - `pred`: Predicate logic
            
            **Example Functions:**
            - `streq`: String equals
            - `gt`: Greater than
            - `lt`: Less than
            - `in`: In array
            - `and`: Logical AND
            - `or`: Logical OR
            """)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Get Segments", type="secondary"):
                with st.spinner("Getting segments..."):
                    access_token = get_adobe_access_token()
                    if access_token:
                        success = get_adobe_segments_enhanced(access_token, client_id, company_id)
                        if success:
                            st.success("✅ Segments retrieved successfully!")
                        else:
                            st.error("❌ Failed to get segments")
                    else:
                        st.error("❌ Failed to get access token")
        
        with col2:
            if st.button("🏷️ Create Test Segment", type="secondary"):
                with st.spinner("Creating test segment..."):
                    # Sample segment payload
                    segment_payload = {
                        "name": "Test Segment from Enhanced API",
                        "description": "This is a test segment created via enhanced Adobe Analytics 2.0 API",
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
                                        "name": "variables/evar1"
                                    },
                                    "str": "test_value"
                                }
                            }
                        }
                    }
                    
                    result = create_analytics_segment_from_json(segment_payload)
                    
                    if result['status'] == 'success':
                        st.success("✅ Segment created successfully!")
                        st.json(result['data'])
                        st.balloons()
                    else:
                        st.error(f"❌ Failed to create segment: {result['message']}")
                        if 'code' in result:
                            st.error(f"Status Code: {result['code']}")
        
        with col3:
            if st.button("🔄 Full API Test", type="primary"):
                with st.spinner("Running full API test..."):
                    access_token = get_adobe_access_token()
                    if access_token:
                        st.success("✅ Access Token obtained successfully!")
                        
                        # Test getting segments
                        segments_success = get_adobe_segments_enhanced(access_token, client_id, company_id)
                        
                        if segments_success:
                            # Test creating segment
                            segment_payload = {
                                "name": "Full Test Segment",
                                "description": "Segment created during full API test",
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
                                                "name": "variables/evar1"
                                            },
                                            "str": "test_value"
                                        }
                                    }
                                }
                            }
                            
                            result = create_analytics_segment_from_json(segment_payload)
                            
                            if result['status'] == 'success':
                                st.success("🎉 All enhanced API tests passed successfully!")
                                st.json(result['data'])
                                st.balloons()
                            else:
                                st.error(f"❌ Failed to create segment during full test: {result['message']}")
                                if 'code' in result:
                                    st.error(f"Status Code: {result['code']}")
                        else:
                            st.error("❌ Failed to get segments during full test")
                    else:
                        st.error("❌ Failed to get access token for full test")
    else:
        st.warning("⚠️ Cannot test enhanced API functionality - Company ID missing")
        st.info("""
        **To enable enhanced API testing:**
        1. Configure your `ADOBE_COMPANY_ID` in `.streamlit/secrets.toml`
        2. Make sure it's a valid 32-character hex string
        3. Restart the app and try again
        """)
    
    st.markdown("---")
    
    # Test Refactored Function
    st.header("🔧 Test Refactored Function")
    
    if validate_api_secrets():
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧪 Test Refactored Function", type="primary"):
                with st.spinner("Testing refactored function..."):
                    # Sample segment payload - using the exact working payload structure
                    segment_payload = {
                        "name": "Segment from API",
                        "description": "People starting to visit from homepage",
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
                    
                    result = create_analytics_segment_from_json(segment_payload)
                    
                    if result['status'] == 'success':
                        st.success("✅ Refactored function test successful!")
                        st.json(result['data'])
                        st.balloons()
                    else:
                        st.error(f"❌ Refactored function test failed: {result['message']}")
                        if 'code' in result:
                            st.error(f"Status Code: {result['code']}")
        
        with col2:
            st.info("""
            **JSON-Based Function Test:**
            
            This tests the new `create_analytics_segment_from_json` function that:
            - Accepts complete JSON payloads directly
            - Validates required fields automatically
            - Sends the exact payload structure to Adobe API
            - Returns structured response objects
            - Handles errors properly
            
            **Expected Payload Structure:**
            ```json
            {
              "name": "Segment from API",
              "description": "People starting to visit from homepage",
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
            ```
            
            **Debug Mode Enabled:**
            The function now includes comprehensive debug logging to help identify any payload issues.
            """)
            
            # Show what will be sent
            st.info("**What will be sent:**")
            sample_rules = [
                {
                    "func": "streq",
                    "name": "variables/evar1",
                    "val": "test_value"
                }
            ]
            
            sample_payload = {
                "name": "Segment from API",
                "description": "People starting to visit from homepage",
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
            
            st.json(sample_payload)
    else:
        st.warning("⚠️ Cannot test refactored function - Company ID missing")
    
    st.markdown("---")
    
    # Create Sample Segment (Original functionality)
    st.header("📊 Segment Creation Test (Original)")
    
    # Check if we can create segments
    if not validate_api_secrets():
        st.warning("⚠️ Cannot test segment creation - Company ID missing")
        st.info("""
        **To enable segment creation:**
        1. Configure your `ADOBE_COMPANY_ID` in `.streamlit/secrets.toml`
        2. Make sure it's a valid 32-character hex string
        3. Restart the app and try again
        """)
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🏷️ Create Sample Segment (Original)", type="secondary"):
                with st.spinner("Creating sample segment..."):
                    success = create_sample_segment()
                    if success:
                        st.balloons()
        
        with col2:
            st.info("""
            This will create a test segment with:
            - Name: "Test Segment - High Page Views"
            - Description: "Test segment for users with more than 10 page views"
            - Definition: Page views > 1
            """)
    
    st.markdown("---")
    
    # Test Mobile Users Segment
    st.header("📱 Test Mobile Users Segment")
    
    if validate_api_secrets():
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📱 Create Mobile Users Segment", type="primary"):
                with st.spinner("Creating Mobile Users segment..."):
                    # Mobile Users segment payload - using the exact working payload structure
                    mobile_payload = {
                        "name": "Mobile Users",
                        "description": "Users on mobile devices",
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
                                        "name": "variables/evar1"
                                    },
                                    "str": "Mobile"
                                }
                            }
                        }
                    }
                    
                    result = create_analytics_segment_from_json(mobile_payload)
                    
                    if result['status'] == 'success':
                        st.success("✅ Mobile Users segment created successfully!")
                        st.json(result['data'])
                        st.balloons()
                    else:
                        st.error(f"❌ Failed to create Mobile Users segment: {result['message']}")
                        if 'code' in result:
                            st.error(f"Status Code: {result['code']}")
        
        with col2:
            st.info("""
            **Mobile Users Segment Test:**
            
            This creates a segment for mobile device users using:
            - **Name**: "Mobile Users"
            - **Description**: "Users on mobile devices"
            - **Target**: Visitors where `variables/evar1` equals "Mobile"
            
            **Expected Payload Structure:**
            ```json
            {
              "name": "Mobile Users",
              "description": "Users on mobile devices",
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
                      "name": "variables/evar1"
                    },
                    "str": "Mobile"
                  }
                }
              }
            }
            ```
            
            **What will be sent:**
            The exact payload structure that Adobe Analytics 2.0 API expects.
            """)
            
            # Show what will be sent
            st.info("**What will be sent:**")
            mobile_payload = {
                "name": "Mobile Users",
                "description": "Users on mobile devices",
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
                                "name": "variables/evar1"
                            },
                            "str": "Mobile"
                        }
                    }
                }
            }
            
            st.json(mobile_payload)
    else:
        st.warning("⚠️ Cannot test Mobile Users segment - Company ID missing")
    
    st.markdown("---")
    
    # Debug Information
    st.header("🐛 Debug Information")
    
    if validate_api_secrets():
        company_id = get_company_id()
        client_id = st.secrets.get("ADOBE_CLIENT_ID")
        
        st.info(f"**Current Configuration:**")
        st.info(f"- Company ID: `{company_id}`")
        st.info(f"- Client ID: `{client_id}`")
        
        # Show sample payload structure
        st.info("**Sample Payload Structure:**")
        sample_payload = {
            "name": "Segment from API",
            "description": "People starting to visit from homepage",
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
        st.json(sample_payload)
        
        st.info("**API Endpoint:**")
        st.code(f"https://analytics.adobe.io/api/{company_id}/segments")
        
        st.info("**Required Headers:**")
        headers_info = {
            "Authorization": "Bearer {access_token}",
            "x-api-key": client_id,
            "Content-Type": "application/json"
        }
        st.json(headers_info)
    else:
        st.warning("⚠️ Cannot show debug info - Company ID missing")
    
    st.markdown("---")
    
    # Advanced Rule Examples
    st.header("🔬 Advanced Rule Examples")
    
    if validate_api_secrets():
        st.info("**Complex Segment Rules Examples:**")
        
        # Example 1: Geographic and behavioral targeting
        st.info("**Example 1: US Visitors with High Page Views**")
        geographic_behavioral_rules = [
            {
                "func": "streq",
                "name": "variables/geocountry",
                "val": "United States"
            },
            {
                "func": "gt",
                "name": "variables/pageviews",
                "val": 10
            }
        ]
        st.json(geographic_behavioral_rules)
        
        # Example 2: Multiple event conditions
        st.info("**Example 2: Cart Abandoners**")
        cart_abandonment_rules = [
            {
                "func": "gt",
                "name": "variables/cart_value",
                "val": 0
            },
            {
                "func": "streq",
                "name": "variables/checkout_step",
                "val": "cart_view"
            },
            {
                "func": "not",
                "name": "variables/purchase_completed"
            }
        ]
        st.json(cart_abandonment_rules)
        
        # Example 3: Time-based targeting
        st.info("**Example 3: Weekend Visitors**")
        weekend_rules = [
            {
                "func": "in",
                "name": "variables/day_of_week",
                "vals": ["Saturday", "Sunday"]
            }
        ]
        st.json(weekend_rules)
        
        st.info("**Usage:** Pass any of these rule arrays to the `rules` parameter of `create_analytics_segment()`")
    else:
        st.warning("⚠️ Cannot show advanced examples - Company ID missing")
    
    st.markdown("---")
    
    # Usage Instructions
    st.header("📖 Usage Instructions")
    st.markdown("""
    ### 🔧 Integration with Main App
    
    To use this API in your main Streamlit app:
    
    ```python
    from adobe_api import create_analytics_segment_from_json, get_adobe_access_token
    
    # Create a segment using JSON payload
    segment_payload = {
        "name": "My Custom Segment",
        "description": "Users who visited specific pages",
        "rsid": "your_report_suite_id",
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
                        "name": "variables/geocountry"
                    },
                    "str": "United States"
                }
            }
        }
    }
    
    result = create_analytics_segment_from_json(segment_payload)
    ```
    
    ### 🚨 Security Notes
    
    - All API credentials are stored in Streamlit secrets
    - Access tokens are obtained fresh for each request
    - No sensitive data is logged or displayed
    - Use environment variables in production
    
    ### 📚 API Documentation
    
    - [Adobe Analytics 2.0 API Reference](https://developer.adobe.com/analytics-apis/docs/2.0/)
    - [Adobe IMS Authentication](https://developer.adobe.com/authentication/auth-overview/)
    - [Segment Builder API](https://developer.adobe.com/analytics-apis/docs/2.0/guides/endpoints/segments/)
    
    ### 🆕 Enhanced Features
    
    - **Better Error Handling**: Comprehensive error messages and debugging info
    - **Enhanced Testing**: Multiple test scenarios with detailed feedback
    - **Improved Logging**: Better visibility into API requests and responses
    - **Full API Test**: Complete end-to-end testing workflow
    """)

if __name__ == "__main__":
    main() 