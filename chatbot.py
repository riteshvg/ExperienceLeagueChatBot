#!/usr/bin/env python3
"""
Adobe Analytics Chatbot
A simple chatbot that uses the FAISS knowledge base to answer questions about Adobe Analytics.
"""

import os
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def load_knowledge_base():
    """Load the FAISS knowledge base"""
    index_path = Path("./faiss_index")
    
    if not index_path.exists():
        print("❌ Error: FAISS index not found!")
        print("Please run ingest.py first to build the knowledge base.")
        return None
    
    print("🧠 Loading knowledge base...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    vectorstore = FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)
    print("✅ Knowledge base loaded successfully!")
    return vectorstore

def chat_with_bot():
    """Main chat loop"""
    print("🤖 Adobe Analytics Chatbot")
    print("=" * 50)
    print("Ask me anything about Adobe Analytics implementation!")
    print("Type 'quit' to exit.")
    print("=" * 50)
    
    # Load knowledge base
    vectorstore = load_knowledge_base()
    if vectorstore is None:
        return
    
    while True:
        try:
            # Get user input
            query = input("\n💬 You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Thanks for chatting!")
                break
            
            if not query:
                continue
            
            # Search for relevant documents
            print("🔍 Searching knowledge base...")
            results = vectorstore.similarity_search(query, k=3)
            
            if results:
                print("\n📚 Found relevant information:")
                print("-" * 40)
                
                for i, doc in enumerate(results, 1):
                    print(f"\n📄 Source {i}:")
                    # Extract source URL if available
                    source_url = "Unknown source"
                    if hasattr(doc, 'metadata') and doc.metadata:
                        source_url = doc.metadata.get('source', 'Unknown source')
                    
                    print(f"📍 Source: {source_url}")
                    print(f"📝 Content: {doc.page_content[:300]}...")
                    
                    if len(doc.page_content) > 300:
                        print("   (Content truncated for display)")
            else:
                print("❌ No relevant information found in the knowledge base.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for chatting!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    chat_with_bot() 