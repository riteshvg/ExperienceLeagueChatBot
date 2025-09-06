#!/usr/bin/env python3
"""
Segment Configuration Module

This module provides centralized configuration constants and mappings
for the Adobe Analytics segment creation system.
"""

# API Configuration Constants
ADOBE_API_BASE_URL = "https://analytics.adobe.io/api"

API_ENDPOINTS = {
    "segments": "/segments",
    "validate": "/segments/validate",
    "dimensions": "/reportsuites/{rsid}/dimensions",
    "metrics": "/reportsuites/{rsid}/metrics",
    "reportsuites": "/reportsuites"
}

REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": "{client_id}",
    "Authorization": "Bearer {access_token}"
}

# Segment Creation Constants
DEFAULT_SEGMENT_VERSION = [1, 0, 0]
DEFAULT_SEGMENT_FUNC = "segment"

CONTEXT_TYPES = ["hits", "visits", "visitors"]

SUPPORTED_OPERATORS = [
    "streq", "streq-in", "streq-not", "streq-not-in",
    "exists", "not-exists", "gt", "gte", "lt", "lte"
]

# Natural Language Patterns
SEGMENT_KEYWORDS = [
    "create segment", "segment for", "users who", "visitors that",
    "build segment", "make segment", "audience for", "cohort for",
    "user group", "visitor group", "targeting", "filter users",
    "user filter", "segment targeting", "audience targeting"
]

CONDITION_PATTERNS = {
    "device": ["mobile", "desktop", "tablet", "phone", "computer"],
    "page": ["homepage", "product", "checkout", "login", "registration"],
    "event": ["purchase", "cart_add", "newsletter", "download", "video"],
    "campaign": ["email", "social", "search", "display"],
    "geography": ["country", "state", "city", "usa", "california"],
    "behavior": ["conversion", "bounce", "time", "page views", "session"]
}

LOGIC_OPERATORS = {
    "and": "and",
    "or": "or",
    "who": "and",
    "that": "and",
    "which": "and",
    "but": "and",
    "also": "and"
}

# Variable Mapping Reference
ADOBE_VARIABLE_MAPPINGS = {
    # Device and Technology
    "device": "variables/mobiledevicetype",
    "browser": "variables/browser",
    "operating_system": "variables/operatingsystem",
    "screen_resolution": "variables/screenresolution",
    
    # Pages and Content
    "page": "variables/page",
    "site_section": "variables/sitesection",
    "page_name": "variables/pagename",
    "page_url": "variables/pageurl",
    
    # Campaign and Marketing
    "campaign": "variables/trackingcode",
    "referrer": "variables/referrer",
    "search_engine": "variables/searchengine",
    "search_keyword": "variables/searchkeyword",
    
    # Geography
    "country": "variables/geocountry",
    "state": "variables/geostate",
    "city": "variables/geocity",
    "zip": "variables/geozip",
    
    # Time and Date
    "hour": "variables/hour",
    "day_of_week": "variables/dayofweek",
    "month": "variables/month",
    "year": "variables/year",
    
    # Metrics
    "page_views": "metrics/pageviews",
    "visits": "metrics/visits",
    "visitors": "metrics/visitors",
    "bounce_rate": "metrics/bouncerate",
    "time_on_site": "metrics/timespent",
    "revenue": "metrics/revenue",
    "orders": "metrics/orders",
    
    # Events
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

OPERATOR_MAPPINGS = {
    "equals": "streq",
    "contains": "streq-in",
    "not_equals": "streq-not",
    "not_contains": "streq-not-in",
    "exists": "exists",
    "not_exists": "not-exists",
    "greater_than": "gt",
    "greater_than_or_equal": "gte",
    "less_than": "lt",
    "less_than_or_equal": "lte"
}

CONTEXT_SUGGESTIONS = {
    "hits": [
        "page", "site_section", "campaign", "browser", "operating_system",
        "referrer", "purchase", "cart_add", "cart_remove", "checkout",
        "newsletter", "download", "video", "search", "social_share",
        "email_click", "form_submit", "login", "registration", "logout"
    ],
    "visits": [
        "device", "country", "state", "city", "page_views", "visits",
        "bounce_rate", "time_on_site", "revenue", "orders"
    ],
    "visitors": [
        "visitors", "user_type", "customer_tier", "subscription"
    ]
}

# Error Messages
API_ERROR_MESSAGES = {
    400: "Bad Request - Invalid parameters provided",
    401: "Unauthorized - Invalid or expired credentials",
    403: "Forbidden - Insufficient permissions",
    404: "Not Found - Resource not found",
    408: "Request Timeout - Request took too long",
    429: "Too Many Requests - Rate limit exceeded",
    500: "Internal Server Error - Adobe Analytics server error",
    502: "Bad Gateway - Invalid response from server",
    503: "Service Unavailable - Adobe Analytics service down",
    504: "Gateway Timeout - Request timeout"
}

VALIDATION_ERROR_MESSAGES = {
    "missing_name": "Segment name is required",
    "missing_description": "Segment description is required",
    "missing_rsid": "Report Suite ID is required",
    "invalid_context": "Context must be one of: hits, visits, visitors",
    "no_conditions": "At least one condition is required",
    "invalid_operator": "Invalid operator specified",
    "missing_variable": "Variable name is required",
    "invalid_value": "Invalid value provided"
}

USER_ERROR_MESSAGES = {
    "invalid_input": "Please provide valid input",
    "missing_required": "Please fill in all required fields",
    "invalid_format": "Invalid format provided",
    "connection_failed": "Failed to connect to Adobe Analytics",
    "api_error": "Adobe Analytics API error occurred",
    "validation_failed": "Segment validation failed",
    "creation_failed": "Segment creation failed"
}

# UI Text Constants
SUCCESS_MESSAGES = {
    "detection": "✅ Segment request detected",
    "parsing": "✅ Message parsed successfully",
    "mapping": "✅ Variables mapped to Adobe Analytics format",
    "validation": "✅ Segment validation successful",
    "creation": "🎉 Segment created successfully",
    "metadata_collected": "✅ Segment metadata collected",
    "credentials_saved": "✅ API credentials saved",
    "workflow_complete": "🎉 Segment creation workflow completed"
}

PROMPT_MESSAGES = {
    "segment_name": "Enter segment name:",
    "segment_description": "Enter segment description:",
    "report_suite_id": "Enter Report Suite ID:",
    "context_level": "Select context level:",
    "missing_parameters": "Please provide missing parameter information:",
    "api_credentials": "Configure Adobe Analytics API credentials:",
    "confirmation": "Please review and confirm segment creation:",
    "additional_conditions": "Add additional conditions (optional):"
}

CONFIRMATION_MESSAGES = {
    "create_segment": "✅ Create Segment",
    "cancel_creation": "❌ Cancel",
    "test_connection": "🔗 Test Connection",
    "continue_workflow": "➡️ Continue",
    "reset_workflow": "🔄 Reset",
    "save_credentials": "💾 Save Credentials"
}

# Workflow Status Messages
WORKFLOW_STATUS_MESSAGES = {
    "detection": "🔍 Analyzing segment request...",
    "mapping": "🔄 Mapping variables to Adobe Analytics references...",
    "user_input": "📝 Collecting user input...",
    "metadata": "📋 Collecting segment metadata...",
    "building": "🔨 Building segment definition...",
    "confirmation": "🤔 Getting user confirmation...",
    "api_credentials": "🔐 Configuring API credentials...",
    "validation": "🔍 Validating segment with Adobe Analytics...",
    "creation": "🚀 Creating segment in Adobe Analytics..."
}

# Default Values
DEFAULT_VALUES = {
    "segment_name": "Generated Segment",
    "segment_description": "Auto-generated from user request",
    "report_suite_id": "",
    "context": "visitors",
    "client_id": "",
    "access_token": "",
    "company_id": "",
    "timeout": 30
}

# UI Configuration
UI_CONFIG = {
    "sidebar_width": 300,
    "max_conditions": 10,
    "max_retries": 3,
    "refresh_interval": 1000,
    "show_debug": False
}

# Validation Rules
VALIDATION_RULES = {
    "min_name_length": 3,
    "max_name_length": 100,
    "min_description_length": 10,
    "max_description_length": 500,
    "min_rsid_length": 3,
    "max_rsid_length": 50,
    "max_conditions": 20
}

# API Rate Limits
RATE_LIMITS = {
    "requests_per_minute": 100,
    "requests_per_hour": 1000,
    "concurrent_requests": 5
}

# Supported File Types
SUPPORTED_FILE_TYPES = {
    "import": [".json", ".csv"],
    "export": [".json", ".csv", ".txt"]
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "segment_creation.log"
}
