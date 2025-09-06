#!/usr/bin/env python3
"""
Segment Chat Handler Module

This module provides functionality to integrate segment creation workflow
with the existing Streamlit chatbot interface.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
import json

# Import the segment creation modules
try:
    from segment_parser import segment_parser
    from variable_mapper import variable_mapper
    from segment_builder import segment_builder
    from adobe_api_client import create_adobe_client
    from user_input_collector import (
        collect_missing_parameters, 
        collect_api_credentials,
        get_confirmation,
        collect_segment_metadata,
        show_validation_results,
        show_creation_results
    )
    SEGMENT_MODULES_AVAILABLE = True
except ImportError as e:
    SEGMENT_MODULES_AVAILABLE = False
    st.error(f"Segment modules not available: {e}")


def handle_segment_request(user_message: str, chat_container) -> None:
    """
    Main orchestration function for segment creation flow
    
    Args:
        user_message (str): User's message containing segment request
        chat_container: Streamlit container for chat display
    """
    if not SEGMENT_MODULES_AVAILABLE:
        with chat_container:
            st.error("❌ Segment creation modules not available")
        return
    
    # Initialize session state for segment workflow
    if "segment_workflow_state" not in st.session_state:
        st.session_state.segment_workflow_state = {
            "step": "detection",
            "components": [],
            "mappings": [],
            "missing_parameters": [],
            "user_inputs": {},
            "segment_definition": None,
            "api_credentials": {}
        }
    
    workflow_state = st.session_state.segment_workflow_state
    
    with chat_container:
        # Step 1: Parse user message for segment components
        if workflow_state["step"] == "detection":
            st.info("🔍 Analyzing your segment request...")
            
            components = segment_parser.parse_segment_components(user_message)
            workflow_state["components"] = components["conditions"]
            workflow_state["step"] = "mapping"
            
            if not components["conditions"]:
                st.warning("⚠️ No segment conditions detected in your message")
                return
            
            st.success(f"✅ Found {len(components['conditions'])} segment conditions")
        
        # Step 2: Map variables to Adobe Analytics references
        if workflow_state["step"] == "mapping":
            st.info("🔄 Mapping variables to Adobe Analytics references...")
            
            mappings = []
            for component in workflow_state["components"]:
                mapping = variable_mapper.map_variable(component)
                mappings.append(mapping)
            
            workflow_state["mappings"] = mappings
            
            # Check for missing mappings
            missing_mappings = variable_mapper.get_missing_mappings(workflow_state["components"])
            workflow_state["missing_parameters"] = missing_mappings
            
            if missing_mappings:
                st.warning(f"⚠️ {len(missing_mappings)} parameters need user input")
                workflow_state["step"] = "user_input"
            else:
                st.success("✅ All variables mapped successfully")
                workflow_state["step"] = "metadata"
        
        # Step 3: Collect missing parameters and user input
        if workflow_state["step"] == "user_input":
            st.info("📝 Please provide missing parameter information...")
            
            # Get available variables (mock data for now)
            available_variables = {
                "evar": ["1", "2", "3", "4", "5"],
                "prop": ["1", "2", "3"],
                "event": ["purchase", "cart_add", "checkout", "newsletter"]
            }
            
            user_mappings = collect_missing_parameters(
                workflow_state["missing_parameters"], 
                available_variables
            )
            
            if user_mappings:
                # Update mappings with user input
                for i, mapping in enumerate(workflow_state["mappings"]):
                    if mapping["original_variable"] in user_mappings:
                        mapping["name"] = user_mappings[mapping["original_variable"]]
                
                st.success("✅ User parameters collected")
                workflow_state["step"] = "metadata"
            else:
                st.warning("⚠️ Please fill in all required parameters")
                return
        
        # Step 4: Collect segment metadata
        if workflow_state["step"] == "metadata":
            st.info("📋 Please provide segment details...")
            
            metadata = collect_segment_metadata()
            
            if metadata["name"] and metadata["rsid"]:
                workflow_state["user_inputs"] = metadata
                workflow_state["step"] = "building"
                st.success("✅ Segment metadata collected")
            else:
                st.warning("⚠️ Please provide segment name and RSID")
                return
        
        # Step 5: Build segment definition and show summary
        if workflow_state["step"] == "building":
            st.info("🔨 Building segment definition...")
            
            # Get suggested context
            suggested_context = variable_mapper.suggest_context(workflow_state["components"])
            workflow_state["user_inputs"]["context"] = suggested_context
            
            # Build segment definition
            segment_definition = segment_builder.build_segment_definition(
                workflow_state["components"],
                workflow_state["mappings"],
                workflow_state["user_inputs"]
            )
            
            workflow_state["segment_definition"] = segment_definition
            
            # Display summary
            summary = segment_builder.format_segment_summary(segment_definition)
            display_segment_summary(summary)
            
            workflow_state["step"] = "confirmation"
        
        # Step 6: Get user confirmation for creation
        if workflow_state["step"] == "confirmation":
            st.info("🤔 Please review and confirm segment creation...")
            
            summary = segment_builder.format_segment_summary(workflow_state["segment_definition"])
            confirmed = get_confirmation(summary)
            
            if confirmed:
                workflow_state["step"] = "api_credentials"
            elif confirmed is False:
                st.info("❌ Segment creation cancelled")
                reset_segment_workflow()
                return
        
        # Step 7: Collect API credentials
        if workflow_state["step"] == "api_credentials":
            st.info("🔐 Please configure Adobe Analytics API credentials...")
            
            credentials = collect_api_credentials()
            
            if all(credentials.values()):
                workflow_state["api_credentials"] = credentials
                workflow_state["step"] = "validation"
                st.success("✅ API credentials configured")
            else:
                st.warning("⚠️ Please provide all API credentials")
                return
        
        # Step 8: Validate and create segment via API
        if workflow_state["step"] == "validation":
            st.info("🔍 Validating segment with Adobe Analytics API...")
            
            # Create API client
            client = create_adobe_client(
                workflow_state["api_credentials"]["client_id"],
                workflow_state["api_credentials"]["access_token"],
                workflow_state["api_credentials"]["company_id"]
            )
            
            # Validate segment
            validation_result = client.validate_segment(
                workflow_state["segment_definition"]["definition"],
                workflow_state["segment_definition"]["rsid"]
            )
            
            show_validation_results(validation_result)
            
            if validation_result["success"]:
                workflow_state["step"] = "creation"
                st.success("✅ Segment validation successful")
            else:
                st.error("❌ Segment validation failed")
                return
        
        # Step 9: Create segment
        if workflow_state["step"] == "creation":
            st.info("🚀 Creating segment in Adobe Analytics...")
            
            # Create API client
            client = create_adobe_client(
                workflow_state["api_credentials"]["client_id"],
                workflow_state["api_credentials"]["access_token"],
                workflow_state["api_credentials"]["company_id"]
            )
            
            # Create segment
            creation_result = client.create_segment(workflow_state["segment_definition"])
            
            show_creation_results(creation_result)
            
            if creation_result["success"]:
                st.success("🎉 Segment created successfully!")
                display_creation_results(creation_result)
                reset_segment_workflow()
            else:
                st.error("❌ Segment creation failed")
                return


def display_segment_summary(summary_text: str) -> None:
    """
    Show formatted segment description
    
    Args:
        summary_text (str): Formatted segment summary
    """
    st.markdown("### 📊 Segment Preview")
    st.markdown(summary_text)


def display_creation_results(api_response: Dict[str, Any]) -> None:
    """
    Show success message with segment ID or error message
    
    Args:
        api_response (Dict[str, Any]): API response from segment creation
    """
    if api_response.get("success", False):
        data = api_response.get("data", {})
        segment_id = data.get("id", "Unknown")
        segment_name = data.get("name", "Unknown")
        
        st.success(f"🎉 **Segment Created Successfully!**")
        st.info(f"**Segment ID:** `{segment_id}`")
        st.info(f"**Segment Name:** `{segment_name}`")
        
        # Show additional details if available
        if "description" in data:
            st.info(f"**Description:** {data['description']}")
        if "rsid" in data:
            st.info(f"**Report Suite ID:** {data['rsid']}")
    else:
        error = api_response.get("error", {})
        message = api_response.get("message", "Unknown error")
        
        st.error(f"❌ **Segment Creation Failed**")
        st.error(f"**Error:** {message}")
        
        if error:
            st.error(f"**Details:** {json.dumps(error, indent=2)}")


def reset_segment_workflow() -> None:
    """Reset the segment workflow state"""
    if "segment_workflow_state" in st.session_state:
        del st.session_state.segment_workflow_state


def get_current_workflow_step() -> str:
    """
    Get the current workflow step
    
    Returns:
        str: Current workflow step
    """
    if "segment_workflow_state" in st.session_state:
        return st.session_state.segment_workflow_state.get("step", "detection")
    return "detection"


def is_segment_workflow_active() -> bool:
    """
    Check if segment workflow is currently active
    
    Returns:
        bool: True if workflow is active
    """
    return "segment_workflow_state" in st.session_state


def get_workflow_progress() -> Dict[str, Any]:
    """
    Get current workflow progress information
    
    Returns:
        Dict[str, Any]: Workflow progress details
    """
    if not is_segment_workflow_active():
        return {"active": False}
    
    workflow_state = st.session_state.segment_workflow_state
    
    return {
        "active": True,
        "step": workflow_state.get("step", "detection"),
        "components_count": len(workflow_state.get("components", [])),
        "mappings_count": len(workflow_state.get("mappings", [])),
        "missing_parameters_count": len(workflow_state.get("missing_parameters", [])),
        "has_metadata": bool(workflow_state.get("user_inputs", {}).get("name")),
        "has_credentials": bool(workflow_state.get("api_credentials", {}).get("client_id")),
        "has_definition": bool(workflow_state.get("segment_definition"))
    }


def continue_segment_workflow() -> None:
    """Continue the segment workflow from current step"""
    if not is_segment_workflow_active():
        return
    
    workflow_state = st.session_state.segment_workflow_state
    current_step = workflow_state.get("step", "detection")
    
    # This would be called from the main chat handler
    # to continue the workflow from where it left off
    pass


def cancel_segment_workflow() -> None:
    """Cancel the current segment workflow"""
    reset_segment_workflow()
    st.info("❌ Segment creation workflow cancelled")


def show_workflow_status() -> None:
    """Show current workflow status in the UI"""
    if not is_segment_workflow_active():
        return
    
    progress = get_workflow_progress()
    
    st.sidebar.markdown("### 🔧 Segment Creation Status")
    
    steps = [
        ("detection", "🔍 Detection"),
        ("mapping", "🔄 Mapping"),
        ("user_input", "📝 User Input"),
        ("metadata", "📋 Metadata"),
        ("building", "🔨 Building"),
        ("confirmation", "🤔 Confirmation"),
        ("api_credentials", "🔐 API Credentials"),
        ("validation", "🔍 Validation"),
        ("creation", "🚀 Creation")
    ]
    
    current_step = progress["step"]
    
    for step_id, step_name in steps:
        if step_id == current_step:
            st.sidebar.markdown(f"**{step_name}** ⏳")
        elif steps.index((step_id, step_name)) < steps.index((current_step, next(name for id, name in steps if id == current_step))):
            st.sidebar.markdown(f"✅ {step_name}")
        else:
            st.sidebar.markdown(f"⏸️ {step_name}")
    
    # Show progress details
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Components:** {progress['components_count']}")
    st.sidebar.markdown(f"**Mappings:** {progress['mappings_count']}")
    st.sidebar.markdown(f"**Missing:** {progress['missing_parameters_count']}")
    
    if st.sidebar.button("❌ Cancel Workflow"):
        cancel_segment_workflow()
        st.rerun()
