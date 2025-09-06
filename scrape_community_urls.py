#!/usr/bin/env python3
"""
Community and GitHub Content Scraper
Scrapes Adobe Analytics community discussions, StackOverflow, and GitHub repositories
"""

import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urlparse, urljoin
import time
from pathlib import Path
import json

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

def scrape_github_readme(url):
    """Scrape GitHub README content from raw URLs"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error scraping GitHub README {url}: {e}")
        return None

def scrape_community_urls():
    """Scrape community and GitHub URLs"""
    
    # Community URLs
    community_urls = [
        # StackOverflow - Real user problems & solutions
        "https://stackoverflow.com/questions/tagged/adobe-analytics",
        "https://stackoverflow.com/questions/tagged/adobe-analytics?pageSize=50&sort=frequent",
        "https://stackoverflow.com/questions/tagged/adobe-analytics?sort=votes&pageSize=50",
        "https://stackoverflow.com/questions/20643944/questions-about-omniture-sitecatalyst-or-adobe-analytics",
        "https://stackoverflow.com/questions/64904442/how-exactly-does-a-website-connect-to-adobe-analytics",
        
        # Adobe Experience League Community
        "https://experienceleaguecommunities.adobe.com/t5/adobe-analytics-questions/bd-p/adobe-analytics-qanda",
        "https://experienceleaguecommunities.adobe.com/t5/adobe-analytics-discussions/bd-p/adobe-analytics-discussions",
        "https://experienceleaguecommunities.adobe.com/t5/adobe-analytics/ct-p/adobe-analytics-community",
        
        # FAQ and Troubleshooting
        "https://experienceleague.adobe.com/en/docs/analytics/analyze/analysis-workspace/workspace-faq/faq",
        "https://experienceleague.adobe.com/docs/analytics/analyze/analysis-workspace/workspace-faq/error-messages.html",
        "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/administration/key-admin-skills/are-you-asking-the-right-questions"
    ]

    github_urls = [
        # Official Adobe Documentation Repos
        "https://github.com/AdobeDocs/analytics-2.0-apis",
        "https://github.com/AdobeDocs/analytics.en", 
        "https://github.com/AdobeDocs/analytics-1.4-apis",
        "https://adobedocs.github.io/analytics-2.0-apis/",
        
        # Code Examples & SDKs
        "https://github.com/Adobe-Marketing-Cloud/analytics-samples",
        "https://github.com/Adobe-Marketing-Cloud/analytics-realtime-dashboard-example",
        "https://github.com/SDITools/adobe-analytics-v20-rstats",
        "https://github.com/CDCgov/adobeanalyticsr",
        
        # Additional Examples (scrape README and key files)
        "https://raw.githubusercontent.com/AdobeDocs/analytics-2.0-apis/master/README.md",
        "https://raw.githubusercontent.com/Adobe-Marketing-Cloud/analytics-samples/master/README.md",
        "https://raw.githubusercontent.com/CDCgov/adobeanalyticsr/master/README.md"
    ]
    
    # Combine all URLs
    all_urls = community_urls + github_urls
    
    # Create output directory
    output_dir = Path("adobe_docs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Starting to scrape {len(all_urls)} community and GitHub URLs...")
    print(f"Output directory: {output_dir.absolute()}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    successful_scrapes = 0
    failed_scrapes = 0
    
    for i, url in enumerate(all_urls, 1):
        try:
            print(f"\n[{i}/{len(all_urls)}] Scraping: {url}")
            
            # Handle GitHub raw URLs differently
            if url.startswith("https://raw.githubusercontent.com/"):
                content = scrape_github_readme(url)
                if content:
                    filename = create_safe_filename(url)
                    filepath = output_dir / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"Source URL: {url}\n")
                        f.write("=" * 80 + "\n\n")
                        f.write(content)
                    
                    print(f"✓ Saved: {filename}")
                    print(f"  Content length: {len(content)} characters")
                    successful_scrapes += 1
                else:
                    print(f"✗ Failed to scrape GitHub README: {url}")
                    failed_scrapes += 1
                continue
            
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
        time.sleep(2)  # Longer delay for community sites
    
    print(f"\n" + "="*60)
    print(f"Community and GitHub scraping completed!")
    print(f"✅ Successful scrapes: {successful_scrapes}")
    print(f"❌ Failed scrapes: {failed_scrapes}")
    print(f"📁 Content saved to: {output_dir.absolute()}")
    print(f"="*60)

if __name__ == "__main__":
    scrape_community_urls()
