#!/usr/bin/env python3
"""
Targeted Adobe Analytics Documentation Scraper
Scrapes specific Adobe Analytics documentation URLs provided by the user.
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

def scrape_specific_urls():
    """Scrape the specific URLs provided by the user"""
    
    # Fixed URLs provided by the user
    core_urls = [
        "https://experienceleague.adobe.com/en/docs/analytics/analyze/admin-overview/analytics-overview",
        "https://experienceleague.adobe.com/en/docs/analytics/analyze/home",
        "https://experienceleague.adobe.com/en/docs/analytics/admin/home",
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/home",
        "https://experienceleague.adobe.com/en/docs/analytics/components/home",
        "https://experienceleague.adobe.com/en/docs/analytics/export/home",
        "https://experienceleague.adobe.com/en/docs/analytics/import/home"
    ]

    api_urls = [
        "https://developer.adobe.com/analytics-apis/docs/2.0/",
        "https://developer.adobe.com/analytics-apis/docs/1.4/",
        "https://developer.adobe.com/analytics-apis/docs/2.0/apis/",
        "https://developer.adobe.com/analytics-apis/docs/2.0/guides/endpoints/reports/",
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/apis/using-analysis-workspace-to-build-api-2-requests"
    ]

    implementation_urls = [
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/js/overview",
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/home",
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/vars/overview",
        "https://experienceleague.adobe.com/docs/analytics/implementation/vars/config-vars/configuration-variables.html",
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/vars/page-vars/page-variables",
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/vars/page-vars/dynamic-variables",
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/vars/functions/t-method",
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/vars/plugins/impl-plugins",
        "https://experienceleague.adobe.com/docs/analytics/implementation/js/troubleshooting.html"
    ]

    component_urls = [
        "https://experienceleague.adobe.com/en/docs/analytics/analyze/analysis-workspace/components/analysis-workspace-components",
        "https://experienceleague.adobe.com/en/docs/analytics/components/segmentation/seg-overview",
        "https://experienceleague.adobe.com/en/docs/analytics/components/segmentation/segmentation-workflow/seg-build",
        "https://experienceleague.adobe.com/en/docs/analytics/components/segmentation/segmentation-workflow/seg-publish",
        "https://experienceleague.adobe.com/en/docs/analytics/components/segmentation/seg-containers",
        "https://experienceleague.adobe.com/en/docs/analytics/components/calculated-metrics/cm-overview",
        "https://experienceleague.adobe.com/en/docs/analytics/components/calculated-metrics/calcmetric-workflow/cm-build-metrics",
        "https://experienceleague.adobe.com/en/docs/analytics/components/calculated-metrics/calcmetric-workflow/metrics-with-segments",
        "https://experienceleague.adobe.com/en/docs/analytics/implementation/vars/page-vars/campaign"
    ]

    analysis_urls = [
        "https://experienceleague.adobe.com/docs/analytics/analyze/analysis-workspace/visualizations/fallout/fallout-flow.html",
        "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-workspace/visualizations/fallout/fallout-flow",
        "https://experienceleague.adobe.com/docs/analytics-learn/tutorials/analysis-workspace/analyzing-customer-journeys/multi-dimensional-fallout.html",
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/analysis-workspace/analyzing-customer-journeys/understand-your-data-fallout-flow",
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/analysis-workspace/analyzing-customer-journeys/understanding-and-using-journey-iq-cross-device-analytics",
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/intro-to-analytics/what-can-aa-do-for-me/how-adobe-analysis-workspace-can-change-your-business"
    ]
    
    # Combine all URLs
    all_urls = core_urls + api_urls + implementation_urls + component_urls + analysis_urls
    
    # Create output directory
    output_dir = Path("adobe_docs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Starting to scrape {len(all_urls)} specific Adobe Analytics documentation pages...")
    print(f"Output directory: {output_dir.absolute()}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    successful_scrapes = 0
    failed_scrapes = 0
    
    for i, url in enumerate(all_urls, 1):
        try:
            print(f"\n[{i}/{len(all_urls)}] Scraping: {url}")
            
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
                successful_scrapes += 1
                
            else:
                print(f"✗ No <main> tag found in: {url}")
                failed_scrapes += 1
                
        except requests.RequestException as e:
            print(f"✗ Error fetching {url}: {e}")
            failed_scrapes += 1
        except Exception as e:
            print(f"✗ Error processing {url}: {e}")
            failed_scrapes += 1
        
        # Add a small delay to be respectful to the server
        time.sleep(1)
    
    print(f"\n" + "="*60)
    print(f"Scraping completed!")
    print(f"✅ Successful scrapes: {successful_scrapes}")
    print(f"❌ Failed scrapes: {failed_scrapes}")
    print(f"📁 Content saved to: {output_dir.absolute()}")
    print(f"="*60)

if __name__ == "__main__":
    scrape_specific_urls()
