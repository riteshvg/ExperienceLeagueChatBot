#!/usr/bin/env python3
"""
Test script for the enhanced action detection system in app.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the enhanced functions
    from app import detect_create_action, detect_segment_creation_intent, generate_segment_suggestions
    
    print("✅ Successfully imported enhanced action detection functions")
    
    # Test cases for different types of queries
    test_queries = [
        # Simple segment creation
        "Create a segment for mobile users",
        "Build a segment for visitors from the United States",
        "Make a segment for people who spent more than 10 minutes on site",
        
        # Complex segment creation
        "Create a segment for mobile users from California who visited more than 5 pages",
        "Build a segment for desktop visitors from New York who converted during business hours",
        "Make a segment for tablet users who added items to cart on weekends",
        
        # Other actions
        "Create a dashboard for analytics",
        "Build a calculated metric for conversion rate",
        "Make a report for page performance",
        
        # No action
        "What is Adobe Analytics?",
        "How do I implement tracking?",
        "Show me the documentation"
    ]
    
    print("\n🧪 Testing Enhanced Action Detection:")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        # Test the main detection function
        action_type, details = detect_create_action(query)
        
        if action_type:
            print(f"   ✅ Action detected: {action_type}")
            
            if action_type == 'segment' and isinstance(details, dict):
                print(f"   📊 Intent Details:")
                print(f"      - Target Audience: {details.get('target_audience', 'N/A')}")
                print(f"      - Geographic: {details.get('geographic', 'N/A')}")
                print(f"      - Device: {details.get('device', 'N/A')}")
                print(f"      - Behavioral: {details.get('behavioral', [])}")
                print(f"      - Time-based: {details.get('time_based', 'N/A')}")
                print(f"      - Custom Variables: {details.get('custom_variables', [])}")
                print(f"      - Confidence: {details.get('intent_confidence', 'N/A')}")
                
                # Test segment suggestions
                print(f"   🎯 Segment Suggestions:")
                suggestions = generate_segment_suggestions(details)
                print(f"      - Suggested Name: {suggestions['segment_name']}")
                print(f"      - Suggested Description: {suggestions['segment_description']}")
                print(f"      - Recommended Rules: {len(suggestions['recommended_rules'])} rules")
                print(f"      - Next Steps: {len(suggestions['next_steps'])} steps")
                
            else:
                print(f"   📝 Details: {details}")
        else:
            print(f"   ❌ No action detected")
    
    print("\n🎯 Testing Specific Segment Intent Detection:")
    print("=" * 60)
    
    # Test specific segment detection
    segment_queries = [
        "Create a segment for mobile users from California",
        "Build a segment for visitors who spent more than 10 minutes on site",
        "Make a segment for people who converted during business hours"
    ]
    
    for i, query in enumerate(segment_queries, 1):
        print(f"\n{i}. Segment Query: '{query}'")
        
        # Test the segment-specific function directly
        action_type, intent_details = detect_segment_creation_intent(query, query.lower())
        
        print(f"   📊 Intent Analysis:")
        for key, value in intent_details.items():
            if key != 'action_type':  # Skip action_type as it's always 'segment'
                print(f"      - {key.replace('_', ' ').title()}: {value}")
        
        # Test suggestions
        print(f"   🎯 Generated Suggestions:")
        suggestions = generate_segment_suggestions(intent_details)
        print(f"      - Name: {suggestions['segment_name']}")
        print(f"      - Description: {suggestions['segment_description']}")
        print(f"      - Rules Count: {len(suggestions['recommended_rules'])}")
        print(f"      - Next Steps: {suggestions['next_steps'][:2]}...")  # Show first 2 steps
    
    print("\n🎉 All tests completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1) 