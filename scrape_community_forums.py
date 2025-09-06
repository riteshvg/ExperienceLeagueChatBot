#!/usr/bin/env python3
"""
Community Forums and StackOverflow Scraper
Specialized scraper for StackOverflow, Adobe Experience League Communities, and other forum sites
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

def scrape_stackoverflow_questions(url):
    """Scrape StackOverflow question pages"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        content_parts = []
        
        # Extract question title
        title_elem = soup.find('h1', class_='s-post-title')
        if title_elem:
            content_parts.append(f"Question: {title_elem.get_text(strip=True)}")
        
        # Extract question content
        question_elem = soup.find('div', class_='s-prose')
        if question_elem:
            content_parts.append(f"Question Content: {question_elem.get_text(separator=' ', strip=True)}")
        
        # Extract answers
        answers = soup.find_all('div', class_='answer')
        for i, answer in enumerate(answers, 1):
            answer_content = answer.find('div', class_='s-prose')
            if answer_content:
                content_parts.append(f"Answer {i}: {answer_content.get_text(separator=' ', strip=True)}")
        
        # Extract tags
        tags_elem = soup.find('div', class_='post-taglist')
        if tags_elem:
            tags = [tag.get_text(strip=True) for tag in tags_elem.find_all('a', class_='post-tag')]
            content_parts.append(f"Tags: {', '.join(tags)}")
        
        return '\n\n'.join(content_parts) if content_parts else None
        
    except Exception as e:
        print(f"Error scraping StackOverflow question {url}: {e}")
        return None

def scrape_stackoverflow_tag_page(url):
    """Scrape StackOverflow tag listing pages"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        content_parts = []
        
        # Extract page title
        title_elem = soup.find('h1')
        if title_elem:
            content_parts.append(f"Page: {title_elem.get_text(strip=True)}")
        
        # Extract question summaries
        questions = soup.find_all('div', class_='s-post-summary')
        for i, question in enumerate(questions[:20], 1):  # Limit to first 20 questions
            question_title = question.find('h3', class_='s-post-summary--content-title')
            if question_title:
                title_link = question_title.find('a')
                if title_link:
                    content_parts.append(f"Question {i}: {title_link.get_text(strip=True)}")
            
            # Extract question excerpt
            excerpt = question.find('div', class_='s-post-summary--content-excerpt')
            if excerpt:
                content_parts.append(f"Excerpt: {excerpt.get_text(strip=True)}")
            
            # Extract tags
            tags = question.find_all('a', class_='post-tag')
            if tags:
                tag_texts = [tag.get_text(strip=True) for tag in tags]
                content_parts.append(f"Tags: {', '.join(tag_texts)}")
            
            content_parts.append("---")
        
        return '\n\n'.join(content_parts) if content_parts else None
        
    except Exception as e:
        print(f"Error scraping StackOverflow tag page {url}: {e}")
        return None

def scrape_adobe_community(url):
    """Scrape Adobe Experience League Community pages"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        content_parts = []
        
        # Extract page title
        title_elem = soup.find('h1')
        if title_elem:
            content_parts.append(f"Community Page: {title_elem.get_text(strip=True)}")
        
        # Look for discussion threads or posts
        discussions = soup.find_all('div', class_='lia-message-body-content')
        for i, discussion in enumerate(discussions[:15], 1):  # Limit to first 15 discussions
            content_parts.append(f"Discussion {i}: {discussion.get_text(separator=' ', strip=True)}")
        
        # Alternative selectors for community content
        if not discussions:
            posts = soup.find_all('div', class_='lia-content')
            for i, post in enumerate(posts[:15], 1):
                content_parts.append(f"Post {i}: {post.get_text(separator=' ', strip=True)}")
        
        # Look for question/answer pairs
        qa_pairs = soup.find_all('div', class_='lia-question')
        for i, qa in enumerate(qa_pairs[:10], 1):
            content_parts.append(f"Q&A {i}: {qa.get_text(separator=' ', strip=True)}")
        
        return '\n\n'.join(content_parts) if content_parts else None
        
    except Exception as e:
        print(f"Error scraping Adobe Community {url}: {e}")
        return None

def scrape_community_forums():
    """Main function to scrape community forums and StackOverflow"""
    
    # Community URLs to scrape
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
    ]
    
    # Create output directory
    output_dir = Path("adobe_docs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Starting to scrape {len(community_urls)} community forum URLs...")
    print(f"Output directory: {output_dir.absolute()}")
    
    successful_scrapes = 0
    failed_scrapes = 0
    
    for i, url in enumerate(community_urls, 1):
        try:
            print(f"\n[{i}/{len(community_urls)}] Scraping: {url}")
            
            content = None
            
            # Determine scraper based on URL
            if 'stackoverflow.com/questions/' in url and '/tagged/' not in url:
                # Individual StackOverflow question
                content = scrape_stackoverflow_questions(url)
            elif 'stackoverflow.com/questions/tagged/' in url:
                # StackOverflow tag page
                content = scrape_stackoverflow_tag_page(url)
            elif 'experienceleaguecommunities.adobe.com' in url:
                # Adobe Community
                content = scrape_adobe_community(url)
            else:
                print(f"✗ Unknown URL format: {url}")
                failed_scrapes += 1
                continue
            
            if content and len(content.strip()) > 100:  # Only save if we got meaningful content
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
                print(f"✗ No meaningful content found in: {url}")
                failed_scrapes += 1
                
        except Exception as e:
            print(f"✗ Error processing {url}: {e}")
            failed_scrapes += 1
        
        # Add a longer delay for community sites to be respectful
        time.sleep(3)
    
    print(f"\n" + "="*60)
    print(f"Community forums scraping completed!")
    print(f"✅ Successful scrapes: {successful_scrapes}")
    print(f"❌ Failed scrapes: {failed_scrapes}")
    print(f"📁 Content saved to: {output_dir.absolute()}")
    print(f"="*60)

if __name__ == "__main__":
    scrape_community_forums()
