#!/usr/bin/env python3
"""
Adobe Analytics Segment Parser Module

This module provides functionality to analyze chat messages for segment creation
requests and parse natural language into structured segment components.
"""

import re
from typing import Dict, List, Optional, Tuple


class SegmentParser:
    """Parser for analyzing segment creation requests from natural language"""
    
    def __init__(self):
        # Keywords that indicate segment creation intent
        self.segment_intent_keywords = [
            'create segment', 'segment for', 'users who', 'visitors that',
            'build segment', 'make segment', 'audience for', 'cohort for',
            'user group', 'visitor group', 'targeting', 'filter users',
            'user filter', 'segment targeting', 'audience targeting'
        ]
        
        # Device type patterns
        self.device_patterns = {
            'mobile': ['mobile', 'phone', 'smartphone', 'ios', 'android', 'cell phone'],
            'desktop': ['desktop', 'computer', 'pc', 'mac', 'laptop', 'workstation'],
            'tablet': ['tablet', 'ipad', 'android tablet', 'surface']
        }
        
        # Page/URL patterns
        self.page_patterns = {
            'homepage': ['homepage', 'home page', 'main page', 'landing page'],
            'product': ['product page', 'product pages', 'product detail', 'product details'],
            'checkout': ['checkout', 'check out', 'purchase', 'buy', 'shopping cart'],
            'login': ['login', 'sign in', 'log in', 'authentication'],
            'registration': ['register', 'registration', 'sign up', 'signup']
        }
        
        # Event patterns
        self.event_patterns = {
            'purchase': ['purchased', 'bought', 'conversion', 'converted', 'sale'],
            'cart_add': ['added to cart', 'cart add', 'added cart', 'cart addition'],
            'newsletter': ['newsletter', 'email signup', 'email subscription'],
            'download': ['downloaded', 'download', 'file download'],
            'video': ['video', 'watched video', 'video play', 'video view']
        }
        
        # Campaign patterns
        self.campaign_patterns = {
            'email': ['email campaign', 'email marketing', 'newsletter', 'email blast'],
            'social': ['social media', 'facebook', 'twitter', 'instagram', 'linkedin'],
            'search': ['search', 'google', 'seo', 'organic search', 'paid search'],
            'display': ['display ad', 'banner', 'display campaign', 'retargeting']
        }
        
        # eVar patterns (custom variables)
        self.evar_patterns = {
            'user_type': ['premium users', 'free users', 'subscribers', 'members'],
            'customer_tier': ['gold', 'silver', 'bronze', 'platinum', 'vip'],
            'subscription': ['subscribed', 'subscription', 'member', 'premium member']
        }
        
        # Geographic patterns
        self.geo_patterns = {
            'country': ['usa', 'united states', 'us', 'canada', 'uk', 'germany', 'france'],
            'state': ['california', 'texas', 'new york', 'florida', 'illinois'],
            'city': ['new york', 'los angeles', 'chicago', 'houston', 'phoenix']
        }
        
        # Logic connectors
        self.logic_connectors = ['and', 'or', 'who', 'that', 'which', 'but', 'also']
        
        # Context indicators
        self.context_patterns = {
            'visitors': ['visitors', 'visitor', 'users', 'user', 'people', 'audience'],
            'visits': ['visits', 'visit', 'sessions', 'session', 'trips', 'trip'],
            'hits': ['hits', 'hit', 'page views', 'pageview', 'interactions', 'interaction']
        }

    def detect_segment_request(self, user_message: str) -> bool:
        """
        Detect if the user message contains segment creation intent
        
        Args:
            user_message (str): User's input message
            
        Returns:
            bool: True if segment creation is requested
        """
        if not user_message or not isinstance(user_message, str):
            return False
            
        message_lower = user_message.lower().strip()
        
        # Check for segment intent keywords
        for keyword in self.segment_intent_keywords:
            if keyword in message_lower:
                return True
        
        # Check for pattern combinations that suggest segment creation
        # e.g., "users who visited" or "visitors that purchased"
        visitor_patterns = ['users who', 'visitors that', 'people who', 'audience who', 'visitors from', 'users from']
        action_patterns = ['visited', 'purchased', 'clicked', 'viewed', 'downloaded', 'watched', 'added', 'from']
        
        for visitor_pattern in visitor_patterns:
            if visitor_pattern in message_lower:
                for action_pattern in action_patterns:
                    if action_pattern in message_lower:
                        return True
        
        # Check for geographic + action patterns
        geo_action_patterns = ['from', 'who', 'that']
        for geo_pattern in geo_action_patterns:
            if geo_pattern in message_lower:
                # Check if there are geographic terms
                geo_terms = ['california', 'texas', 'new york', 'usa', 'canada', 'mobile', 'desktop', 'tablet']
                for geo_term in geo_terms:
                    if geo_term in message_lower:
                        return True
        
        return False

    def parse_segment_components(self, user_message: str) -> Dict:
        """
        Parse natural language message into structured segment components
        
        Args:
            user_message (str): User's natural language message
            
        Returns:
            Dict: Structured segment data with conditions, logic, context, and description
        """
        if not user_message or not isinstance(user_message, str):
            return self._empty_segment_data()
        
        message_lower = user_message.lower().strip()
        
        # Initialize result structure
        result = {
            "conditions": [],
            "logic": "and",
            "context": "visitors",
            "description": self._generate_description(message_lower)
        }
        
        # Extract conditions
        conditions = []
        
        # Parse device conditions
        device_conditions = self._parse_device_conditions(message_lower)
        conditions.extend(device_conditions)
        
        # Parse page conditions
        page_conditions = self._parse_page_conditions(message_lower)
        conditions.extend(page_conditions)
        
        # Parse event conditions
        event_conditions = self._parse_event_conditions(message_lower)
        conditions.extend(event_conditions)
        
        # Parse campaign conditions
        campaign_conditions = self._parse_campaign_conditions(message_lower)
        conditions.extend(campaign_conditions)
        
        # Parse eVar conditions
        evar_conditions = self._parse_evar_conditions(message_lower)
        conditions.extend(evar_conditions)
        
        # Parse geographic conditions
        geo_conditions = self._parse_geo_conditions(message_lower)
        conditions.extend(geo_conditions)
        
        # Determine logic connector
        logic = self._determine_logic(message_lower)
        
        # Determine context
        context = self._determine_context(message_lower)
        
        result["conditions"] = conditions
        result["logic"] = logic
        result["context"] = context
        
        return result

    def _empty_segment_data(self) -> Dict:
        """Return empty segment data structure"""
        return {
            "conditions": [],
            "logic": "and",
            "context": "visitors",
            "description": "Custom segment"
        }

    def _parse_device_conditions(self, message: str) -> List[Dict]:
        """Parse device type conditions from message"""
        conditions = []
        
        for device_type, patterns in self.device_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    conditions.append({
                        "variable": "device",
                        "operator": "equals",
                        "value": device_type,
                        "type": "device"
                    })
                    break  # Only add one condition per device type
        
        return conditions

    def _parse_page_conditions(self, message: str) -> List[Dict]:
        """Parse page/URL conditions from message"""
        conditions = []
        
        for page_type, patterns in self.page_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    conditions.append({
                        "variable": "page",
                        "operator": "contains",
                        "value": page_type,
                        "type": "page"
                    })
                    break
        
        return conditions

    def _parse_event_conditions(self, message: str) -> List[Dict]:
        """Parse event conditions from message"""
        conditions = []
        
        for event_type, patterns in self.event_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    conditions.append({
                        "variable": "event",
                        "operator": "exists",
                        "value": event_type,
                        "type": "event"
                    })
                    break
        
        return conditions

    def _parse_campaign_conditions(self, message: str) -> List[Dict]:
        """Parse campaign conditions from message"""
        conditions = []
        
        for campaign_type, patterns in self.campaign_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    conditions.append({
                        "variable": "campaign",
                        "operator": "contains",
                        "value": campaign_type,
                        "type": "campaign"
                    })
                    break
        
        return conditions

    def _parse_evar_conditions(self, message: str) -> List[Dict]:
        """Parse eVar conditions from message"""
        conditions = []
        
        for evar_type, patterns in self.evar_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    conditions.append({
                        "variable": "evar",
                        "operator": "equals",
                        "value": evar_type,
                        "type": "evar"
                    })
                    break
        
        return conditions

    def _parse_geo_conditions(self, message: str) -> List[Dict]:
        """Parse geographic conditions from message"""
        conditions = []
        
        for geo_type, patterns in self.geo_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    conditions.append({
                        "variable": "geography",
                        "operator": "equals",
                        "value": pattern,
                        "type": "geography"
                    })
                    break
        
        return conditions

    def _determine_logic(self, message: str) -> str:
        """Determine the logic connector (and/or) from message"""
        # Check for explicit logic connectors
        if ' or ' in message:
            return 'or'
        elif ' and ' in message:
            return 'and'
        
        # Check for implicit connectors
        if 'who' in message or 'that' in message:
            return 'and'
        
        # Default to 'and' for most cases
        return 'and'

    def _determine_context(self, message: str) -> str:
        """Determine the segment context (visitors/visits/hits) from message"""
        for context_type, patterns in self.context_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    return context_type
        
        # Default to visitors
        return 'visitors'

    def _generate_description(self, message: str) -> str:
        """Generate a human-readable description from the message"""
        # Clean up the message for description
        description = message.strip()
        
        # Remove common filler words
        filler_words = ['please', 'can you', 'i need', 'i want', 'help me', 'create', 'build', 'make']
        for word in filler_words:
            description = description.replace(word, '').strip()
        
        # Capitalize first letter
        if description:
            description = description[0].upper() + description[1:]
        
        # Add "Segment" if not already present
        if 'segment' not in description.lower():
            description += ' Segment'
        
        return description

    def validate_conditions(self, conditions: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate parsed conditions for completeness and correctness
        
        Args:
            conditions (List[Dict]): List of parsed conditions
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        if not conditions:
            errors.append("No conditions found in the message")
            return False, errors
        
        # Validate each condition
        for i, condition in enumerate(conditions):
            if not isinstance(condition, dict):
                errors.append(f"Condition {i+1} is not a valid dictionary")
                continue
            
            required_fields = ['variable', 'operator', 'value', 'type']
            for field in required_fields:
                if field not in condition:
                    errors.append(f"Condition {i+1} missing required field: {field}")
            
            # Validate operator values
            valid_operators = ['equals', 'contains', 'exists', 'greater_than', 'less_than']
            if condition.get('operator') not in valid_operators:
                errors.append(f"Condition {i+1} has invalid operator: {condition.get('operator')}")
        
        return len(errors) == 0, errors


# Global instance for easy access
segment_parser = SegmentParser()
