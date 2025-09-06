#!/usr/bin/env python3
"""
Adobe Analytics API Client Module

This module provides functionality to interact with Adobe Analytics API
for segment validation, creation, and variable retrieval.
"""

import requests
import json
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class AdobeAnalyticsClient:
    """Client for Adobe Analytics API integration"""
    
    def __init__(self, client_id: str, client_secret: str, org_id: str, access_token: str = None):
        """
        Initialize Adobe Analytics API client with OAuth support
        
        Args:
            client_id (str): Adobe Analytics client ID
            client_secret (str): Adobe Analytics client secret
            org_id (str): Adobe Analytics organization ID
            access_token (str): OAuth access token (optional, will be generated if not provided)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.org_id = org_id
        self.access_token = access_token
        self.token_expires_at = None
        
        # OAuth endpoints
        self.oauth_base_url = "https://ims-na1.adobelogin.com"
        self.oauth_token_url = f"{self.oauth_base_url}/ims/token/v3"
        
        # Analytics API base URL (will be set after getting token)
        self.base_url = None
        
        # Initialize headers (will be updated when token is obtained)
        self.headers = {
            "x-api-key": client_id,
            "Content-Type": "application/json"
        }
        
        # Generate access token if not provided
        if not self.access_token:
            self._generate_access_token()
    
    def _generate_access_token(self) -> bool:
        """
        Generate OAuth access token using client credentials
        
        Returns:
            bool: True if token generation successful, False otherwise
        """
        try:
            # Prepare OAuth request
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "openid,AdobeID,read_organizations,additional_info.projectedProductContext,read_analytics"
            }
            
            # Make OAuth request
            response = requests.post(
                self.oauth_token_url,
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                
                # Calculate token expiration
                expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update headers with new token
                self.headers["Authorization"] = f"Bearer {self.access_token}"
                
                # Get company ID from token and set base URL
                self._get_company_id()
                
                return True
            else:
                print(f"OAuth token generation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error generating OAuth token: {str(e)}")
            return False
    
    def _ensure_valid_token(self) -> bool:
        """
        Ensure we have a valid access token, refresh if necessary
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        # Check if token exists and is not expired
        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            return self._generate_access_token()
        
        return True
    
    def _get_company_id(self) -> bool:
        """
        Get company ID from Adobe Analytics API using the access token
        
        Returns:
            bool: True if company ID retrieved successfully, False otherwise
        """
        try:
            # Make request to get company information
            response = requests.get(
                "https://analytics.adobe.io/api/me",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                company_data = response.json()
                company_id = company_data.get("imsUserId", "").split("@")[0]  # Extract company ID from IMS user ID
                
                if company_id:
                    self.company_id = company_id
                    self.base_url = f"https://analytics.adobe.io/api/{company_id}"
                    return True
                else:
                    print("Could not extract company ID from response")
                    return False
            else:
                print(f"Failed to get company ID: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error getting company ID: {str(e)}")
            return False
    
    def validate_segment(self, definition: Dict, rsid: str) -> Dict:
        """
        Validate a segment definition using Adobe Analytics API
        
        Args:
            definition (Dict): Segment definition to validate
            rsid (str): Report Suite ID
            
        Returns:
            Dict: Validation results with success/error status
        """
        try:
            # Ensure we have a valid token
            if not self._ensure_valid_token():
                return {
                    "success": False,
                    "status_code": 401,
                    "error": {"error": "token_error", "error_description": "Failed to obtain valid access token"},
                    "message": "Authentication failed - unable to obtain access token"
                }
            
            # Prepare the validation payload
            payload = {
                "rsid": rsid,
                "definition": definition
            }
            
            # Make the API request
            response = requests.post(
                f"{self.base_url}/segments/validate",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Parse response
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json(),
                    "message": "Segment validation successful"
                }
            else:
                error_data = self._parse_error_response(response)
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_data,
                    "message": f"Segment validation failed: {error_data.get('error_description', 'Unknown error')}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "status_code": 408,
                "error": {"error": "timeout", "error_description": "Request timed out"},
                "message": "Request timed out while validating segment"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status_code": 503,
                "error": {"error": "connection_error", "error_description": "Connection failed"},
                "message": "Failed to connect to Adobe Analytics API"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "error": {"error": "internal_error", "error_description": str(e)},
                "message": f"Unexpected error during validation: {str(e)}"
            }
    
    def create_segment(self, definition: Dict) -> Dict:
        """
        Create a segment using Adobe Analytics API
        
        Args:
            definition (Dict): Complete segment definition
            
        Returns:
            Dict: Created segment details or error
        """
        try:
            # Make the API request
            response = requests.put(
                f"{self.base_url}/segments",
                headers=self.headers,
                json=definition,
                timeout=30
            )
            
            # Parse response
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json(),
                    "message": "Segment created successfully"
                }
            else:
                error_data = self._parse_error_response(response)
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_data,
                    "message": f"Segment creation failed: {error_data.get('error_description', 'Unknown error')}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "status_code": 408,
                "error": {"error": "timeout", "error_description": "Request timed out"},
                "message": "Request timed out while creating segment"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status_code": 503,
                "error": {"error": "connection_error", "error_description": "Connection failed"},
                "message": "Failed to connect to Adobe Analytics API"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "error": {"error": "internal_error", "error_description": str(e)},
                "message": f"Unexpected error during segment creation: {str(e)}"
            }
    
    def get_available_variables(self, rsid: str, variable_type: str) -> Dict:
        """
        Get available dimensions or metrics for a report suite
        
        Args:
            rsid (str): Report Suite ID
            variable_type (str): "dimensions" or "metrics"
            
        Returns:
            Dict: List of available variables or error
        """
        if variable_type not in ["dimensions", "metrics"]:
            return {
                "success": False,
                "status_code": 400,
                "error": {"error": "invalid_parameter", "error_description": "variable_type must be 'dimensions' or 'metrics'"},
                "message": "Invalid variable_type parameter"
            }
        
        try:
            # Make the API request
            response = requests.get(
                f"{self.base_url}/reportsuites/{rsid}/{variable_type}",
                headers=self.headers,
                timeout=30
            )
            
            # Parse response
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json(),
                    "message": f"Successfully retrieved {variable_type}"
                }
            else:
                error_data = self._parse_error_response(response)
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_data,
                    "message": f"Failed to retrieve {variable_type}: {error_data.get('error_description', 'Unknown error')}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "status_code": 408,
                "error": {"error": "timeout", "error_description": "Request timed out"},
                "message": f"Request timed out while retrieving {variable_type}"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status_code": 503,
                "error": {"error": "connection_error", "error_description": "Connection failed"},
                "message": "Failed to connect to Adobe Analytics API"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "error": {"error": "internal_error", "error_description": str(e)},
                "message": f"Unexpected error while retrieving {variable_type}: {str(e)}"
            }
    
    def get_segment_info(self, segment_id: str) -> Dict:
        """
        Get information about a specific segment
        
        Args:
            segment_id (str): Segment ID
            
        Returns:
            Dict: Segment information or error
        """
        try:
            # Make the API request
            response = requests.get(
                f"{self.base_url}/segments/{segment_id}",
                headers=self.headers,
                timeout=30
            )
            
            # Parse response
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json(),
                    "message": "Successfully retrieved segment information"
                }
            else:
                error_data = self._parse_error_response(response)
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_data,
                    "message": f"Failed to retrieve segment: {error_data.get('error_description', 'Unknown error')}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "status_code": 408,
                "error": {"error": "timeout", "error_description": "Request timed out"},
                "message": "Request timed out while retrieving segment"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status_code": 503,
                "error": {"error": "connection_error", "error_description": "Connection failed"},
                "message": "Failed to connect to Adobe Analytics API"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "error": {"error": "internal_error", "error_description": str(e)},
                "message": f"Unexpected error while retrieving segment: {str(e)}"
            }
    
    def list_segments(self, rsid: str, limit: int = 100) -> Dict:
        """
        List segments for a report suite
        
        Args:
            rsid (str): Report Suite ID
            limit (int): Maximum number of segments to return
            
        Returns:
            Dict: List of segments or error
        """
        try:
            # Prepare query parameters
            params = {
                "rsid": rsid,
                "limit": limit
            }
            
            # Make the API request
            response = requests.get(
                f"{self.base_url}/segments",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            # Parse response
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json(),
                    "message": "Successfully retrieved segments list"
                }
            else:
                error_data = self._parse_error_response(response)
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_data,
                    "message": f"Failed to retrieve segments: {error_data.get('error_description', 'Unknown error')}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "status_code": 408,
                "error": {"error": "timeout", "error_description": "Request timed out"},
                "message": "Request timed out while retrieving segments"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status_code": 503,
                "error": {"error": "connection_error", "error_description": "Connection failed"},
                "message": "Failed to connect to Adobe Analytics API"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "error": {"error": "internal_error", "error_description": str(e)},
                "message": f"Unexpected error while retrieving segments: {str(e)}"
            }
    
    def _parse_error_response(self, response: requests.Response) -> Dict:
        """
        Parse error response from Adobe Analytics API
        
        Args:
            response (requests.Response): HTTP response object
            
        Returns:
            Dict: Parsed error information
        """
        try:
            error_data = response.json()
        except (ValueError, json.JSONDecodeError):
            error_data = {
                "error": "parse_error",
                "error_description": "Failed to parse error response",
                "raw_response": response.text
            }
        
        # Add status code to error data
        error_data["http_status"] = response.status_code
        
        return error_data
    
    def test_connection(self) -> Dict:
        """
        Test the connection to Adobe Analytics API
        
        Returns:
            Dict: Connection test results
        """
        try:
            # Make a simple API request to test connection
            response = requests.get(
                f"{self.base_url}/reportsuites",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "message": "Connection test successful",
                    "data": {"company_id": self.company_id, "base_url": self.base_url}
                }
            else:
                error_data = self._parse_error_response(response)
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_data,
                    "message": f"Connection test failed: {error_data.get('error_description', 'Unknown error')}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "status_code": 408,
                "error": {"error": "timeout", "error_description": "Request timed out"},
                "message": "Connection test timed out"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status_code": 503,
                "error": {"error": "connection_error", "error_description": "Connection failed"},
                "message": "Connection test failed - unable to connect"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "error": {"error": "internal_error", "error_description": str(e)},
                "message": f"Connection test failed with unexpected error: {str(e)}"
            }
    
    def get_credentials_info(self) -> Dict:
        """
        Get information about the current credentials (without sensitive data)
        
        Returns:
            Dict: Credentials information
        """
        return {
            "client_id": self.client_id,
            "company_id": self.company_id,
            "base_url": self.base_url,
            "has_access_token": bool(self.access_token),
            "access_token_length": len(self.access_token) if self.access_token else 0
        }


# Factory function for easy client creation
def create_adobe_client(client_id: str, client_secret: str, org_id: str, access_token: str = None) -> AdobeAnalyticsClient:
    """
    Factory function to create Adobe Analytics client with OAuth
    
    Args:
        client_id (str): Adobe Analytics client ID
        client_secret (str): Adobe Analytics client secret
        org_id (str): Adobe Analytics organization ID
        access_token (str): OAuth access token (optional)
        
    Returns:
        AdobeAnalyticsClient: Configured client instance
    """
    return AdobeAnalyticsClient(client_id, client_secret, org_id, access_token)
