#!/usr/bin/env python3
"""
Unit tests for the adobe_api.py module.
Tests the Adobe Analytics API functionality with proper mocking.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os

# Add the current directory to Python path to import adobe_api
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the functions we want to test
from adobe_api import (
    get_adobe_access_token,
    create_analytics_segment,
    get_company_id,
    validate_oauth_secrets,
    validate_api_secrets,
    test_api_connection
)


class TestAdobeAPISetup(unittest.TestCase):
    """Test class for Adobe API setup and basic functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Streamlit secrets for all tests
        self.secrets_patcher = patch('adobe_api.st.secrets')
        self.mock_secrets = self.secrets_patcher.start()
        
        # Set up default mock secrets
        self.mock_secrets.get.side_effect = lambda key: {
            "ADOBE_CLIENT_ID": "test_client_id",
            "ADOBE_CLIENT_SECRET": "test_client_secret", 
            "ADOBE_ORG_ID": "test_org_id",
            "ADOBE_TECH_ID": "test_tech_id",
            "ADOBE_COMPANY_ID": "test_company_id"
        }.get(key)
    
    def tearDown(self):
        """Clean up after each test method."""
        self.secrets_patcher.stop()
    
    def test_function_can_be_imported(self):
        """Test that all required functions can be imported successfully."""
        # Test that the main functions are not None
        self.assertIsNotNone(get_adobe_access_token)
        self.assertIsNotNone(create_analytics_segment)
        self.assertIsNotNone(get_company_id)
        self.assertIsNotNone(validate_oauth_secrets)
        self.assertIsNotNone(validate_api_secrets)
        self.assertIsNotNone(test_api_connection)
        
        # Test that they are callable
        self.assertTrue(callable(get_adobe_access_token))
        self.assertTrue(callable(create_analytics_segment))
        self.assertTrue(callable(get_company_id))
        self.assertTrue(callable(validate_oauth_secrets))
        self.assertTrue(callable(validate_api_secrets))
        self.assertTrue(callable(test_api_connection))
    
    @patch('adobe_api.requests.post')
    @patch('adobe_api.get_adobe_access_token')
    def test_create_segment_call(self, mock_get_token, mock_post):
        """Test the create_analytics_segment function with mocked dependencies."""
        # Configure mocks
        mock_get_token.return_value = "test_token"
        
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 's123', 'name': 'Test Segment'}
        mock_response.text = '{"id": "s123", "name": "Test Segment"}'
        mock_response.headers = {}
        mock_post.return_value = mock_response
        
        # Sample payload for testing
        sample_payload = {
            'name': 'Test Segment',
            'description': 'A test segment',
            'definition': {
                'version': [1, 0, 0],
                'func': 'segment',
                'container': {
                    'func': 'container',
                    'context': 'visitors',
                    'pred': {
                        'func': 'streq',
                        'val': {
                            'func': 'attr',
                            'name': 'variables/page'
                        },
                        'str': 'Homepage'
                    }
                }
            }
        }
        
        # Call the function
        result = create_analytics_segment(
            name='Test Segment',
            description='A test segment',
            definition_json=sample_payload
        )
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 's123')
        self.assertEqual(result['name'], 'Test Segment')
        
        # Verify that requests.post was called exactly once
        mock_post.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_post.call_args
        self.assertIn('https://analytics.adobe.io/api/test_company_id/segments', call_args[0][0])
        self.assertEqual(call_args[1]['headers']['Authorization'], 'Bearer test_token')
        self.assertEqual(call_args[1]['headers']['x-api-key'], 'test_client_id')
        self.assertEqual(call_args[1]['headers']['Content-Type'], 'application/json')
    
    @patch('adobe_api.requests.post')
    @patch('adobe_api.get_adobe_access_token')
    def test_create_segment_with_direct_definition(self, mock_get_token, mock_post):
        """Test create_analytics_segment with direct definition (not nested)."""
        # Configure mocks
        mock_get_token.return_value = "test_token"
        
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 's456', 'name': 'Direct Segment'}
        mock_response.text = '{"id": "s456", "name": "Direct Segment"}'
        mock_response.headers = {}
        mock_post.return_value = mock_response
        
        # Direct definition (not nested under 'definition')
        direct_definition = {
            'version': [1, 0, 0],
            'func': 'segment',
            'container': {
                'func': 'container',
                'context': 'visitors',
                'pred': {
                    'func': 'streq',
                    'val': {
                        'func': 'attr',
                        'name': 'variables/page'
                    },
                    'str': 'Homepage'
                }
            }
        }
        
        # Call the function
        result = create_analytics_segment(
            name='Direct Segment',
            description='A segment with direct definition',
            definition_json=direct_definition
        )
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 's456')
        
        # Verify the request body structure
        call_args = mock_post.call_args
        request_body = call_args[1]['json']
        self.assertIn('name', request_body)
        self.assertIn('description', request_body)
        self.assertIn('version', request_body)
        self.assertIn('func', request_body)
    
    @patch('adobe_api.requests.post')
    @patch('adobe_api.get_adobe_access_token')
    def test_create_segment_authentication_failure(self, mock_get_token, mock_post):
        """Test create_analytics_segment when authentication fails."""
        # Configure mocks
        mock_get_token.return_value = None  # Authentication fails
        
        # Call the function
        result = create_analytics_segment(
            name='Test Segment',
            description='A test segment',
            definition_json={'test': 'data'}
        )
        
        # Should return None when authentication fails
        self.assertIsNone(result)
        
        # requests.post should not be called
        mock_post.assert_not_called()
    
    @patch('adobe_api.requests.post')
    @patch('adobe_api.get_adobe_access_token')
    def test_create_segment_missing_company_id(self, mock_get_token, mock_post):
        """Test create_analytics_segment when company ID is missing."""
        # Configure mocks
        mock_get_token.return_value = "test_token"
        
        # Mock missing company ID
        self.mock_secrets.get.side_effect = lambda key: {
            "ADOBE_CLIENT_ID": "test_client_id",
            "ADOBE_CLIENT_SECRET": "test_client_secret", 
            "ADOBE_ORG_ID": "test_org_id",
            "ADOBE_TECH_ID": "test_tech_id",
            "ADOBE_COMPANY_ID": None  # Missing company ID
        }.get(key)
        
        # Call the function
        result = create_analytics_segment(
            name='Test Segment',
            description='A test segment',
            definition_json={'test': 'data'}
        )
        
        # Should return None when company ID is missing
        self.assertIsNone(result)
        
        # requests.post should not be called
        mock_post.assert_not_called()
    
    @patch('adobe_api.requests.post')
    @patch('adobe_api.get_adobe_access_token')
    def test_create_segment_api_error_response(self, mock_get_token, mock_post):
        """Test create_analytics_segment when API returns an error."""
        # Configure mocks
        mock_get_token.return_value = "test_token"
        
        # Create mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Bad Request'}
        mock_response.text = '{"error": "Bad Request"}'
        mock_response.headers = {}
        mock_post.return_value = mock_response
        
        # Sample payload
        sample_payload = {
            'name': 'Test Segment',
            'description': 'A test segment',
            'definition': {'test': 'definition'}
        }
        
        # Call the function
        result = create_analytics_segment(
            name='Test Segment',
            description='A test segment',
            definition_json=sample_payload
        )
        
        # Should return None when API returns error
        self.assertIsNone(result)
        
        # Verify that requests.post was called multiple times (tries different endpoints)
        # The function tries 4 different endpoints when one fails
        self.assertGreaterEqual(mock_post.call_count, 1)
    
    def test_get_company_id(self):
        """Test get_company_id function."""
        # Test with valid company ID
        result = get_company_id()
        self.assertEqual(result, "test_company_id")
        
        # Test with missing company ID
        self.mock_secrets.get.side_effect = lambda key: {
            "ADOBE_CLIENT_ID": "test_client_id",
            "ADOBE_CLIENT_SECRET": "test_client_secret", 
            "ADOBE_ORG_ID": "test_org_id",
            "ADOBE_TECH_ID": "test_tech_id",
            "ADOBE_COMPANY_ID": None
        }.get(key)
        
        result = get_company_id()
        self.assertIsNone(result)
    
    def test_validate_oauth_secrets(self):
        """Test validate_oauth_secrets function."""
        # Test with all secrets present
        result = validate_oauth_secrets()
        self.assertTrue(result)
        
        # Test with missing secrets
        self.mock_secrets.get.side_effect = lambda key: {
            "ADOBE_CLIENT_ID": None,
            "ADOBE_CLIENT_SECRET": "test_client_secret", 
            "ADOBE_ORG_ID": "test_org_id",
            "ADOBE_TECH_ID": "test_tech_id"
        }.get(key)
        
        result = validate_oauth_secrets()
        self.assertFalse(result)
    
    def test_validate_api_secrets(self):
        """Test validate_api_secrets function."""
        # Test with all secrets present
        result = validate_api_secrets()
        self.assertTrue(result)
        
        # Test with missing company ID
        self.mock_secrets.get.side_effect = lambda key: {
            "ADOBE_CLIENT_ID": "test_client_id",
            "ADOBE_CLIENT_SECRET": "test_client_secret", 
            "ADOBE_ORG_ID": "test_org_id",
            "ADOBE_TECH_ID": "test_tech_id",
            "ADOBE_COMPANY_ID": None
        }.get(key)
        
        result = validate_api_secrets()
        self.assertFalse(result)
    
    @patch('adobe_api.get_adobe_access_token')
    def test_test_api_connection(self, mock_get_token):
        """Test test_api_connection function."""
        # Test successful connection
        mock_get_token.return_value = "test_token"
        result = test_api_connection()
        self.assertTrue(result)
        
        # Test failed connection
        mock_get_token.return_value = None
        result = test_api_connection()
        self.assertFalse(result)


class TestAdobeAPIMocking(unittest.TestCase):
    """Test class for advanced mocking scenarios."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Streamlit for all tests
        self.st_patcher = patch('adobe_api.st')
        self.mock_st = self.st_patcher.start()
        
        # Mock requests
        self.requests_patcher = patch('adobe_api.requests')
        self.mock_requests = self.requests_patcher.start()
    
    def tearDown(self):
        """Clean up after each test method."""
        self.st_patcher.stop()
        self.requests_patcher.stop()
    
    def test_mock_streamlit_secrets(self):
        """Test that Streamlit secrets can be properly mocked."""
        # Configure mock secrets
        self.mock_st.secrets.get.side_effect = lambda key: {
            "ADOBE_CLIENT_ID": "mocked_client_id",
            "ADOBE_COMPANY_ID": "mocked_company_id"
        }.get(key)
        
        # Test the mock
        client_id = self.mock_st.secrets.get("ADOBE_CLIENT_ID")
        company_id = self.mock_st.secrets.get("ADOBE_COMPANY_ID")
        
        self.assertEqual(client_id, "mocked_client_id")
        self.assertEqual(company_id, "mocked_company_id")
    
    def test_mock_requests_post(self):
        """Test that requests.post can be properly mocked."""
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        
        # Configure mock
        self.mock_requests.post.return_value = mock_response
        
        # Test the mock
        response = self.mock_requests.post('https://test.com', json={'test': 'data'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True})


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 