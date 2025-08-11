#!/usr/bin/env python3
"""
Simple test script to verify the new segment creation functions in adobe_api.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test importing the new functions
    from adobe_api import (
        create_analytics_segment_from_json,
        create_analytics_segment_enhanced,
        get_adobe_segments
    )
    
    print("✅ Successfully imported new functions:")
    print(f"  - create_analytics_segment_from_json: {create_analytics_segment_from_json}")
    print(f"  - create_analytics_segment_enhanced: {create_analytics_segment_enhanced}")
    print(f"  - get_adobe_segments: {get_adobe_segments}")
    
    # Test function signatures
    print("\n📝 Function signatures:")
    print(f"  - create_analytics_segment_from_json.__annotations__: {create_analytics_segment_from_json.__annotations__}")
    print(f"  - create_analytics_segment_enhanced.__annotations__: {create_analytics_segment_enhanced.__annotations__}")
    print(f"  - get_adobe_segments.__annotations__: {get_adobe_segments.__annotations__}")
    
    # Test docstrings
    print("\n📚 Function documentation:")
    print(f"  - create_analytics_segment_from_json.__doc__: {create_analytics_segment_from_json.__doc__[:100]}...")
    print(f"  - create_analytics_segment_enhanced.__doc__: {create_analytics_segment_enhanced.__doc__[:100]}...")
    print(f"  - get_adobe_segments.__doc__: {get_adobe_segments.__doc__[:100]}...")
    
    print("\n🎉 All new functions imported successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1) 