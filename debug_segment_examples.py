#!/usr/bin/env python3
"""
Debug Segment Examples in Vector Database

This script investigates why segment examples are not being found correctly.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_segment_examples():
    """Debug the segment examples in the vector database."""
    print("🔍 DEBUGGING SEGMENT EXAMPLES IN VECTOR DATABASE")
    print("=" * 60)
    
    try:
        from app import load_knowledge_base
        
        vectorstore = load_knowledge_base()
        if vectorstore is None:
            print("❌ Failed to load knowledge base")
            return
        
        print(f"✅ Knowledge base loaded successfully")
        print(f"📊 Total documents: {vectorstore.index.ntotal}")
        
        # Test 1: Search for segment examples
        print("\n🔍 Test 1: Search for 'segment examples'")
        results = vectorstore.similarity_search("segment examples", k=5)
        print(f"Found {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"\n📋 Result {i+1}:")
            print(f"   Metadata: {result.metadata}")
            print(f"   Content preview: {result.page_content[:200]}...")
        
        # Test 2: Search for specific examples
        print("\n🔍 Test 2: Search for 'New Zealand'")
        results = vectorstore.similarity_search("New Zealand", k=3)
        print(f"Found {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"\n📋 Result {i+1}:")
            print(f"   Metadata: {result.metadata}")
            print(f"   Content preview: {result.page_content[:200]}...")
        
        # Test 3: Search for mobile users
        print("\n🔍 Test 3: Search for 'mobile users'")
        results = vectorstore.similarity_search("mobile users", k=3)
        print(f"Found {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"\n📋 Result {i+1}:")
            print(f"   Metadata: {result.metadata}")
            print(f"   Content preview: {result.page_content[:200]}...")
        
        # Test 4: Check all metadata types
        print("\n🔍 Test 4: Check all metadata types")
        results = vectorstore.similarity_search("Adobe Analytics", k=20)
        
        metadata_types = {}
        for result in results:
            metadata_type = result.metadata.get('type', 'unknown')
            if metadata_type not in metadata_types:
                metadata_types[metadata_type] = 0
            metadata_types[metadata_type] += 1
        
        print("Metadata types found:")
        for metadata_type, count in metadata_types.items():
            print(f"   {metadata_type}: {count}")
        
        # Test 5: Look for segment examples by content
        print("\n🔍 Test 5: Look for segment examples by content")
        segment_examples = []
        for result in results:
            if 'segment' in result.page_content.lower() and 'example' in result.page_content.lower():
                segment_examples.append(result)
        
        print(f"Found {len(segment_examples)} potential segment examples by content")
        for i, result in enumerate(segment_examples[:3]):
            print(f"\n📋 Potential Example {i+1}:")
            print(f"   Metadata: {result.metadata}")
            print(f"   Content preview: {result.page_content[:300]}...")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_segment_examples() 