#!/bin/bash

echo "🚀 Adobe Experience League Chatbot Deployment Script"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found!"
    exit 1
fi

echo "✅ All files present"

echo ""
echo "🌐 Choose your deployment platform:"
echo "1. Streamlit Cloud (Recommended)"
echo "2. Heroku"
echo "3. Railway"
echo "4. Local deployment only"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📋 Streamlit Cloud Deployment Steps:"
        echo "1. Push your code to GitHub:"
        echo "   git remote add origin <your-github-repo-url>"
        echo "   git push -u origin main"
        echo ""
        echo "2. Go to https://share.streamlit.io"
        echo "3. Connect your GitHub account"
        echo "4. Select this repository"
        echo "5. Set main file path: app.py"
        echo "6. Add secrets in dashboard:"
        echo "   GROQ_API_KEY = your_groq_api_key_here"
        echo "7. Deploy!"
        ;;
    2)
        echo ""
        echo "📋 Heroku Deployment Steps:"
        echo "1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
        echo "2. Login to Heroku: heroku login"
        echo "3. Create app: heroku create your-app-name"
        echo "4. Set environment variables:"
        echo "   heroku config:set GROQ_API_KEY=your_groq_api_key_here"
        echo "5. Deploy: git push heroku main"
        echo "6. Open app: heroku open"
        ;;
    3)
        echo ""
        echo "📋 Railway Deployment Steps:"
        echo "1. Go to https://railway.app"
        echo "2. Connect your GitHub account"
        echo "3. Select this repository"
        echo "4. Set environment variables:"
        echo "   GROQ_API_KEY = your_groq_api_key_here"
        echo "5. Deploy automatically!"
        ;;
    4)
        echo ""
        echo "📋 Local Deployment Steps:"
        echo "1. Install dependencies: pip install -r requirements.txt"
        echo "2. Set up Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
        echo "3. Pull model: ollama pull llama3:8b"
        echo "4. Scrape docs: python scrape.py"
        echo "5. Build KB: python ingest.py"
        echo "6. Run app: streamlit run app.py"
        ;;
    *)
        echo "❌ Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "🎯 Integration with your blog (www.thelearningproject.in):"
echo ""
echo "Option A - Iframe Embed (Simplest):"
echo "Add this HTML to your blog post:"
echo "<iframe src=\"https://your-app-url\" width=\"100%\" height=\"800px\" frameborder=\"0\"></iframe>"
echo ""
echo "Option B - Custom Domain:"
echo "1. Deploy your app"
echo "2. Add custom domain in platform settings"
echo "3. Point subdomain (e.g., chat.thelearningproject.in) to your app"
echo ""
echo "Option C - Full Integration:"
echo "1. Create API endpoints for the chatbot"
echo "2. Build custom frontend matching your blog design"
echo "3. Integrate via AJAX/JavaScript"

echo ""
echo "✅ Deployment script completed!"
echo "📚 Check README.md for detailed instructions" 