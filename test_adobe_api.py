#!/usr/bin/env python3
"""
Test script for Adobe Analytics 2.0 API functionality.
This script demonstrates how to use the adobe_api.py module.
"""

import streamlit as st
from adobe_api import (
    test_api_connection, 
    create_sample_segment, 
    validate_oauth_secrets,
    validate_api_secrets,
    get_company_id
)

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
    
    # Create Sample Segment
    st.header("📊 Segment Creation Test")
    
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
            if st.button("🏷️ Create Sample Segment", type="secondary"):
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
    
    # Usage Instructions
    st.header("📖 Usage Instructions")
    st.markdown("""
    ### 🔧 Integration with Main App
    
    To use this API in your main Streamlit app:
    
    ```python
    from adobe_api import create_analytics_segment, get_adobe_access_token
    
    # Create a segment
    result = create_analytics_segment(
        name="My Custom Segment",
        description="Users who visited specific pages",
        definition_json=your_segment_definition
    )
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
    """)

if __name__ == "__main__":
    main() 