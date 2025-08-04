# Adobe Experience League Documentation Chatbot

A Streamlit-based chatbot that answers questions about Adobe Experience League solutions using local LLMs and a comprehensive knowledge base.

## 🚀 Quick Deploy Options

### Option 1: Streamlit Cloud (Recommended)

1. **Fork this repository** to your GitHub account
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Connect your GitHub account**
4. **Select this repository**
5. **Set the main file path**: `app.py`
6. **Add secrets** in Streamlit Cloud dashboard:
   ```
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
7. **Deploy!** Your app will be live at `https://your-app-name.streamlit.app`

### Option 2: Heroku

1. **Install Heroku CLI**
2. **Create `Procfile`**:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Option 3: Railway

1. **Connect your GitHub repo** to Railway
2. **Set environment variables**:
   - `GROQ_API_KEY`
3. **Deploy automatically**

## 🔧 Local Setup

### Prerequisites

- Python 3.8+
- Groq API key (required for default cloud LLM)
- Ollama (optional, for local LLM fallback)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ChatBotAdobe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up Groq API key (required)
# Add your Groq API key to .streamlit/secrets.toml:
# GROQ_API_KEY = "your_groq_api_key_here"

# Optional: Set up Ollama for local fallback
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3:8b

# Scrape documentation
python scrape.py

# Build knowledge base
python ingest.py

# Run the application
streamlit run app.py
```

## 📁 Project Structure

```
ChatBotAdobe/
├── app.py                 # Main Streamlit application
├── scrape.py             # Adobe docs scraper
├── ingest.py             # Knowledge base builder
├── requirements.txt      # Python dependencies
├── .streamlit/          # Streamlit configuration
├── adobe_docs/          # Scraped documentation
├── faiss_index/         # Vector store
└── README.md           # This file
```

## 🔑 Environment Variables

- `GROQ_API_KEY`: Your Groq API key for cloud LLM access

## 🌐 Integration with Your Blog

### Option A: Iframe Embed (Simplest)

Add this to your blog post:

```html
<iframe
  src="https://your-app-name.streamlit.app"
  width="100%"
  height="800px"
  frameborder="0"
>
</iframe>
```

### Option B: Custom Domain

1. **Deploy to Streamlit Cloud**
2. **Add custom domain** in Streamlit Cloud settings
3. **Point your subdomain** (e.g., `chat.thelearningproject.in`) to the Streamlit app

### Option C: Full Integration

1. **Deploy backend** to your server
2. **Create API endpoints** for the chatbot
3. **Build custom frontend** that matches your blog design
4. **Integrate via AJAX/JavaScript**

## 🎯 Features

- ✅ Local and cloud LLM support (Ollama + Groq)
- ✅ Comprehensive Adobe documentation knowledge base
- ✅ Real-time token monitoring
- ✅ Auto-hide info boxes
- ✅ Message reactions and feedback
- ✅ Source document linking
- ✅ Follow-up question suggestions
- ✅ Response time tracking
- ✅ Copy to clipboard functionality

## 🔒 Security Notes

- Keep your API keys secure
- Use environment variables for sensitive data
- Consider rate limiting for public deployments
- Monitor usage and costs

## 📊 Performance Tips

- Use Groq for faster responses
- Consider caching for frequently asked questions
- Monitor memory usage with large knowledge bases
- Optimize chunk sizes for your use case

## 🆘 Troubleshooting

- **Ollama not connecting**: Ensure `ollama serve` is running
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Knowledge base errors**: Re-run `python ingest.py`
- **Deployment issues**: Check Streamlit Cloud logs

## 📞 Support

For deployment help, check:

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Heroku Documentation](https://devcenter.heroku.com/)
- [Railway Documentation](https://docs.railway.app/)
