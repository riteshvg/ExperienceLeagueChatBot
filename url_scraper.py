#!/usr/bin/env python3
"""
Adobe Analytics URL Scraper
Discovers working Adobe Analytics documentation URLs from the main documentation page.
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
from pathlib import Path

def discover_analytics_urls():
    """Discover working Adobe Analytics documentation URLs"""
    base_url = "https://experienceleague.adobe.com/en/docs/analytics"
    
    print(f"🔍 Discovering Adobe Analytics documentation URLs from: {base_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    discovered_urls = []
    
    try:
        # Fetch the main documentation page
        response = requests.get(base_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links that contain '/docs/analytics/'
        analytics_links = []
        
        # Look for links in various formats
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/docs/analytics/' in href:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = f"https://experienceleague.adobe.com{href}"
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(base_url, href)
                
                analytics_links.append(full_url)
        
        # Also look for links in data attributes and other places
        for element in soup.find_all(['div', 'span', 'article'], attrs={'data-href': True}):
            href = element.get('data-href')
            if href and '/docs/analytics/' in href:
                if href.startswith('/'):
                    full_url = f"https://experienceleague.adobe.com{href}"
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(base_url, href)
                analytics_links.append(full_url)
        
        # Remove duplicates while preserving order
        unique_urls = []
        seen = set()
        for url in analytics_links:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
        
        print(f"✅ Discovered {len(unique_urls)} unique Adobe Analytics documentation URLs")
        
        # Test each URL to see if it's accessible
        print("\n🧪 Testing URLs for accessibility...")
        working_urls = []
        
        for i, url in enumerate(unique_urls, 1):
            try:
                print(f"[{i}/{len(unique_urls)}] Testing: {url}")
                test_response = requests.head(url, headers=headers, timeout=10)
                if test_response.status_code == 200:
                    working_urls.append(url)
                    print(f"✅ Working: {url}")
                else:
                    print(f"❌ Failed ({test_response.status_code}): {url}")
            except Exception as e:
                print(f"❌ Error testing {url}: {e}")
        
        print(f"\n🎉 Found {len(working_urls)} working URLs out of {len(unique_urls)} discovered")
        
        # Save working URLs to a file
        if working_urls:
            output_file = Path("working_urls.txt")
            with open(output_file, 'w') as f:
                for url in working_urls:
                    f.write(f'"{url}",\n')
            print(f"💾 Saved working URLs to: {output_file.absolute()}")
        
        return working_urls
        
    except Exception as e:
        print(f"❌ Error discovering URLs: {e}")
        return []

def main():
    """Main function"""
    working_urls = discover_analytics_urls()
    
    if working_urls:
        print(f"\n📋 Working URLs found:")
        for i, url in enumerate(working_urls, 1):
            print(f"{i:2d}. {url}")
    else:
        print("\n❌ No working URLs found. You may need to manually verify some URLs.")

if __name__ == "__main__":
    main() 