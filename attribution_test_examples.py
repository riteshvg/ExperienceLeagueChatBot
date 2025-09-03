#!/usr/bin/env python3
"""
Attribution Test Examples for SourceAttributor

This file provides real-world examples of Stack Overflow and Adobe documentation
sources that you can test with the source attribution system.
"""

from source_attributor import SourceAttributor, quick_attribution
import json

def test_stack_overflow_examples():
    """Test Stack Overflow attribution examples"""
    print("🔍 Testing Stack Overflow Attribution Examples")
    print("=" * 60)
    
    # Real Stack Overflow examples (based on actual question patterns)
    stackoverflow_examples = [
        "stackoverflow_78840462_Distinct_week_segmentation_for_user_clustering",
        "stackoverflow_78918962_How_to_ignore_quotunused_expressionquot_warning_fr",
        "stackoverflow_79176155_How_can_I_bump_the_Python_package_version_using_uv",
        "stackoverflow_79392777_Adobe_Analytics_API_20_What_is_the_equivalent_endp",
        "stackoverflow_79572869_How_to_hide_api_routes_generated_by_swagger",
        "stackoverflow_79574822_Child_class_entity_is_not_deleting_in_many_to_many",
        "stackoverflow_79620726_Implementing_Referral_Deeplinks_in_iOS_with_Swift",
        "stackoverflow_79682974_GitHub_Copilot_Pro_active_but_VS_Code_says_monthly",
        "stackoverflow_79711708_Is_it_possible_to_use_retries_and_deadletter_queue",
        "stackoverflow_79720046_Combining_multiple_unknown_queries_using_Union"
    ]
    
    attributor = SourceAttributor()
    
    print("📚 Stack Overflow Examples with CC BY-SA 4.0 License:")
    print()
    
    for i, source in enumerate(stackoverflow_examples, 1):
        try:
            # Extract metadata
            metadata = attributor.extract_metadata_from_source(source)
            
            # Generate attributions in different formats
            plain_attr = attributor.generate_attribution(metadata, "plain_text")
            markdown_attr = attributor.generate_attribution(metadata, "markdown")
            detailed_attr = attributor.generate_attribution(metadata, "detailed")
            
            print(f"{i}. Source: {source}")
            print(f"   Title: {metadata.title}")
            print(f"   URL: {metadata.url}")
            print(f"   License: {metadata.license_type.value}")
            print(f"   Compliance: {plain_attr.compliance_status}")
            
            if plain_attr.warnings:
                print(f"   ⚠️ Warnings: {', '.join(plain_attr.warnings)}")
            if plain_attr.errors:
                print(f"   ❌ Errors: {', '.join(plain_attr.errors)}")
            
            print(f"   📝 Plain Text: {plain_attr.attribution_text}")
            print(f"   🔗 Markdown: {markdown_attr.attribution_markdown}")
            print(f"   📋 Detailed: {detailed_attr.attribution_markdown[:100]}...")
            print()
            
        except Exception as e:
            print(f"{i}. Error processing {source}: {str(e)}")
            print()
    
    return stackoverflow_examples

def test_adobe_documentation_examples():
    """Test Adobe documentation attribution examples"""
    print("📖 Testing Adobe Documentation Attribution Examples")
    print("=" * 60)
    
    # Real Adobe documentation examples (based on your existing files)
    adobe_docs_examples = [
        "en_docs_analytics_implementation_home",
        "en_docs_analytics_admin_admin_tools_manage_report_suites_edit_report_suite_report_suite_general_proc",
        "en_docs_analytics_analyze_admin_overview_analytics_overview",
        "en_docs_analytics_analyze_home",
        "en_docs_analytics_components_calculated_metrics_cm_overview",
        "en_docs_analytics_components_home",
        "en_docs_analytics_components_segmentation_seg_overview",
        "en_docs_analytics_export_home",
        "en_docs_analytics_implementation_aep_edge_hit_types",
        "en_docs_analytics_implementation_home",
        "en_docs_analytics_import_home",
        "en_docs_analytics_integration_home",
        "en_docs_analytics_release_notes_doc_updates",
        "en_docs_analytics_release_notes_latest",
        "en_docs_analytics_technotes_home"
    ]
    
    # Adobe browse page examples
    adobe_browse_examples = [
        "en_browse_advertising",
        "en_browse_analytics",
        "en_browse_audience_manager",
        "en_browse_campaign",
        "en_browse_commerce",
        "en_browse_creative_cloud_for_enterprise",
        "en_browse_customer_journey_analytics",
        "en_browse_document_cloud",
        "en_browse_dynamic_media_classic",
        "en_browse_experience_cloud_administration_and_interface_services",
        "en_browse_experience_manager",
        "en_browse_experience_platform_data_collection",
        "en_browse_experience_platform",
        "en_browse_genstudio_for_performance_marketing",
        "en_browse_journey_optimizer_b2b_edition",
        "en_browse_journey_optimizer",
        "en_browse_learning_manager",
        "en_browse_marketo_engage",
        "en_browse_mix_modeler",
        "en_browse_pass",
        "en_browse_real_time_customer_data_platform",
        "en_browse_target",
        "en_browse_workfront"
    ]
    
    attributor = SourceAttributor()
    
    print("📚 Adobe Documentation Examples (Implementation & Components):")
    print()
    
    for i, source in enumerate(adobe_docs_examples[:5], 1):  # Show first 5
        try:
            metadata = attributor.extract_metadata_from_source(source)
            attribution = attributor.generate_attribution(metadata, "detailed")
            
            print(f"{i}. Source: {source}")
            print(f"   Title: {metadata.title}")
            print(f"   URL: {metadata.url}")
            print(f"   License: {metadata.license_type.value}")
            print(f"   Compliance: {attribution.compliance_status}")
            print(f"   📋 Attribution: {attribution.attribution_markdown[:120]}...")
            print()
            
        except Exception as e:
            print(f"{i}. Error processing {source}: {str(e)}")
            print()
    
    print("🌐 Adobe Browse Page Examples:")
    print()
    
    for i, source in enumerate(adobe_browse_examples[:5], 1):  # Show first 5
        try:
            metadata = attributor.extract_metadata_from_source(source)
            attribution = attributor.generate_attribution(metadata, "markdown")
            
            print(f"{i}. Source: {source}")
            print(f"   Title: {metadata.title}")
            print(f"   URL: {metadata.url}")
            print(f"   License: {metadata.license_type.value}")
            print(f"   Compliance: {attribution.compliance_status}")
            print(f"   🔗 Attribution: {attribution.attribution_markdown}")
            print()
            
        except Exception as e:
            print(f"{i}. Error processing {source}: {str(e)}")
            print()
    
    return adobe_docs_examples + adobe_browse_examples

def test_mixed_source_attribution():
    """Test mixed source types with bulk attribution"""
    print("🔄 Testing Mixed Source Attribution")
    print("=" * 60)
    
    # Mixed sources from different types
    mixed_sources = [
        # Stack Overflow examples
        "stackoverflow_78840462_Distinct_week_segmentation_for_user_clustering",
        "stackoverflow_79392777_Adobe_Analytics_API_20_What_is_the_equivalent_endp",
        
        # Adobe documentation examples
        "en_docs_analytics_implementation_home",
        "en_docs_analytics_components_segmentation_seg_overview",
        "en_browse_analytics",
        "en_browse_customer_journey_analytics",
        
        # Generic web examples (for comparison)
        "external_blog_post",
        "github_repository",
        "medium_article"
    ]
    
    attributor = SourceAttributor()
    
    print("📊 Generating Bulk Attribution Report:")
    print()
    
    try:
        # Generate attributions for all sources
        attributions = attributor.generate_bulk_attribution(mixed_sources, "detailed")
        
        # Group by source type
        by_type = {}
        for attr in attributions:
            source_type = attr.source_metadata.source_type.value
            if source_type not in by_type:
                by_type[source_type] = []
            by_type[source_type].append(attr)
        
        # Display grouped results
        for source_type, attrs in by_type.items():
            print(f"🔍 {source_type.replace('_', ' ').title()} Sources ({len(attrs)}):")
            for attr in attrs:
                print(f"   • {attr.source_metadata.title}")
                print(f"     Compliance: {attr.compliance_status}")
                if attr.warnings:
                    print(f"     ⚠️ {', '.join(attr.warnings)}")
                if attr.errors:
                    print(f"     ❌ {', '.join(attr.errors)}")
            print()
        
        # Generate compliance summary
        compliant_count = sum(1 for attr in attributions if attr.compliance_status == "compliant")
        warnings_count = sum(1 for attr in attributions if attr.compliance_status == "compliant_with_warnings")
        non_compliant_count = sum(1 for attr in attributions if attr.compliance_status == "non_compliant")
        
        print(f"📈 Compliance Summary:")
        print(f"   ✅ Compliant: {compliant_count}")
        print(f"   ⚠️ With Warnings: {warnings_count}")
        print(f"   ❌ Non-Compliant: {non_compliant_count}")
        print(f"   📊 Total Sources: {len(attributions)}")
        print()
        
        # Export report
        json_report = attributor.export_attribution_report(attributions, "json")
        print(f"📤 JSON Report Generated ({len(json_report)} characters)")
        
        # Save to file for inspection
        with open("attribution_test_report.json", "w") as f:
            f.write(json_report)
        print("💾 Report saved to 'attribution_test_report.json'")
        
    except Exception as e:
        print(f"❌ Error generating bulk attribution: {str(e)}")
    
    return mixed_sources

def test_quick_attribution():
    """Test quick attribution function"""
    print("⚡ Testing Quick Attribution Function")
    print("=" * 60)
    
    quick_examples = [
        "stackoverflow_78840462_Distinct_week_segmentation_for_user_clustering",
        "en_docs_analytics_implementation_home",
        "en_browse_analytics"
    ]
    
    print("🚀 Quick Attribution Examples:")
    print()
    
    for i, source in enumerate(quick_examples, 1):
        try:
            # Test different formats
            plain_text = quick_attribution(source, "plain_text")
            markdown = quick_attribution(source, "markdown")
            
            print(f"{i}. Source: {source}")
            print(f"   📝 Plain Text: {plain_text}")
            print(f"   🔗 Markdown: {markdown}")
            print()
            
        except Exception as e:
            print(f"{i}. Error with {source}: {str(e)}")
            print()
    
    return quick_examples

def test_compliance_validation():
    """Test compliance validation for different source types"""
    print("⚖️ Testing Compliance Validation")
    print("=" * 60)
    
    test_sources = [
        "stackoverflow_78840462_Distinct_week_segmentation_for_user_clustering",
        "en_docs_analytics_implementation_home",
        "en_browse_analytics",
        "external_blog_post"
    ]
    
    attributor = SourceAttributor()
    
    print("🔍 Individual Source Compliance Validation:")
    print()
    
    for i, source in enumerate(test_sources, 1):
        try:
            metadata = attributor.extract_metadata_from_source(source)
            compliance_status, warnings, errors = attributor._validate_attribution_compliance(metadata)
            
            print(f"{i}. Source: {source}")
            print(f"   Type: {metadata.source_type.value}")
            print(f"   License: {metadata.license_type.value}")
            print(f"   Requires Attribution: {metadata.requires_attribution}")
            print(f"   Required Fields: {', '.join(metadata.attribution_required_fields)}")
            print(f"   Compliance Status: {compliance_status}")
            
            if warnings:
                print(f"   ⚠️ Warnings: {', '.join(warnings)}")
            if errors:
                print(f"   ❌ Errors: {', '.join(errors)}")
            
            print()
            
        except Exception as e:
            print(f"{i}. Error validating {source}: {str(e)}")
            print()
    
    return test_sources

def main():
    """Run all attribution tests"""
    print("🎯 Source Attribution System - Test Examples")
    print("=" * 80)
    print()
    
    # Test Stack Overflow examples
    stackoverflow_sources = test_stack_overflow_examples()
    print()
    
    # Test Adobe documentation examples
    adobe_sources = test_adobe_documentation_examples()
    print()
    
    # Test mixed source attribution
    mixed_sources = test_mixed_source_attribution()
    print()
    
    # Test quick attribution
    quick_sources = test_quick_attribution()
    print()
    
    # Test compliance validation
    validation_sources = test_compliance_validation()
    print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 80)
    print(f"✅ Stack Overflow Examples Tested: {len(stackoverflow_sources)}")
    print(f"✅ Adobe Documentation Examples Tested: {len(adobe_sources)}")
    print(f"✅ Mixed Source Examples Tested: {len(mixed_sources)}")
    print(f"✅ Quick Attribution Examples Tested: {len(quick_sources)}")
    print(f"✅ Compliance Validation Examples Tested: {len(validation_sources)}")
    print()
    print("🎉 All attribution tests completed successfully!")
    print()
    print("💡 Next Steps:")
    print("   1. Review the generated attributions above")
    print("   2. Check the 'attribution_test_report.json' file for detailed results")
    print("   3. Integrate the SourceAttributor into your RAG chatbot")
    print("   4. Test with your actual source data")

if __name__ == "__main__":
    main()

