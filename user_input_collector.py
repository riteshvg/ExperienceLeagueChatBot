#!/usr/bin/env python3
"""
User Input Collector Module

This module provides functionality to collect missing parameters and user inputs
using Streamlit widgets for the segment creation workflow.
"""

import streamlit as st
from typing import Dict, List, Optional, Any


def collect_missing_parameters(missing_mappings: List[str], available_variables: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Collect missing parameters using Streamlit widgets
    
    Args:
        missing_mappings (List[str]): List of missing variable mappings
        available_variables (Dict[str, List[str]]): Available variables by type
        
    Returns:
        Dict[str, str]: Dictionary of user-provided mappings
    """
    if not missing_mappings:
        return {}
    
    user_mappings = {}
    
    for missing_mapping in missing_mappings:
        mapping_type, variable_name = missing_mapping.split(": ", 1)
        
        if mapping_type == "eVar":
            # eVar selection
            evar_options = available_variables.get("evar", [])
            if evar_options:
                selected_evar = st.selectbox(
                    f"Select eVar for {variable_name}:",
                    options=evar_options,
                    key=f"evar_{variable_name}"
                )
                user_mappings[variable_name] = f"variables/evar{selected_evar}"
            else:
                # Custom eVar input
                custom_evar = st.text_input(
                    f"Enter eVar number for {variable_name}:",
                    placeholder="e.g., 1, 2, 3...",
                    key=f"custom_evar_{variable_name}"
                )
                if custom_evar:
                    user_mappings[variable_name] = f"variables/evar{custom_evar}"
        
        elif mapping_type == "Prop":
            # Prop selection
            prop_options = available_variables.get("prop", [])
            if prop_options:
                selected_prop = st.selectbox(
                    f"Select Prop for {variable_name}:",
                    options=prop_options,
                    key=f"prop_{variable_name}"
                )
                user_mappings[variable_name] = f"variables/prop{selected_prop}"
            else:
                # Custom Prop input
                custom_prop = st.text_input(
                    f"Enter Prop number for {variable_name}:",
                    placeholder="e.g., 1, 2, 3...",
                    key=f"custom_prop_{variable_name}"
                )
                if custom_prop:
                    user_mappings[variable_name] = f"variables/prop{custom_prop}"
        
        elif mapping_type == "Event":
            # Event selection
            event_options = available_variables.get("event", [])
            if event_options:
                selected_event = st.selectbox(
                    f"Select Event for {variable_name}:",
                    options=event_options,
                    key=f"event_{variable_name}"
                )
                user_mappings[variable_name] = f"events/{selected_event}"
            else:
                # Custom Event input
                custom_event = st.text_input(
                    f"Enter Event name for {variable_name}:",
                    placeholder="e.g., purchase, cart_add...",
                    key=f"custom_event_{variable_name}"
                )
                if custom_event:
                    user_mappings[variable_name] = f"events/{custom_event}"
        
        elif mapping_type == "Custom":
            # Custom variable input
            custom_variable = st.text_input(
                f"Enter variable name for {variable_name}:",
                placeholder="e.g., variables/custom_var",
                key=f"custom_{variable_name}"
            )
            if custom_variable:
                user_mappings[variable_name] = custom_variable
        
        else:
            # Unknown type - text input
            unknown_variable = st.text_input(
                f"Enter variable name for {variable_name}:",
                placeholder="e.g., variables/unknown_var",
                key=f"unknown_{variable_name}"
            )
            if unknown_variable:
                user_mappings[variable_name] = unknown_variable
    
    return user_mappings


def collect_operator_selection(variable_name: str, available_operators: List[str] = None) -> str:
    """
    Collect operator selection for a variable
    
    Args:
        variable_name (str): Name of the variable
        available_operators (List[str]): Available operators (optional)
        
    Returns:
        str: Selected operator
    """
    if available_operators is None:
        available_operators = ["equals", "contains", "exists", "greater_than", "less_than"]
    
    selected_operator = st.selectbox(
        f"Select operator for {variable_name}:",
        options=available_operators,
        key=f"operator_{variable_name}"
    )
    
    return selected_operator


def collect_value_input(variable_name: str, variable_type: str = "string") -> str:
    """
    Collect value input for a variable
    
    Args:
        variable_name (str): Name of the variable
        variable_type (str): Type of variable (string, number, boolean)
        
    Returns:
        str: Input value
    """
    if variable_type == "number":
        value = st.number_input(
            f"Enter value for {variable_name}:",
            key=f"value_{variable_name}"
        )
        return str(value)
    elif variable_type == "boolean":
        value = st.selectbox(
            f"Select value for {variable_name}:",
            options=["true", "false"],
            key=f"value_{variable_name}"
        )
        return value
    else:
        value = st.text_input(
            f"Enter value for {variable_name}:",
            key=f"value_{variable_name}"
        )
        return value


def collect_api_credentials() -> Dict[str, str]:
    """
    Collect OAuth API credentials using Streamlit sidebar
    
    Returns:
        Dict[str, str]: Dictionary of OAuth credentials
    """
    with st.sidebar:
        st.header("🔐 Adobe Analytics OAuth Configuration")
        st.info("💡 Configure your OAuth credentials to access Adobe Analytics API")
        
        # Initialize session state for credentials
        if "api_credentials" not in st.session_state:
            st.session_state.api_credentials = {
                "client_id": "",
                "client_secret": "",
                "org_id": ""
            }
        
        # Adobe Client ID
        client_id = st.text_input(
            "Adobe Client ID:",
            value=st.session_state.api_credentials.get("client_id", ""),
            type="password",
            key="api_client_id",
            help="Your Adobe Analytics API Client ID"
        )
        
        # Adobe Client Secret
        client_secret = st.text_input(
            "Adobe Client Secret:",
            value=st.session_state.api_credentials.get("client_secret", ""),
            type="password",
            key="api_client_secret",
            help="Your Adobe Analytics API Client Secret"
        )
        
        # Adobe Organization ID
        org_id = st.text_input(
            "Adobe Organization ID:",
            value=st.session_state.api_credentials.get("org_id", ""),
            key="api_org_id",
            help="Your Adobe Analytics Organization ID"
        )
        
        # Save credentials to session state
        if client_id and client_secret and org_id:
            st.session_state.api_credentials = {
                "client_id": client_id,
                "client_secret": client_secret,
                "org_id": org_id
            }
            
            # Test connection button
            if st.button("🔗 Test OAuth Connection", key="test_oauth_connection"):
                st.session_state.test_connection = True
                st.success("✅ OAuth credentials configured! Access token will be generated automatically.")
        
        return st.session_state.api_credentials


def get_confirmation(segment_summary: str) -> bool:
    """
    Get user confirmation for segment creation
    
    Args:
        segment_summary (str): Human-readable segment summary
        
    Returns:
        bool: True if user confirms creation
    """
    st.markdown("### 📋 Segment Summary")
    st.markdown(segment_summary)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        create_segment = st.button(
            "✅ Create Segment",
            type="primary",
            key="create_segment_confirm"
        )
    
    with col2:
        cancel_creation = st.button(
            "❌ Cancel",
            key="cancel_segment_creation"
        )
    
    if create_segment:
        return True
    elif cancel_creation:
        return False
    
    return False


def collect_segment_metadata() -> Dict[str, str]:
    """
    Collect segment metadata (name, description, etc.)
    
    Returns:
        Dict[str, str]: Segment metadata
    """
    st.markdown("### 📝 Segment Details")
    
    # Segment name
    segment_name = st.text_input(
        "Segment Name:",
        value=st.session_state.get("segment_name", ""),
        key="segment_name_input"
    )
    
    # Segment description
    segment_description = st.text_area(
        "Segment Description:",
        value=st.session_state.get("segment_description", ""),
        key="segment_description_input"
    )
    
    # Report Suite ID
    report_suite_id = st.text_input(
        "Report Suite ID:",
        value=st.session_state.get("report_suite_id", ""),
        key="segment_rsid_input"
    )
    
    # Context level
    context_level = st.selectbox(
        "Context Level:",
        options=["visitors", "visits", "hits"],
        index=0,
        key="segment_context_input"
    )
    
    # Store in session state
    st.session_state.segment_name = segment_name
    st.session_state.segment_description = segment_description
    st.session_state.report_suite_id = report_suite_id
    st.session_state.context_level = context_level
    
    return {
        "name": segment_name,
        "description": segment_description,
        "rsid": report_suite_id,
        "context": context_level
    }


def collect_additional_conditions() -> List[Dict[str, str]]:
    """
    Collect additional conditions for the segment
    
    Returns:
        List[Dict[str, str]]: List of additional conditions
    """
    st.markdown("### ➕ Additional Conditions")
    
    additional_conditions = []
    
    if st.checkbox("Add additional condition", key="add_condition_checkbox"):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            variable_name = st.text_input(
                "Variable:",
                placeholder="e.g., device, page, event",
                key="additional_variable"
            )
        
        with col2:
            operator = st.selectbox(
                "Operator:",
                options=["equals", "contains", "exists", "greater_than", "less_than"],
                key="additional_operator"
            )
        
        with col3:
            value = st.text_input(
                "Value:",
                placeholder="e.g., mobile, homepage",
                key="additional_value"
            )
        
        if variable_name and operator and value:
            additional_conditions.append({
                "variable": variable_name,
                "operator": operator,
                "value": value,
                "type": "custom"
            })
    
    return additional_conditions


def show_validation_results(validation_result: Dict[str, Any]) -> None:
    """
    Show validation results to the user
    
    Args:
        validation_result (Dict[str, Any]): Validation result from API
    """
    if validation_result.get("success", False):
        st.success("✅ Segment validation successful!")
        if "data" in validation_result:
            st.json(validation_result["data"])
    else:
        st.error("❌ Segment validation failed!")
        if "error" in validation_result:
            st.error(f"Error: {validation_result['error']}")
        if "message" in validation_result:
            st.error(f"Message: {validation_result['message']}")


def show_creation_results(creation_result: Dict[str, Any]) -> None:
    """
    Show segment creation results to the user
    
    Args:
        creation_result (Dict[str, Any]): Creation result from API
    """
    if creation_result.get("success", False):
        st.success("🎉 Segment created successfully!")
        if "data" in creation_result:
            st.json(creation_result["data"])
    else:
        st.error("❌ Segment creation failed!")
        if "error" in creation_result:
            st.error(f"Error: {creation_result['error']}")
        if "message" in creation_result:
            st.error(f"Message: {creation_result['message']}")


def clear_session_state() -> None:
    """Clear segment-related session state"""
    keys_to_clear = [
        "segment_name", "segment_description", "report_suite_id", "context_level",
        "api_credentials", "test_connection", "segment_metadata"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def get_session_state_value(key: str, default: Any = None) -> Any:
    """
    Get value from session state with default
    
    Args:
        key (str): Session state key
        default (Any): Default value if key doesn't exist
        
    Returns:
        Any: Session state value or default
    """
    return st.session_state.get(key, default)


def set_session_state_value(key: str, value: Any) -> None:
    """
    Set value in session state
    
    Args:
        key (str): Session state key
        value (Any): Value to set
    """
    st.session_state[key] = value
