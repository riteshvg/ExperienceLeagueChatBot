#!/usr/bin/env python3
"""
Stack Overflow Scraper for Adobe Documentation Chatbot
Fetches Adobe-related questions and answers from Stack Overflow API
"""

import requests
import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any

class StackOverflowScraper:
    def __init__(self, api_key: str = None):
        """
        Initialize Stack Overflow scraper
        
        Args:
            api_key: Stack Overflow API key (optional, but recommended for higher rate limits)
        """
        self.api_key = api_key
        self.base_url = "https://api.stackexchange.com/2.3"
        self.headers = {
            'User-Agent': 'Adobe-Documentation-Chatbot/1.0'
        }
        
        # Create stackoverflow_docs directory
        self.docs_path = Path("./stackoverflow_docs")
        self.docs_path.mkdir(exist_ok=True)
        
        # Adobe-related tags to search for
        self.adobe_tags = [
            'adobe-analytics',
            'adobe-target',
            'adobe-experience-manager',
            'adobe-campaign',
            'adobe-experience-platform',
            'adobe-audience-manager',
            'adobe-commerce',
            'adobe-journey-optimizer',
            'adobe-customer-journey-analytics',
            'adobe-dynamic-media',
            'adobe-workfront',
            'adobe-creative-cloud',
            'adobe-document-cloud',
            'adobe-marketo',
            'adobe-commerce-cloud',
            'adobe-experience-cloud',
            'adobe-analytics-implementation',
            'adobe-analytics-tracking',
            'adobe-analytics-api',
            'adobe-analytics-segmentation',
            'adobe-analytics-calculated-metrics',
            'adobe-analytics-workspace',
            'adobe-analytics-export',
            'adobe-analytics-import',
            'adobe-analytics-integration',
            'adobe-analytics-admin',
            'adobe-analytics-components',
            'adobe-analytics-release-notes',
            'adobe-analytics-technotes'
        ]
        
        # Additional search terms for broader coverage
        self.search_terms = [
            'Adobe Analytics',
            'Adobe Target',
            'Adobe Experience Manager',
            'Adobe Campaign',
            'Adobe Experience Platform',
            'Adobe Audience Manager',
            'Adobe Commerce',
            'Adobe Journey Optimizer',
            'Adobe Customer Journey Analytics',
            'Adobe Dynamic Media',
            'Adobe Workfront',
            'Adobe Creative Cloud',
            'Adobe Document Cloud',
            'Adobe Marketo',
            'Adobe Commerce Cloud',
            'Adobe Experience Cloud',
            'Adobe Analytics implementation',
            'Adobe Analytics tracking',
            'Adobe Analytics API',
            'Adobe Analytics segmentation',
            'Adobe Analytics calculated metrics',
            'Adobe Analytics workspace',
            'Adobe Analytics export',
            'Adobe Analytics import',
            'Adobe Analytics integration',
            'Adobe Analytics admin',
            'Adobe Analytics components',
            'Adobe Analytics release notes',
            'Adobe Analytics technotes'
        ]

    def search_questions(self, tag: str = None, search_term: str = None, days_back: int = 365) -> List[Dict]:
        """
        Search for questions on Stack Overflow
        
        Args:
            tag: Specific tag to search for
            search_term: Search term to look for
            days_back: How many days back to search
            
        Returns:
            List of question dictionaries
        """
        questions = []
        
        # Calculate date range
        from_date = int((datetime.now() - timedelta(days=days_back)).timestamp())
        
        # Build search parameters
        params = {
            'fromdate': from_date,
            'order': 'desc',
            'sort': 'activity',
            'site': 'stackoverflow',
            'pagesize': 100,  # Maximum allowed
            'filter': 'withbody'  # Include question body
        }
        
        if tag:
            params['tagged'] = tag
        elif search_term:
            params['intitle'] = search_term
        
        try:
            response = requests.get(
                f"{self.base_url}/search/advanced",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            if 'items' in data:
                questions.extend(data['items'])
                
            # Handle pagination if needed
            while 'has_more' in data and data['has_more'] and len(questions) < 1000:
                if 'page' not in params:
                    params['page'] = 2
                else:
                    params['page'] += 1
                
                time.sleep(1)  # Rate limiting
                response = requests.get(
                    f"{self.base_url}/search/advanced",
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                if 'items' in data:
                    questions.extend(data['items'])
                    
        except Exception as e:
            print(f"❌ Error searching questions for {tag or search_term}: {e}")
            
        return questions

    def get_answers(self, question_ids: List[int]) -> Dict[int, List[Dict]]:
        """
        Get answers for specific question IDs
        
        Args:
            question_ids: List of question IDs
            
        Returns:
            Dictionary mapping question_id to list of answers
        """
        answers = {}
        
        # Process in batches of 100 (API limit)
        batch_size = 100
        for i in range(0, len(question_ids), batch_size):
            batch = question_ids[i:i + batch_size]
            
            params = {
                'order': 'desc',
                'sort': 'votes',
                'site': 'stackoverflow',
                'filter': 'withbody',
                'pagesize': 100
            }
            
            # Add question IDs to params
            params['ids'] = ';'.join(map(str, batch))
            
            try:
                response = requests.get(
                    f"{self.base_url}/questions/{';'.join(map(str, batch))}/answers",
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()
                
                data = response.json()
                if 'items' in data:
                    for answer in data['items']:
                        question_id = answer.get('question_id')
                        if question_id not in answers:
                            answers[question_id] = []
                        answers[question_id].append(answer)
                        
            except Exception as e:
                print(f"❌ Error getting answers for batch: {e}")
                
            time.sleep(1)  # Rate limiting
            
        return answers

    def clean_text(self, text: str) -> str:
        """
        Clean HTML and format text content
        
        Args:
            text: Raw HTML text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

    def create_safe_filename(self, title: str, question_id: int) -> str:
        """
        Create a safe filename for saving content
        
        Args:
            title: Question title
            question_id: Stack Overflow question ID
            
        Returns:
            Safe filename
        """
        # Clean the title
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        safe_title = safe_title.strip('_')
        
        # Limit length and add question ID
        if len(safe_title) > 50:
            safe_title = safe_title[:50]
            
        return f"stackoverflow_{question_id}_{safe_title}.txt"

    def save_qa_content(self, question: Dict, answers: List[Dict]) -> str:
        """
        Save question and answers to a text file
        
        Args:
            question: Question dictionary
            answers: List of answer dictionaries
            
        Returns:
            Filename of saved content
        """
        question_id = question.get('question_id', 0)
        title = question.get('title', 'Untitled')
        body = self.clean_text(question.get('body', ''))
        tags = question.get('tags', [])
        score = question.get('score', 0)
        view_count = question.get('view_count', 0)
        answer_count = question.get('answer_count', 0)
        
        # Create filename
        filename = self.create_safe_filename(title, question_id)
        filepath = self.docs_path / filename
        
        # Prepare content
        content = f"""Stack Overflow Question: {title}
Question ID: {question_id}
Score: {score}
Views: {view_count}
Answers: {answer_count}
Tags: {', '.join(tags)}
URL: https://stackoverflow.com/questions/{question_id}

QUESTION:
{body}

"""
        
        # Add answers
        if answers:
            content += "ANSWERS:\n\n"
            for i, answer in enumerate(answers, 1):
                answer_body = self.clean_text(answer.get('body', ''))
                answer_score = answer.get('score', 0)
                answer_id = answer.get('answer_id', 0)
                
                content += f"Answer {i} (Score: {answer_score}, ID: {answer_id}):\n"
                content += f"https://stackoverflow.com/a/{answer_id}\n\n"
                content += f"{answer_body}\n\n"
                content += "-" * 80 + "\n\n"
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return filename

    def scrape_adobe_content(self, max_questions_per_tag: int = 50) -> List[str]:
        """
        Main function to scrape Adobe-related content from Stack Overflow
        
        Args:
            max_questions_per_tag: Maximum questions to fetch per tag
            
        Returns:
            List of saved filenames
        """
        saved_files = []
        total_questions = 0
        
        print("🚀 Starting Stack Overflow scraping for Adobe content...")
        print(f"📁 Saving files to: {self.docs_path}")
        
        # Search by tags
        print("\n🔍 Searching by Adobe-related tags...")
        for tag in self.adobe_tags:
            print(f"  Searching tag: {tag}")
            questions = self.search_questions(tag=tag)
            
            if questions:
                # Get answers for these questions
                question_ids = [q['question_id'] for q in questions[:max_questions_per_tag]]
                answers = self.get_answers(question_ids)
                
                # Save content
                for question in questions[:max_questions_per_tag]:
                    question_answers = answers.get(question['question_id'], [])
                    filename = self.save_qa_content(question, question_answers)
                    saved_files.append(filename)
                    total_questions += 1
                    
                print(f"    ✅ Found {len(questions)} questions, saved {min(len(questions), max_questions_per_tag)}")
            else:
                print(f"    ⚠️  No questions found for tag: {tag}")
                
            time.sleep(2)  # Rate limiting between tags
        
        # Search by terms
        print("\n🔍 Searching by Adobe-related terms...")
        for term in self.search_terms:
            print(f"  Searching term: {term}")
            questions = self.search_questions(search_term=term)
            
            if questions:
                # Get answers for these questions
                question_ids = [q['question_id'] for q in questions[:max_questions_per_tag]]
                answers = self.get_answers(question_ids)
                
                # Save content
                for question in questions[:max_questions_per_tag]:
                    question_answers = answers.get(question['question_id'], [])
                    filename = self.save_qa_content(question, question_answers)
                    saved_files.append(filename)
                    total_questions += 1
                    
                print(f"    ✅ Found {len(questions)} questions, saved {min(len(questions), max_questions_per_tag)}")
            else:
                print(f"    ⚠️  No questions found for term: {term}")
                
            time.sleep(2)  # Rate limiting between terms
        
        print(f"\n🎉 Stack Overflow scraping completed!")
        print(f"📊 Summary:")
        print(f"   - Total questions processed: {total_questions}")
        print(f"   - Files saved: {len(saved_files)}")
        print(f"   - Directory: {self.docs_path.absolute()}")
        
        return saved_files

def main():
    """Main function to run Stack Overflow scraping"""
    
    # Initialize scraper
    scraper = StackOverflowScraper()
    
    # Run scraping
    saved_files = scraper.scrape_adobe_content(max_questions_per_tag=30)
    
    print(f"\n✅ Stack Overflow content saved to: {scraper.docs_path}")
    print(f"📝 Next steps:")
    print(f"   1. Run: python ingest.py --include-stackoverflow")
    print(f"   2. Restart your Streamlit app")
    print(f"   3. Test with Adobe-related questions!")

if __name__ == "__main__":
    main()
