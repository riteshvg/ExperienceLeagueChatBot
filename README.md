# Adobe Analytics Q&A Assistant

A comprehensive question-answering system for Adobe Analytics documentation using LangChain, FAISS vector store, and Ollama LLM.

## 🚀 Features

- **Web Scraping**: Automatically discovers and scrapes Adobe Analytics documentation
- **Knowledge Base**: FAISS vector store with 14 documents and 111 chunks
- **LLM Integration**: Uses Ollama with llama3:8b for intelligent responses
- **Web Interface**: Beautiful Streamlit web app for easy interaction
- **Source Attribution**: Shows which documents were used to answer questions

## 📁 Project Structure

```
ChatBotAdobe/
├── scrape.py          # Scrapes Adobe Analytics documentation
├── url_scraper.py     # Discovers working URLs automatically
├── ingest.py          # Builds FAISS knowledge base
├── chatbot.py         # Terminal-based chatbot
├── app.py             # Streamlit web application
├── adobe_docs/        # Scraped documentation files
├── faiss_index/       # FAISS vector store
└── working_urls.txt   # Verified working URLs
```

## 🛠️ Installation

1. **Clone and setup virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Install Ollama:**

```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

3. **Pull the required model:**

```bash
ollama pull llama3:8b
```

## 🔧 Usage

### 1. Build Knowledge Base

```bash
# Discover working URLs
python3 url_scraper.py

# Scrape documentation
python3 scrape.py

# Build knowledge base
python3 ingest.py
```

### 2. Run the Web App

```bash
# Start Ollama (in a separate terminal)
ollama serve

# Run Streamlit app
streamlit run app.py
```

### 3. Use Terminal Chatbot

```bash
python3 chatbot.py
```

## 📊 Knowledge Base Content

The system includes documentation on:

- **Analysis Workspace**: Fundamentals, navigation, collaboration
- **Administration**: User management, report suites, configuration
- **Implementation**: Web SDK, mobile SDK, server-side implementation
- **Components**: Segments, calculated metrics, virtual report suites
- **Export/Import**: Data feeds, warehouse, FTP/SFTP
- **Integrations**: Adobe Experience Cloud integrations
- **Release Notes**: Latest updates and documentation changes
- **Tech Notes**: Technical articles and troubleshooting

## 🎯 Example Questions

- "How do I implement Adobe Analytics?"
- "What is Analysis Workspace?"
- "How do I create segments?"
- "What are the different implementation methods?"
- "How do I export data from Adobe Analytics?"
- "What integrations are available?"

## 🔧 Technical Details

- **Vector Store**: FAISS with all-MiniLM-L6-v2 embeddings
- **LLM**: Ollama with llama3:8b (4.7GB model)
- **Chunking**: 1000 characters with 150 character overlap
- **Retrieval**: Top 3 most relevant chunks per query
- **Web Framework**: Streamlit for the web interface

## 🚨 Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama list

# Start Ollama if not running
ollama serve
```

### Model Not Found

```bash
# Pull the required model
ollama pull llama3:8b
```

### FAISS Index Issues

```bash
# Rebuild the knowledge base
python3 ingest.py
```

## 📈 Performance

- **Documents**: 14 Adobe Analytics documentation pages
- **Chunks**: 111 semantic chunks
- **Response Time**: ~2-5 seconds per query
- **Accuracy**: High relevance with source attribution

## 🤝 Contributing

1. Add new URLs to `scrape.py`
2. Run `url_scraper.py` to discover working URLs
3. Update the knowledge base with `ingest.py`
4. Test with the web app or chatbot

## 📝 License

This project is for educational purposes. Please respect Adobe's terms of service when scraping their documentation.
