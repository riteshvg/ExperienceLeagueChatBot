#!/usr/bin/env python3
"""
Automated Knowledge Base Refresh System
Keeps Adobe Analytics Chatbot knowledge base current with latest documentation and Stack Overflow content.
"""

import os
import time
import schedule
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kb_refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KnowledgeBaseRefresher:
    def __init__(self, config_file="refresh_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.last_refresh_file = "last_refresh.json"
        
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "refresh_schedule": {
                "adobe_docs": "daily",  # daily, weekly, monthly
                "stackoverflow": "daily",
                "full_rebuild": "weekly"
            },
            "adobe_urls": [
                "https://experienceleague.adobe.com/docs/analytics.html",
                "https://experienceleague.adobe.com/docs/analytics/admin/home",
                "https://experienceleague.adobe.com/docs/analytics/analyze/home",
                "https://experienceleague.adobe.com/docs/analytics/components/home",
                "https://experienceleague.adobe.com/docs/analytics/implementation/home",
                "https://experienceleague.adobe.com/docs/analytics/export/home",
                "https://experienceleague.adobe.com/docs/analytics/integration/home",
                "https://experienceleague.adobe.com/docs/analytics/release-notes/latest",
                "https://experienceleague.adobe.com/docs/analytics/technotes/home"
            ],
            "stackoverflow_tags": [
                "adobe-analytics",
                "adobe-analytics-api", 
                "adobe-analytics-implementation",
                "adobe-analytics-segmentation",
                "adobe-analytics-calculated-metrics",
                "adobe-analytics-workspace",
                "adobe-analytics-reporting"
            ],
            "max_new_docs_per_refresh": 50,
            "auto_restart_app": False,
            "backup_before_refresh": True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def get_last_refresh_time(self):
        """Get the last refresh time for each component"""
        if os.path.exists(self.last_refresh_file):
            try:
                with open(self.last_refresh_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "adobe_docs": None,
            "stackoverflow": None,
            "full_rebuild": None
        }
    
    def update_last_refresh_time(self, component):
        """Update the last refresh time for a component"""
        last_refresh = self.get_last_refresh_time()
        last_refresh[component] = datetime.now().isoformat()
        
        with open(self.last_refresh_file, 'w') as f:
            json.dump(last_refresh, f, indent=2)
    
    def should_refresh(self, component):
        """Check if a component should be refreshed based on schedule"""
        last_refresh = self.get_last_refresh_time()
        last_time = last_refresh.get(component)
        
        if not last_time:
            return True
        
        last_time = datetime.fromisoformat(last_time)
        now = datetime.now()
        
        schedule_type = self.config["refresh_schedule"].get(component, "daily")
        
        if schedule_type == "daily":
            return (now - last_time).days >= 1
        elif schedule_type == "weekly":
            return (now - last_time).days >= 7
        elif schedule_type == "monthly":
            return (now - last_time).days >= 30
        
        return False
    
    def backup_knowledge_base(self):
        """Create backup of current knowledge base"""
        if not self.config["backup_before_refresh"]:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backup_{timestamp}"
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup Adobe docs
            if os.path.exists("adobe_docs"):
                subprocess.run(["cp", "-r", "adobe_docs", f"{backup_dir}/"])
            
            # Backup Stack Overflow docs
            if os.path.exists("stackoverflow_docs"):
                subprocess.run(["cp", "-r", "stackoverflow_docs", f"{backup_dir}/"])
            
            # Backup FAISS index
            if os.path.exists("faiss_index"):
                subprocess.run(["cp", "-r", "faiss_index", f"{backup_dir}/"])
            
            logger.info(f"Knowledge base backed up to {backup_dir}")
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
    
    def refresh_adobe_docs(self):
        """Refresh Adobe documentation"""
        if not self.should_refresh("adobe_docs"):
            logger.info("Adobe docs refresh not needed yet")
            return
        
        logger.info("Starting Adobe docs refresh...")
        
        try:
            # Run the scraper
            result = subprocess.run([
                "python", "scrape.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Adobe docs refresh completed successfully")
                self.update_last_refresh_time("adobe_docs")
            else:
                logger.error(f"Adobe docs refresh failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error refreshing Adobe docs: {e}")
    
    def refresh_stackoverflow(self):
        """Refresh Stack Overflow content"""
        if not self.should_refresh("stackoverflow"):
            logger.info("Stack Overflow refresh not needed yet")
            return
        
        logger.info("Starting Stack Overflow refresh...")
        
        try:
            # Run the Stack Overflow scraper
            result = subprocess.run([
                "python", "stackoverflow_scraper.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Stack Overflow refresh completed successfully")
                self.update_last_refresh_time("stackoverflow")
            else:
                logger.error(f"Stack Overflow refresh failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error refreshing Stack Overflow: {e}")
    
    def rebuild_knowledge_base(self):
        """Rebuild the FAISS knowledge base"""
        if not self.should_refresh("full_rebuild"):
            logger.info("Full rebuild not needed yet")
            return
        
        logger.info("Starting knowledge base rebuild...")
        
        try:
            # Run the ingest script
            result = subprocess.run([
                "python", "ingest.py", "--include-stackoverflow"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Knowledge base rebuild completed successfully")
                self.update_last_refresh_time("full_rebuild")
            else:
                logger.error(f"Knowledge base rebuild failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error rebuilding knowledge base: {e}")
    
    def check_for_new_content(self):
        """Check if there's new content available without downloading"""
        logger.info("Checking for new content...")
        
        try:
            # Check Adobe docs for updates
            for url in self.config["adobe_urls"][:3]:  # Check first 3 URLs
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Look for last modified or updated indicators
                        last_modified = soup.find('meta', {'name': 'last-modified'})
                        if last_modified:
                            logger.info(f"Found last modified: {last_modified.get('content')}")
                except Exception as e:
                    logger.warning(f"Could not check {url}: {e}")
            
            # Check Stack Overflow for new questions
            for tag in self.config["stackoverflow_tags"][:3]:  # Check first 3 tags
                try:
                    api_url = f"https://api.stackexchange.com/2.3/questions?order=desc&sort=activity&tagged={tag}&site=stackoverflow&pagesize=5"
                    response = requests.get(api_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('items'):
                            newest_question = data['items'][0]
                            creation_date = datetime.fromtimestamp(newest_question['creation_date'])
                            if (datetime.now() - creation_date).days < 7:
                                logger.info(f"Found recent questions for tag {tag}")
                except Exception as e:
                    logger.warning(f"Could not check Stack Overflow for {tag}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking for new content: {e}")
    
    def restart_application(self):
        """Restart the Streamlit application if configured"""
        if not self.config["auto_restart_app"]:
            return
        
        logger.info("Restarting application...")
        
        try:
            # Kill existing Streamlit processes
            subprocess.run(["pkill", "-f", "streamlit"], check=False)
            time.sleep(2)
            
            # Start new Streamlit process
            subprocess.Popen([
                "streamlit", "run", "app.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info("Application restarted successfully")
            
        except Exception as e:
            logger.error(f"Error restarting application: {e}")
    
    def run_full_refresh(self):
        """Run a complete refresh cycle"""
        logger.info("Starting full knowledge base refresh cycle...")
        
        # Backup current knowledge base
        self.backup_knowledge_base()
        
        # Refresh content
        self.refresh_adobe_docs()
        self.refresh_stackoverflow()
        
        # Rebuild knowledge base
        self.rebuild_knowledge_base()
        
        # Restart application if configured
        self.restart_application()
        
        logger.info("Full refresh cycle completed")
    
    def run_incremental_refresh(self):
        """Run incremental refresh (only new content)"""
        logger.info("Starting incremental refresh...")
        
        # Check for new content first
        self.check_for_new_content()
        
        # Refresh only if needed
        if self.should_refresh("adobe_docs"):
            self.refresh_adobe_docs()
        
        if self.should_refresh("stackoverflow"):
            self.refresh_stackoverflow()
        
        # Always rebuild after any refresh
        self.rebuild_knowledge_base()
        
        logger.info("Incremental refresh completed")

def main():
    """Main function to run the refresher"""
    refresher = KnowledgeBaseRefresher()
    
    # Parse command line arguments
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "full":
            refresher.run_full_refresh()
        elif command == "incremental":
            refresher.run_incremental_refresh()
        elif command == "adobe":
            refresher.refresh_adobe_docs()
        elif command == "stackoverflow":
            refresher.refresh_stackoverflow()
        elif command == "rebuild":
            refresher.rebuild_knowledge_base()
        elif command == "check":
            refresher.check_for_new_content()
        elif command == "schedule":
            # Set up scheduled refresh
            schedule.every().day.at("02:00").do(refresher.run_incremental_refresh)
            schedule.every().sunday.at("03:00").do(refresher.run_full_refresh)
            
            logger.info("Scheduled refresh started. Press Ctrl+C to stop.")
            
            while True:
                schedule.run_pending()
                time.sleep(60)
        else:
            print("Usage: python auto_refresh.py [full|incremental|adobe|stackoverflow|rebuild|check|schedule]")
    else:
        # Default to incremental refresh
        refresher.run_incremental_refresh()

if __name__ == "__main__":
    main() 