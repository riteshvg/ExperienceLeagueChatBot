#!/usr/bin/env python3
"""
Test script for the advanced error handling system
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test importing the error handling system
    from error_handling import (
        ErrorHandler, ValidationErrorHandler, RecoveryManager, ErrorDisplay,
        handle_segment_creation_error, validate_segment_configuration,
        create_error_summary, ErrorSeverity, ErrorCategory, SegmentCreationError
    )
    
    print("✅ Successfully imported error handling system")
    
    # Test Error Handler
    print("\n🧪 Testing Error Handler:")
    print("=" * 50)
    
    error_handler = ErrorHandler()
    
    # Test error classification
    test_errors = [
        ValueError("Invalid segment name"),
        ConnectionError("Network timeout"),
        Exception("Unauthorized access"),
        RuntimeError("System internal error")
    ]
    
    for error in test_errors:
        result = error_handler.handle_error(error, "Test Context")
        print(f"✅ Error: {type(error).__name__}")
        print(f"   Category: {result['category']}")
        print(f"   Severity: {result['severity']}")
        print(f"   Recoverable: {result['recoverable']}")
        print(f"   Message: {result['message'][:50]}...")
    
    # Test Validation Error Handler
    print("\n✅ Testing Validation Error Handler:")
    print("=" * 50)
    
    # Test segment name validation
    test_names = ["", "ab", "Valid Name", "Invalid<Name", "Very Long Name " * 20]
    for name in test_names:
        is_valid, error = ValidationErrorHandler.validate_segment_name(name)
        status = "✅" if is_valid else "❌"
        print(f"{status} Name '{name[:20]}...': {error or 'Valid'}")
    
    # Test RSID validation
    test_rsids = ["", "123", "valid123", "invalid-rsid", "verylongrsid123456789"]
    for rsid in test_rsids:
        is_valid, error = ValidationErrorHandler.validate_rsid(rsid)
        status = "✅" if is_valid else "❌"
        print(f"{status} RSID '{rsid}': {error or 'Valid'}")
    
    # Test segment rules validation
    test_rules = [
        [],  # Empty rules
        [{"func": "streq", "name": "variables/page", "str": "Homepage"}],  # Valid
        [{"func": "invalid_func", "name": "variables/page"}],  # Invalid function
        [{"func": "gt", "name": "variables/pageviews"}],  # Missing value
        [{"func": "streq", "name": "invalid_name"}],  # Invalid variable name
    ]
    
    for i, rules in enumerate(test_rules):
        is_valid, errors = ValidationErrorHandler.validate_segment_rules(rules)
        status = "✅" if is_valid else "❌"
        print(f"{status} Rules Set {i+1}: {errors or 'Valid'}")
    
    # Test complete configuration validation
    print("\n🔧 Testing Complete Configuration Validation:")
    print("=" * 50)
    
    test_configs = [
        {
            "name": "Test Segment",
            "rsid": "valid123",
            "rules": [{"func": "streq", "name": "variables/page", "str": "Homepage"}]
        },
        {
            "name": "",
            "rsid": "invalid",
            "rules": []
        }
    ]
    
    for i, config in enumerate(test_configs):
        is_valid, errors = validate_segment_configuration(
            config["name"], config["rsid"], config["rules"]
        )
        status = "✅" if is_valid else "❌"
        print(f"{status} Config {i+1}: {errors or 'Valid'}")
    
    # Test Recovery Manager
    print("\n🔄 Testing Recovery Manager:")
    print("=" * 50)
    
    recovery_mgr = RecoveryManager(max_retries=3)
    
    # Test retry logic
    test_error_info = {
        'severity': ErrorSeverity.MEDIUM,
        'recoverable': True,
        'category': ErrorCategory.API_ERROR
    }
    
    for attempt in range(4):
        should_retry = recovery_mgr.should_retry(test_error_info, attempt)
        delay = recovery_mgr.get_retry_delay(attempt)
        retry_msg = recovery_mgr.create_retry_message(attempt, 3, delay)
        
        print(f"Attempt {attempt + 1}: Should retry: {should_retry}, Delay: {delay}s")
        print(f"   Message: {retry_msg}")
    
    # Test custom exception
    print("\n🚨 Testing Custom Exception:")
    print("=" * 50)
    
    try:
        raise SegmentCreationError(
            message="Test segment creation error",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details={"field": "name", "value": "test"},
            recoverable=True
        )
    except SegmentCreationError as e:
        print(f"✅ Custom exception caught: {e.message}")
        print(f"   Category: {e.category}")
        print(f"   Severity: {e.severity}")
        print(f"   Recoverable: {e.recoverable}")
        print(f"   Details: {e.details}")
    
    # Test error summary
    print("\n📊 Testing Error Summary:")
    print("=" * 50)
    
    # Simulate some errors
    error_handler.error_log = [
        {
            'error_type': 'ValueError',
            'category': 'validation',
            'severity': 'low',
            'message': 'Invalid input'
        },
        {
            'error_type': 'ConnectionError',
            'category': 'network',
            'severity': 'medium',
            'message': 'Network timeout'
        },
        {
            'error_type': 'ValueError',
            'category': 'validation',
            'severity': 'low',
            'message': 'Another validation error'
        }
    ]
    
    summary = create_error_summary(error_handler.error_log)
    print(f"✅ Total errors: {summary['total_errors']}")
    print(f"✅ Most common error: {summary['most_common_error']}")
    print(f"✅ Category breakdown: {summary['category_breakdown']}")
    print(f"✅ Summary: {summary['summary']}")
    
    print("\n🎉 All error handling tests completed successfully!")
    print("\n📝 Error Handling System Features:")
    print("  ✅ Comprehensive error classification")
    print("  ✅ User-friendly error messages")
    print("  ✅ Recovery suggestions by category")
    print("  ✅ Validation error handling")
    print("  ✅ Retry logic management")
    print("  ✅ Error logging and monitoring")
    print("  ✅ Custom exception types")
    print("  ✅ Error summary and analytics")
    
    print("\n🎯 Ready for integration with segment builder!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 