#!/usr/bin/env python3
"""
Test script for Stack Overflow integration
"""

import os
from pathlib import Path

def test_stackoverflow_integration():
    """Test the Stack Overflow integration"""
    
    print("🧪 Testing Stack Overflow Integration...")
    
    # Test 1: Check if stackoverflow_scraper.py exists
    if Path("stackoverflow_scraper.py").exists():
        print("✅ stackoverflow_scraper.py exists")
    else:
        print("❌ stackoverflow_scraper.py not found")
    
    # Test 2: Check if ingest.py supports --include-stackoverflow
    with open("ingest.py", "r") as f:
        content = f.read()
        if "--include-stackoverflow" in content:
            print("✅ ingest.py supports --include-stackoverflow flag")
        else:
            print("❌ ingest.py does not support --include-stackoverflow flag")
    
    # Test 3: Check if app.py has Stack Overflow URL handling
    with open("app.py", "r") as f:
        content = f.read()
        if "stackoverflow_" in content and "stackoverflow.com/questions" in content:
            print("✅ app.py has Stack Overflow URL handling")
        else:
            print("❌ app.py missing Stack Overflow URL handling")
    
    # Test 4: Check if stackoverflow_docs directory exists
    if Path("stackoverflow_docs").exists():
        stackoverflow_files = list(Path("stackoverflow_docs").glob("*.txt"))
        print(f"✅ stackoverflow_docs directory exists with {len(stackoverflow_files)} files")
    else:
        print("ℹ️  stackoverflow_docs directory does not exist (will be created when scraping)")
    
    print("\n📋 Usage Instructions:")
    print("1. Run: python stackoverflow_scraper.py")
    print("2. Run: python ingest.py --include-stackoverflow")
    print("3. Start your Streamlit app: streamlit run app.py")
    print("4. Test with Adobe-related questions!")

if __name__ == "__main__":
    test_stackoverflow_integration()
