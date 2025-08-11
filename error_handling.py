#!/usr/bin/env python3
"""
Advanced Error Handling and Edge Cases for Adobe Analytics Segment Creation

This module provides comprehensive error handling, validation, and recovery
mechanisms for the segment creation workflow.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import streamlit as st


class ErrorSeverity(Enum):
    """Error severity levels for classification and handling."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors for better organization and handling."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    API_ERROR = "api_error"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    USER_INPUT = "user_input"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class SegmentCreationError(Exception):
    """Custom exception for segment creation errors."""
    
    def __init__(self, message: str, category: ErrorCategory, severity: ErrorSeverity, 
                 details: Optional[Dict[str, Any]] = None, recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = None  # Will be set by error handler


class ErrorHandler:
    """Comprehensive error handling system for segment creation."""
    
    def __init__(self):
        self.error_log = []
        self.recovery_suggestions = {
            ErrorCategory.VALIDATION: [
                "Check that all required fields are filled",
                "Verify the segment name is unique",
                "Ensure the RSID is correct",
                "Review the segment rules for syntax errors"
            ],
            ErrorCategory.AUTHENTICATION: [
                "Verify your Adobe API credentials",
                "Check if your access token has expired",
                "Ensure you have the required API scopes",
                "Contact your Adobe administrator for access"
            ],
            ErrorCategory.API_ERROR: [
                "Check the Adobe Analytics API status",
                "Verify your segment definition format",
                "Ensure you're not exceeding API limits",
                "Review the error details for specific issues"
            ],
            ErrorCategory.NETWORK: [
                "Check your internet connection",
                "Verify firewall settings",
                "Try again in a few minutes",
                "Contact your network administrator"
            ],
            ErrorCategory.CONFIGURATION: [
                "Verify your Adobe Analytics configuration",
                "Check your report suite settings",
                "Ensure proper permissions are set",
                "Review your organization settings"
            ]
        }
    
    def handle_error(self, error: Exception, context: str = "Unknown") -> Dict[str, Any]:
        """
        Handle any error and return structured error information.
        
        Args:
            error: The exception that occurred
            context: Context where the error occurred
            
        Returns:
            Dictionary with error details and recovery suggestions
        """
        # Classify the error
        error_info = self.classify_error(error)
        
        # Log the error
        self.log_error(error, context, error_info)
        
        # Generate recovery suggestions
        recovery_suggestions = self.get_recovery_suggestions(error_info['category'])
        
        # Create user-friendly error message
        user_message = self.create_user_message(error_info, recovery_suggestions)
        
        return {
            'error_type': error_info['type'],
            'category': error_info['category'],
            'severity': error_info['severity'],
            'message': user_message,
            'recovery_suggestions': recovery_suggestions,
            'recoverable': error_info['recoverable'],
            'technical_details': error_info['details'],
            'context': context
        }
    
    def classify_error(self, error: Exception) -> Dict[str, Any]:
        """Classify the error based on its type and content."""
        
        # Default classification
        error_info = {
            'type': type(error).__name__,
            'category': ErrorCategory.UNKNOWN,
            'severity': ErrorSeverity.MEDIUM,
            'recoverable': True,
            'details': {}
        }
        
        # Classify based on error type and message
        error_message = str(error).lower()
        
        # Authentication errors
        if any(keyword in error_message for keyword in ['unauthorized', 'authentication', 'token', 'credential']):
            error_info.update({
                'category': ErrorCategory.AUTHENTICATION,
                'severity': ErrorSeverity.HIGH,
                'recoverable': True
            })
        
        # API errors
        elif any(keyword in error_message for keyword in ['api', 'endpoint', 'request', 'response']):
            error_info.update({
                'category': ErrorCategory.API_ERROR,
                'severity': ErrorSeverity.MEDIUM,
                'recoverable': True
            })
        
        # Network errors
        elif any(keyword in error_message for keyword in ['network', 'connection', 'timeout', 'dns']):
            error_info.update({
                'category': ErrorCategory.NETWORK,
                'severity': ErrorSeverity.MEDIUM,
                'recoverable': True
            })
        
        # Validation errors
        elif any(keyword in error_message for keyword in ['validation', 'invalid', 'required', 'format']):
            error_info.update({
                'category': ErrorCategory.VALIDATION,
                'severity': ErrorSeverity.LOW,
                'recoverable': True
            })
        
        # Configuration errors
        elif any(keyword in error_message for keyword in ['config', 'setting', 'permission', 'scope']):
            error_info.update({
                'category': ErrorCategory.CONFIGURATION,
                'severity': ErrorSeverity.MEDIUM,
                'recoverable': True
            })
        
        # System errors (usually not recoverable)
        elif any(keyword in error_message for keyword in ['system', 'internal', 'fatal', 'critical']):
            error_info.update({
                'category': ErrorCategory.SYSTEM,
                'severity': ErrorSeverity.CRITICAL,
                'recoverable': False
            })
        
        return error_info
    
    def get_recovery_suggestions(self, category: ErrorCategory) -> List[str]:
        """Get recovery suggestions for a specific error category."""
        return self.recovery_suggestions.get(category, [
            "Try again in a few minutes",
            "Check the error details for more information",
            "Contact support if the problem persists"
        ])
    
    def create_user_message(self, error_info: Dict[str, Any], recovery_suggestions: List[str]) -> str:
        """Create a user-friendly error message."""
        
        severity_icons = {
            ErrorSeverity.LOW: "ℹ️",
            ErrorSeverity.MEDIUM: "⚠️",
            ErrorSeverity.HIGH: "🚨",
            ErrorSeverity.CRITICAL: "💥"
        }
        
        icon = severity_icons.get(error_info['severity'], "❌")
        
        if error_info['recoverable']:
            message = f"{icon} {error_info['type']} occurred. This issue can usually be resolved."
        else:
            message = f"{icon} {error_info['type']} occurred. This is a system issue that may require support."
        
        return message
    
    def log_error(self, error: Exception, context: str, error_info: Dict[str, Any]):
        """Log the error for debugging and monitoring."""
        log_entry = {
            'timestamp': None,  # Will be set by logging system
            'error_type': error_info['type'],
            'category': error_info['category'].value,
            'severity': error_info['severity'].value,
            'message': str(error),
            'context': context,
            'traceback': traceback.format_exc(),
            'details': error_info['details']
        }
        
        self.error_log.append(log_entry)
        
        # Log to console for debugging
        print(f"ERROR [{error_info['category'].value.upper()}] {error_info['type']}: {error}")
        print(f"Context: {context}")
        print(f"Severity: {error_info['severity'].value}")
        if error_info['details']:
            print(f"Details: {error_info['details']}")


class ValidationErrorHandler:
    """Specialized error handler for validation errors."""
    
    @staticmethod
    def validate_segment_name(name: str) -> Tuple[bool, Optional[str]]:
        """Validate segment name format and uniqueness."""
        if not name or not name.strip():
            return False, "Segment name is required"
        
        if len(name.strip()) < 3:
            return False, "Segment name must be at least 3 characters long"
        
        if len(name.strip()) > 100:
            return False, "Segment name must be less than 100 characters"
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '&', '"', "'", '\\', '/']
        for char in invalid_chars:
            if char in name:
                return False, f"Segment name contains invalid character: {char}"
        
        return True, None
    
    @staticmethod
    def validate_rsid(rsid: str) -> Tuple[bool, Optional[str]]:
        """Validate Report Suite ID format."""
        if not rsid or not rsid.strip():
            return False, "Report Suite ID is required"
        
        # RSID should be alphanumeric and typically 8-20 characters
        if not rsid.strip().isalnum():
            return False, "Report Suite ID should contain only letters and numbers"
        
        if len(rsid.strip()) < 8 or len(rsid.strip()) > 20:
            return False, "Report Suite ID should be 8-20 characters long"
        
        return True, None
    
    @staticmethod
    def validate_segment_rules(rules: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Validate segment rules structure and content."""
        errors = []
        
        if not rules:
            return False, ["At least one rule is required"]
        
        for i, rule in enumerate(rules):
            rule_errors = []
            
            # Check required fields
            if 'func' not in rule:
                rule_errors.append("Function type is required")
            elif rule['func'] not in ['streq', 'gt', 'lt', 'gte', 'lte', 'contains', 'regex']:
                rule_errors.append(f"Invalid function type: {rule['func']}")
            
            if 'name' not in rule:
                rule_errors.append("Variable name is required")
            elif not rule['name'].startswith('variables/'):
                rule_errors.append("Variable name should start with 'variables/'")
            
            # Check value field based on function type
            if rule.get('func') in ['gt', 'lt', 'gte', 'lte']:
                if 'val' not in rule or not isinstance(rule['val'], (int, float)):
                    rule_errors.append("Numeric value is required for comparison functions")
            elif rule.get('func') in ['streq', 'contains']:
                if not rule.get('str') and not rule.get('val'):
                    rule_errors.append("String value is required for string functions")
            
            if rule_errors:
                errors.append(f"Rule {i+1}: {'; '.join(rule_errors)}")
        
        return len(errors) == 0, errors


class RecoveryManager:
    """Manages error recovery and retry logic."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_delays = [1, 5, 15]  # Delays in seconds
    
    def should_retry(self, error_info: Dict[str, Any], attempt: int) -> bool:
        """Determine if an operation should be retried."""
        if attempt >= self.max_retries:
            return False
        
        # Don't retry critical or non-recoverable errors
        if error_info['severity'] == ErrorSeverity.CRITICAL or not error_info['recoverable']:
            return False
        
        # Don't retry validation errors (user needs to fix them)
        if error_info['category'] == ErrorCategory.VALIDATION:
            return False
        
        return True
    
    def get_retry_delay(self, attempt: int) -> int:
        """Get the delay before the next retry attempt."""
        if attempt < len(self.retry_delays):
            return self.retry_delays[attempt]
        return self.retry_delays[-1]  # Use the last delay for subsequent attempts
    
    def create_retry_message(self, attempt: int, max_retries: int, delay: int) -> str:
        """Create a user-friendly retry message."""
        if attempt == 0:
            return f"🔄 Attempting to resolve the issue... (Attempt {attempt + 1}/{max_retries})"
        else:
            return f"🔄 Retrying... (Attempt {attempt + 1}/{max_retries}) - Waiting {delay} seconds"


class ErrorDisplay:
    """Handles the display of errors in the Streamlit UI."""
    
    @staticmethod
    def show_error(error_info: Dict[str, Any]):
        """Display an error in the Streamlit UI."""
        
        severity_colors = {
            ErrorSeverity.LOW: "info",
            ErrorSeverity.MEDIUM: "warning",
            ErrorSeverity.HIGH: "error",
            ErrorSeverity.CRITICAL: "error"
        }
        
        color = severity_colors.get(error_info['severity'], "error")
        
        # Show main error message
        if color == "info":
            st.info(error_info['message'])
        elif color == "warning":
            st.warning(error_info['message'])
        else:
            st.error(error_info['message'])
        
        # Show recovery suggestions
        if error_info['recovery_suggestions']:
            with st.expander("💡 How to resolve this issue"):
                for i, suggestion in enumerate(error_info['recovery_suggestions'], 1):
                    st.markdown(f"{i}. {suggestion}")
        
        # Show technical details for debugging (collapsed by default)
        if error_info['technical_details']:
            with st.expander("🔧 Technical Details (for debugging)"):
                st.json(error_info['technical_details'])
    
    @staticmethod
    def show_retry_progress(attempt: int, max_retries: int, delay: int):
        """Show retry progress in the UI."""
        progress = (attempt + 1) / max_retries
        st.progress(progress)
        
        if attempt == 0:
            st.info(f"🔄 Attempting to resolve the issue... (Attempt {attempt + 1}/{max_retries})")
        else:
            st.warning(f"🔄 Retrying... (Attempt {attempt + 1}/{max_retries}) - Waiting {delay} seconds")


# Global error handler instance
error_handler = ErrorHandler()
validation_handler = ValidationErrorHandler()
recovery_manager = RecoveryManager()
error_display = ErrorDisplay()


def handle_segment_creation_error(error: Exception, context: str = "Segment Creation") -> Dict[str, Any]:
    """
    Convenience function to handle segment creation errors.
    
    Args:
        error: The exception that occurred
        context: Context where the error occurred
        
    Returns:
        Dictionary with error details and recovery suggestions
    """
    return error_handler.handle_error(error, context)


def validate_segment_configuration(name: str, rsid: str, rules: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate complete segment configuration.
    
    Args:
        name: Segment name
        rsid: Report Suite ID
        rules: List of segment rules
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate name
    is_name_valid, name_error = validation_handler.validate_segment_name(name)
    if not is_name_valid:
        errors.append(name_error)
    
    # Validate RSID
    is_rsid_valid, rsid_error = validation_handler.validate_rsid(rsid)
    if not is_rsid_valid:
        errors.append(rsid_error)
    
    # Validate rules
    are_rules_valid, rule_errors = validation_handler.validate_segment_rules(rules)
    if not are_rules_valid:
        errors.extend(rule_errors)
    
    return len(errors) == 0, errors


def create_error_summary(error_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a summary of errors for monitoring and debugging.
    
    Args:
        error_log: List of error log entries
        
    Returns:
        Summary statistics and insights
    """
    if not error_log:
        return {"total_errors": 0, "summary": "No errors recorded"}
    
    # Count by category
    category_counts = {}
    severity_counts = {}
    
    for entry in error_log:
        category = entry['category']
        severity = entry['severity']
        
        category_counts[category] = category_counts.get(category, 0) + 1
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Find most common errors
    error_types = [entry['error_type'] for entry in error_log]
    most_common_error = max(set(error_types), key=error_types.count)
    
    return {
        "total_errors": len(error_log),
        "category_breakdown": category_counts,
        "severity_breakdown": severity_counts,
        "most_common_error": most_common_error,
        "recent_errors": error_log[-5:],  # Last 5 errors
        "summary": f"Total errors: {len(error_log)}, Most common: {most_common_error}"
    } 