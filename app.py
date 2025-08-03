#!/usr/bin/env python3
"""
Adobe Analytics Q&A Web App
A Streamlit web application that answers questions about Adobe Analytics using a FAISS knowledge base and Ollama LLM.
"""

import streamlit as st
import os
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Page configuration
st.set_page_config(page_title="Adobe Analytics Bot", layout="wide", page_icon="🤖")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource
def load_knowledge_base():
    """Load the FAISS knowledge base"""
    index_path = Path("./faiss_index")
    
    if not index_path.exists():
        st.error("❌ FAISS index not found! Please run ingest.py first to build the knowledge base.")
        return None
    
    try:
        # Load embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load FAISS vector store
        vectorstore = FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)
        return vectorstore
    except Exception as e:
        st.error(f"❌ Error loading knowledge base: {e}")
        return None

@st.cache_resource
def setup_qa_chain(_vectorstore):
    """Setup the QA chain with Ollama LLM"""
    try:
        # Initialize Ollama LLM
        llm = OllamaLLM(
            model="llama3:8b",  # Using the available model
            temperature=0.1,
            base_url="http://localhost:11434"
        )
        
        # Create prompt template
        prompt_template = """You are a helpful assistant that answers questions about Adobe Analytics based on the provided context.

Context: {context}

Question: {question}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to answer the question, say so. Be helpful and accurate in your response.

Answer:"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=_vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        return qa_chain
    except Exception as e:
        st.error(f"❌ Error setting up QA chain: {e}")
        return None

def main():
    """Main Streamlit app"""
    
    # Header
    st.title("🤖 Adobe Analytics Documentation Bot")
    st.caption("This chatbot is powered by local open-source models and Adobe's official documentation.")
    
    # Sidebar for controls and information
    with st.sidebar:
        st.header("About")
        st.markdown("This POC demonstrates a chatbot built with LangChain and Ollama and powered by Adobe Analytics documentation")
        
        st.markdown("""
        **Tech Stack:**
        - **FAISS Vector Store**: For semantic search
        - **Ollama LLM**: llama3:8b for text generation
        - **Adobe Analytics Docs**: 14 documents with 111 chunks
        - **Streamlit**: For the web app
        - **LangChain**: For the chatbot
        - **Ollama**: For the LLM
        - **HuggingFace**: For the embeddings
        """)
        
        # Check Ollama connection silently (for app functionality)
        try:
            import ollama
            client = ollama.Client(host='http://localhost:11434')
            models = client.list()
            # Connection successful - app will work
        except Exception:
            # Connection failed - app will show error when user tries to ask questions
            pass
        
        # Clear chat button
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Pre-defined question prompts in sidebar
        st.markdown("---")
        st.markdown("**💡 Try asking questions like:**")
        
        # Define the example questions
        example_questions = [
            "What is Adobe Analytics?",
            "How do I implement tracking?",
            "What are calculated metrics?",
            "Explain segmentation",
            "How to export data?",
            "What are the latest features?"
        ]
        
        # Display questions in sidebar
        for i, question in enumerate(example_questions):
            if st.button(f"• {question}", key=f"sidebar_q{i}", help="Click to add this question to chat"):
                # Set the question in session state to be used in chat input
                st.session_state.selected_question = question
                st.rerun()
    
    # Load knowledge base
    with st.spinner("Loading knowledge base..."):
        vectorstore = load_knowledge_base()
    
    if vectorstore is None:
        st.stop()
    
    # Setup QA chain
    with st.spinner("Setting up QA chain..."):
        qa_chain = setup_qa_chain(vectorstore)
    
    if qa_chain is None:
        st.stop()
    
    st.success("✅ Ready to answer questions!")
    
    # Main chat interface
    st.markdown("---")
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    

    
    # Initialize selected question in session state if not exists
    if "selected_question" not in st.session_state:
        st.session_state.selected_question = ""
    
    # Initialize input text in session state if not exists
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
    
    # Initialize processing state if not exists
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    
    # If a question was selected, set it as input text
    if st.session_state.selected_question:
        st.session_state.input_text = st.session_state.selected_question
        st.session_state.selected_question = ""  # Clear the selection
    
    # Show processing message when model is running
    if st.session_state.is_processing:
        st.info("🤔 Processing your question... Please wait.")
        st.markdown("---")
    else:
        # Create a form for the input area (handles Enter key automatically)
        with st.form(key="chat_form", clear_on_submit=True):
            # Create columns for input and button
            input_col, button_col = st.columns([6, 1])
            
            with input_col:
                # Text input with the question pre-filled
                user_input = st.text_input(
                    "Ask a question about Adobe Analytics...",
                    value=st.session_state.input_text,
                    key="chat_input",
                    placeholder="Ask a question about Adobe Analytics... (Press Enter to send)",
                    label_visibility="collapsed"
                )
            
            with button_col:
                # Send button positioned next to input
                send_button = st.form_submit_button("Send", help="Send message")
        
                # Handle sending the message (both button click and Enter key)
        if send_button and user_input.strip():
            prompt = user_input.strip()
            st.session_state.input_text = ""  # Clear the input
            st.session_state.is_processing = True  # Set processing state
            
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Get answer
                        response = qa_chain.invoke({"query": prompt})
                        answer = response["result"]
                        
                        # Display answer
                        st.markdown(answer)
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        # Use an expander for sources
                        with st.expander("View Sources"):
                            st.write("The answer was generated based on the following documents:")
                            if "source_documents" in response:
                                for doc in response["source_documents"]:
                                    # Display the filename from metadata
                                    st.markdown(f"- `{doc.metadata.get('source', 'Unknown')}`")
                            else:
                                st.write("No source documents available.")
                        
                        # Reset processing state after successful response
                        st.session_state.is_processing = False
                                
                    except Exception as e:
                        error_msg = f"❌ Error generating answer: {e}"
                        st.error(error_msg)
                        st.info("Please make sure Ollama is running with the llama3:8b model.")
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        
                        # Reset processing state after error
                        st.session_state.is_processing = False
            
            st.rerun()

if __name__ == "__main__":
    main()
