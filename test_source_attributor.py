#!/usr/bin/env python3
"""
Test Suite for SourceAttributor Class

This module provides comprehensive testing for the SourceAttributor class,
demonstrating its capabilities and validating functionality.
"""

import unittest
from source_attributor import (
    SourceAttributor, 
    SourceMetadata, 
    SourceType, 
    LicenseType,
    AttributionResult,
    create_source_attributor,
    quick_attribution
)


class TestSourceAttributor(unittest.TestCase):
    """Test cases for SourceAttributor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.attributor = SourceAttributor()
        
        # Test source examples
        self.stackoverflow_source = "stackoverflow_12345_how_to_implement_adobe_analytics"
        self.adobe_docs_source = "en_docs_analytics_implementation_home"
        self.adobe_browse_source = "en_browse_analytics"
        self.generic_source = "generic_web_source"
        self.unknown_source = "unknown_format_source"
    
    def test_source_type_identification(self):
        """Test source type identification"""
        print("\n🔍 Testing source type identification...")
        
        # Test Stack Overflow identification
        source_type = self.attributor.identify_source_type(self.stackoverflow_source)
        self.assertEqual(source_type, SourceType.STACK_OVERFLOW)
        print(f"✅ Stack Overflow: {self.stackoverflow_source} -> {source_type.value}")
        
        # Test Adobe docs identification
        source_type = self.attributor.identify_source_type(self.adobe_docs_source)
        self.assertEqual(source_type, SourceType.ADOBE_DOCS)
        print(f"✅ Adobe Docs: {self.adobe_docs_source} -> {source_type.value}")
        
        # Test Adobe browse identification
        source_type = self.attributor.identify_source_type(self.adobe_browse_source)
        self.assertEqual(source_type, SourceType.ADOBE_DOCS)
        print(f"✅ Adobe Browse: {self.adobe_browse_source} -> {source_type.value}")
        
        # Test generic web identification
        source_type = self.attributor.identify_source_type(self.generic_source)
        self.assertEqual(source_type, SourceType.GENERIC_WEB)
        print(f"✅ Generic Web: {self.generic_source} -> {source_type.value}")
    
    def test_metadata_extraction(self):
        """Test metadata extraction from sources"""
        print("\n📊 Testing metadata extraction...")
        
        # Test Stack Overflow metadata
        metadata = self.attributor.extract_metadata_from_source(self.stackoverflow_source)
        self.assertEqual(metadata.source_type, SourceType.STACK_OVERFLOW)
        self.assertEqual(metadata.license_type, LicenseType.CC_BY_SA_4_0)
        self.assertTrue(metadata.requires_attribution)
        self.assertIn("title", metadata.attribution_required_fields)
        self.assertIn("author", metadata.attribution_required_fields)
        self.assertIn("url", metadata.attribution_required_fields)
        self.assertIn("license_type", metadata.attribution_required_fields)
        print(f"✅ Stack Overflow metadata: {metadata.title} -> {metadata.url}")
        
        # Test Adobe docs metadata
        metadata = self.attributor.extract_metadata_from_source(self.adobe_docs_source)
        self.assertEqual(metadata.source_type, SourceType.ADOBE_DOCS)
        self.assertEqual(metadata.license_type, LicenseType.ADOBE_PROPRIETARY)
        self.assertTrue(metadata.requires_attribution)
        print(f"✅ Adobe docs metadata: {metadata.title} -> {metadata.url}")
        
        # Test generic web metadata
        metadata = self.attributor.extract_metadata_from_source(self.generic_source)
        self.assertEqual(metadata.source_type, SourceType.GENERIC_WEB)
        self.assertEqual(metadata.license_type, LicenseType.UNKNOWN)
        self.assertFalse(metadata.requires_attribution)
        print(f"✅ Generic web metadata: {metadata.title} -> {metadata.url}")
    
    def test_title_generation(self):
        """Test title generation from source identifiers"""
        print("\n📝 Testing title generation...")
        
        # Test Stack Overflow title
        title = self.attributor._generate_title_from_source(self.stackoverflow_source)
        self.assertIn("Stack Overflow Question", title)
        print(f"✅ Stack Overflow title: {title}")
        
        # Test Adobe docs title
        title = self.attributor._generate_title_from_source(self.adobe_docs_source)
        self.assertIn("Analytics Implementation Home", title)
        print(f"✅ Adobe docs title: {title}")
        
        # Test Adobe browse title
        title = self.attributor._generate_title_from_source(self.adobe_browse_source)
        self.assertIn("Analytics", title)
        print(f"✅ Adobe browse title: {title}")
        
        # Test generic title
        title = self.attributor._generate_title_from_source(self.generic_source)
        self.assertIn("Generic Web Source", title)
        print(f"✅ Generic title: {title}")
    
    def test_url_generation(self):
        """Test URL generation from source identifiers"""
        print("\n🌐 Testing URL generation...")
        
        # Test Stack Overflow URL
        url = self.attributor._generate_url_from_source(self.stackoverflow_source, SourceType.STACK_OVERFLOW)
        self.assertIn("stackoverflow.com/questions/12345", url)
        print(f"✅ Stack Overflow URL: {url}")
        
        # Test Adobe docs URL
        url = self.attributor._generate_url_from_source(self.adobe_docs_source, SourceType.ADOBE_DOCS)
        self.assertIn("experienceleague.adobe.com", url)
        self.assertIn("analytics/implementation/home", url)
        print(f"✅ Adobe docs URL: {url}")
        
        # Test Adobe browse URL
        url = self.attributor._generate_url_from_source(self.adobe_browse_source, SourceType.ADOBE_DOCS)
        self.assertIn("experienceleague.adobe.com", url)
        self.assertIn("browse/analytics", url)
        print(f"✅ Adobe browse URL: {url}")
    
    def test_attribution_generation(self):
        """Test attribution generation in different formats"""
        print("\n📋 Testing attribution generation...")
        
        # Test Stack Overflow attribution
        metadata = self.attributor.extract_metadata_from_source(self.stackoverflow_source)
        attribution = self.attributor.generate_attribution(metadata, "plain_text")
        
        self.assertIsInstance(attribution, AttributionResult)
        self.assertIn("Stack Overflow", attribution.attribution_text)
        self.assertIn("CC BY-SA 4.0", attribution.attribution_text)
        # Stack Overflow without author is non_compliant due to missing required fields
        self.assertEqual(attribution.compliance_status, "non_compliant")
        print(f"✅ Stack Overflow attribution: {attribution.attribution_text}")
        
        # Test Adobe docs attribution
        metadata = self.attributor.extract_metadata_from_source(self.adobe_docs_source)
        attribution = self.attributor.generate_attribution(metadata, "markdown")
        
        self.assertIsInstance(attribution, AttributionResult)
        self.assertIn("Adobe Inc.", attribution.attribution_markdown)
        self.assertEqual(attribution.compliance_status, "compliant")
        print(f"✅ Adobe docs attribution: {attribution.attribution_markdown}")
        
        # Test detailed format
        attribution = self.attributor.generate_attribution(metadata, "detailed")
        self.assertIn("**Source:**", attribution.attribution_markdown)
        self.assertIn("**Platform:**", attribution.attribution_markdown)
        print(f"✅ Detailed attribution format: {attribution.attribution_markdown[:100]}...")
    
    def test_bulk_attribution(self):
        """Test bulk attribution generation"""
        print("\n📚 Testing bulk attribution...")
        
        sources = [self.stackoverflow_source, self.adobe_docs_source, self.generic_source]
        attributions = self.attributor.generate_bulk_attribution(sources, "plain_text")
        
        self.assertEqual(len(attributions), 3)
        self.assertIsInstance(attributions[0], AttributionResult)
        
        print(f"✅ Bulk attribution generated for {len(attributions)} sources")
        for i, attr in enumerate(attributions):
            print(f"   {i+1}. {attr.attribution_text}")
    
    def test_export_formats(self):
        """Test export functionality in different formats"""
        print("\n📤 Testing export formats...")
        
        sources = [self.stackoverflow_source, self.adobe_docs_source]
        attributions = self.attributor.generate_bulk_attribution(sources)
        
        # Test JSON export
        json_export = self.attributor.export_attribution_report(attributions, "json")
        self.assertIsInstance(json_export, str)
        self.assertIn("stackoverflow", json_export.lower())
        print(f"✅ JSON export: {len(json_export)} characters")
        
        # Test Markdown export
        markdown_export = self.attributor.export_attribution_report(attributions, "markdown")
        self.assertIsInstance(markdown_export, str)
        self.assertIn("# Source Attribution Report", markdown_export)
        print(f"✅ Markdown export: {len(markdown_export)} characters")
        
        # Test plain text export
        text_export = self.attributor.export_attribution_report(attributions, "plain_text")
        self.assertIsInstance(text_export, str)
        self.assertIn("SOURCE ATTRIBUTION REPORT", text_export)
        print(f"✅ Plain text export: {len(text_export)} characters")
    
    def test_license_compliance(self):
        """Test license compliance validation"""
        print("\n⚖️ Testing license compliance...")
        
        # Test CC BY-SA 4.0 compliance
        metadata = self.attributor.extract_metadata_from_source(self.stackoverflow_source)
        compliance_status, warnings, errors = self.attributor._validate_attribution_compliance(metadata)
        
        # Stack Overflow without author is non_compliant due to missing required fields
        self.assertEqual(compliance_status, "non_compliant")
        self.assertIn("author", errors[0])  # Should error about missing author
        # CC BY-SA 4.0 license also generates a warning about missing author
        self.assertEqual(len(warnings), 1)
        self.assertIn("author", warnings[0])
        print(f"✅ CC BY-SA 4.0 compliance: {compliance_status} (errors: {len(errors)}, warnings: {len(warnings)})")
        
        # Test Adobe proprietary compliance
        metadata = self.attributor.extract_metadata_from_source(self.adobe_docs_source)
        compliance_status, warnings, errors = self.attributor._validate_attribution_compliance(metadata)
        
        self.assertEqual(compliance_status, "compliant")
        self.assertEqual(len(warnings), 0)
        self.assertEqual(len(errors), 0)
        print(f"✅ Adobe proprietary compliance: {compliance_status}")
    
    def test_utility_functions(self):
        """Test utility functions"""
        print("\n🔧 Testing utility functions...")
        
        # Test factory function
        attributor = create_source_attributor()
        self.assertIsInstance(attributor, SourceAttributor)
        print("✅ Factory function works")
        
        # Test quick attribution
        attribution_text = quick_attribution(self.stackoverflow_source, "plain_text")
        self.assertIsInstance(attribution_text, str)
        self.assertIn("Stack Overflow", attribution_text)
        print(f"✅ Quick attribution: {attribution_text}")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing error handling...")
        
        # Test empty source
        with self.assertRaises(ValueError):
            self.attributor.identify_source_type("")
        
        # Test invalid source type
        with self.assertRaises(ValueError):
            self.attributor.identify_source_type(None)
        
        # Test invalid export format
        metadata = self.attributor.extract_metadata_from_source(self.adobe_docs_source)
        attribution = self.attributor.generate_attribution(metadata)
        
        with self.assertRaises(ValueError):
            self.attributor.export_attribution_report([attribution], "invalid_format")
        
        print("✅ Error handling works correctly")
    
    def test_integration_scenarios(self):
        """Test real-world integration scenarios"""
        print("\n🌍 Testing integration scenarios...")
        
        # Scenario 1: Mixed source types
        mixed_sources = [
            "stackoverflow_789_how_to_debug_adobe_analytics",
            "en_docs_analytics_components_segmentation_seg_overview",
            "en_browse_customer_journey_analytics",
            "external_blog_post"
        ]
        
        attributions = self.attributor.generate_bulk_attribution(mixed_sources, "markdown")
        
        # Verify we have the right mix
        source_types = [attr.source_metadata.source_type for attr in attributions]
        self.assertIn(SourceType.STACK_OVERFLOW, source_types)
        self.assertIn(SourceType.ADOBE_DOCS, source_types)
        self.assertIn(SourceType.GENERIC_WEB, source_types)
        
        print(f"✅ Mixed source types handled: {[st.value for st in source_types]}")
        
        # Scenario 2: Compliance reporting
        compliant_count = sum(1 for attr in attributions if attr.compliance_status == "compliant")
        warnings_count = sum(1 for attr in attributions if attr.compliance_status == "compliant_with_warnings")
        non_compliant_count = sum(1 for attr in attributions if attr.compliance_status == "non_compliant")
        
        print(f"✅ Compliance report: {compliant_count} compliant, {warnings_count} with warnings, {non_compliant_count} non-compliant")
        
        # Scenario 3: Export for different use cases
        # JSON for API responses
        json_report = self.attributor.export_attribution_report(attributions, "json")
        self.assertIsInstance(json_report, str)
        
        # Markdown for documentation
        markdown_report = self.attributor.export_attribution_report(attributions, "markdown")
        self.assertIsInstance(markdown_report, str)
        
        print("✅ Integration scenarios completed successfully")


def run_demo():
    """Run a demonstration of the SourceAttributor capabilities"""
    print("🎯 SourceAttributor Demo")
    print("=" * 50)
    
    # Create attributor
    attributor = SourceAttributor()
    
    # Demo sources
    demo_sources = [
        "stackoverflow_12345_how_to_implement_adobe_analytics",
        "en_docs_analytics_implementation_home",
        "en_browse_analytics",
        "external_blog_post"
    ]
    
    print("\n📚 Processing demo sources...")
    for source in demo_sources:
        try:
            # Identify source type
            source_type = attributor.identify_source_type(source)
            print(f"\n🔍 Source: {source}")
            print(f"   Type: {source_type.value}")
            
            # Extract metadata
            metadata = attributor.extract_metadata_from_source(source)
            print(f"   Title: {metadata.title}")
            print(f"   URL: {metadata.url}")
            print(f"   License: {metadata.license_type.value}")
            
            # Generate attribution
            attribution = attributor.generate_attribution(metadata, "plain_text")
            print(f"   Attribution: {attribution.attribution_text}")
            print(f"   Compliance: {attribution.compliance_status}")
            
            if attribution.warnings:
                print(f"   ⚠️ Warnings: {', '.join(attribution.warnings)}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n📊 Generating bulk attribution report...")
    try:
        attributions = attributor.generate_bulk_attribution(demo_sources, "markdown")
        report = attributor.export_attribution_report(attributions, "markdown")
        print("✅ Markdown report generated successfully!")
        print(f"Report length: {len(report)} characters")
        
        # Show first few lines
        print("\n📋 Report preview:")
        lines = report.split('\n')[:10]
        for line in lines:
            print(f"   {line}")
        print("   ...")
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
    
    print("\n🎉 Demo completed!")


if __name__ == "__main__":
    # Run demo first
    run_demo()
    
    print("\n" + "=" * 50)
    print("🧪 Running unit tests...")
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
