#!/usr/bin/env python3
"""
Quick Test to See What Segment Examples Are Actually Findable
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    """Quick test to see what's findable."""
    print("🔍 QUICK TEST: What Segment Examples Are Findable?")
    print("=" * 60)
    
    try:
        from app import load_knowledge_base
        
        vectorstore = load_knowledge_base()
        if vectorstore is None:
            print("❌ Failed to load knowledge base")
            return
        
        print(f"✅ Knowledge base loaded with {vectorstore.index.ntotal} documents")
        
        # Test various search terms
        test_terms = [
            "Mobile",
            "mobile",
            "Chrome",
            "chrome",
            "Purchase",
            "purchase",
            "Revenue",
            "revenue",
            "Device",
            "device",
            "Browser",
            "browser",
            "Conversion",
            "conversion"
        ]
        
        found_examples = {}
        
        for term in test_terms:
            results = vectorstore.similarity_search(term, k=3)
            segment_examples = [r for r in results if r.metadata.get('type') == 'segment_example']
            
            if segment_examples:
                found_examples[term] = segment_examples
                print(f"✅ '{term}': Found {len(segment_examples)} examples")
                for example in segment_examples:
                    print(f"   📋 {example.metadata.get('name', 'Unknown')}")
            else:
                print(f"❌ '{term}': No examples found")
        
        print(f"\n📊 Summary: Found examples for {len(found_examples)} search terms")
        
        # Show all unique examples found
        all_examples = set()
        for examples in found_examples.values():
            for example in examples:
                all_examples.add(example.metadata.get('name', 'Unknown'))
        
        print(f"\n🔍 All unique examples found:")
        for example in sorted(all_examples):
            print(f"   📋 {example}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test() 