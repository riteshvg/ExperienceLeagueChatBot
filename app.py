#!/usr/bin/env python3
"""
Adobe Experience League Documentation Chatbot
A Streamlit web application that answers questions about Adobe Experience League solutions using a FAISS knowledge base and Ollama LLM.
"""

import streamlit as st
import os
import time
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Page configuration
st.set_page_config(page_title="Adobe Experience League Documentation Chatbot", layout="wide", page_icon="🤖")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize auto-hide timer
if "page_load_time" not in st.session_state:
    st.session_state.page_load_time = time.time()
    st.session_state.show_info_boxes = True

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
def setup_qa_chain(_vectorstore, provider="Groq (Cloud)"):
    """Setup the QA chain with selected LLM provider"""
    try:
        # Initialize LLM based on provider selection
        if provider == "Groq (Cloud)":
            try:
                # Initialize Groq LLM
                groq_api_key = st.secrets.get("GROQ_API_KEY", "")
                if not groq_api_key:
                    st.error("❌ Groq API key not found. Please add GROQ_API_KEY to Streamlit secrets.")
                    return None
                
                llm = ChatGroq(
                    groq_api_key=groq_api_key,
                    model_name="llama3-8b-8192",
                    temperature=0.1
                )
                
                # Test the connection with a simple call
                try:
                    test_response = llm.invoke("Hello")
                    st.success("✅ Groq connection successful!")
                except Exception as groq_error:
                    if "rate limit" in str(groq_error).lower() or "quota" in str(groq_error).lower():
                        st.error("❌ Groq rate limit exceeded. Please try again later or switch to Ollama.")
                    elif "unauthorized" in str(groq_error).lower() or "invalid" in str(groq_error).lower():
                        st.error("❌ Invalid Groq API key. Please check your API key.")
                    else:
                        st.error(f"❌ Groq connection error: {groq_error}")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error initializing Groq: {e}")
                return None
        else:
            # Initialize Ollama LLM (fallback)
            try:
                llm = OllamaLLM(
                    model="llama3:8b",  # Using the available model
                    temperature=0.1,
                    base_url="http://localhost:11434"
                )
                
                # Test the connection with a simple call
                try:
                    test_response = llm.invoke("Hello")
                    st.success("✅ Ollama connection successful!")
                except Exception as ollama_error:
                    st.error("❌ Ollama connection failed. Please ensure Ollama is running with `ollama serve`")
                    st.info("💡 You can switch to 'Groq (Cloud)' in the sidebar for cloud-based responses.")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error initializing Ollama: {e}")
                return None
        
        # Create prompt template
        prompt_template = """You are a helpful assistant that answers questions about Adobe Experience League solutions based on the provided context.

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

def generate_follow_up_questions(answer, original_question):
    """Generate relevant follow-up questions based on the answer content and original question"""
    
    # Define topic-based follow-up questions
    follow_up_mapping = {
        "analysis workspace": [
            "How do I export data from Analysis Workspace?",
            "How can I schedule Analysis Workspace reports?",
            "What are the different visualization types in Analysis Workspace?",
            "How do I create calculated metrics in Analysis Workspace?",
            "How do I share Analysis Workspace projects?"
        ],
        "calculated metrics": [
            "How do I create calculated metrics?",
            "What are the different types of calculated metrics?",
            "How do I use calculated metrics in segments?",
            "How do I share calculated metrics with my team?",
            "What are the best practices for calculated metrics?"
        ],
        "segmentation": [
            "How do I create segments in Adobe Analytics?",
            "What are the different segment types?",
            "How do I use segments in Analysis Workspace?",
            "How do I share segments with my team?",
            "What are the segment comparison features?"
        ],
        "implementation": [
            "How do I implement Adobe Analytics tracking?",
            "What are the required implementation variables?",
            "How do I validate my implementation?",
            "How do I set up e-commerce tracking?",
            "What are the best practices for implementation?"
        ],
        "export": [
            "How do I export data from Adobe Analytics?",
            "How do I schedule automated exports?",
            "How do I export Analysis Workspace projects?",
            "What are the export limitations?"
        ],
        "admin": [
            "How do I manage user permissions in Adobe Analytics?",
            "How do I set up data governance?",
            "How do I configure report suites?",
            "How do I manage calculated metrics at admin level?",
            "What are the admin best practices?"
        ],
        "integration": [
            "How do I integrate Adobe Analytics with other tools?",
            "How do I connect to Adobe Experience Platform?",
            "How do I set up data connectors?",
            "How do I integrate with Google Analytics?",
            "What are the available API integrations?"
        ]
    }
    
    # Convert to lowercase for matching
    answer_lower = answer.lower()
    question_lower = original_question.lower()
    
    # Find relevant topics based on content
    relevant_topics = []
    
    for topic, questions in follow_up_mapping.items():
        if topic in answer_lower or topic in question_lower:
            relevant_topics.append(topic)
    
    # Always return some questions - either topic-specific or general
    if relevant_topics:
        # Get questions for the most relevant topic
        primary_topic = relevant_topics[0]
        questions = follow_up_mapping[primary_topic]
        
        # Filter out questions that might be too similar to the original question
        filtered_questions = []
        for question in questions:
            # Check if the question is too similar to the original
            similarity_score = sum(word in question_lower for word in question.lower().split())
            if similarity_score < 4:  # Increased threshold to be less restrictive
                filtered_questions.append(question)
        
        # If we filtered out too many, add some back
        if len(filtered_questions) < 2:
            filtered_questions = questions[:4]
        
        return filtered_questions[:4]  # Return up to 4 relevant questions
    else:
        # Use general questions if no specific topics found
        general_questions = [
            "How do I export data from this feature?",
            "What are the best practices for this functionality?",
            "How do I share this with my team?",
            "What are the limitations of this feature?",
            "How do I customize this for my needs?"
        ]
        return general_questions[:4]  # Return 4 general questions

def main():
    """Main Streamlit app"""
    
    # Header
    st.title("🤖 Adobe Experience League Documentation Chatbot")
    st.caption("This chatbot is powered by local open-source models and Adobe's official documentation.")
    
    # Sidebar for controls and information
    with st.sidebar:
        st.header("About")
        st.markdown("This POC demonstrates a chatbot built with LangChain and Ollama and powered by Adobe Experience League documentation")
        
        st.markdown("""
        **Tech Stack:**
        - **FAISS Vector Store**: For semantic search
        - **Ollama LLM**: llama3:8b for text generation
        - **Streamlit**: For the web app
        - **LangChain**: For the chatbot
        - **HuggingFace**: For the embeddings
        """)
        
        # Theme Selection
        
        
        # Apply theme
        
        
        # LLM Provider Selection
        st.markdown("**🤖 LLM Provider:**")
        llm_provider = st.selectbox(
            "Choose your LLM provider:",
            ["Groq (Cloud)", "Ollama (Local)"],
            key="llm_provider"
        )
        
        
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
            st.session_state.show_welcome = True  # Reset welcome message
            st.rerun()
        
        # Pre-defined question prompts in sidebar
        st.markdown("---")
        st.markdown("**💡 Try asking questions like:**")
        
        # Define the example questions
        example_questions = [
            "What is Adobe Analytics?",
            "How do I implement tracking?",
            "What are calculated metrics in Adobe Analytics?",
            "How does Adobe Target work?",
            "How does Adobe Experience Manager work?",
            "What are the latest features in Adobe Analytics?"
        ]
        
        # Display questions in sidebar
        for i, question in enumerate(example_questions):
            if st.button(f"• {question}", key=f"sidebar_q{i}", help="Click to add this question to chat"):
                # Set the question in session state to be used in chat input
                st.session_state.selected_question = question
                st.rerun()
        
        # Usage Statistics
        st.markdown("---")
        st.markdown("**📊 Usage Statistics:**")
        
        # Initialize usage stats if not exists
        if "usage_stats" not in st.session_state:
            st.session_state.usage_stats = {
                "total_questions": 0,
                "total_responses": 0,
                "avg_response_time": 0,
                "last_question_time": None
            }
        
        # Display stats
        st.metric("Questions Asked", st.session_state.usage_stats["total_questions"])
        st.metric("Responses Generated", st.session_state.usage_stats["total_responses"])
        if st.session_state.usage_stats["avg_response_time"] > 0:
            st.metric("Avg Response Time", f"{st.session_state.usage_stats['avg_response_time']:.1f}s")
    
    # Load knowledge base
    with st.spinner("Loading knowledge base..."):
        vectorstore = load_knowledge_base()
    
    if vectorstore is None:
        st.stop()
    
    # Setup QA chain
    with st.spinner("Setting up QA chain..."):
        qa_chain = setup_qa_chain(vectorstore, llm_provider)
    
    if qa_chain is None:
        st.stop()
    
    # Comprehensive info section at the top (auto-hide after 3 seconds)
    current_time = time.time()
    time_since_load = current_time - st.session_state.page_load_time
    
    # Auto-hide after 3 seconds unless manually closed
    if time_since_load > 3 and st.session_state.show_info_boxes:
        st.session_state.show_info_boxes = False
    
    if st.session_state.show_info_boxes:
        with st.container():
            # Show countdown for auto-hide
            remaining_time = max(0, 3 - time_since_load)
            if remaining_time > 0:
                st.caption(f"⏰ Info boxes will auto-hide in {remaining_time:.1f}s")
            
            # Status indicators
            status_col1, status_col2, status_col3, status_col4 = st.columns([2, 2, 2, 1])
            
            with status_col1:
                st.success("✅ Ready to answer questions!")
            
            with status_col2:
                # Show current LLM provider
                current_provider = st.session_state.get("llm_provider", "Groq (Cloud)")
                st.info(f"🤖 Using: {current_provider}")
            
            with status_col3:
                # Show knowledge base status
                st.info("📚 Knowledge Base: 84 docs, 764 chunks")
            
            with status_col4:
                # Close button for the entire info section
                if st.button("❌", key="close_info", help="Close info section"):
                    st.session_state.show_info_boxes = False
                    st.rerun()
            
            # Welcome message for new users
            if not st.session_state.messages:
                # Initialize welcome message state
                if "show_welcome" not in st.session_state:
                    st.session_state.show_welcome = True
                
                if st.session_state.show_welcome:
                    st.markdown("---")
                    st.info("""
                    🎉 **Welcome to Adobe Experience League Documentation Chatbot!**
                    
                    **💡 Tips:**
                    - Ask questions about Adobe Experience League solutions features, implementation, or best practices
                    - Use the sidebar to quickly access common questions
                    - Groq (cloud) is the default for fast responses, Ollama (local) is available as fallback
                    - Check the "View Sources" expander to see which documents were used
                    - Use reactions (👍👎💡) to provide feedback on responses
                    
                    **🚀 Getting Started:**
                    Try asking: "What is Adobe Analytics?" or "How do I implement tracking?"
                    """)
    
    # Main chat interface
    st.markdown("---")
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources for assistant messages if available
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 View Sources", expanded=False):
                    st.write("**The answer was generated based on the following documents:**")
                    for i, source in enumerate(message["sources"], 1):
                        source_name = source
                        # Clean up the source name for better display
                        if source_name.endswith('.txt'):
                            source_name = source_name[:-4]  # Remove .txt extension
                        if source_name.startswith('en_docs_'):
                            source_name = source_name[8:]  # Remove en_docs_ prefix
                        source_name = source_name.replace('_', ' ').title()  # Format nicely
                        
                        # Create Adobe Analytics documentation URL based on source name
                        base_url = "https://experienceleague.adobe.com/docs/analytics.html"
                        
                        # Map source names to specific Adobe Analytics URLs
                        url_mapping = {
                            "analytics admin home": "https://experienceleague.adobe.com/docs/analytics/admin/admin-overview/home.html",
                            "analytics analyze admin-overview analytics-overview": "https://experienceleague.adobe.com/docs/analytics/analyze/home.html",
                            "analytics analyze home": "https://experienceleague.adobe.com/docs/analytics/analyze/home.html",
                            "analytics components calculated-metrics cm-overview": "https://experienceleague.adobe.com/docs/analytics/components/calculated-metrics/calcmetrics-overview.html",
                            "analytics components home": "https://experienceleague.adobe.com/docs/analytics/components/home.html",
                            "analytics components segmentation seg-overview": "https://experienceleague.adobe.com/docs/analytics/components/segmentation/seg-overview.html",
                            "analytics export home": "https://experienceleague.adobe.com/docs/analytics/export/home.html",
                            "analytics implementation home": "https://experienceleague.adobe.com/docs/analytics/implementation/home.html",
                            "analytics import home": "https://experienceleague.adobe.com/docs/analytics/import/home.html",
                            "analytics integration home": "https://experienceleague.adobe.com/docs/analytics/integration/home.html",
                            "analytics release-notes doc-updates": "https://experienceleague.adobe.com/docs/analytics/release-notes/latest.html",
                            "analytics release-notes latest": "https://experienceleague.adobe.com/docs/analytics/release-notes/latest.html",
                            "analytics technotes home": "https://experienceleague.adobe.com/docs/analytics/technotes/home.html",
                            # Add more specific mappings based on actual source files
                            "docs analytics implementation home": "https://experienceleague.adobe.com/docs/analytics/implementation/home.html",
                            "en docs analytics admin home": "https://experienceleague.adobe.com/docs/analytics/admin/admin-overview/home.html",
                            "en docs analytics analyze admin-overview analytics-overview": "https://experienceleague.adobe.com/docs/analytics/analyze/home.html",
                            "en docs analytics analyze home": "https://experienceleague.adobe.com/docs/analytics/analyze/home.html",
                            "en docs analytics components calculated-metrics cm-overview": "https://experienceleague.adobe.com/docs/analytics/components/calculated-metrics/calcmetrics-overview.html",
                            "en docs analytics components home": "https://experienceleague.adobe.com/docs/analytics/components/home.html",
                            "en docs analytics components segmentation seg-overview": "https://experienceleague.adobe.com/docs/analytics/components/segmentation/seg-overview.html",
                            "en docs analytics export home": "https://experienceleague.adobe.com/docs/analytics/export/home.html",
                            "en docs analytics implementation home": "https://experienceleague.adobe.com/docs/analytics/implementation/home.html",
                            "en docs analytics import home": "https://experienceleague.adobe.com/docs/analytics/import/home.html",
                            "en docs analytics integration home": "https://experienceleague.adobe.com/docs/analytics/integration/home.html",
                            "en docs analytics release-notes doc-updates": "https://experienceleague.adobe.com/docs/analytics/release-notes/latest.html",
                            "en docs analytics release-notes latest": "https://experienceleague.adobe.com/docs/analytics/release-notes/latest.html",
                            "en docs analytics technotes home": "https://experienceleague.adobe.com/docs/analytics/technotes/home.html"
                        }
                        
                        # Get the appropriate URL for this source
                        source_key = source_name.lower().replace(' ', ' ')
                        
                        # Try exact match first
                        doc_url = url_mapping.get(source_key, None)
                        
                        # If no exact match, try partial matching
                        if doc_url is None:
                            for key, url in url_mapping.items():
                                if key in source_key or source_key in key:
                                    doc_url = url
                                    break
                        
                        # Fallback to base URL if no match found
                        if doc_url is None:
                            doc_url = base_url
                        
                        # Create clickable link that opens in new window
                        st.markdown(f"**{i}.** [{source_name}]({doc_url})", help=f"Click to open {source_name} in a new window")
                    
                    # Also extract and display any URLs found in the message content
                    if "content" in message:
                        import re
                        urls = re.findall(r'https?://[^\s<>"]+', message["content"])
                        if urls:
                            st.markdown("---")
                            st.markdown("**🔗 Links in Response:**")
                            for i, url in enumerate(urls[:3], 1):  # Show up to 3 links
                                display_name = url.split('/')[-1] if '/' in url else url
                                display_name = display_name.replace('_', ' ').replace('-', ' ').title()
                                if len(display_name) > 40:
                                    display_name = display_name[:37] + "..."
                                st.markdown(f"**{i}.** [{display_name}]({url})", help=f"Click to open {url}")
    

    
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
    
    # Show processing status in the main info section
    if st.session_state.is_processing:
        # Initialize processing message state
        if "show_processing" not in st.session_state:
            st.session_state.show_processing = True
        
        if st.session_state.show_processing:
            st.markdown("---")
            with st.container():
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.warning("🤔 Processing your question... Please wait.")
                with col2:
                    if st.button("❌", key="close_processing", help="Hide processing message"):
                        st.session_state.show_processing = False
                        st.rerun()
    else:
        # Reset processing state when not processing
        st.session_state.show_processing = False
        # Create a form for the input area (handles Enter key automatically)
        with st.form(key="chat_form", clear_on_submit=True):
            # Create columns for input and button
            input_col, button_col = st.columns([6, 1])
            
            with input_col:
                # Text input with the question pre-filled
                user_input = st.text_input(
                    "Ask a question about Adobe Experience League solutions...",
                    value=st.session_state.input_text,
                    key="chat_input",
                    placeholder="Ask a question about any Adobe Experience League solutions... (Press Enter to send)",
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
            
            # Update usage statistics
            st.session_state.usage_stats["total_questions"] += 1
            st.session_state.usage_stats["last_question_time"] = time.time()
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Start timer for response time
                        start_time = time.time()
                        
                        # Get answer with error handling
                        try:
                            response = qa_chain.invoke({"query": prompt})
                            answer = response["result"]
                        except Exception as api_error:
                            error_message = str(api_error).lower()
                            
                            if "rate limit" in error_message or "quota" in error_message:
                                st.error("❌ Groq rate limit exceeded. Please try again later or switch to Ollama.")
                                st.info("💡 You can switch to 'Ollama (Local)' in the sidebar to continue using the chatbot.")
                            elif "unauthorized" in error_message or "invalid" in error_message:
                                st.error("❌ Invalid Groq API key. Please check your API key in Streamlit secrets.")
                            elif "timeout" in error_message:
                                st.error("❌ Groq request timed out. Please try again.")
                            else:
                                st.error(f"❌ Error calling Groq API: {api_error}")
                            
                            # Add error message to chat history
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": "Sorry, I encountered an error while processing your request. Please try again or switch to Ollama (Local) in the sidebar.",
                                "sources": []
                            })
                            
                            # Reset processing state
                            st.session_state.is_processing = False
                            st.rerun()
                        
                        # Calculate response time
                        end_time = time.time()
                        response_time = end_time - start_time
                        
                        # Display answer with copy button
                        col1, col2 = st.columns([6, 1])
                        with col1:
                            st.markdown(answer)
                            
                            # Extract and display links from source documents
                            if "source_documents" in response:
                                links_found = []
                                video_links = []
                                
                                for doc in response["source_documents"]:
                                    # Extract URLs from document content
                                    import re
                                    urls = re.findall(r'https?://[^\s<>"]+', doc.page_content)
                                    
                                    for url in urls:
                                        if 'video.tv.adobe.com' in url:
                                            video_links.append(url)
                                        else:
                                            links_found.append(url)
                                
                                # Display video links first (if any)
                                if video_links:
                                    unique_videos = list(set(video_links))
                                    st.markdown("---")
                                    st.markdown("**🎥 Related Videos:**")
                                    for i, video_url in enumerate(unique_videos[:3], 1):  # Show up to 3 videos
                                        # Extract video ID for display
                                        video_id = video_url.split('/v/')[-1].split('?')[0] if '/v/' in video_url else video_url.split('/')[-1]
                                        st.markdown(f"**{i}.** [Adobe TV Video {video_id}]({video_url})", help=f"Click to watch video {video_id}")
                                
                                # Display other links
                                if links_found:
                                    unique_links = list(set(links_found))
                                    st.markdown("---")
                                    st.markdown("**🔗 Related Links:**")
                                    for i, link in enumerate(unique_links[:5], 1):  # Show up to 5 links
                                        # Clean up the link for display
                                        display_name = link.split('/')[-1] if '/' in link else link
                                        display_name = display_name.replace('_', ' ').replace('-', ' ').title()
                                        if len(display_name) > 50:
                                            display_name = display_name[:47] + "..."
                                        
                                        st.markdown(f"**{i}.** [{display_name}]({link})", help=f"Click to open {link}")
                        
                        with col2:
                            # Copy to clipboard button
                            if st.button("📋 Copy", key=f"copy_{len(st.session_state.messages)}", help="Copy response to clipboard"):
                                st.write("✅ Copied to clipboard!")
                                # Note: Actual clipboard functionality requires additional setup
                        

                        
                        # Display response time with enhanced styling
                        if response_time > 10:
                            st.warning(f"⏱️ Response time: {response_time:.1f} seconds")
                        elif response_time > 5:
                            st.info(f"⏱️ Response time: {response_time:.1f} seconds")
                        else:
                            st.success(f"⏱️ Response time: {response_time:.1f} seconds")
                        
                        # Prepare sources for display
                        sources = []
                        if "source_documents" in response:
                            for doc in response["source_documents"]:
                                sources.append(doc.metadata.get('source', 'Unknown'))
                        
                        # Add assistant response to chat history with sources
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer,
                            "sources": sources
                        })
                        
                        # Update usage statistics
                        st.session_state.usage_stats["total_responses"] += 1
                        # Update average response time
                        current_avg = st.session_state.usage_stats["avg_response_time"]
                        total_responses = st.session_state.usage_stats["total_responses"]
                        new_avg = ((current_avg * (total_responses - 1)) + response_time) / total_responses
                        st.session_state.usage_stats["avg_response_time"] = new_avg
                        
                        # Reset processing state after successful response
                        st.session_state.is_processing = False
                        
                        # Message reactions - placed completely outside chat message for better visibility
                        st.markdown("---")
                        st.markdown("**💬 How was this response?**")
                        reaction_col1, reaction_col2, reaction_col3 = st.columns([1, 1, 1])
                        with reaction_col1:
                            if st.button("👍 Helpful", key=f"thumbs_up_{len(st.session_state.messages)}", help="This response was helpful"):
                                st.success("✅ Thank you for the feedback!")
                        with reaction_col2:
                            if st.button("👎 Not Helpful", key=f"thumbs_down_{len(st.session_state.messages)}", help="This response was not helpful"):
                                st.error("❌ We'll work to improve!")
                        with reaction_col3:
                            if st.button("💡 Suggest", key=f"suggest_{len(st.session_state.messages)}", help="Suggest improvement"):
                                st.info("💡 Thanks for the suggestion!")
                        

                                
                    except Exception as e:
                        error_msg = f"❌ Error generating answer: {e}"
                        st.error(error_msg)
                        st.info("Please make sure Ollama is running with the llama3:8b model.")
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        
                        # Reset processing state after error
                        st.session_state.is_processing = False
            

            
            # Generate and display follow-up questions after successful response
            if 'answer' in locals() and 'prompt' in locals():
                follow_up_questions = generate_follow_up_questions(answer, prompt)
                if follow_up_questions:
                    st.markdown("---")
                    st.markdown("**💡 You might also want to ask:**")
                    
                    # Create columns for follow-up questions
                    col1, col2 = st.columns(2)
                    for i, question in enumerate(follow_up_questions):
                        if i < 3:  # First 3 questions in left column
                            with col1:
                                if st.button(f"• {question}", key=f"followup_{i}", help="Click to ask this follow-up question"):
                                    st.session_state.selected_question = question
                                    st.rerun()
                        else:  # Next 3 questions in right column
                            with col2:
                                if st.button(f"• {question}", key=f"followup_{i}", help="Click to ask this follow-up question"):
                                    st.session_state.selected_question = question
                                    st.rerun()
            
            st.rerun()

if __name__ == "__main__":
    main()