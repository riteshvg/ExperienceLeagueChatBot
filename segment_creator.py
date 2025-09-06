#!/usr/bin/env python3
"""
Adobe Analytics Segment Creator Module

This module provides functionality to create Adobe Analytics segments based on
natural language requests from users. It integrates with the existing chat flow
and provides a seamless segment creation experience.
"""

import streamlit as st
import json
import re
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SegmentDefinition:
    """Data class to hold segment definition information"""
    name: str
    description: str
    container: str  # 'visitor', 'visit', or 'hit'
    rules: List[Dict]
    rsid: str


class SegmentCreator:
    """Main class for handling Adobe Analytics segment creation"""
    
    def __init__(self):
        self.api_base_url = "https://analytics.adobe.io/api"
        self.segment_patterns = {
            'visitor': ['visitor', 'visitors', 'user', 'users', 'person', 'people', 'audience'],
            'visit': ['visit', 'visits', 'session', 'sessions', 'trip', 'trips'],
            'hit': ['hit', 'hits', 'page view', 'page views', 'click', 'clicks', 'interaction']
        }
        
        self.device_patterns = {
            'mobile': ['mobile', 'phone', 'smartphone', 'ios', 'android'],
            'desktop': ['desktop', 'computer', 'pc', 'mac', 'laptop'],
            'tablet': ['tablet', 'ipad', 'android tablet']
        }
        
        self.geographic_patterns = {
            'country': ['country', 'nation', 'usa', 'united states', 'us', 'canada', 'uk', 'germany'],
            'city': ['city', 'town', 'new york', 'london', 'toronto', 'berlin'],
            'state': ['state', 'province', 'california', 'texas', 'ontario']
        }
    
    def detect_segment_request(self, user_input: str) -> bool:
        """
        Detect if the user is requesting segment creation
        
        Args:
            user_input (str): User's input text
            
        Returns:
            bool: True if segment creation is requested
        """
        user_input_lower = user_input.lower()
        
        # Check for segment-related keywords
        segment_keywords = [
            'create segment', 'build segment', 'make segment', 'segment for',
            'audience', 'cohort', 'user group', 'visitor group',
            'targeting', 'filter users', 'user filter'
        ]
        
        return any(keyword in user_input_lower for keyword in segment_keywords)
    
    def parse_segment_request(self, user_input: str) -> Dict:
        """
        Parse natural language segment request into structured data
        
        Args:
            user_input (str): User's natural language request
            
        Returns:
            Dict: Parsed segment information
        """
        user_input_lower = user_input.lower()
        
        # Initialize segment info
        segment_info = {
            'container': 'visitor',  # Default container
            'device': None,
            'geographic': None,
            'behavioral': [],
            'conditions': [],
            'confidence': 'medium'
        }
        
        # Detect container type
        for container, patterns in self.segment_patterns.items():
            if any(pattern in user_input_lower for pattern in patterns):
                segment_info['container'] = container
                break
        
        # Detect device targeting
        for device, patterns in self.device_patterns.items():
            if any(pattern in user_input_lower for pattern in patterns):
                segment_info['device'] = device
                break
        
        # Detect geographic targeting
        for geo_type, patterns in self.geographic_patterns.items():
            if any(pattern in user_input_lower for pattern in patterns):
                segment_info['geographic'] = geo_type
                break
        
        # Detect behavioral conditions
        behavioral_conditions = {
            'page_views': ['page views', 'pages', 'pageviews'],
            'time_on_site': ['time on site', 'session duration', 'visit length'],
            'conversion': ['conversion', 'purchase', 'goal', 'objective'],
            'cart': ['cart', 'shopping cart', 'basket'],
            'bounce': ['bounce', 'single page', 'immediate exit']
        }
        
        for behavior, patterns in behavioral_conditions.items():
            if any(pattern in user_input_lower for pattern in patterns):
                segment_info['behavioral'].append(behavior)
        
        # Set confidence based on detected information
        detected_count = sum([
            1 if segment_info['device'] else 0,
            1 if segment_info['geographic'] else 0,
            len(segment_info['behavioral']),
            1 if segment_info['container'] != 'visitor' else 0
        ])
        
        if detected_count >= 3:
            segment_info['confidence'] = 'high'
        elif detected_count >= 1:
            segment_info['confidence'] = 'medium'
        else:
            segment_info['confidence'] = 'low'
        
        return segment_info
    
    def generate_segment_name(self, user_input: str, segment_info: Dict) -> str:
        """
        Generate a descriptive segment name based on the request
        
        Args:
            user_input (str): Original user input
            segment_info (Dict): Parsed segment information
            
        Returns:
            str: Generated segment name
        """
        name_parts = []
        
        # Add device information
        if segment_info.get('device'):
            name_parts.append(f"{segment_info['device'].title()} Users")
        
        # Add geographic information
        if segment_info.get('geographic'):
            geo_type = segment_info['geographic']
            if geo_type == 'country':
                name_parts.append("from Specific Country")
            elif geo_type == 'city':
                name_parts.append("from Specific City")
            elif geo_type == 'state':
                name_parts.append("from Specific State")
        
        # Add behavioral information
        for behavior in segment_info.get('behavioral', []):
            if behavior == 'page_views':
                name_parts.append("with High Page Views")
            elif behavior == 'time_on_site':
                name_parts.append("with Long Session Duration")
            elif behavior == 'conversion':
                name_parts.append("who Converted")
            elif behavior == 'cart':
                name_parts.append("who Added to Cart")
            elif behavior == 'bounce':
                name_parts.append("with Low Bounce Rate")
        
        # If no specific patterns detected, use generic name
        if not name_parts:
            name_parts = ["Custom Segment"]
        
        return " ".join(name_parts)
    
    def generate_segment_description(self, user_input: str, segment_info: Dict) -> str:
        """
        Generate a descriptive segment description
        
        Args:
            user_input (str): Original user input
            segment_info (Dict): Parsed segment information
            
        Returns:
            str: Generated segment description
        """
        description_parts = []
        
        container = segment_info.get('container', 'visitor')
        description_parts.append(f"Segment targeting {container}")
        
        if segment_info.get('device'):
            description_parts.append(f"using {segment_info['device']} devices")
        
        if segment_info.get('geographic'):
            geo_type = segment_info['geographic']
            description_parts.append(f"from specific {geo_type}")
        
        if segment_info.get('behavioral'):
            behaviors = segment_info['behavioral']
            if len(behaviors) == 1:
                description_parts.append(f"with {behaviors[0].replace('_', ' ')}")
            else:
                behavior_text = ", ".join([b.replace('_', ' ') for b in behaviors[:-1]])
                description_parts.append(f"with {behavior_text} and {behaviors[-1].replace('_', ' ')}")
        
        return " ".join(description_parts) + "."
    
    def build_segment_rules(self, segment_info: Dict) -> List[Dict]:
        """
        Build Adobe Analytics segment rules based on parsed information
        
        Args:
            segment_info (Dict): Parsed segment information
            
        Returns:
            List[Dict]: Adobe Analytics segment rules
        """
        rules = []
        
        # Device targeting rule
        if segment_info.get('device'):
            device_rule = {
                "container": "visitor",
                "predicate": {
                    "type": "dimension",
                    "dimension": "device",
                    "operator": "equals",
                    "value": segment_info['device']
                }
            }
            rules.append(device_rule)
        
        # Geographic targeting rule
        if segment_info.get('geographic'):
            geo_type = segment_info['geographic']
            geo_rule = {
                "container": "visitor",
                "predicate": {
                    "type": "dimension",
                    "dimension": geo_type,
                    "operator": "exists"
                }
            }
            rules.append(geo_rule)
        
        # Behavioral rules
        for behavior in segment_info.get('behavioral', []):
            if behavior == 'page_views':
                page_views_rule = {
                    "container": "visitor",
                    "predicate": {
                        "type": "metric",
                        "metric": "page_views",
                        "operator": "greater_than",
                        "value": 5
                    }
                }
                rules.append(page_views_rule)
            elif behavior == 'time_on_site':
                time_rule = {
                    "container": "visitor",
                    "predicate": {
                        "type": "metric",
                        "metric": "time_on_site",
                        "operator": "greater_than",
                        "value": 300  # 5 minutes
                    }
                }
                rules.append(time_rule)
            elif behavior == 'conversion':
                conversion_rule = {
                    "container": "visitor",
                    "predicate": {
                        "type": "event",
                        "event": "conversion",
                        "operator": "exists"
                    }
                }
                rules.append(conversion_rule)
            elif behavior == 'cart':
                cart_rule = {
                    "container": "visitor",
                    "predicate": {
                        "type": "event",
                        "event": "cart_add",
                        "operator": "exists"
                    }
                }
                rules.append(cart_rule)
        
        return rules
    
    def create_segment_definition(self, user_input: str, segment_info: Dict, rsid: str) -> SegmentDefinition:
        """
        Create a complete segment definition
        
        Args:
            user_input (str): Original user input
            segment_info (Dict): Parsed segment information
            rsid (str): Report Suite ID
            
        Returns:
            SegmentDefinition: Complete segment definition
        """
        name = self.generate_segment_name(user_input, segment_info)
        description = self.generate_segment_description(user_input, segment_info)
        rules = self.build_segment_rules(segment_info)
        
        return SegmentDefinition(
            name=name,
            description=description,
            container=segment_info.get('container', 'visitor'),
            rules=rules,
            rsid=rsid
        )
    
    def display_segment_preview(self, segment_def: SegmentDefinition) -> None:
        """
        Display segment definition preview in Streamlit
        
        Args:
            segment_def (SegmentDefinition): Segment definition to display
        """
        st.markdown("### 📊 Segment Preview")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Segment Name:**")
            st.info(segment_def.name)
            
            st.markdown("**Description:**")
            st.info(segment_def.description)
        
        with col2:
            st.markdown("**Container:**")
            st.info(segment_def.container.title())
            
            st.markdown("**Report Suite ID:**")
            st.info(segment_def.rsid)
        
        # Display rules
        st.markdown("**Rules:**")
        for i, rule in enumerate(segment_def.rules, 1):
            with st.expander(f"Rule {i}: {rule.get('predicate', {}).get('dimension', rule.get('predicate', {}).get('metric', 'Custom'))}"):
                st.json(rule)
    
    def create_adobe_segment(self, segment_def: SegmentDefinition, access_token: str) -> Dict:
        """
        Create segment in Adobe Analytics via API
        
        Args:
            segment_def (SegmentDefinition): Segment definition
            access_token (str): Adobe Analytics access token
            
        Returns:
            Dict: API response
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'x-api-key': st.secrets.get('ADOBE_API_KEY', ''),
            'x-proxy-global-company-id': st.secrets.get('ADOBE_COMPANY_ID', '')
        }
        
        payload = {
            "name": segment_def.name,
            "description": segment_def.description,
            "rsid": segment_def.rsid,
            "definition": {
                "container": {
                    "type": segment_def.container,
                    "rules": segment_def.rules
                }
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_base_url}/segments",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def handle_segment_creation_flow(self, user_input: str) -> None:
        """
        Handle the complete segment creation flow in Streamlit
        
        Args:
            user_input (str): User's natural language request
        """
        st.markdown("---")
        st.markdown("### 🔧 Adobe Analytics Segment Creator")
        
        # Parse the segment request
        segment_info = self.parse_segment_request(user_input)
        
        # Get RSID from user
        rsid = st.text_input(
            "Report Suite ID (RSID):",
            placeholder="Enter your Adobe Analytics Report Suite ID",
            help="This is required to create the segment"
        )
        
        if not rsid:
            st.warning("⚠️ Please enter a Report Suite ID to continue")
            return
        
        # Create segment definition
        segment_def = self.create_segment_definition(user_input, segment_info, rsid)
        
        # Display preview
        self.display_segment_preview(segment_def)
        
        # Confirmation and creation
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Create Segment", type="primary"):
                # Check for required secrets
                access_token = st.secrets.get('ADOBE_ACCESS_TOKEN', '')
                if not access_token:
                    st.error("❌ Adobe Analytics access token not found. Please configure ADOBE_ACCESS_TOKEN in Streamlit secrets.")
                    return
                
                # Create the segment
                with st.spinner("Creating segment in Adobe Analytics..."):
                    result = self.create_adobe_segment(segment_def, access_token)
                
                if result.get('success', True) and 'error' not in result:
                    st.success("🎉 Segment created successfully!")
                    st.json(result)
                else:
                    st.error(f"❌ Failed to create segment: {result.get('error', 'Unknown error')}")
        
        with col2:
            if st.button("🔄 Modify Segment", type="secondary"):
                st.info("💡 Segment modification feature coming soon!")
        
        # Show segment definition as JSON for debugging
        with st.expander("🔍 Raw Segment Definition (JSON)"):
            st.json({
                "name": segment_def.name,
                "description": segment_def.description,
                "container": segment_def.container,
                "rsid": segment_def.rsid,
                "rules": segment_def.rules
            })


# Global instance for easy access
segment_creator = SegmentCreator()
