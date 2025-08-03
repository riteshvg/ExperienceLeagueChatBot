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
    
    # List of diverse Adobe Analytics documentation URLs to scrape
    urls = [
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
        "https://experienceleague.adobe.com/en/docs/analytics/release-notes/doc-updates"
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