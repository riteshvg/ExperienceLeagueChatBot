#!/usr/bin/env python3
"""
Interactive Segment Builder Workflow for Adobe Analytics

This module provides a comprehensive interface for building Adobe Analytics segments
with human intervention points and intelligent suggestions based on user intent.
"""

import streamlit as st
import json
from typing import Dict, Any, List, Optional
import sys
import os

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import detect_create_action, generate_segment_suggestions
from adobe_api import create_analytics_segment_from_json, get_company_id


class SegmentBuilder:
    """
    Interactive segment builder with human intervention workflow.
    """
    
    def __init__(self):
        """Initialize the segment builder."""
        self.session_state = st.session_state
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables for the segment builder."""
        if 'segment_builder_state' not in self.session_state:
            self.session_state.segment_builder_state = {
                'current_step': 'intent_detection',
                'user_query': '',
                'detected_intent': None,
                'segment_suggestions': None,
                'segment_config': {
                    'name': '',
                    'description': '',
                    'rsid': '',
                    'target_audience': 'visitors',
                    'rules': []
                },
                'custom_rules': [],
                'validation_errors': [],
                'creation_status': None
            }
        
        # Check if we have pre-populated intent from the main app
        if 'segment_intent' in self.session_state:
            intent_data = self.session_state.segment_intent
            self.session_state.segment_builder_state.update({
                'current_step': 'configuration',  # Skip to configuration step
                'user_query': intent_data.get('prompt', ''),
                'detected_intent': intent_data.get('action_details'),
                'segment_suggestions': intent_data.get('suggestions'),
                'segment_config': {
                    'name': intent_data.get('suggestions', {}).get('segment_name', ''),
                    'description': intent_data.get('suggestions', {}).get('segment_description', ''),
                    'rsid': '',
                    'target_audience': intent_data.get('action_details', {}).get('target_audience', 'visitors'),
                    'rules': intent_data.get('suggestions', {}).get('recommended_rules', [])
                }
            })
            
            # Clear the segment intent to avoid re-processing
            del self.session_state.segment_intent
    
    def render_intent_detection_step(self):
        """Render the intent detection step."""
        st.header("🎯 Step 1: Intent Detection")
        st.markdown("Let me understand what kind of segment you want to create.")
        
        # User input for segment creation
        user_query = st.text_area(
            "Describe the segment you want to create:",
            placeholder="e.g., Create a segment for mobile users from California who visited more than 5 pages",
            height=100,
            key="segment_query_input"
        )
        
        if st.button("🔍 Analyze Intent", type="primary"):
            if user_query.strip():
                self.session_state.segment_builder_state['user_query'] = user_query
                self.analyze_user_intent(user_query)
            else:
                st.error("Please describe the segment you want to create.")
        
        # Show examples
        with st.expander("💡 Example Queries"):
            st.markdown("""
            **Simple Segments:**
            - "Create a segment for mobile users"
            - "Build a segment for visitors from the United States"
            - "Make a segment for people who spent more than 10 minutes on site"
            
            **Complex Segments:**
            - "Create a segment for mobile users from California who visited more than 5 pages"
            - "Build a segment for desktop visitors from New York who converted during business hours"
            - "Make a segment for tablet users who added items to cart on weekends"
            """)
    
    def analyze_user_intent(self, query: str):
        """Analyze user intent and move to next step."""
        with st.spinner("🔍 Analyzing your request..."):
            # Detect action and intent
            action_type, details = detect_create_action(query)
            
            if action_type == 'segment':
                self.session_state.segment_builder_state['detected_intent'] = details
                
                # Generate suggestions
                suggestions = generate_segment_suggestions(details)
                self.session_state.segment_builder_state['segment_suggestions'] = suggestions
                
                # Pre-populate segment config
                self.session_state.segment_builder_state['segment_config'].update({
                    'name': suggestions['segment_name'],
                    'description': suggestions['segment_description'],
                    'target_audience': details.get('target_audience', 'visitors')
                })
                
                # Move to configuration step
                self.session_state.segment_builder_state['current_step'] = 'configuration'
                st.success("✅ Intent detected! Moving to configuration...")
                st.rerun()
            else:
                st.error(f"❌ I detected a '{action_type}' action, but this builder is for segments only.")
    
    def render_configuration_step(self):
        """Render the segment configuration step."""
        st.header("⚙️ Step 2: Segment Configuration")
        st.markdown("Review and customize your segment configuration.")
        
        intent = self.session_state.segment_builder_state['detected_intent']
        suggestions = self.session_state.segment_builder_state['segment_suggestions']
        config = self.session_state.segment_builder_state['segment_config']
        
        # Display detected intent summary
        st.subheader("📊 Detected Intent")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Confidence", suggestions['confidence'].title())
            st.metric("Target Audience", intent.get('target_audience', 'visitors').title())
            if intent.get('device'):
                st.metric("Device Type", intent['device'].title())
        
        with col2:
            if intent.get('geographic'):
                st.metric("Geographic", intent['geographic'].title())
            if intent.get('time_based'):
                st.metric("Time-based", intent['time_based'].replace('_', ' ').title())
            if intent.get('behavioral'):
                st.metric("Behavioral Rules", len(intent['behavioral']))
        
        st.markdown("---")
        
        # Segment basic information
        st.subheader("📝 Basic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            config['name'] = st.text_input(
                "Segment Name",
                value=config['name'],
                help="A descriptive name for your segment"
            )
            
            config['rsid'] = st.text_input(
                "Report Suite ID",
                value=config.get('rsid', ''),
                placeholder="e.g., argupaepdemo",
                help="The Adobe Analytics Report Suite ID where this segment will be created"
            )
        
        with col2:
            config['description'] = st.text_area(
                "Description",
                value=config['description'],
                height=100,
                help="A detailed description of what this segment represents"
            )
            
            config['target_audience'] = st.selectbox(
                "Target Audience",
                options=['visitors', 'visits', 'hits'],
                index=['visitors', 'visits', 'hits'].index(config['target_audience']),
                help="The level at which this segment will be applied"
            )
        
        # Rules configuration
        st.subheader("🔧 Segment Rules")
        
        if suggestions['recommended_rules']:
            st.info(f"💡 I've generated {len(suggestions['recommended_rules'])} recommended rules based on your intent.")
            
            # Display recommended rules
            for i, rule in enumerate(suggestions['recommended_rules']):
                with st.expander(f"Rule {i+1}: {rule.get('func', 'Unknown')} - {rule.get('name', 'Unknown')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        rule['func'] = st.selectbox(
                            "Function",
                            options=['streq', 'gt', 'lt', 'gte', 'lte', 'contains', 'regex'],
                            index=['streq', 'gt', 'lt', 'gte', 'lte', 'contains', 'regex'].index(rule.get('func', 'streq')),
                            key=f"rule_{i}_func"
                        )
                    
                    with col2:
                        rule['name'] = st.text_input(
                            "Variable Name",
                            value=rule.get('name', ''),
                            key=f"rule_{i}_name"
                        )
                    
                    with col3:
                        if rule['func'] in ['gt', 'lt', 'gte', 'lte']:
                            rule['val'] = st.number_input(
                                "Value",
                                value=rule.get('val', 0),
                                key=f"rule_{i}_val"
                            )
                        else:
                            rule['val'] = st.text_input(
                                "Value",
                                value=rule.get('val', ''),
                                key=f"rule_{i}_val"
                            )
                    
                    # Add custom string field for string comparisons
                    if rule['func'] in ['streq', 'contains']:
                        rule['str'] = st.text_input(
                            "String Value",
                            value=rule.get('str', rule.get('val', '')),
                            key=f"rule_{i}_str"
                        )
            
            config['rules'] = suggestions['recommended_rules']
        else:
            st.warning("⚠️ No specific rules detected. You'll need to add custom rules.")
            config['rules'] = []
        
        # Custom rules section
        st.subheader("➕ Add Custom Rules")
        
        if st.button("Add Custom Rule"):
            self.session_state.segment_builder_state['custom_rules'].append({
                'func': 'streq',
                'name': 'variables/page',
                'val': '',
                'str': ''
            })
        
        # Display custom rules
        for i, rule in enumerate(self.session_state.segment_builder_state['custom_rules']):
            with st.expander(f"Custom Rule {i+1}"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    rule['func'] = st.selectbox(
                        "Function",
                        options=['streq', 'gt', 'lt', 'gte', 'lte', 'contains', 'regex'],
                        index=['streq', 'gt', 'lt', 'gte', 'lte', 'contains', 'regex'].index(rule.get('func', 'streq')),
                        key=f"custom_rule_{i}_func"
                    )
                
                with col2:
                    rule['name'] = st.text_input(
                        "Variable",
                        value=rule.get('name', ''),
                        key=f"custom_rule_{i}_name"
                    )
                
                with col3:
                    if rule['func'] in ['gt', 'lt', 'gte', 'lte']:
                        rule['val'] = st.number_input(
                            "Value",
                            value=rule.get('val', 0),
                            key=f"custom_rule_{i}_val"
                        )
                    else:
                        rule['val'] = st.text_input(
                            "Value",
                            value=rule.get('val', ''),
                            key=f"custom_rule_{i}_val"
                        )
                
                with col4:
                    if rule['func'] in ['streq', 'contains']:
                        rule['str'] = st.text_input(
                            "String",
                            value=rule.get('str', ''),
                            key=f"custom_rule_{i}_str"
                        )
                    
                    if st.button("🗑️ Remove", key=f"remove_rule_{i}"):
                        self.session_state.segment_builder_state['custom_rules'].pop(i)
                        st.rerun()
        
        # Add custom rules to main config
        config['rules'].extend(self.session_state.segment_builder_state['custom_rules'])
        
        # Next steps
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔙 Back to Intent", type="secondary"):
                self.session_state.segment_builder_state['current_step'] = 'intent_detection'
                st.rerun()
        
        with col2:
            if st.button("✅ Continue to Review", type="primary"):
                if self.validate_configuration():
                    self.session_state.segment_builder_state['current_step'] = 'review'
                    st.rerun()
        
        with col3:
            if st.button("🏠 Back to Main App", type="secondary"):
                st.switch_page("app.py")
    
    def validate_configuration(self) -> bool:
        """Validate the segment configuration."""
        config = self.session_state.segment_builder_state['segment_config']
        errors = []
        
        if not config['name'].strip():
            errors.append("Segment name is required")
        
        if not config['rsid'].strip():
            errors.append("Report Suite ID is required")
        
        if not config['rules']:
            errors.append("At least one rule is required")
        
        # Validate rules
        for i, rule in enumerate(config['rules']):
            if not rule.get('name'):
                errors.append(f"Rule {i+1}: Variable name is required")
            
            # For string comparison functions, we need either 'str' or 'val' field
            if rule.get('func') in ['streq', 'contains']:
                if not rule.get('str') and not rule.get('val'):
                    errors.append(f"Rule {i+1}: String value is required for {rule['func']}")
        
        self.session_state.segment_builder_state['validation_errors'] = errors
        
        if errors:
            st.error("❌ Please fix the following errors:")
            for error in errors:
                st.error(f"  - {error}")
            return False
        
        return True
    
    def render_review_step(self):
        """Render the review and creation step."""
        st.header("📋 Step 3: Review & Create")
        st.markdown("Review your segment configuration before creating it.")
        
        config = self.session_state.segment_builder_state['segment_config']
        
        # Configuration summary
        st.subheader("📊 Configuration Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Name:** {config['name']}")
            st.info(f"**Description:** {config['description']}")
            st.info(f"**Target Audience:** {config['target_audience']}")
        
        with col2:
            st.info(f"**Report Suite ID:** {config['rsid']}")
            st.info(f"**Total Rules:** {len(config['rules'])}")
            st.info(f"**Status:** Ready to create")
        
        # Rules preview
        st.subheader("🔧 Rules Preview")
        
        for i, rule in enumerate(config['rules']):
            with st.expander(f"Rule {i+1}: {rule.get('func', 'Unknown')}"):
                st.json(rule)
        
        # JSON preview
        st.subheader("📄 Generated JSON")
        
        segment_payload = self.build_segment_payload()
        
        st.code(json.dumps(segment_payload, indent=2), language="json")
        
        # Creation actions
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔙 Back to Configuration", type="secondary"):
                self.session_state.segment_builder_state['current_step'] = 'configuration'
                st.rerun()
        
        with col2:
            if st.button("💾 Save Configuration", type="secondary"):
                self.save_configuration(segment_payload)
        
        with col3:
            if st.button("🚀 Create Segment", type="primary"):
                self.create_segment(segment_payload)
        
        with col4:
            if st.button("🏠 Back to Main App", type="secondary"):
                st.switch_page("app.py")
    
    def build_segment_payload(self) -> Dict[str, Any]:
        """Build the complete segment payload for Adobe Analytics API."""
        config = self.session_state.segment_builder_state['segment_config']
        
        # Build the definition structure
        if len(config['rules']) == 1:
            # Single rule
            rule = config['rules'][0]
            definition = {
                "version": [1, 0, 0],
                "func": "segment",
                "container": {
                    "func": "container",
                    "context": config['target_audience'],
                    "pred": {
                        "func": rule.get("func", "streq"),
                        "val": {
                            "func": "attr",
                            "name": rule.get("name", "variables/page")
                        }
                    }
                }
            }
            
            # Add string value for string comparisons
            if rule.get('func') in ['streq', 'contains'] and rule.get('str'):
                definition["container"]["pred"]["str"] = rule['str']
        else:
            # Multiple rules
            definition = {
                "version": [1, 0, 0],
                "func": "segment",
                "container": {
                    "func": "container",
                    "context": config['target_audience'],
                    "pred": {
                        "func": "and",
                        "vals": []
                    }
                }
            }
            
            # Build individual rule predicates
            for rule in config['rules']:
                rule_pred = {
                    "func": rule.get("func", "streq"),
                    "val": {
                        "func": "attr",
                        "name": rule.get("name", "variables/page")
                    }
                }
                
                # Add string value for string comparisons
                if rule.get('func') in ['streq', 'contains'] and rule.get('str'):
                    rule_pred["str"] = rule['str']
                
                definition["container"]["pred"]["vals"].append(rule_pred)
        
        # Build the complete payload
        payload = {
            "name": config['name'],
            "description": config['description'],
            "rsid": config['rsid'],
            "definition": definition
        }
        
        return payload
    
    def save_configuration(self, payload: Dict[str, Any]):
        """Save the segment configuration for later use."""
        # This could save to a file, database, or session state
        st.success("✅ Configuration saved successfully!")
        st.info("You can now create the segment or modify the configuration further.")
    
    def create_segment(self, payload: Dict[str, Any]):
        """Create the segment using the Adobe Analytics API."""
        with st.spinner("🚀 Creating your segment..."):
            try:
                # Get company ID
                company_id = get_company_id()
                if not company_id:
                    st.error("❌ Company ID not found. Please check your configuration.")
                    return
                
                # Create the segment
                result = create_analytics_segment_from_json(payload)
                
                if result.get('status') == 'success':
                    self.session_state.segment_builder_state['creation_status'] = {
                        'status': 'success',
                        'data': result.get('data', {})
                    }
                    st.success("🎉 Segment created successfully!")
                    
                    # Show segment details
                    st.subheader("✅ Segment Created")
                    st.json(result.get('data', {}))
                    
                    # Move to completion step
                    self.session_state.segment_builder_state['current_step'] = 'completion'
                    st.rerun()
                else:
                    self.session_state.segment_builder_state['creation_status'] = {
                        'status': 'error',
                        'message': result.get('message', 'Unknown error')
                    }
                    st.error(f"❌ Failed to create segment: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Error creating segment: {str(e)}")
                self.session_state.segment_builder_state['creation_status'] = {
                    'status': 'error',
                    'message': str(e)
                }
    
    def render_completion_step(self):
        """Render the completion step."""
        st.header("🎉 Step 4: Completion")
        st.markdown("Your segment has been created successfully!")
        
        status = self.session_state.segment_builder_state['creation_status']
        
        if status and status.get('status') == 'success':
            st.success("✅ Segment created successfully in Adobe Analytics!")
            
            # Show segment details
            st.subheader("📊 Segment Details")
            st.json(status.get('data', {}))
            
            # Next steps
            st.subheader("🔄 What's Next?")
            st.markdown("""
            - **Use the segment** in Analysis Workspace
            - **Share the segment** with your team
            - **Modify the segment** if needed
            - **Create another segment** for different criteria
            """)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Create Another Segment", type="primary"):
                    self.reset_builder()
                    st.rerun()
            
            with col2:
                if st.button("🏠 Back to Main App", type="secondary"):
                    st.switch_page("app.py")
            
            with col3:
                if st.button("📚 Ask More Questions", type="secondary"):
                    st.switch_page("app.py")
        else:
            st.error("❌ Segment creation failed. Please check the error details above.")
            
            if st.button("🔙 Back to Configuration", type="secondary"):
                self.session_state.segment_builder_state['current_step'] = 'configuration'
                st.rerun()
    
    def reset_builder(self):
        """Reset the builder to initial state."""
        self.session_state.segment_builder_state = {
            'current_step': 'intent_detection',
            'user_query': '',
            'detected_intent': None,
            'segment_suggestions': None,
            'segment_config': {
                'name': '',
                'description': '',
                'rsid': '',
                'target_audience': 'visitors',
                'rules': []
            },
            'custom_rules': [],
            'validation_errors': [],
            'creation_status': None
        }
    
    def render(self):
        """Main render method for the segment builder."""
        st.set_page_config(
            page_title="Adobe Analytics Segment Builder",
            page_icon="🔧",
            layout="wide"
        )
        
        st.title("🔧 Adobe Analytics Segment Builder")
        st.markdown("Create sophisticated segments with intelligent suggestions and human intervention.")
        
        # Progress indicator
        steps = ['intent_detection', 'configuration', 'review', 'completion']
        current_step = self.session_state.segment_builder_state['current_step']
        current_index = steps.index(current_step) if current_step in steps else 0
        
        st.progress((current_index + 1) / len(steps))
        
        # Step navigation
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**1. Intent Detection** {'✅' if current_index >= 0 else '⏳'}")
        with col2:
            st.markdown(f"**2. Configuration** {'✅' if current_index >= 1 else '⏳'}")
        with col3:
            st.markdown(f"**3. Review** {'✅' if current_index >= 2 else '⏳'}")
        with col4:
            st.markdown(f"**4. Completion** {'✅' if current_index >= 3 else '⏳'}")
        
        st.markdown("---")
        
        # Render current step
        if current_step == 'intent_detection':
            self.render_intent_detection_step()
        elif current_step == 'configuration':
            self.render_configuration_step()
        elif current_step == 'review':
            self.render_review_step()
        elif current_step == 'completion':
            self.render_completion_step()
        else:
            st.error("❌ Unknown step. Resetting to intent detection.")
            self.session_state.segment_builder_state['current_step'] = 'intent_detection'
            st.rerun()


def main():
    """Main function to run the segment builder."""
    builder = SegmentBuilder()
    builder.render()


if __name__ == "__main__":
    main() 