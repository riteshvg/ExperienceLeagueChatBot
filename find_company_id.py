#!/usr/bin/env python3
"""
Helper script to find your Adobe Analytics Company ID
"""

import streamlit as st

def main():
    st.set_page_config(
        page_title="Find Adobe Company ID",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Find Your Adobe Analytics Company ID")
    
    st.markdown("""
    ## 🚨 **Your Current Company ID is Invalid!**
    
    **Current Value:** `adober1f` (only 9 characters)
    
    **Required Format:** 32-character hexadecimal string
    
    ---
    """)
    
    st.header("📍 **Step-by-Step Guide to Find Your Company ID**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ **Access Adobe Analytics**")
        st.markdown("""
        - Go to [Adobe Analytics](https://analytics.adobe.com)
        - Sign in with your Adobe ID
        - Make sure you have **Admin** access
        """)
        
        st.subheader("2️⃣ **Navigate to Admin Console**")
        st.markdown("""
        - Click **Admin** in the top navigation
        - Select **Company Settings**
        - Look for **Company Information** section
        """)
    
    with col2:
        st.subheader("3️⃣ **Find Company ID**")
        st.markdown("""
        - Look for **Company ID** or **Global Company ID**
        - It should be a long string like:
          `1234567890abcdef1234567890abcdef`
        - Copy the entire string
        """)
        
        st.subheader("4️⃣ **Update Your Secrets**")
        st.markdown("""
        - Open `.streamlit/secrets.toml`
        - Replace the current value with the correct one
        - Restart your Streamlit app
        """)
    
    st.markdown("---")
    
    st.header("🔧 **Alternative Methods**")
    
    st.subheader("**Method A: Check Your Analytics URL**")
    st.markdown("""
    When you're in Adobe Analytics, look at the URL:
    ```
    https://analytics.adobe.com/#/YOUR_COMPANY_ID/reports
    ```
    The part after `#/` and before `/reports` is often your Company ID.
    """)
    
    st.subheader("**Method B: Adobe Developer Console**")
    st.markdown("""
    1. Go to [Adobe Developer Console](https://developer.adobe.com/console)
    2. Select your project
    3. Check the project details for Company ID
    """)
    
    st.subheader("**Method C: Contact Your Admin**")
    st.markdown("""
    If you can't find it, contact your Adobe Analytics administrator.
    They should have access to this information.
    """)
    
    st.markdown("---")
    
    st.header("⚠️ **Important Notes**")
    
    st.info("""
    - **Company ID ≠ Organization ID** (they're different)
    - **Company ID ≠ Report Suite ID** (they're different)
    - Company ID is specific to Adobe Analytics
    - It's usually 32 characters long
    - Format: hexadecimal (0-9, a-f)
    """)
    
    st.warning("""
    **Don't confuse with:**
    - `ADOBE_ORG_ID`: Your Adobe organization ID
    - `ADOBE_COMPANY_ID`: Your Adobe Analytics company ID
    - Report Suite IDs: Individual report suite identifiers
    """)
    
    st.markdown("---")
    
    st.header("🧪 **Test Your New Company ID**")
    
    st.markdown("""
    Once you update your Company ID:
    1. Restart your Streamlit app
    2. Run the API connection test
    3. Try creating a sample segment
    4. The 403 error should be resolved
    """)
    
    st.success("""
    **Expected Result:**
    - ✅ API connection successful
    - ✅ Sample segment created
    - ✅ No more 403 errors
    """)

if __name__ == "__main__":
    main() 