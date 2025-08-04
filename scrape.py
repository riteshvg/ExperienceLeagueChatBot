#!/usr/bin/env python3
"""
Adobe Analytics Documentation Scraper
Scrapes Adobe Analytics documentation and extracts text content from <main> tags.
"""

import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urlparse, urljoin
import time
from pathlib import Path

def create_safe_filename(url):
    """Create a safe filename from URL"""
    parsed = urlparse(url)
    # Remove protocol and domain, keep path
    path = parsed.path.strip('/')
    if not path:
        path = 'index'
    
    # Replace special characters with underscores
    filename = re.sub(r'[^\w\-_.]', '_', path)
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return f"{filename}.txt"

def scrape_adobe_docs():
    """Main function to scrape Adobe Analytics documentation"""
    
    # Comprehensive list of Adobe Experience League documentation URLs to scrape
    urls = [
        # Core Analytics Documentation
        "https://experienceleague.adobe.com/en/docs/analytics/analyze/admin-overview/analytics-overview",
        "https://experienceleague.adobe.com/en/docs/analytics/analyze/home",
        "https://experienceleague.adobe.com/en/docs/analytics/admin/home",
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/home",
        "https://experienceleague.adobe.com/en/docs/analytics/components/home",
        "https://experienceleague.adobe.com/en/docs/analytics/export/home",
        "https://experienceleague.adobe.com/en/docs/analytics/import/home",
        "https://experienceleague.adobe.com/en/docs/analytics/integration/home",
        "https://experienceleague.adobe.com/en/docs/analytics/technotes/home",
        "https://experienceleague.adobe.com/en/docs/analytics/release-notes/latest",
        "https://experienceleague.adobe.com/en/docs/analytics/release-notes/doc-updates",
        
        # Analytics Platform and CJA
        "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-overview/cja-b2c-overview/data-analysis-ai",
        "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-workspace/attribution/algorithmic",
        "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-workspace/attribution/best-practices",
        "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-workspace/attribution/models",
        "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-workspace/attribution/overview",
        
        # Customer Journey Analytics
        "https://experienceleague.adobe.com/en/docs/customer-journey-analytics",
        "https://experienceleague.adobe.com/en/docs/customer-journey-analytics-learn/tutorials/analysis-workspace/workspace-projects/analysis-workspace-overview",
        "https://experienceleague.adobe.com/en/docs/customer-journey-analytics-learn/tutorials/cja-basics/what-is-customer-journey-analytics",
        "https://experienceleague.adobe.com/en/docs/customer-journey-analytics-learn/tutorials/overview",
        
        # Analytics Learn Tutorials
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/administration/key-admin-skills/translating-adobe-analytics-technical-language",
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/analysis-use-cases/setting-up-in-market-zip-code-analysis-use-case",
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/analysis-workspace/building-freeform-tables/row-and-column-settings-in-freeform-tables",
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/exporting/report-builder/upgrade-and-reschedule-workbooks",
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/overview",
        
        # Analytics Admin Tools
        "https://experienceleague.adobe.com/en/docs/analytics/admin/admin-tools/manage-report-suites/edit-report-suite/report-suite-general/processing-rules/pr-copy",
        "https://experienceleague.adobe.com/en/docs/analytics/admin/admin-tools/manage-report-suites/edit-report-suite/report-suite-general/processing-rules/pr-interface",
        "https://experienceleague.adobe.com/en/docs/analytics/admin/admin-tools/manage-report-suites/edit-report-suite/report-suite-general/processing-rules/pr-use-cases",
        
        # Analytics Implementation
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/aep-edge/hit-types",
        
        # Blueprints and Architecture
        "https://experienceleague.adobe.com/en/docs/blueprints-learn/architecture/architecture-overview/experience-cloud",
        "https://experienceleague.adobe.com/en/docs/blueprints-learn/architecture/architecture-overview/platform-applications",
        "https://experienceleague.adobe.com/en/docs/blueprints-learn/architecture/customer-journey-analytics/cja-ajo",
        "https://experienceleague.adobe.com/en/docs/blueprints-learn/architecture/customer-journey-analytics/cja-rtcdp",
        
        # Certification
        "https://experienceleague.adobe.com/en/docs/certification/program/technical-certifications/aa/aa-overview",
        "https://experienceleague.adobe.com/en/docs/certification/program/technical-certifications/aem/aem-overview",
        
        # Knowledge Base Articles
        "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-25262",
        "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-26568",
        "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-26635",
        "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-26946",
        "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-16598",
        "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-17254",
        "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-17580",
        "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-20022",
        
        # Home Tutorials and Documentation
        "https://experienceleague.adobe.com/en/docs/home-tutorials",
        "https://experienceleague.adobe.com/en/docs/release-notes/experience-cloud/current",
        
        # Browse Pages
        "https://experienceleague.adobe.com/en/browse/analytics",
        "https://experienceleague.adobe.com/en/browse/advertising",
        "https://experienceleague.adobe.com/en/browse/audience-manager",
        "https://experienceleague.adobe.com/en/browse/campaign",
        "https://experienceleague.adobe.com/en/browse/commerce",
        "https://experienceleague.adobe.com/en/browse/creative-cloud-for-enterprise",
        "https://experienceleague.adobe.com/en/browse/customer-journey-analytics",
        "https://experienceleague.adobe.com/en/browse/document-cloud",
        "https://experienceleague.adobe.com/en/browse/dynamic-media-classic",
        "https://experienceleague.adobe.com/en/browse/experience-cloud-administration-and-interface-services",
        "https://experienceleague.adobe.com/en/browse/experience-manager",
        "https://experienceleague.adobe.com/en/browse/experience-platform",
        "https://experienceleague.adobe.com/en/browse/experience-platform/data-collection",
        "https://experienceleague.adobe.com/en/browse/genstudio-for-performance-marketing",
        "https://experienceleague.adobe.com/en/browse/journey-optimizer",
        "https://experienceleague.adobe.com/en/browse/journey-optimizer-b2b-edition",
        "https://experienceleague.adobe.com/en/browse/learning-manager",
        "https://experienceleague.adobe.com/en/browse/marketo-engage",
        "https://experienceleague.adobe.com/en/browse/mix-modeler",
        "https://experienceleague.adobe.com/en/browse/pass",
        "https://experienceleague.adobe.com/en/browse/real-time-customer-data-platform",
        "https://experienceleague.adobe.com/en/browse/target",
        "https://experienceleague.adobe.com/en/browse/workfront",
        
        # Playlists
        "https://experienceleague.adobe.com/en/playlists/analytics-build-freeform-tables",
        "https://experienceleague.adobe.com/en/playlists/analytics-configure-and-manage-conversion-variables",
        "https://experienceleague.adobe.com/en/playlists/analytics-configure-marketing-channels-to-show-success",
        "https://experienceleague.adobe.com/en/playlists/analytics-configure-report-suite-general-settings-in-adobe-analytics",
        "https://experienceleague.adobe.com/en/playlists/analytics-get-started-with-analysis-workspace",
        "https://experienceleague.adobe.com/en/playlists/analytics-integrate-with-adobe-campaign",
        "https://experienceleague.adobe.com/en/playlists/analytics-use-visualizations-to-tell-your-data-stories",
        "https://experienceleague.adobe.com/en/playlists/customer-journey-analytics-connect-to-data",
        "https://experienceleague.adobe.com/en/playlists/customer-journey-analytics-create-data-views",
        "https://experienceleague.adobe.com/en/playlists/customer-journey-analytics-create-filters-and-cross-channel-visualizations",
        "https://experienceleague.adobe.com/en/playlists/customer-journey-analytics-get-started-foundational-concepts",
        
        # Perspectives
        "https://experienceleague.adobe.com/en/perspectives/building-data-culture-and-a-better-solution-design-reference",
        "https://experienceleague.adobe.com/en/perspectives/create-a-news-and-announcements-project",
        "https://experienceleague.adobe.com/en/perspectives/create-basic-recorded-training-sessions-short-videos",
        "https://experienceleague.adobe.com/en/perspectives/create-standardized-naming-conventions"
    ]
    
    # Create output directory
    output_dir = Path("adobe_docs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Starting to scrape {len(urls)} Adobe Analytics documentation pages...")
    print(f"Output directory: {output_dir.absolute()}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for i, url in enumerate(urls, 1):
        try:
            print(f"\n[{i}/{len(urls)}] Scraping: {url}")
            
            # Fetch the HTML content
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main content tag
            main_content = soup.find('main')
            
            if main_content:
                # Extract all text from the main content
                text_content = main_content.get_text(separator='\n', strip=True)
                
                # Create filename from URL
                filename = create_safe_filename(url)
                filepath = output_dir / filename
                
                # Save the extracted text to a file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Source URL: {url}\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(text_content)
                
                print(f"✓ Saved: {filename}")
                print(f"  Content length: {len(text_content)} characters")
                
            else:
                print(f"✗ No <main> tag found in: {url}")
                
        except requests.RequestException as e:
            print(f"✗ Error fetching {url}: {e}")
        except Exception as e:
            print(f"✗ Error processing {url}: {e}")
        
        # Add a small delay to be respectful to the server
        time.sleep(1)
    
    print(f"\nScraping completed! Check the '{output_dir}' folder for extracted content.")

if __name__ == "__main__":
    scrape_adobe_docs() 