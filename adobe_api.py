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
        ims_endpoint = "https://ims-na1.adobelogin.com/ims/token"
        
        # Prepare form data for Adobe IMS
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
            'scope': 'AdobeID,openid'
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
        api_endpoint = f"https://analytics.adobe.io/api/{company_id}/segments"
        
        # Prepare request headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': client_id,
            'Content-Type': 'application/json'
        }
        
        # Prepare request body
        request_body = {
            'name': name,
            'description': description,
            'definition': definition_json
        }
        
        # Make POST request to create segment
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=request_body,
            timeout=60
        )
        
        # Check if request was successful
        response.raise_for_status()
        
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
    return st.secrets.get("ADOBE_COMPANY_ID")


def validate_secrets() -> bool:
    """
    Validate that all required Adobe API secrets are present.
    
    Returns:
        bool: True if all secrets are present, False otherwise
    """
    required_secrets = [
        "ADOBE_CLIENT_ID",
        "ADOBE_CLIENT_SECRET", 
        "ADOBE_ORG_ID",
        "ADOBE_TECH_ID",
        "ADOBE_COMPANY_ID"
    ]
    
    missing_secrets = []
    for secret in required_secrets:
        if not st.secrets.get(secret):
            missing_secrets.append(secret)
    
    if missing_secrets:
        st.error(f"Missing required secrets: {', '.join(missing_secrets)}")
        return False
    
    return True


# Example usage and testing functions
def test_api_connection() -> bool:
    """
    Test the Adobe API connection by attempting to get an access token.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        if not validate_secrets():
            return False
            
        access_token = get_adobe_access_token()
        if access_token:
            st.success("✅ Successfully connected to Adobe API")
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
    
    Returns:
        bool: True if segment created successfully, False otherwise
    """
    try:
        # Sample segment definition for page views > 10
        sample_definition = {
            "container": {
                "func": "container",
                "pred": {
                    "func": "pred",
                    "expr": {
                        "func": "expr",
                        "func_name": "gt",
                        "args": [
                            {"func": "attr", "name": "page_views"},
                            {"func": "const", "val": 10}
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


if __name__ == "__main__":
    # This section runs when the script is executed directly
    st.title("Adobe Analytics 2.0 API Test")
    
    if st.button("Test API Connection"):
        test_api_connection()
    
    if st.button("Create Sample Segment"):
        create_sample_segment()
    
    # Display current secrets status (without revealing values)
    st.subheader("Secrets Status")
    secrets_status = {}
    for secret in ["ADOBE_CLIENT_ID", "ADOBE_CLIENT_SECRET", "ADOBE_ORG_ID", "ADOBE_TECH_ID", "ADOBE_COMPANY_ID"]:
        secrets_status[secret] = "✅ Present" if st.secrets.get(secret) else "❌ Missing"
    
    for secret, status in secrets_status.items():
        st.write(f"{secret}: {status}")
