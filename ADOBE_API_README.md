# 🔐 Adobe Analytics 2.0 API Integration

This directory contains Python scripts for securely interacting with the Adobe Analytics 2.0 API using Streamlit and the `requests` library.

## 📁 Files

- **`adobe_api.py`** - Main API module with authentication and segment creation functions
- **`test_adobe_api.py`** - Interactive test suite for testing API functionality
- **`ADOBE_API_README.md`** - This documentation file

## 🚀 Quick Start

### 1. Install Dependencies

The required dependencies are already included in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Configure Adobe API Credentials

Create a `.streamlit/secrets.toml` file in your project root:

```toml
# Adobe Analytics 2.0 API Credentials
ADOBE_CLIENT_ID = "your_client_id_here"
ADOBE_CLIENT_SECRET = "your_client_secret_here"
ADOBE_ORG_ID = "your_organization_id_here"
ADOBE_TECH_ID = "your_technical_account_id_here"
ADOBE_COMPANY_ID = "your_analytics_company_id_here"
```

### 3. Test the API

Run the test suite to verify your configuration:

```bash
streamlit run test_adobe_api.py
```

## 🔧 Core Functions

### Authentication

#### `get_adobe_access_token()`
- **Purpose**: Obtains a JWT access token from Adobe Identity Management System
- **Returns**: Access token string or `None` if failed
- **Security**: Uses `st.secrets` for credential storage
- **Error Handling**: Comprehensive error handling with user-friendly messages

### Segment Creation

#### `create_analytics_segment(name, description, definition_json)`
- **Purpose**: Creates a new Adobe Analytics segment via API
- **Parameters**:
  - `name` (str): Segment name
  - `description` (str): Segment description  
  - `definition_json` (dict): Segment definition in Adobe's JSON format
- **Returns**: API response JSON or `None` if failed
- **Headers**: Automatically includes required Authorization and x-api-key headers

### Utility Functions

#### `validate_secrets()`
- **Purpose**: Checks if all required secrets are configured
- **Returns**: `True` if all secrets present, `False` otherwise

#### `get_company_id()`
- **Purpose**: Retrieves the configured Adobe Analytics company ID
- **Returns**: Company ID string or `None` if missing

## 📊 Example Usage

### Basic Segment Creation

```python
from adobe_api import create_analytics_segment

# Define segment for users with >10 page views
segment_definition = {
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

# Create the segment
result = create_analytics_segment(
    name="High Engagement Users",
    description="Users with more than 10 page views per session",
    definition_json=segment_definition
)

if result:
    print("Segment created successfully!")
    print(f"Segment ID: {result.get('id')}")
else:
    print("Failed to create segment")
```

### Integration with Main App

```python
import streamlit as st
from adobe_api import create_analytics_segment, validate_secrets

def create_segment_ui():
    if not validate_secrets():
        st.error("Adobe API credentials not configured")
        return
    
    with st.form("create_segment"):
        name = st.text_input("Segment Name")
        description = st.text_area("Description")
        
        if st.form_submit_button("Create Segment"):
            # Your segment definition logic here
            definition = {"container": {...}}  # Your JSON definition
            
            result = create_analytics_segment(name, description, definition)
            if result:
                st.success("Segment created successfully!")
                st.json(result)
            else:
                st.error("Failed to create segment")
```

## 🔒 Security Features

### Credential Management
- **Streamlit Secrets**: All API credentials stored in `st.secrets`
- **No Hardcoding**: No credentials in source code
- **Environment Variables**: Support for production deployment

### API Security
- **JWT Authentication**: Secure token-based authentication
- **Fresh Tokens**: Access tokens obtained for each request
- **Secure Headers**: Proper Authorization and x-api-key headers
- **Timeout Protection**: Request timeouts to prevent hanging

### Error Handling
- **No Sensitive Data Logging**: Credentials never logged or displayed
- **User-Friendly Errors**: Clear error messages without exposing internals
- **Graceful Degradation**: App continues to function even if API fails

## 🧪 Testing

### Test Suite Features
- **Connection Testing**: Verify API credentials work
- **Segment Creation**: Test segment creation with sample data
- **Secrets Validation**: Check if all required credentials are present
- **Interactive UI**: Streamlit-based test interface

### Running Tests
```bash
# Run the full test suite
streamlit run test_adobe_api.py

# Test individual functions
python3 -c "
from adobe_api import test_api_connection, validate_secrets
print(f'Secrets valid: {validate_secrets()}')
print(f'API connection: {test_api_connection()}')
"
```

## 📚 Adobe API Resources

### Official Documentation
- [Adobe Analytics 2.0 API Reference](https://developer.adobe.com/analytics-apis/docs/2.0/)
- [Adobe IMS Authentication](https://developer.adobe.com/authentication/auth-overview/)
- [Segment Builder API](https://developer.adobe.com/analytics-apis/docs/2.0/guides/endpoints/segments/)

### Segment Definition Examples
- [Adobe Analytics Segment Builder](https://experienceleague.adobe.com/docs/analytics/components/segmentation/segmentation-workflow/seg-build.html)
- [Segment Definition Reference](https://experienceleague.adobe.com/docs/analytics/components/segmentation/segmentation-workflow/seg-build.html#segment-definition)

## 🚨 Troubleshooting

### Common Issues

#### Missing Secrets
```
❌ Missing required secrets: ADOBE_CLIENT_ID, ADOBE_CLIENT_SECRET
```
**Solution**: Configure all required secrets in `.streamlit/secrets.toml`

#### Authentication Failed
```
❌ Failed to connect to Adobe API
```
**Solution**: Verify your credentials and ensure your Adobe account has API access

#### Company ID Issues
```
❌ Missing ADOBE_COMPANY_ID secret
```
**Solution**: Find your company ID in Adobe Analytics Admin Console

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
export STREAMLIT_LOG_LEVEL=debug
streamlit run test_adobe_api.py
```

## 🔄 Updates and Maintenance

### Version Compatibility
- **Adobe Analytics API**: 2.0+
- **Python**: 3.8+
- **Streamlit**: 1.28.0+
- **Requests**: 2.31.0+

### Contributing
When updating the API integration:
1. Test with `test_adobe_api.py`
2. Verify error handling works
3. Update this documentation
4. Test in your main application

## 📞 Support

For issues with:
- **Adobe API**: Contact Adobe Developer Support
- **This Integration**: Check the test suite and error messages
- **Streamlit**: Refer to [Streamlit Documentation](https://docs.streamlit.io/)

---

**⚠️ Important**: Never commit your `.streamlit/secrets.toml` file to version control. Add it to `.gitignore` to prevent accidental exposure of credentials. 