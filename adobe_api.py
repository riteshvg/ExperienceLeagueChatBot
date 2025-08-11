import requests
import os
import streamlit as st
import json
from typing import Dict, Any, Optional


def get_adobe_access_token() -> Optional[str]:
    """
    Get Adobe access token using JWT authentication.
    
    Returns:
        str: Access token if successful, None if failed
        
    Raises:
        Exception: If required secrets are missing or API call fails
    """
    try:
        # Read required secrets from Streamlit
        client_id = st.secrets.get("ADOBE_CLIENT_ID")
        client_secret = st.secrets.get("ADOBE_CLIENT_SECRET")
        org_id = st.secrets.get("ADOBE_ORG_ID")
        tech_id = st.secrets.get("ADOBE_TECH_ID")
        
        # Validate that all required secrets are present
        if not all([client_id, client_secret, org_id, tech_id]):
            missing_secrets = []
            if not client_id:
                missing_secrets.append("ADOBE_CLIENT_ID")
            if not client_secret:
                missing_secrets.append("ADOBE_CLIENT_SECRET")
            if not org_id:
                missing_secrets.append("ADOBE_ORG_ID")
            if not tech_id:
                missing_secrets.append("ADOBE_TECH_ID")
            
            raise ValueError(f"Missing required secrets: {', '.join(missing_secrets)}")
        
        # Adobe Identity Management System endpoint for client credentials
        ims_endpoint = "https://ims-na1.adobelogin.com/ims/token/v3"
        
        # Prepare form data for Adobe IMS
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
            'scope': 'openid, AdobeID, additional_info.projectedProductContext'
        }
        
        # Make POST request to get access token
        st.info(f"Making request to: {ims_endpoint}")
        st.info(f"Payload: {payload}")
        
        response = requests.post(
            ims_endpoint,
            data=payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        st.info(f"Response status: {response.status_code}")
        st.info(f"Response headers: {dict(response.headers)}")
        
        # Check if request was successful
        if response.status_code != 200:
            try:
                error_data = response.json()
                st.error(f"IMS Error: {error_data}")
            except:
                st.error(f"IMS Error: {response.text}")
            response.raise_for_status()
        
        # Parse JSON response
        token_data = response.json()
        
        # Extract access token
        if 'access_token' in token_data:
            return token_data['access_token']
        else:
            raise ValueError(f"Access token not found in response: {token_data}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"HTTP request failed: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Failed to get access token: {str(e)}")
        return None


def create_analytics_segment(name: str, description: str, definition_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new Adobe Analytics segment using the API.
    
    Args:
        name (str): Name of the segment
        description (str): Description of the segment
        definition_json (dict): Segment definition in JSON format
        
    Returns:
        dict: API response JSON if successful, None if failed
        
    Raises:
        Exception: If segment creation fails
    """
    try:
        # Get fresh access token
        access_token = get_adobe_access_token()
        if not access_token:
            st.error("Failed to obtain access token")
            return None
        
        # Read company ID from secrets
        company_id = st.secrets.get("ADOBE_COMPANY_ID")
        if not company_id:
            st.error("Missing ADOBE_COMPANY_ID secret")
            return None
        
        # Read client ID for x-api-key header
        client_id = st.secrets.get("ADOBE_CLIENT_ID")
        if not client_id:
            st.error("Missing ADOBE_CLIENT_ID secret")
            return None
        
        # Construct API endpoint URL
        # Adobe company IDs can vary in length - validate format instead of length
        if not company_id or not company_id.strip():
            st.error("Company ID cannot be empty")
            return None
        
        # Check if company ID contains only valid characters (alphanumeric and hyphens)
        if not company_id.replace('-', '').replace('_', '').isalnum():
            st.warning(f"Company ID '{company_id}' contains invalid characters. Adobe company IDs should contain only letters, numbers, hyphens, and underscores.")
            return None
        
        # Try multiple possible endpoints for Adobe Analytics API
        # Some companies might have different endpoint structures
        possible_endpoints = [
            f"https://analytics.adobe.io/api/{company_id}/segments",
            f"https://analytics.adobe.io/api/{company_id}/segments/",
            f"https://analytics.adobe.io/api/{company_id}/segments/create",
            f"https://analytics.adobe.io/api/{company_id}/segments/create/"
        ]
        
        api_endpoint = possible_endpoints[0]  # Start with the first one
        
        # Prepare request headers with all required Adobe Analytics headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': client_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Prepare request body
        # Adobe Analytics 2.0 API expects the definition at root level
        request_body = {
            'name': name,
            'description': description
        }
        
        # For Adobe Analytics 2.0 API, the definition should be at root level
        # Extract the inner definition if it's nested under 'definition' key
        if isinstance(definition_json, dict):
            if 'definition' in definition_json:
                # If definition_json has a nested 'definition', extract it
                inner_definition = definition_json['definition']
                request_body.update(inner_definition)
                st.info(f"🔧 Extracted nested definition: {inner_definition}")
            else:
                # Otherwise, merge the entire definition_json
                request_body.update(definition_json)
                st.info(f"🔧 Merged definition directly: {definition_json}")
        else:
            st.error("Invalid definition format. Expected dictionary.")
            return None
        
        st.info(f"🎯 Final request body: {request_body}")
        
        # Try multiple endpoints if one fails
        for endpoint in possible_endpoints:
            st.info(f"🔍 Trying endpoint: {endpoint}")
            st.info(f"📤 Request body: {request_body}")
            st.info(f"🔑 Headers: {dict(headers)}")
            
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=request_body,
                    timeout=60
                )
                
                st.info(f"📥 Response status: {response.status_code}")
                st.info(f"📥 Response headers: {dict(response.headers)}")
                
                # If successful, break out of the loop
                if response.status_code < 400:
                    st.success(f"✅ Success with endpoint: {endpoint}")
                    st.info(f"📥 Response body: {response.text}")
                    break
                    
                # If it's a 403025 error, try the next endpoint
                if response.status_code == 403:
                    try:
                        error_detail = response.json()
                        if error_detail.get('error_code') == '403025':
                            st.warning(f"⚠️ Endpoint {endpoint} returned 403025 - trying next endpoint...")
                            st.info(f"📥 Error details: {error_detail}")
                            continue
                    except:
                        st.warning(f"⚠️ Endpoint {endpoint} returned 403 but couldn't parse error details")
                        st.info(f"📥 Response text: {response.text}")
                        continue
                
                # For other errors, show details
                st.error(f"❌ Endpoint {endpoint} failed with status {response.status_code}")
                try:
                    error_detail = response.json()
                    st.error(f"📥 Error details: {error_detail}")
                except:
                    st.error(f"📥 Response text: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Request to {endpoint} failed: {str(e)}")
                continue
        else:
            # If we've tried all endpoints and none worked
            st.error("❌ All endpoints failed. Please check your Adobe Analytics permissions.")
            st.info("💡 Check the detailed error messages above to understand what went wrong")
            return None
        
        # Return the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"HTTP request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                st.error(f"API Error Details: {error_detail}")
            except:
                st.error(f"HTTP Status: {e.response.status_code}")
        return None
    except Exception as e:
        st.error(f"Failed to create segment: {str(e)}")
        return None


def get_company_id() -> Optional[str]:
    """
    Get Adobe Analytics company ID from secrets.
    
    Returns:
        str: Company ID if found, None if missing
    """
    company_id = st.secrets.get("ADOBE_COMPANY_ID")
    
    if not company_id or not company_id.strip():
        st.warning("⚠️ Company ID is missing or empty")
        return None
    
    # Check if company ID contains only valid characters
    if not company_id.replace('-', '').replace('_', '').isalnum():
        st.warning(f"⚠️ Company ID '{company_id}' contains invalid characters")
        st.info("""
        **Adobe Company ID Format:**
        - Should contain only letters, numbers, hyphens, and underscores
        - Length can vary (not always 32 characters)
        - Example: `adober1f`, `company-123`, `analytics_456`
        
        **Current value:** `{company_id}` (contains invalid characters)
        """.format(company_id=company_id))
        return None
    
    return company_id


def validate_oauth_secrets() -> bool:
    """
    Validate that all required OAuth secrets are present for token generation.
    
    Returns:
        bool: True if all OAuth secrets are present, False otherwise
    """
    oauth_secrets = [
        "ADOBE_CLIENT_ID",
        "ADOBE_CLIENT_SECRET", 
        "ADOBE_ORG_ID",
        "ADOBE_TECH_ID"
    ]
    
    missing_secrets = []
    for secret in oauth_secrets:
        if not st.secrets.get(secret):
            missing_secrets.append(secret)
    
    if missing_secrets:
        st.error(f"Missing required OAuth secrets: {', '.join(missing_secrets)}")
        return False
    
    return True


def validate_api_secrets() -> bool:
    """
    Validate that all required secrets are present for API calls.
    
    Returns:
        bool: True if all API secrets are present, False otherwise
    """
    # First validate OAuth secrets
    if not validate_oauth_secrets():
        return False
    
    # Then validate company ID for API calls
    company_id = st.secrets.get("ADOBE_COMPANY_ID")
    if not company_id:
        st.error("❌ Missing ADOBE_COMPANY_ID secret for API calls")
        st.info("""
        **Company ID is required for:**
        - Creating segments
        - Making Analytics API calls
        - But NOT for getting OAuth tokens
        """)
        return False
    
    # Validate company ID format
    if not company_id.replace('-', '').replace('_', '').isalnum():
        st.error("❌ Invalid Company ID format. Contains invalid characters.")
        st.info("""
        **Adobe Company ID Format:**
        - Should contain only letters, numbers, hyphens, and underscores
        - Length can vary (not always 32 characters)
        - Examples: `adober1f`, `company-123`, `analytics_456`
        
        **Current value:** `{company_id}` (contains invalid characters)
        """.format(company_id=company_id))
        return False
    
    return True


def validate_secrets() -> bool:
    """
    Validate that all required Adobe API secrets are present.
    This is a legacy function that now calls validate_api_secrets().
    
    Returns:
        bool: True if all secrets are present, False otherwise
    """
    return validate_api_secrets()


# Example usage and testing functions
def test_api_connection() -> bool:
    """
    Test the Adobe API connection by attempting to get an access token.
    This only requires OAuth secrets, not the company ID.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        if not validate_oauth_secrets():
            return False
            
        access_token = get_adobe_access_token()
        if access_token:
            st.success("✅ Successfully connected to Adobe API")
            st.info("""
            **OAuth Authentication Successful!**
            
            You can now:
            - ✅ Get access tokens
            - ✅ Make authenticated requests
            
            **Next step:** Configure your Company ID to make Analytics API calls
            """)
            return True
        else:
            st.error("❌ Failed to connect to Adobe API")
            return False
    except Exception as e:
        st.error(f"❌ API connection test failed: {str(e)}")
        return False


def create_sample_segment() -> bool:
    """
    Create a sample segment for testing purposes.
    This requires both OAuth secrets AND company ID.
    
    Returns:
        bool: True if segment created successfully, False otherwise
    """
    try:
        # First validate that we have all required secrets for API calls
        if not validate_api_secrets():
            st.error("❌ Cannot create segment - missing required secrets")
            return False
        
        # Sample segment definition using Adobe Analytics 2.0 API format
        # This creates a simple segment for page views > 1
        # The API expects the definition at root level, not nested under 'definition'
        sample_definition = {
            "container": {
                "func": "container",
                "context": "visitors",
                "pred": {
                    "func": "pred",
                    "expr": {
                        "func": "expr",
                        "func_name": "gt",
                        "args": [
                            {"func": "attr", "name": "page_views"},
                            {"func": "const", "val": 1}
                        ]
                    }
                }
            }
        }
        
        result = create_analytics_segment(
            name="Test Segment - High Page Views",
            description="Test segment for users with more than 10 page views",
            definition_json=sample_definition
        )
        
        if result:
            st.success("✅ Sample segment created successfully")
            st.json(result)
            return True
        else:
            st.error("❌ Failed to create sample segment")
            return False
            
    except Exception as e:
        st.error(f"❌ Sample segment creation failed: {str(e)}")
        return False


def create_analytics_segment_from_json(segment_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create Adobe Analytics segment using a complete JSON payload.
    
    This function takes a complete segment definition JSON and sends it directly to the API.
    It's designed for integration with the main app where users provide complete segment definitions.
    
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
    try:
        # 1. Authentication and Setup - Get access token, client ID, and company ID
        access_token = get_adobe_access_token()
        if not access_token:
            return {'status': 'error', 'message': 'Failed to authenticate with Adobe.'}
        
        # Read credentials from Streamlit secrets
        client_id = st.secrets.get("ADOBE_CLIENT_ID")
        company_id = st.secrets.get("ADOBE_COMPANY_ID")
        
        if not client_id or not company_id:
            return {'status': 'error', 'message': 'Missing required credentials (ADOBE_CLIENT_ID or ADOBE_COMPANY_ID)'}
        
        # 2. Validate the input payload
        required_fields = ['name', 'description', 'rsid', 'definition']
        for field in required_fields:
            if field not in segment_payload:
                return {'status': 'error', 'message': f'Missing required field: {field}'}
        
        # 3. Use the provided payload directly
        body = segment_payload.copy()
        
        # 4. Construct URL and headers
        url = f"https://analytics.adobe.io/api/{company_id}/segments"
        headers = {
            'Authorization': f"Bearer {access_token}",
            'x-api-key': client_id,
            'Content-Type': 'application/json'
        }
        
        # 5. Make the API POST request
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(body),
            timeout=30
        )
        
        # 6. Handle the response
        if response.status_code in [200, 201]:  # Adobe Analytics returns 200 for successful creation
            response_data = response.json()
            return {'status': 'success', 'data': response_data}
        else:
            # Try to parse error response as JSON
            try:
                error_json = response.json()
                return {'status': 'error', 'code': response.status_code, 'message': str(error_json)}
            except:
                return {'status': 'error', 'code': response.status_code, 'message': response.text}
            
    except requests.exceptions.RequestException as e:
        return {'status': 'error', 'message': f'Request failed: {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}


def create_analytics_segment_enhanced(name: str, description: str, rsid: str, container_context: str, rules: list) -> Dict[str, Any]:
    """
    Enhanced segment creation function that builds the segment definition from parameters.
    
    This function provides a more user-friendly interface for creating segments by accepting
    simple parameters and building the complex Adobe Analytics segment definition structure.
    
    Args:
        name (str): Name of the segment
        description (str): Description of the segment
        rsid (str): Report Suite ID
        container_context (str): The context for the container (e.g., "visitors", "visits", "hits")
        rules (list): List of rule dictionaries for the segment
        
    Returns:
        dict: Response dictionary with status and data/error information
        
    Example rules structure:
        rules = [
            {'func': 'streq', 'name': 'variables/geocountry', 'val': 'United States'},
            {'func': 'gt', 'name': 'variables/pageviews', 'val': 10}
        ]
    """
    try:
        # 1. Authentication and Setup
        access_token = get_adobe_access_token()
        if not access_token:
            return {'status': 'error', 'message': 'Failed to authenticate with Adobe.'}
        
        # Read credentials
        client_id = st.secrets.get("ADOBE_CLIENT_ID")
        company_id = st.secrets.get("ADOBE_COMPANY_ID")
        
        if not client_id or not company_id:
            return {'status': 'error', 'message': 'Missing required credentials (ADOBE_CLIENT_ID or ADOBE_COMPANY_ID)'}
        
        # 2. Build the segment definition structure
        if len(rules) == 1:
            # Single rule - use the exact structure from working examples
            rule = rules[0]
            definition = {
                "version": [1, 0, 0],
                "func": "segment",
                "container": {
                    "func": "container",
                    "context": container_context,
                    "pred": {
                        "func": rule.get("func", "streq"),
                        "val": {
                            "func": "attr",
                            "name": rule.get("name", "variables/page")
                        },
                        "str": rule.get("val", "Homepage")
                    }
                }
            }
        else:
            # Multiple rules - extend the structure for multiple conditions
            definition = {
                "version": [1, 0, 0],
                "func": "segment",
                "container": {
                    "func": "container",
                    "context": container_context,
                    "pred": {
                        "func": "and",
                        "vals": []
                    }
                }
            }
            
            # Build individual rule predicates
            for rule in rules:
                rule_pred = {
                    "func": rule.get("func", "streq"),
                    "val": {
                        "func": "attr",
                        "name": rule.get("name", "variables/page")
                    },
                    "str": rule.get("val", "Homepage")
                }
                definition["container"]["pred"]["vals"].append(rule_pred)
        
        # 3. Construct the final payload
        body = {
            "name": name,
            "description": description,
            "rsid": rsid,
            "definition": definition
        }
        
        # 4. Make the API request
        url = f"https://analytics.adobe.io/api/{company_id}/segments"
        headers = {
            'Authorization': f"Bearer {access_token}",
            'x-api-key': client_id,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(body),
            timeout=30
        )
        
        # 5. Handle the response
        if response.status_code in [200, 201]:  # Adobe Analytics returns 200 for successful creation
            response_data = response.json()
            return {'status': 'success', 'data': response_data}
        else:
            try:
                error_json = response.json()
                return {'status': 'error', 'code': response.status_code, 'message': str(error_json)}
            except:
                return {'status': 'error', 'code': response.status_code, 'message': response.text}
            
    except requests.exceptions.RequestException as e:
        return {'status': 'error', 'message': f'Request failed: {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}


def get_adobe_segments(access_token: str, client_id: str, company_id: str) -> Dict[str, Any]:
    """
    Get Adobe Analytics segments using the access token.
    
    Args:
        access_token (str): Valid access token
        client_id (str): Adobe client ID
        company_id (str): Adobe company ID
        
    Returns:
        dict: Response dictionary with status and data/error information
    """
    try:
        # Construct API endpoint URL
        segments_endpoint = f"https://analytics.adobe.io/api/{company_id}/segments"
        
        # Request headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': client_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Make GET request
        response = requests.get(
            segments_endpoint,
            headers=headers,
            timeout=30
        )
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                segments_data = response.json()
                return {'status': 'success', 'data': segments_data}
            except json.JSONDecodeError as e:
                return {'status': 'error', 'message': f'Failed to parse JSON response: {e}'}
        else:
            # Try to get error details
            try:
                error_data = response.json()
                return {'status': 'error', 'code': response.status_code, 'message': str(error_data)}
            except:
                return {'status': 'error', 'code': response.status_code, 'message': response.text}
            
    except requests.exceptions.RequestException as e:
        return {'status': 'error', 'message': f'Request failed: {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}


if __name__ == "__main__":
    # This section runs when the script is executed directly
    st.title("Adobe Analytics 2.0 API Test")
    
    if st.button("Test API Connection"):
        test_api_connection()
    
    if st.button("Create Sample Segment"):
        create_sample_segment()
    
    # Display current secrets status (without revealing values)
    st.subheader("🔑 Secrets Status")
    
    # OAuth Secrets (required for token generation)
    st.subheader("🔐 OAuth Secrets (Required for API Connection)")
    oauth_secrets = ["ADOBE_CLIENT_ID", "ADOBE_CLIENT_SECRET", "ADOBE_ORG_ID", "ADOBE_TECH_ID"]
    oauth_status = {}
    for secret in oauth_secrets:
        oauth_status[secret] = "✅ Present" if st.secrets.get(secret) else "❌ Missing"
    
    for secret, status in oauth_status.items():
        st.write(f"{secret}: {status}")
    
    # Company ID (required for Analytics API calls)
    st.subheader("🏢 Company ID (Required for Analytics API Calls)")
    company_id = st.secrets.get("ADOBE_COMPANY_ID")
    if company_id:
        # Check if company ID contains only valid characters
        if company_id.replace('-', '').replace('_', '').isalnum():
            st.success(f"✅ Company ID '{company_id}' format looks correct")
            st.info(f"**Length:** {len(company_id)} characters")
        else:
            st.error(f"❌ Company ID '{company_id}' contains invalid characters!")
            st.info("""
            **Adobe Company ID Format:**
            - Should contain only letters, numbers, hyphens, and underscores
            - Length can vary (not always 32 characters)
            - Examples: `adober1f`, `company-123`, `analytics_456`
            
            **Current value:** `{company_id}` (contains invalid characters)
            """.format(company_id=company_id))
    else:
        st.warning("⚠️ Company ID is missing - needed for Analytics API calls")
        st.info("""
        **Company ID is only required for:**
        - Creating segments
        - Making Analytics API calls
        - **NOT for getting OAuth tokens**
        """)
    
    # Validation Summary
    st.subheader("📋 Validation Summary")
    oauth_valid = validate_oauth_secrets()
    api_valid = validate_api_secrets()
    
    if oauth_valid:
        st.success("✅ OAuth Secrets: Valid (can get access tokens)")
    else:
        st.error("❌ OAuth Secrets: Invalid (cannot get access tokens)")
    
    if api_valid:
        st.success("✅ API Secrets: Valid (can make Analytics API calls)")
    else:
        st.warning("⚠️ API Secrets: Incomplete (cannot make Analytics API calls)")
    
    if oauth_valid and not api_valid:
        st.info("""
        **Current Status:** You can authenticate but cannot make Analytics API calls.
        **Next Step:** Configure your Company ID to enable full functionality.
        """)
