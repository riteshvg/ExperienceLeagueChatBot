#!/usr/bin/env python3
"""
Adobe Analytics API Client Module

This module provides functionality to interact with Adobe Analytics API
for segment validation, creation, and variable retrieval.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class AdobeAnalyticsClient:
    """Client for Adobe Analytics API integration"""
    
    def __init__(self, client_id: str, access_token: str, company_id: str):
        """
        Initialize Adobe Analytics API client
        
        Args:
            client_id (str): Adobe Analytics client ID (API key)
            access_token (str): OAuth access token
            company_id (str): Adobe Analytics company ID
        """
        self.client_id = client_id
        self.access_token = access_token
        self.company_id = company_id
        self.base_url = f"https://analytics.adobe.io/api/{company_id}"
        
        # Common headers for all requests
        self.headers = {
            "x-api-key": client_id,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
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
def create_adobe_client(client_id: str, access_token: str, company_id: str) -> AdobeAnalyticsClient:
    """
    Factory function to create Adobe Analytics client
    
    Args:
        client_id (str): Adobe Analytics client ID
        access_token (str): OAuth access token
        company_id (str): Adobe Analytics company ID
        
    Returns:
        AdobeAnalyticsClient: Configured client instance
    """
    return AdobeAnalyticsClient(client_id, access_token, company_id)
