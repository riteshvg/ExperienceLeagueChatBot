# Knowledge Base Refresh Guide

## 📋 Overview

This guide explains how to use the automated knowledge base refresh system to keep your Adobe Analytics Chatbot current with the latest Adobe documentation and Stack Overflow content.

## 🚀 **Quick Start**

### **1. Install Dependencies**

```bash
# Update requirements with new dependencies
python update_requirements.py

# Install new dependencies
pip install schedule beautifulsoup4
```

### **2. Run Your First Refresh**

```bash
# Run incremental refresh (recommended for first time)
python auto_refresh.py incremental

# Or run full refresh (downloads everything)
python auto_refresh.py full
```

### **3. Set Up Scheduled Refresh**

```bash
# Start scheduled refresh (runs daily at 2 AM, weekly full refresh)
python auto_refresh.py schedule
```

---

## 🔧 **Configuration**

### **refresh_config.json Settings**

The system uses a JSON configuration file to control refresh behavior:

```json
{
  "refresh_schedule": {
    "adobe_docs": "daily", // How often to refresh Adobe docs
    "stackoverflow": "daily", // How often to refresh Stack Overflow
    "full_rebuild": "weekly" // How often to rebuild FAISS index
  },
  "adobe_urls": [
    // List of Adobe Experience League URLs to monitor
  ],
  "stackoverflow_tags": [
    // Stack Overflow tags to monitor for new questions
  ],
  "max_new_docs_per_refresh": 50,
  "auto_restart_app": false, // Auto-restart Streamlit app after refresh
  "backup_before_refresh": true // Create backup before refresh
}
```

### **Schedule Options**

- **`daily`**: Refresh every 24 hours
- **`weekly`**: Refresh every 7 days
- **`monthly`**: Refresh every 30 days

---

## 📝 **Usage Commands**

### **Manual Refresh Commands**

```bash
# Full refresh (downloads all content and rebuilds index)
python auto_refresh.py full

# Incremental refresh (only new content since last refresh)
python auto_refresh.py incremental

# Refresh only Adobe documentation
python auto_refresh.py adobe

# Refresh only Stack Overflow content
python auto_refresh.py stackoverflow

# Rebuild FAISS index only
python auto_refresh.py rebuild

# Check for new content without downloading
python auto_refresh.py check

# Start scheduled refresh (runs continuously)
python auto_refresh.py schedule
```

### **Scheduled Refresh**

The system can run automatically on a schedule:

```bash
# Start scheduled refresh (runs in background)
python auto_refresh.py schedule
```

**Default Schedule:**

- **Daily at 2:00 AM**: Incremental refresh
- **Weekly on Sunday at 3:00 AM**: Full refresh

---

## 📊 **Monitoring & Logs**

### **Log Files**

- **`kb_refresh.log`**: Main log file with all refresh activities
- **`last_refresh.json`**: Tracks when each component was last refreshed

### **Log Levels**

```python
# Available log levels
"INFO"    # General information
"WARNING" # Non-critical issues
"ERROR"   # Critical errors
"DEBUG"   # Detailed debugging info
```

### **Sample Log Output**

```
2024-01-15 02:00:01 - INFO - Starting incremental refresh...
2024-01-15 02:00:02 - INFO - Checking for new content...
2024-01-15 02:00:05 - INFO - Found recent questions for tag adobe-analytics
2024-01-15 02:00:10 - INFO - Starting Adobe docs refresh...
2024-01-15 02:00:45 - INFO - Adobe docs refresh completed successfully
2024-01-15 02:01:00 - INFO - Starting knowledge base rebuild...
2024-01-15 02:01:30 - INFO - Knowledge base rebuild completed successfully
2024-01-15 02:01:31 - INFO - Incremental refresh completed
```

---

## 🔄 **Refresh Types**

### **1. Incremental Refresh**

- **What it does**: Downloads only new content since last refresh
- **When to use**: Daily maintenance, quick updates
- **Time**: 5-15 minutes
- **Command**: `python auto_refresh.py incremental`

### **2. Full Refresh**

- **What it does**: Downloads all content and rebuilds entire index
- **When to use**: Weekly maintenance, after major changes
- **Time**: 30-60 minutes
- **Command**: `python auto_refresh.py full`

### **3. Component-Specific Refresh**

- **Adobe Docs**: `python auto_refresh.py adobe`
- **Stack Overflow**: `python auto_refresh.py stackoverflow`
- **FAISS Index**: `python auto_refresh.py rebuild`

---

## 🛡️ **Backup & Recovery**

### **Automatic Backups**

The system automatically creates backups before each refresh:

```bash
# Backup location
backup_20240115_020000/
├── adobe_docs/
├── stackoverflow_docs/
└── faiss_index/
```

### **Manual Backup**

```bash
# Create manual backup
python auto_refresh.py backup

# Restore from backup
cp -r backup_20240115_020000/adobe_docs/ ./adobe_docs/
cp -r backup_20240115_020000/stackoverflow_docs/ ./stackoverflow_docs/
cp -r backup_20240115_020000/faiss_index/ ./faiss_index/
```

---

## ⚙️ **Advanced Configuration**

### **Customizing Refresh Schedule**

Edit `refresh_config.json`:

```json
{
  "refresh_schedule": {
    "adobe_docs": "weekly", // Change to weekly
    "stackoverflow": "daily", // Keep daily
    "full_rebuild": "monthly" // Change to monthly
  }
}
```

### **Adding New URLs**

Add new Adobe Experience League URLs:

```json
{
  "adobe_urls": [
    "https://experienceleague.adobe.com/docs/analytics.html",
    "https://experienceleague.adobe.com/docs/analytics/admin/home",
    // Add your new URL here
    "https://experienceleague.adobe.com/docs/your-new-url"
  ]
}
```

### **Adding New Stack Overflow Tags**

Add new tags to monitor:

```json
{
  "stackoverflow_tags": [
    "adobe-analytics",
    "adobe-analytics-api",
    // Add your new tag here
    "adobe-analytics-your-new-tag"
  ]
}
```

### **Performance Settings**

Adjust performance parameters:

```json
{
  "performance_settings": {
    "max_concurrent_scrapes": 3, // Number of parallel scrapes
    "request_delay": 1, // Delay between requests (seconds)
    "timeout_seconds": 30 // Request timeout
  }
}
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Refresh Fails with Network Error**

```bash
# Check internet connection
ping experienceleague.adobe.com

# Check if URLs are accessible
curl -I https://experienceleague.adobe.com/docs/analytics.html
```

#### **2. FAISS Index Build Fails**

```bash
# Check available memory
free -h

# Check disk space
df -h

# Rebuild with verbose output
python ingest.py --include-stackoverflow --verbose
```

#### **3. Scheduled Refresh Not Running**

```bash
# Check if process is running
ps aux | grep auto_refresh

# Check logs for errors
tail -f kb_refresh.log

# Restart scheduled refresh
pkill -f auto_refresh
python auto_refresh.py schedule
```

#### **4. Application Not Restarting**

```bash
# Check if auto_restart_app is enabled
grep "auto_restart_app" refresh_config.json

# Manually restart application
pkill -f streamlit
streamlit run app.py
```

### **Debug Mode**

Enable detailed logging:

```python
# Edit auto_refresh.py
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kb_refresh.log'),
        logging.StreamHandler()
    ]
)
```

---

## 📈 **Performance Optimization**

### **Recommended Settings for Different Environments**

#### **Development Environment**

```json
{
  "refresh_schedule": {
    "adobe_docs": "weekly",
    "stackoverflow": "weekly",
    "full_rebuild": "monthly"
  },
  "max_new_docs_per_refresh": 20,
  "auto_restart_app": false
}
```

#### **Production Environment**

```json
{
  "refresh_schedule": {
    "adobe_docs": "daily",
    "stackoverflow": "daily",
    "full_rebuild": "weekly"
  },
  "max_new_docs_per_refresh": 100,
  "auto_restart_app": true,
  "backup_before_refresh": true
}
```

#### **High-Traffic Environment**

```json
{
  "refresh_schedule": {
    "adobe_docs": "daily",
    "stackoverflow": "daily",
    "full_rebuild": "daily"
  },
  "max_new_docs_per_refresh": 200,
  "auto_restart_app": true,
  "performance_settings": {
    "max_concurrent_scrapes": 5,
    "request_delay": 0.5,
    "timeout_seconds": 60
  }
}
```

---

## 🔄 **Integration with CI/CD**

### **GitHub Actions Example**

Create `.github/workflows/kb-refresh.yml`:

```yaml
name: Knowledge Base Refresh

on:
  schedule:
    - cron: '0 2 * * *' # Daily at 2 AM
  workflow_dispatch: # Manual trigger

jobs:
  refresh:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run incremental refresh
        run: |
          python auto_refresh.py incremental

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Auto-refresh knowledge base" || exit 0
          git push
```

### **Docker Integration**

Create `Dockerfile.refresh`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "auto_refresh.py", "schedule"]
```

---

## 📊 **Monitoring Dashboard**

### **Health Check Script**

Create `health_check.py`:

```python
#!/usr/bin/env python3
import json
import os
from datetime import datetime

def check_kb_health():
    """Check knowledge base health"""

    # Check last refresh times
    if os.path.exists("last_refresh.json"):
        with open("last_refresh.json", "r") as f:
            last_refresh = json.load(f)

        for component, timestamp in last_refresh.items():
            if timestamp:
                last_time = datetime.fromisoformat(timestamp)
                days_ago = (datetime.now() - last_time).days
                print(f"✅ {component}: {days_ago} days ago")
            else:
                print(f"❌ {component}: Never refreshed")

    # Check file counts
    adobe_count = len(list(Path("./adobe_docs").glob("*.txt")))
    so_count = len(list(Path("./stackoverflow_docs").glob("*.txt")))

    print(f"📊 Adobe docs: {adobe_count}")
    print(f"📊 Stack Overflow docs: {so_count}")
    print(f"📊 Total docs: {adobe_count + so_count}")

if __name__ == "__main__":
    check_kb_health()
```

---

## 🎯 **Best Practices**

### **1. Schedule Management**

- **Daily**: Use incremental refresh for regular updates
- **Weekly**: Use full refresh for comprehensive updates
- **Monthly**: Review and clean up old content

### **2. Resource Management**

- **Memory**: Monitor memory usage during refresh
- **Disk Space**: Keep backups for 30 days maximum
- **Network**: Use appropriate delays to avoid rate limiting

### **3. Error Handling**

- **Logs**: Monitor logs for errors and warnings
- **Alerts**: Set up alerts for failed refreshes
- **Recovery**: Have backup and recovery procedures

### **4. Security**

- **API Keys**: Store API keys securely
- **Access Control**: Limit access to refresh scripts
- **Backups**: Encrypt sensitive backup data

---

## 📞 **Support**

### **Getting Help**

1. **Check Logs**: Review `kb_refresh.log` for error details
2. **Test Commands**: Run individual refresh commands to isolate issues
3. **Check Configuration**: Verify `refresh_config.json` settings
4. **Monitor Resources**: Check disk space, memory, and network

### **Common Commands Reference**

```bash
# Check system health
python health_check.py

# View recent logs
tail -f kb_refresh.log

# Check configuration
cat refresh_config.json

# Test individual components
python auto_refresh.py check
python auto_refresh.py adobe
python auto_refresh.py stackoverflow
python auto_refresh.py rebuild

# Emergency stop
pkill -f auto_refresh
pkill -f streamlit
```

---

## 📝 **Version History**

- **v1.0**: Initial automated refresh system
- **v1.1**: Added incremental refresh and scheduling
- **v1.2**: Added backup and recovery features
- **v1.3**: Added performance optimization and monitoring

---

_This guide should be updated as the refresh system evolves with new features and improvements._
