#!/usr/bin/env python3
"""
Adobe Analytics Variable Mapper Module

This module provides functionality to map parsed segment components to
Adobe Analytics variable references and determine appropriate contexts.
"""

from typing import Dict, List, Optional


# Static mappings dictionary with Adobe Analytics variables
VARIABLE_MAPPINGS = {
    "device": "variables/mobiledevicetype",
    "page": "variables/page", 
    "campaign": "variables/trackingcode",
    "site_section": "variables/sitesection",
    "country": "variables/geocountry",
    "state": "variables/geostate",
    "city": "variables/geocity",
    "browser": "variables/browser",
    "operating_system": "variables/operatingsystem",
    "referrer": "variables/referrer",
    "purchase": "metrics/orders",
    "revenue": "metrics/revenue",
    "page_views": "metrics/pageviews",
    "visits": "metrics/visits",
    "visitors": "metrics/visitors",
    "bounce_rate": "metrics/bouncerate",
    "time_on_site": "metrics/timespent",
    "cart_add": "events/scAdd",
    "cart_remove": "events/scRemove",
    "checkout": "events/scCheckout",
    "purchase_event": "events/purchase",
    "newsletter": "events/newsletter_signup",
    "download": "events/download",
    "video": "events/video_play",
    "search": "events/internal_search",
    "social_share": "events/social_share",
    "email_click": "events/email_click",
    "form_submit": "events/form_submit",
    "login": "events/login",
    "registration": "events/registration",
    "logout": "events/logout"
}

# Operator mappings from parsed operators to Adobe Analytics operators
OPERATOR_MAPPINGS = {
    "equals": "streq",
    "contains": "streq-in",
    "exists": "exists",
    "greater_than": "gt",
    "less_than": "lt",
    "greater_than_or_equal": "gte",
    "less_than_or_equal": "lte",
    "not_equals": "streq-not",
    "not_contains": "streq-not-in",
    "not_exists": "not-exists"
}

# Value mappings for specific variables
VALUE_MAPPINGS = {
    "device": {
        "mobile": "Mobile Phone",
        "desktop": "Desktop",
        "tablet": "Tablet"
    },
    "browser": {
        "chrome": "Chrome",
        "firefox": "Firefox",
        "safari": "Safari",
        "edge": "Microsoft Edge",
        "internet_explorer": "Internet Explorer"
    },
    "operating_system": {
        "windows": "Windows",
        "macos": "Mac OS",
        "linux": "Linux",
        "ios": "iOS",
        "android": "Android"
    }
}

# Context suggestions based on variable types
CONTEXT_RULES = {
    "hits": [
        "page", "site_section", "campaign", "browser", "operating_system",
        "referrer", "purchase_event", "cart_add", "cart_remove", "checkout",
        "newsletter", "download", "video", "search", "social_share",
        "email_click", "form_submit", "login", "registration", "logout"
    ],
    "visits": [
        "device", "country", "state", "city", "purchase", "revenue",
        "page_views", "visits", "bounce_rate", "time_on_site"
    ],
    "visitors": [
        "visitors", "user_type", "customer_tier", "subscription"
    ]
}


class VariableMapper:
    """Mapper for converting parsed components to Adobe Analytics variables"""
    
    def __init__(self):
        self.variable_mappings = VARIABLE_MAPPINGS
        self.operator_mappings = OPERATOR_MAPPINGS
        self.value_mappings = VALUE_MAPPINGS
        self.context_rules = CONTEXT_RULES
    
    def map_variable(self, component: Dict) -> Dict:
        """
        Map a parsed component to Adobe Analytics variable format
        
        Args:
            component (Dict): Parsed component with variable, operator, value, type
            
        Returns:
            Dict: Mapped component with Adobe Analytics variable reference
        """
        if not isinstance(component, dict):
            return {}
        
        variable_type = component.get("variable", "")
        operator = component.get("operator", "equals")
        value = component.get("value", "")
        component_type = component.get("type", "")
        
        # Map variable name
        mapped_name = self.variable_mappings.get(variable_type, "")
        
        # Map operator
        mapped_operator = self.operator_mappings.get(operator, operator)
        
        # Map value if specific mapping exists
        mapped_value = value
        if variable_type in self.value_mappings:
            value_mapping = self.value_mappings[variable_type]
            mapped_value = value_mapping.get(value.lower(), value)
        
        # Handle special cases for different variable types
        if component_type == "event":
            # Events need special handling
            mapped_name = self._map_event_variable(variable_type, value)
        elif component_type == "evar":
            # eVar variables need user specification
            mapped_name = f"variables/evar{variable_type}" if variable_type.isdigit() else f"variables/evar_{variable_type}"
        elif component_type == "prop":
            # Prop variables need user specification
            mapped_name = f"variables/prop{variable_type}" if variable_type.isdigit() else f"variables/prop_{variable_type}"
        elif component_type == "geography":
            # Geographic variables need special mapping
            mapped_name = self._map_geography_variable(variable_type, value)
        
        return {
            "name": mapped_name,
            "operator": mapped_operator,
            "value": mapped_value,
            "type": component_type,
            "original_variable": variable_type
        }
    
    def get_missing_mappings(self, components: List[Dict]) -> List[str]:
        """
        Identify unmapped variables that need user input
        
        Args:
            components (List[Dict]): List of parsed components
            
        Returns:
            List[str]: List of variables requiring eVar/prop/event specification
        """
        missing_mappings = []
        
        for component in components:
            if not isinstance(component, dict):
                continue
            
            variable_type = component.get("variable", "")
            component_type = component.get("type", "")
            
            # Check if variable is not in standard mappings
            if variable_type not in self.variable_mappings:
                if component_type == "evar":
                    missing_mappings.append(f"eVar: {variable_type}")
                elif component_type == "prop":
                    missing_mappings.append(f"Prop: {variable_type}")
                elif component_type == "event":
                    missing_mappings.append(f"Event: {variable_type}")
                elif component_type == "custom":
                    missing_mappings.append(f"Custom: {variable_type}")
                else:
                    missing_mappings.append(f"Unknown: {variable_type}")
        
        return missing_mappings
    
    def suggest_context(self, components: List[Dict]) -> str:
        """
        Return appropriate context based on variable types and persistence needs
        
        Args:
            components (List[Dict]): List of parsed components
            
        Returns:
            str: Suggested context ("hits", "visits", "visitors")
        """
        if not components:
            return "visitors"
        
        # Count variable types by context
        context_scores = {"hits": 0, "visits": 0, "visitors": 0}
        
        for component in components:
            if not isinstance(component, dict):
                continue
            
            variable_type = component.get("variable", "")
            component_type = component.get("type", "")
            
            # Score based on variable type
            for context, variables in self.context_rules.items():
                if variable_type in variables:
                    context_scores[context] += 1
                elif component_type in ["event", "page", "site_section"]:
                    context_scores["hits"] += 1
                elif component_type in ["device", "geography", "campaign"]:
                    context_scores["visits"] += 1
                elif component_type in ["evar", "user_type", "subscription"]:
                    context_scores["visitors"] += 1
        
        # Return context with highest score, default to visitors
        if context_scores["hits"] > context_scores["visits"] and context_scores["hits"] > context_scores["visitors"]:
            return "hits"
        elif context_scores["visits"] > context_scores["visitors"]:
            return "visits"
        else:
            return "visitors"
    
    def _map_event_variable(self, variable_type: str, value: str) -> str:
        """Map event variables to Adobe Analytics event format"""
        event_mappings = {
            "purchase": "events/purchase",
            "cart_add": "events/scAdd",
            "cart_remove": "events/scRemove",
            "checkout": "events/scCheckout",
            "newsletter": "events/newsletter_signup",
            "download": "events/download",
            "video": "events/video_play",
            "search": "events/internal_search",
            "social_share": "events/social_share",
            "email_click": "events/email_click",
            "form_submit": "events/form_submit",
            "login": "events/login",
            "registration": "events/registration",
            "logout": "events/logout"
        }
        
        return event_mappings.get(variable_type, f"events/{variable_type}")
    
    def _map_geography_variable(self, variable_type: str, value: str) -> str:
        """Map geography variables to Adobe Analytics geography format"""
        geo_mappings = {
            "country": "variables/geocountry",
            "state": "variables/geostate",
            "city": "variables/geocity"
        }
        
        return geo_mappings.get(variable_type, "variables/geocountry")
    
    def get_available_variables(self) -> Dict[str, str]:
        """
        Get all available variable mappings
        
        Returns:
            Dict[str, str]: Dictionary of variable mappings
        """
        return self.variable_mappings.copy()
    
    def get_available_operators(self) -> Dict[str, str]:
        """
        Get all available operator mappings
        
        Returns:
            Dict[str, str]: Dictionary of operator mappings
        """
        return self.operator_mappings.copy()
    
    def get_available_values(self, variable_type: str) -> Dict[str, str]:
        """
        Get available value mappings for a specific variable type
        
        Args:
            variable_type (str): Type of variable to get values for
            
        Returns:
            Dict[str, str]: Dictionary of value mappings for the variable type
        """
        return self.value_mappings.get(variable_type, {})
    
    def is_standard_variable(self, variable_type: str) -> bool:
        """
        Check if a variable type is in the standard mappings
        
        Args:
            variable_type (str): Variable type to check
            
        Returns:
            bool: True if variable is in standard mappings
        """
        return variable_type in self.variable_mappings
    
    def get_variable_info(self, variable_type: str) -> Dict:
        """
        Get detailed information about a variable type
        
        Args:
            variable_type (str): Variable type to get info for
            
        Returns:
            Dict: Variable information including name, type, and available values
        """
        mapped_name = self.variable_mappings.get(variable_type, "")
        available_values = self.get_available_values(variable_type)
        
        return {
            "original_name": variable_type,
            "mapped_name": mapped_name,
            "is_standard": self.is_standard_variable(variable_type),
            "available_values": available_values,
            "context_suggestions": self._get_context_suggestions_for_variable(variable_type)
        }
    
    def _get_context_suggestions_for_variable(self, variable_type: str) -> List[str]:
        """Get context suggestions for a specific variable type"""
        suggestions = []
        
        for context, variables in self.context_rules.items():
            if variable_type in variables:
                suggestions.append(context)
        
        return suggestions if suggestions else ["visitors"]


# Global instance for easy access
variable_mapper = VariableMapper()
