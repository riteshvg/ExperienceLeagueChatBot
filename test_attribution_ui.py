#!/usr/bin/env python3
"""
Quick test script to verify the attribution system works correctly
before testing the UI integration.
"""

def test_attribution_import():
    """Test if the attribution system can be imported"""
    try:
        from source_attributor import SourceAttributor, quick_attribution
        print("✅ Source attribution system imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Failed to import attribution system: {e}")
        return False

def test_basic_functionality():
    """Test basic attribution functionality"""
    try:
        from source_attributor import SourceAttributor, quick_attribution
        
        # Test basic attribution
        test_source = "stackoverflow_78840462_Distinct_week_segmentation_for_user_clustering"
        
        print(f"\n🧪 Testing source: {test_source}")
        
        # Test quick attribution
        plain_text = quick_attribution(test_source, "plain_text")
        markdown = quick_attribution(test_source, "markdown")
        
        print(f"✅ Plain text: {plain_text}")
        print(f"✅ Markdown: {markdown}")
        
        # Test detailed attribution
        attributor = SourceAttributor()
        metadata = attributor.extract_metadata_from_source(test_source)
        attribution = attributor.generate_attribution(metadata, "detailed")
        
        print(f"✅ Title: {metadata.title}")
        print(f"✅ URL: {metadata.url}")
        print(f"✅ Source Type: {metadata.source_type.value}")
        print(f"✅ License: {metadata.license_type.value}")
        print(f"✅ Compliance: {attribution.compliance_status}")
        
        if attribution.warnings:
            print(f"⚠️ Warnings: {attribution.warnings}")
        if attribution.errors:
            print(f"❌ Errors: {attribution.errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing attribution: {e}")
        return False

def test_adobe_docs():
    """Test Adobe documentation attribution"""
    try:
        from source_attributor import SourceAttributor
        
        test_source = "en_docs_analytics_implementation_home"
        print(f"\n🧪 Testing Adobe docs: {test_source}")
        
        attributor = SourceAttributor()
        metadata = attributor.extract_metadata_from_source(test_source)
        attribution = attributor.generate_attribution(metadata, "markdown")
        
        print(f"✅ Title: {metadata.title}")
        print(f"✅ URL: {metadata.url}")
        print(f"✅ Source Type: {metadata.source_type.value}")
        print(f"✅ License: {metadata.license_type.value}")
        print(f"✅ Compliance: {attribution.compliance_status}")
        print(f"✅ Attribution: {attribution.attribution_markdown}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Adobe docs: {e}")
        return False

def test_bulk_attribution():
    """Test bulk attribution functionality"""
    try:
        from source_attributor import SourceAttributor
        
        test_sources = [
            "stackoverflow_78840462_Distinct_week_segmentation_for_user_clustering",
            "en_docs_analytics_implementation_home",
            "en_browse_analytics"
        ]
        
        print(f"\n🧪 Testing bulk attribution for {len(test_sources)} sources")
        
        attributor = SourceAttributor()
        attributions = attributor.generate_bulk_attribution(test_sources, "detailed")
        
        print(f"✅ Generated {len(attributions)} attributions")
        
        # Count compliance
        compliant = sum(1 for attr in attributions if attr.compliance_status == "compliant")
        warnings = sum(1 for attr in attributions if attr.compliance_status == "compliant_with_warnings")
        non_compliant = sum(1 for attr in attributions if attr.compliance_status == "non_compliant")
        
        print(f"📊 Compliance Summary:")
        print(f"   ✅ Compliant: {compliant}")
        print(f"   ⚠️ With Warnings: {warnings}")
        print(f"   ❌ Non-Compliant: {non_compliant}")
        
        # Test export
        json_report = attributor.export_attribution_report(attributions, "json")
        markdown_report = attributor.export_attribution_report(attributions, "markdown")
        
        print(f"✅ JSON Report: {len(json_report)} characters")
        print(f"✅ Markdown Report: {len(markdown_report)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing bulk attribution: {e}")
        return False

def main():
    """Run all tests"""
    print("🎯 Testing Source Attribution System")
    print("=" * 50)
    
    # Test import
    if not test_attribution_import():
        print("\n❌ Cannot proceed without attribution system")
        return
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality test failed")
        return
    
    # Test Adobe docs
    if not test_adobe_docs():
        print("\n❌ Adobe docs test failed")
        return
    
    # Test bulk attribution
    if not test_bulk_attribution():
        print("\n❌ Bulk attribution test failed")
        return
    
    print("\n🎉 All tests passed! Attribution system is ready for UI integration.")
    print("\n💡 You can now test the attribution features in the Streamlit UI:")
    print("   1. Open the 'Source Attribution Testing & Compliance' expander")
    print("   2. Test individual sources or bulk attribution")
    print("   3. Generate compliance reports")
    print("   4. View attribution status for each source in chat responses")

if __name__ == "__main__":
    main()

