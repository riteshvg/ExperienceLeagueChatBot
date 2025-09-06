#!/usr/bin/env python3
"""
Adobe Analytics Segment Builder Module

This module provides functionality to construct Adobe Analytics segment JSON
definitions from parsed components and variable mappings.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class SegmentBuilder:
    """Builder for constructing Adobe Analytics segment definitions"""
    
    def __init__(self):
        self.supported_operators = {
            "streq": "equals",
            "streq-in": "contains",
            "streq-not": "not equals",
            "streq-not-in": "not contains",
            "exists": "exists",
            "not-exists": "does not exist",
            "gt": "greater than",
            "gte": "greater than or equal",
            "lt": "less than",
            "lte": "less than or equal"
        }
        
        self.context_descriptions = {
            "hits": "hits",
            "visits": "visits", 
            "visitors": "visitors"
        }
    
    def build_segment_definition(self, components: List[Dict], mappings: List[Dict], user_inputs: Dict) -> Dict:
        """
        Create complete segment JSON structure from components and mappings
        
        Args:
            components (List[Dict]): Parsed segment components
            mappings (List[Dict]): Mapped Adobe Analytics variables
            user_inputs (Dict): User-provided inputs (name, description, rsid, context)
            
        Returns:
            Dict: Complete Adobe Analytics segment definition
        """
        if not components or not mappings:
            return self._empty_segment_definition()
        
        # Extract user inputs with defaults
        segment_name = user_inputs.get("name", "Generated Segment")
        segment_description = user_inputs.get("description", "Auto-generated from user request")
        rsid = user_inputs.get("rsid", "default_rsid")
        context = user_inputs.get("context", "visitors")
        
        # Build the container structure
        container = self._build_container(mappings, context)
        
        # Create the complete segment definition
        segment_definition = {
            "name": segment_name,
            "description": segment_description,
            "rsid": rsid,
            "definition": {
                "func": "segment",
                "version": [1, 0, 0],
                "container": container
            }
        }
        
        return segment_definition
    
    def format_segment_summary(self, definition: Dict) -> str:
        """
        Convert JSON definition to human-readable text
        
        Args:
            definition (Dict): Adobe Analytics segment definition
            
        Returns:
            str: Human-readable segment summary
        """
        if not definition or "definition" not in definition:
            return "Invalid segment definition"
        
        # Extract basic info
        name = definition.get("name", "Unnamed Segment")
        description = definition.get("description", "No description")
        rsid = definition.get("rsid", "Unknown RSID")
        
        # Extract container info
        container = definition.get("definition", {}).get("container", {})
        context = container.get("type", "visitors")
        rules = container.get("rules", [])
        
        # Build summary
        summary_parts = []
        summary_parts.append(f"**Segment Name:** {name}")
        summary_parts.append(f"**Description:** {description}")
        summary_parts.append(f"**Report Suite ID:** {rsid}")
        summary_parts.append(f"**Context Level:** {self.context_descriptions.get(context, context)}")
        
        if rules:
            summary_parts.append("**Conditions:**")
            for i, rule in enumerate(rules, 1):
                rule_text = self._format_rule_text(rule, i)
                summary_parts.append(f"  {rule_text}")
        elif "pred" in container:
            # Single condition
            summary_parts.append("**Conditions:**")
            rule_text = self._format_rule_text(container["pred"], 1)
            summary_parts.append(f"  {rule_text}")
        else:
            summary_parts.append("**Conditions:** None")
        
        return "\n".join(summary_parts)
    
    def _build_container(self, mappings: List[Dict], context: str) -> Dict:
        """
        Build the container structure for the segment definition
        
        Args:
            mappings (List[Dict]): Mapped Adobe Analytics variables
            context (str): Segment context (hits/visits/visitors)
            
        Returns:
            Dict: Container structure
        """
        if not mappings:
            # No conditions - create empty container
            return {
                "type": context,
                "pred": {
                    "func": "exists",
                    "name": "variables/page"
                }
            }
        elif len(mappings) == 1:
            # Single condition
            return {
                "type": context,
                "pred": self._build_predicate(mappings[0])
            }
        else:
            # Multiple conditions - determine logic
            logic = self._determine_logic(mappings)
            rules = []
            
            for mapping in mappings:
                predicate = self._build_predicate(mapping)
                rules.append(predicate)
            
            return {
                "type": context,
                "func": logic,
                "rules": rules
            }
    
    def _build_predicate(self, mapping: Dict) -> Dict:
        """
        Build a predicate from a single mapping
        
        Args:
            mapping (Dict): Mapped Adobe Analytics variable
            
        Returns:
            Dict: Predicate structure
        """
        name = mapping.get("name", "")
        operator = mapping.get("operator", "streq")
        value = mapping.get("value", "")
        var_type = mapping.get("type", "")
        
        # Handle different operator types
        if operator == "exists":
            return {
                "func": "exists",
                "name": name
            }
        elif operator == "not-exists":
            return {
                "func": "not-exists",
                "name": name
            }
        elif operator in ["gt", "gte", "lt", "lte"]:
            return {
                "func": operator,
                "name": name,
                "val": {
                    "func": "attr",
                    "name": name
                },
                "num": float(value) if value.replace('.', '').replace('-', '').isdigit() else 0
            }
        else:
            # String-based operators
            return {
                "func": operator,
                "name": name,
                "val": {
                    "func": "attr",
                    "name": name
                },
                "str": str(value)
            }
    
    def _determine_logic(self, mappings: List[Dict]) -> str:
        """
        Determine the logic operator for multiple conditions
        
        Args:
            mappings (List[Dict]): List of mappings
            
        Returns:
            str: Logic operator ("and" or "or")
        """
        # For now, default to "and" logic
        # This could be enhanced to analyze the original components for logic indicators
        return "and"
    
    def _format_rule_text(self, rule: Dict, rule_number: int) -> str:
        """
        Format a single rule into human-readable text
        
        Args:
            rule (Dict): Rule predicate
            rule_number (int): Rule number for display
            
        Returns:
            str: Formatted rule text
        """
        func = rule.get("func", "unknown")
        name = rule.get("name", "unknown")
        
        # Extract variable name from full path
        var_name = name.split("/")[-1] if "/" in name else name
        
        if func == "exists":
            return f"{rule_number}. {var_name} exists"
        elif func == "not-exists":
            return f"{rule_number}. {var_name} does not exist"
        elif func in ["gt", "gte", "lt", "lte"]:
            operator_text = self.supported_operators.get(func, func)
            num_value = rule.get("num", 0)
            return f"{rule_number}. {var_name} {operator_text} {num_value}"
        else:
            # String-based operators
            operator_text = self.supported_operators.get(func, func)
            str_value = rule.get("str", "")
            return f"{rule_number}. {var_name} {operator_text} '{str_value}'"
    
    def _empty_segment_definition(self) -> Dict:
        """Return empty segment definition structure"""
        return {
            "name": "Empty Segment",
            "description": "No conditions defined",
            "rsid": "default_rsid",
            "definition": {
                "func": "segment",
                "version": [1, 0, 0],
                "container": {
                    "type": "visitors",
                    "pred": {
                        "func": "exists",
                        "name": "variables/page"
                    }
                }
            }
        }
    
    def validate_segment_definition(self, definition: Dict) -> tuple[bool, List[str]]:
        """
        Validate a segment definition for completeness and correctness
        
        Args:
            definition (Dict): Segment definition to validate
            
        Returns:
            tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        # Check required top-level fields
        required_fields = ["name", "description", "rsid", "definition"]
        for field in required_fields:
            if field not in definition:
                errors.append(f"Missing required field: {field}")
        
        # Check definition structure
        if "definition" in definition:
            defn = definition["definition"]
            if "func" not in defn or defn["func"] != "segment":
                errors.append("Invalid definition function")
            
            if "container" not in defn:
                errors.append("Missing container in definition")
            else:
                container_errors = self._validate_container(defn["container"])
                errors.extend(container_errors)
        
        return len(errors) == 0, errors
    
    def _validate_container(self, container: Dict) -> List[str]:
        """Validate container structure"""
        errors = []
        
        if "type" not in container:
            errors.append("Container missing type")
        elif container["type"] not in ["hits", "visits", "visitors"]:
            errors.append(f"Invalid container type: {container['type']}")
        
        if "pred" in container:
            # Single condition
            pred_errors = self._validate_predicate(container["pred"])
            errors.extend(pred_errors)
        elif "rules" in container:
            # Multiple conditions
            if not isinstance(container["rules"], list):
                errors.append("Container rules must be a list")
            else:
                for i, rule in enumerate(container["rules"]):
                    rule_errors = self._validate_predicate(rule)
                    for error in rule_errors:
                        errors.append(f"Rule {i+1}: {error}")
        else:
            errors.append("Container must have either 'pred' or 'rules'")
        
        return errors
    
    def _validate_predicate(self, predicate: Dict) -> List[str]:
        """Validate predicate structure"""
        errors = []
        
        if "func" not in predicate:
            errors.append("Predicate missing function")
        elif predicate["func"] not in self.supported_operators:
            errors.append(f"Unsupported predicate function: {predicate['func']}")
        
        if "name" not in predicate:
            errors.append("Predicate missing name")
        
        return errors
    
    def get_segment_preview(self, definition: Dict) -> str:
        """
        Get a preview of the segment definition in JSON format
        
        Args:
            definition (Dict): Segment definition
            
        Returns:
            str: Formatted JSON preview
        """
        try:
            return json.dumps(definition, indent=2)
        except Exception as e:
            return f"Error formatting preview: {str(e)}"
    
    def get_condition_count(self, definition: Dict) -> int:
        """
        Get the number of conditions in the segment
        
        Args:
            definition (Dict): Segment definition
            
        Returns:
            int: Number of conditions
        """
        container = definition.get("definition", {}).get("container", {})
        
        if "pred" in container:
            return 1
        elif "rules" in container:
            return len(container["rules"])
        else:
            return 0
    
    def get_context_level(self, definition: Dict) -> str:
        """
        Get the context level of the segment
        
        Args:
            definition (Dict): Segment definition
            
        Returns:
            str: Context level (hits/visits/visitors)
        """
        container = definition.get("definition", {}).get("container", {})
        return container.get("type", "visitors")


# Global instance for easy access
segment_builder = SegmentBuilder()
