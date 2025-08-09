# Starting Commands for Adobe Chatbot

## Quick Start (if already set up)

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
streamlit run app.py
```

## Full Setup (first time only)

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up Groq API key (create .streamlit/secrets.toml file)
mkdir -p .streamlit
echo 'GROQ_API_KEY = "your_groq_api_key_here"' > .streamlit/secrets.toml

# 4. Scrape documentation (if not already done)
python scrape.py

# 5. Build knowledge base (if not already done)
python ingest.py

# 6. Run the application
streamlit run app.py
```

## Access the Application

The application will be available at: `http://localhost:8501`

## Notes

- Only run `scrape.py` and `ingest.py` for initial setup or when updating documentation
- The `faiss_index/` folder contains the pre-built knowledge base
- Make sure your Groq API key is set in `.streamlit/secrets.toml`
