#!/usr/bin/env python3
"""
Ingest Segment Examples into Vector Database

This script loads the segment examples from segmentexamples.json and ingests them
into the FAISS vector database for better segment creation suggestions.
"""

import sys
import os
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_segment_examples():
    """Load segment examples from the JSON file."""
    try:
        with open('segmentexamples.json', 'r', encoding='utf-8') as f:
            examples = json.load(f)
        print(f"✅ Loaded {len(examples)} segment examples from segmentexamples.json")
        return examples
    except Exception as e:
        print(f"❌ Error loading segment examples: {e}")
        return None

def create_document_from_example(example, index):
    """Create a document object from a segment example."""
    from langchain.schema import Document
    
    # Create a comprehensive text representation
    name = example.get('name', '')
    description = example.get('description', '')
    rsid = example.get('rsid', '')
    
    # Extract key information from definition
    definition = example.get('definition', {})
    context = definition.get('container', {}).get('context', '')
    pred_func = definition.get('container', {}).get('pred', {}).get('func', '')
    
    # Create metadata
    metadata = {
        'source': f'segment_example_{index}',
        'type': 'segment_example',
        'name': name,
        'description': description,
        'rsid': rsid,
        'context': context,
        'pred_func': pred_func,
        'category': 'adobe_analytics_segment'
    }
    
    # Create content text
    content = f"""
Segment Name: {name}
Description: {description}
Report Suite ID: {rsid}
Context: {context}
Predicate Function: {pred_func}

This is an Adobe Analytics segment example that demonstrates how to create segments for {description.lower()}.
The segment uses {context} context and {pred_func} predicate function.

Example JSON Structure:
{json.dumps(example, indent=2)}

Use this example as a reference when creating similar segments in Adobe Analytics.
"""
    
    return Document(page_content=content, metadata=metadata)

def ingest_segment_examples():
    """Ingest segment examples into the vector database."""
    print("🚀 Starting Segment Examples Ingestion")
    print("=" * 50)
    
    # Load examples
    examples = load_segment_examples()
    if not examples:
        return False
    
    try:
        # Import required modules
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        
        # Check if FAISS index exists
        index_path = Path("./faiss_index")
        if not index_path.exists():
            print("❌ FAISS index not found! Please run ingest.py first to build the knowledge base.")
            return False
        
        print("🧠 Initializing embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print("📚 Loading existing FAISS index...")
        vectorstore = FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)
        print(f"✅ Knowledge base loaded with {vectorstore.index.ntotal} documents")
        
        # Create documents from examples
        print("📝 Creating documents from segment examples...")
        documents = []
        
        for i, example in enumerate(examples):
            doc = create_document_from_example(example, i)
            documents.append(doc)
            print(f"   📋 Created document for: {example.get('name', 'Unknown')}")
        
        # Add documents to vectorstore
        print(f"\n🔗 Adding {len(documents)} documents to vector database...")
        vectorstore.add_documents(documents)
        
        print(f"✅ Successfully ingested {len(documents)} segment examples")
        
        # Save the updated vectorstore
        print("💾 Saving updated vector database...")
        vectorstore.save_local("faiss_index")
        
        print("🎉 Segment examples ingestion completed successfully!")
        print(f"📊 Total documents in database: {vectorstore.index.ntotal}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run the ingestion process."""
    print("🔧 SEGMENT EXAMPLES INGESTION TOOL")
    print("=" * 60)
    print("This tool will load segment examples from segmentexamples.json")
    print("and ingest them into the FAISS vector database for better")
    print("segment creation suggestions in the application.")
    print("\n" + "=" * 60)
    
    success = ingest_segment_examples()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Restart the main application")
        print("   2. Test segment creation with specific queries")
        print("   3. Verify that suggestions are now more relevant")
        print("   4. Check that geographic locations are correctly detected")
    else:
        print("\n❌ Ingestion failed. Check the errors above.")
    
    print(f"\n📅 Process completed at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 