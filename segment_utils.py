#!/usr/bin/env python3
"""
Shared utilities for Adobe Analytics segment building functionality.

This module provides common functionality for both the standalone segment builder
and the integrated segment builder in the main app, ensuring consistency and
avoiding code duplication.
"""

import streamlit as st
import json
from typing import Dict, Any, List, Optional, Tuple
from error_handling import ValidationErrorHandler, validate_segment_configuration


def _to_pred(rule: dict) -> dict:
    """
    Convert a single simplified rule into a correct Adobe predicate.
    
    Args:
        rule: Single simplified rule object
        
    Returns:
        dict: Bare Adobe Analytics predicate with proper typing and structure
    """
    func = rule.get('func', 'streq')
    name = rule.get('name', 'variables/geocountry')
    
    # Handle different predicate types with correct typing
    if func in ['streq', 'not-streq', 'contains', 'regex']:
        # String functions use "str" type
        return {
            "func": func,
            "val": {
                "func": "attr",
                "name": name
            },
            "str": rule.get('str', rule.get('val', ''))
        }
    elif func in ['gt', 'lt', 'gte', 'lte']:
        # Numeric functions use "num" type
        return {
            "func": func,
            "val": {
                "func": "attr",
                "name": name
            },
            "num": rule.get('val', 0)
        }
    elif func == 'event-exists':
        # Event-exists uses "evt" structure
        return {
            "func": "event-exists",
            "evt": {
                "func": "event",
                "name": rule.get('evt', {}).get('name', 'metrics/purchase')
            }
        }
    elif func == 'streq-in':
        # streq-in uses "list" type and "val" structure
        return {
            "func": "streq-in",
            "val": {
                "func": "attr",
                "name": name
            },
            "list": rule.get('list', [])
        }
    else:
        # Default case for unknown functions
        return {
            "func": func,
            "val": {
                "func": "attr",
                "name": name
            },
            "str": rule.get('str', rule.get('val', ''))
        }


def build_adobe_definition(rules: List[Dict[str, Any]], target_audience: str) -> Dict[str, Any]:
    """
    Transform simplified rules into proper Adobe Analytics 2.0 API segment format
    
    Args:
        rules: List of simplified rule objects
        target_audience: Target audience context (visitors, visits, hits)
    
    Returns:
        dict: Adobe Analytics 2.0 API compatible segment definition
    """
    if not rules:
        return None
    
    # Build array of bare predicates using the centralized helper
    predicates = [_to_pred(rule) for rule in rules]
    
    # Determine the inner predicate structure
    if len(predicates) == 1:
        # Single predicate - use it directly
        inner_pred = predicates[0]
    else:
        # Multiple predicates - combine with AND logic
        inner_pred = {
            "func": "and",
            "preds": predicates
        }
    
    # Return the complete Adobe definition with proper container structure
    return {
        "version": [1, 0, 0],
        "func": "segment",
        "container": {
            "func": "container",
            "context": target_audience,
            "pred": inner_pred
        }
    }


def build_segment_payload(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the complete segment payload for Adobe Analytics API.
    
    Args:
        config: Segment configuration containing name, description, rsid, target_audience, and rules
        
    Returns:
        Complete Adobe Analytics API payload
    """
    # Use the proper Adobe definition builder
    definition = build_adobe_definition(config['rules'], config['target_audience'])
    
    # Build the complete payload
    payload = {
        "name": config['name'],
        "description": config['description'],
        "rsid": config['rsid'],
        "definition": definition
    }
    
    return payload




def render_live_preview_section(config: Dict[str, Any], rules: List[Dict[str, Any]] = None) -> None:
    """
    Display the configured rules in an expandable format and show the Adobe Analytics JSON payload preview.
    
    Args:
        config: Segment configuration
        rules: Optional list of rules to display (if different from config['rules'])
    """
    if rules is None:
        rules = config.get('rules', [])
    
    st.write("**🔍 Live Preview of Configured Rules**")
    
    if rules:
        # Show rules in a nice format with live updates
        for i, rule in enumerate(rules):
            with st.expander(f"Rule {i+1}: {rule.get('description', rule.get('func', 'Custom Rule'))}", expanded=True):
                # Create a more readable display
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write(f"**Type:** {rule.get('type', 'Unknown').title()}")
                    st.write(f"**Function:** {rule.get('func', 'Unknown')}")
                
                with col2:
                    if rule.get('type') == 'geographic':
                        st.write(f"**Target:** {rule.get('val', 'Unknown')}")
                        st.write(f"**Variable:** {rule.get('name', 'Unknown')}")
                    elif rule.get('type') == 'device':
                        st.write(f"**Device:** {rule.get('val', 'Unknown')}")
                        st.write(f"**eVar:** {rule.get('name', 'Unknown')}")
                    elif rule.get('type') == 'behavioral':
                        if rule.get('func') == 'gt':
                            st.write(f"**Threshold:** {rule.get('val', 'Unknown')}")
                            st.write(f"**Metric:** {rule.get('name', 'Unknown')}")
                        elif rule.get('func') == 'event-exists':
                            st.write(f"**Event:** {rule.get('evt', {}).get('name', 'Unknown')}")
                    elif rule.get('type') == 'time_based':
                        if rule.get('func') == 'streq-in':
                            st.write(f"**Values:** {', '.join(rule.get('list', []))}")
                            st.write(f"**Variable:** {rule.get('name', 'Unknown')}")
                    
                    # Show the raw rule structure in a collapsible section
                    with st.expander("📋 Raw Rule Structure", expanded=False):
                        st.json(rule)
        
        # Summary of all rules
        st.success(f"✅ **{len(rules)} rules configured successfully!**")
        
        # Show what the segment will target
        st.write("**🎯 This segment will target:**")
        targeting_summary = []
        for rule in rules:
            targeting_summary.append(rule.get('description', 'Custom rule'))
        
        for summary in targeting_summary:
            st.write(f"• {summary}")
        
        # Preview Adobe Analytics format
        st.subheader("🔍 Adobe Analytics Format Preview")
        st.info("This is how your segment will be structured when sent to Adobe Analytics:")
        
        try:
            with st.spinner('🔄 Generating Adobe Analytics preview...'):
                adobe_payload = build_segment_payload(config)
            
            # Show the Adobe Analytics format
            st.json(adobe_payload)
            
            # Explain the structure
            with st.expander("📚 Understanding Adobe Analytics Format", expanded=False):
                st.write("""
                **Adobe Analytics Segment Structure:**
                
                - **version**: Segment definition version
                - **func**: Function type (always 'segment')
                - **container**: Contains the segment logic
                - **context**: Target audience (visitors, visits, hits)
                - **pred**: Predicate defining the segment conditions
                - **func**: Comparison function (streq, gt, event-exists, etc.)
                - **val**: Value object with attribute function
                - **name**: Variable name (e.g., variables/geocountry)
                - **str**: String value for comparison
                """)
                
        except Exception as e:
            st.error(f"Could not generate Adobe Analytics format preview: {str(e)}")
            
    else:
        st.warning("⚠️ **No rules configured yet.** Please fill in the fields above to see live updates.")
        st.info("💡 **Tip:** As you fill in the fields above, the configured rules will appear here automatically!")


def render_validation_messages(errors: List[str]) -> None:
    """
    Display real-time validation errors in a consistent format.
    
    Args:
        errors: List of error messages to display
    """
    if errors:
        st.error("❌ **Validation Errors:**")
        for error in errors:
            st.error(f"  - {error}")
    else:
        st.success("✅ **Configuration is valid**")


# Import validation functions from error_handling to avoid duplication
from error_handling import (
    validate_segment_name_realtime,
    validate_rsid_realtime,
    validate_rules_realtime,
    validate_segment_config_realtime as _validate_segment_config_realtime,
    get_validation_summary as _get_validation_summary
)

# Re-export for backward compatibility
validate_segment_config_realtime = _validate_segment_config_realtime
get_validation_summary = _get_validation_summary
