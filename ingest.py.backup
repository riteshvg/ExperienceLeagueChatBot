#!/usr/bin/env python3
"""
Adobe Analytics Knowledge Base Builder
Builds a knowledge base from scraped Adobe Analytics documentation using LangChain.
"""

import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def build_knowledge_base():
    """Build a knowledge base from Adobe Analytics documentation"""
    
    print("🔍 Building Adobe Analytics Knowledge Base...")
    
    # Define paths
    docs_path = Path("./adobe_docs")
    index_path = Path("./faiss_index")
    
    # Check if adobe_docs folder exists
    if not docs_path.exists():
        print(f"❌ Error: {docs_path} folder not found!")
        print("Please run scrape.py first to create the documentation files.")
        return
    
    # Check if there are .txt files in the folder
    txt_files = list(docs_path.glob("*.txt"))
    if not txt_files:
        print(f"❌ Error: No .txt files found in {docs_path}")
        print("Please run scrape.py first to create the documentation files.")
        return
    
    print(f"📁 Found {len(txt_files)} text files in {docs_path}")
    
    try:
        # Step 1: Load documents using DirectoryLoader
        print("\n📖 Loading documents...")
        loader = DirectoryLoader(
            path=str(docs_path),
            glob="**/*.txt",
            show_progress=True
        )
        documents = loader.load()
        print(f"✅ Loaded {len(documents)} documents")
        
        # Step 2: Split documents into chunks
        print("\n✂️  Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Step 3: Initialize embeddings
        print("\n🧠 Initializing embeddings with all-MiniLM-L6-v2...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ Embeddings initialized")
        
        # Step 4: Create FAISS vector store
        print("\n🔍 Creating FAISS vector store...")
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )
        print("✅ FAISS vector store created")
        
        # Step 5: Save the index locally
        print(f"\n💾 Saving FAISS index to {index_path}...")
        vectorstore.save_local(str(index_path))
        print("✅ FAISS index saved successfully!")
        
        # Print summary
        print(f"\n🎉 Knowledge base built successfully!")
        print(f"📊 Summary:")
        print(f"   - Documents loaded: {len(documents)}")
        print(f"   - Chunks created: {len(chunks)}")
        print(f"   - Index saved to: {index_path.absolute()}")
        print(f"   - Embedding model: all-MiniLM-L6-v2")
        
        # Test the index
        print(f"\n🧪 Testing the knowledge base...")
        test_query = "Adobe Analytics implementation"
        results = vectorstore.similarity_search(test_query, k=2)
        print(f"✅ Test query '{test_query}' returned {len(results)} results")
        
    except Exception as e:
        print(f"❌ Error building knowledge base: {e}")
        raise

if __name__ == "__main__":
    build_knowledge_base()
