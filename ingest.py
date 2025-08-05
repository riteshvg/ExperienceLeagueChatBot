#!/usr/bin/env python3
"""
Enhanced Knowledge Base Builder
Builds a knowledge base from Adobe Analytics documentation and Stack Overflow content
"""

import os
import argparse
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def build_knowledge_base(include_stackoverflow: bool = False):
    """
    Build a knowledge base from Adobe Analytics documentation and optionally Stack Overflow
    
    Args:
        include_stackoverflow: Whether to include Stack Overflow content
    """
    
    print("🔍 Building Enhanced Knowledge Base...")
    
    # Define paths
    adobe_docs_path = Path("./adobe_docs")
    stackoverflow_docs_path = Path("./stackoverflow_docs")
    index_path = Path("./faiss_index")
    
    all_documents = []
    
    # Load Adobe documentation
    if adobe_docs_path.exists():
        print(f"\n📖 Loading Adobe documentation from {adobe_docs_path}...")
        adobe_txt_files = list(adobe_docs_path.glob("*.txt"))
        if adobe_txt_files:
            adobe_loader = DirectoryLoader(
                path=str(adobe_docs_path),
                glob="**/*.txt",
                show_progress=True
            )
            adobe_docs = adobe_loader.load()
            all_documents.extend(adobe_docs)
            print(f"✅ Loaded {len(adobe_docs)} Adobe documents")
        else:
            print("⚠️  No Adobe documentation files found")
    else:
        print("⚠️  Adobe docs folder not found")
    
    # Load Stack Overflow content if requested
    if include_stackoverflow and stackoverflow_docs_path.exists():
        print(f"\n📖 Loading Stack Overflow content from {stackoverflow_docs_path}...")
        stackoverflow_txt_files = list(stackoverflow_docs_path.glob("*.txt"))
        if stackoverflow_txt_files:
            stackoverflow_loader = DirectoryLoader(
                path=str(stackoverflow_docs_path),
                glob="**/*.txt",
                show_progress=True
            )
            stackoverflow_docs = stackoverflow_loader.load()
            all_documents.extend(stackoverflow_docs)
            print(f"✅ Loaded {len(stackoverflow_docs)} Stack Overflow documents")
        else:
            print("⚠️  No Stack Overflow files found")
    elif include_stackoverflow:
        print("⚠️  Stack Overflow docs folder not found")
    
    if not all_documents:
        print("❌ No documents found to process!")
        return
    
    print(f"\n📊 Total documents to process: {len(all_documents)}")
    
    try:
        # Step 1: Split documents into chunks
        print("\n✂️  Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(all_documents)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Step 2: Initialize embeddings
        print("\n🧠 Initializing embeddings with all-MiniLM-L6-v2...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ Embeddings initialized")
        
        # Step 3: Create FAISS vector store
        print("\n🔍 Creating FAISS vector store...")
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )
        print("✅ FAISS vector store created")
        
        # Step 4: Save the index locally
        print(f"\n💾 Saving FAISS index to {index_path}...")
        vectorstore.save_local(str(index_path))
        print("✅ FAISS index saved successfully!")
        
        # Print summary
        print(f"\n🎉 Knowledge base built successfully!")
        print(f"📊 Summary:")
        print(f"   - Total documents loaded: {len(all_documents)}")
        print(f"   - Chunks created: {len(chunks)}")
        print(f"   - Index saved to: {index_path.absolute()}")
        print(f"   - Embedding model: all-MiniLM-L6-v2")
        if include_stackoverflow:
            print(f"   - Includes Stack Overflow content: ✅")
        else:
            print(f"   - Includes Stack Overflow content: ❌")
        
        # Test the index
        print(f"\n🧪 Testing the knowledge base...")
        test_query = "Adobe Analytics implementation"
        results = vectorstore.similarity_search(test_query, k=2)
        print(f"✅ Test query '{test_query}' returned {len(results)} results")
        
    except Exception as e:
        print(f"❌ Error building knowledge base: {e}")
        raise

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Build knowledge base from Adobe docs and Stack Overflow')
    parser.add_argument('--include-stackoverflow', action='store_true', 
                       help='Include Stack Overflow content in the knowledge base')
    
    args = parser.parse_args()
    
    build_knowledge_base(include_stackoverflow=args.include_stackoverflow)

if __name__ == "__main__":
    main()
