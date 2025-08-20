#!/usr/bin/env python3
"""
Test Ingested Segment Examples and Enhanced Suggestions

This script tests the vector database integration and enhanced segment suggestions
to verify that the ingested data is working correctly.
"""

import sys
import os
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_vector_database_loading():
    """Test if the vector database can be loaded with ingested data."""
    print("🔍 Test 1: Vector Database Loading")
    print("=" * 40)
    
    try:
        from app import load_knowledge_base
        
        vectorstore = load_knowledge_base()
        if vectorstore is None:
            print("❌ Failed to load knowledge base")
            return False
        
        print(f"✅ Knowledge base loaded successfully")
        print(f"📊 Total documents: {vectorstore.index.ntotal}")
        
        # Check if we have segment examples by searching for specific terms
        results = vectorstore.similarity_search("New Zealand", k=3)
        segment_examples = [r for r in results if r.metadata.get('type') == 'segment_example']
        
        print(f"🔍 Found {len(segment_examples)} segment examples in 'New Zealand' search")
        
        if len(segment_examples) > 0:
            print("✅ Segment examples are accessible in vector database")
            # Show example details
            for example in segment_examples[:2]:
                print(f"   📋 {example.metadata.get('name', 'Unknown')}")
                print(f"      Context: {example.metadata.get('context', 'N/A')}")
                print(f"      Function: {example.metadata.get('pred_func', 'N/A')}")
            return True
        else:
            print("❌ No segment examples found in specific search")
            return False
            
    except Exception as e:
        print(f"❌ Error testing vector database: {e}")
        return False

def test_segment_example_search():
    """Test searching for specific types of segment examples."""
    print("\n🔍 Test 2: Segment Example Search")
    print("=" * 40)
    
    try:
        from app import load_knowledge_base
        
        vectorstore = load_knowledge_base()
        if vectorstore is None:
            return False
        
        # Test different search queries that should find segment examples
        test_queries = [
            ("New Zealand", "geographic targeting"),
            ("mobile", "device targeting"),
            ("Chrome", "browser targeting"),
            ("purchase", "conversion targeting"),
            ("revenue", "revenue targeting")
        ]
        
        all_found = True
        for query, description in test_queries:
            results = vectorstore.similarity_search(query, k=3)
            segment_examples = [r for r in results if r.metadata.get('type') == 'segment_example']
            
            if len(segment_examples) > 0:
                print(f"✅ '{query}' ({description}): Found {len(segment_examples)} relevant examples")
                # Show first example name
                if segment_examples:
                    print(f"   📋 Example: {segment_examples[0].metadata.get('name', 'Unknown')}")
            else:
                print(f"❌ '{query}' ({description}): No relevant examples found")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error testing segment search: {e}")
        return False

def test_enhanced_suggestions():
    """Test the enhanced segment suggestions function."""
    print("\n🔍 Test 3: Enhanced Segment Suggestions")
    print("=" * 40)
    
    try:
        from app import generate_segment_suggestions
        
        # Test different intent scenarios
        test_intents = [
            {
                'action_type': 'segment',
                'target_audience': 'visitors',
                'device': 'mobile',
                'geographic': 'country',
                'behavioral': ['page_views'],
                'intent_confidence': 'high'
            },
            {
                'action_type': 'segment',
                'target_audience': 'visitors',
                'geographic': 'country',
                'intent_confidence': 'medium'
            },
            {
                'action_type': 'segment',
                'target_audience': 'visitors',
                'device': 'desktop',
                'behavioral': ['conversion'],
                'intent_confidence': 'high'
            }
        ]
        
        all_passed = True
        for i, intent in enumerate(test_intents):
            print(f"\n🧪 Testing Intent {i+1}: {intent.get('device', 'No device')} + {intent.get('geographic', 'No geo')}")
            
            suggestions = generate_segment_suggestions(intent)
            
            # Check if suggestions have relevant examples
            if 'relevant_examples' in suggestions:
                examples_count = len(suggestions['relevant_examples'])
                print(f"   ✅ Found {examples_count} relevant examples")
                
                if examples_count > 0:
                    for j, example in enumerate(suggestions['relevant_examples'][:2]):
                        print(f"      📋 {j+1}. {example.get('name', 'Unknown')}")
                        print(f"         Context: {example.get('context', 'N/A')}")
                        print(f"         Function: {example.get('pred_func', 'N/A')}")
            else:
                print(f"   ⚠️  No relevant examples found (this might be expected for some intents)")
                # Don't fail the test for this - it's expected behavior
            
            # Check if geographic rules are flexible
            if intent.get('geographic'):
                rules = suggestions.get('recommended_rules', [])
                geographic_rules = [r for r in rules if 'geocountry' in r.get('name', '')]
                
                if geographic_rules:
                    rule = geographic_rules[0]
                    if rule.get('val') == 'Specific Country' or rule.get('str') == 'Specific Country':
                        print(f"   ✅ Geographic rule is flexible: {rule.get('val')}")
                    else:
                        print(f"   ❌ Geographic rule is not flexible: {rule.get('val')}")
                        all_passed = False
                else:
                    print(f"   ❌ No geographic rules found")
                    all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing enhanced suggestions: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_geographic_queries():
    """Test specific geographic queries to ensure they work correctly."""
    print("\n🔍 Test 4: Specific Geographic Queries")
    print("=" * 40)
    
    try:
        from app import load_knowledge_base
        
        vectorstore = load_knowledge_base()
        if vectorstore is None:
            return False
        
        # Test specific country queries
        test_countries = [
            "New Zealand",
            "United States"
        ]
        
        all_found = True
        for country in test_countries:
            results = vectorstore.similarity_search(f"visitors from {country}", k=3)
            segment_examples = [r for r in results if r.metadata.get('type') == 'segment_example']
            
            if len(segment_examples) > 0:
                print(f"✅ '{country}': Found {len(segment_examples)} geographic examples")
                # Show example details
                for example in segment_examples[:1]:
                    print(f"   📋 {example.metadata.get('name', 'Unknown')}")
                    print(f"      Context: {example.metadata.get('context', 'N/A')}")
            else:
                print(f"❌ '{country}': No geographic examples found")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error testing geographic queries: {e}")
        return False

def test_segment_example_metadata():
    """Test the metadata structure of ingested segment examples."""
    print("\n🔍 Test 5: Segment Example Metadata")
    print("=" * 40)
    
    try:
        from app import load_knowledge_base
        
        vectorstore = load_knowledge_base()
        if vectorstore is None:
            return False
        
        # Get segment examples by searching for specific terms that we know exist
        search_queries = ["New Zealand", "Mobile", "Chrome"]
        all_segment_examples = []
        
        for query in search_queries:
            results = vectorstore.similarity_search(query, k=5)
            segment_examples = [r for r in results if r.metadata.get('type') == 'segment_example']
            all_segment_examples.extend(segment_examples)
        
        # Remove duplicates based on name
        unique_examples = {}
        for example in all_segment_examples:
            name = example.metadata.get('name')
            if name and name not in unique_examples:
                unique_examples[name] = example
        
        segment_examples = list(unique_examples.values())
        
        print(f"📊 Found {len(segment_examples)} unique segment examples")
        
        if len(segment_examples) == 0:
            print("❌ No segment examples found")
            return False
        
        # Check metadata structure
        required_fields = ['name', 'description', 'context', 'pred_func', 'category']
        all_valid = True
        
        for i, example in enumerate(segment_examples[:3]):  # Check first 3
            print(f"\n📋 Example {i+1}: {example.metadata.get('name', 'Unknown')}")
            
            for field in required_fields:
                value = example.metadata.get(field, 'MISSING')
                if value == 'MISSING':
                    print(f"   ❌ Missing field: {field}")
                    all_valid = False
                else:
                    print(f"   ✅ {field}: {value}")
        
        # Check if we have the expected examples
        expected_examples = [
            "New Zealand Visitors",
            "Mobile Users"
        ]
        
        found_names = [ex.metadata.get('name') for ex in segment_examples]
        print(f"\n🔍 Checking for expected examples:")
        
        for expected in expected_examples:
            if expected in found_names:
                print(f"   ✅ Found: {expected}")
            else:
                print(f"   ❌ Missing: {expected}")
                all_valid = False
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error testing metadata: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 COMPREHENSIVE TESTING OF INGESTED SEGMENT DATA")
    print("=" * 70)
    print("This test suite verifies that the ingested segment examples")
    print("are working correctly and providing enhanced suggestions.")
    print("\n" + "=" * 70)
    
    tests = [
        ("Vector Database Loading", test_vector_database_loading),
        ("Segment Example Search", test_segment_example_search),
        ("Enhanced Suggestions", test_enhanced_suggestions),
        ("Geographic Queries", test_specific_geographic_queries),
        ("Metadata Structure", test_segment_example_metadata)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🚀 Running: {test_name}")
        print("-" * 50)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The ingested data is working correctly.")
        print("\n🎯 Next Steps:")
        print("   1. Test the web interface with specific queries")
        print("   2. Verify that 'New Zealand' queries work correctly")
        print("   3. Check that relevant examples are displayed")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print(f"\n📅 Test completed at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 