#!/usr/bin/env python3
"""
Adobe Experience League Documentation Chatbot
A Streamlit web application that answers questions about Adobe Experience League solutions using a FAISS knowledge base and Ollama LLM.
"""

import streamlit as st
import os
import time
import re
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def categorize_sources(sources):
    """Categorize sources into Adobe docs and Stack Overflow"""
    adobe_sources = []
    stackoverflow_sources = []
    
    for source in sources:
        if source.startswith('stackoverflow_'):
            stackoverflow_sources.append(source)
        else:
            adobe_sources.append(source)
    
    return adobe_sources, stackoverflow_sources

def has_stackoverflow_sources(sources):
    """Check if any sources are from Stack Overflow"""
    return any(source.startswith('stackoverflow_') for source in sources)

def detect_create_action(query):
    """
    Enhanced function to detect create actions and extract detailed information.
    
    This function now provides more sophisticated detection for segment creation,
    including target audience, conditions, and intent extraction.
    """
    query_lower = query.lower()
    
    # Check if query contains 'create' or similar action words
    action_words = ['create', 'build', 'make', 'set up', 'establish', 'generate']
    has_action = any(word in query_lower for word in action_words)
    
    if not has_action:
        return None, None
    
    # Define supported action objects with enhanced detection
    action_keywords = {
        'dashboard': ['dashboard', 'dashboards', 'board'],
        'segment': ['segment', 'segments', 'segmentation', 'audience', 'cohort'],
        'calculated metrics': ['calculated metrics', 'calculated metric', 'metric', 'metrics', 'kpi'],
        'workspace': ['workspace', 'analysis workspace', 'project', 'analysis'],
        'report': ['report', 'reports', 'reporting'],
        'alert': ['alert', 'alerts', 'notification'],
        'filter': ['filter', 'filters', 'filtering'],
        'visualization': ['visualization', 'chart', 'charts', 'graph', 'plot']
    }
    
    # Find which action object is mentioned
    detected_action = None
    detected_keyword = None
    
    for action_type, keywords in action_keywords.items():
        for keyword in keywords:
            if keyword in query_lower:
                detected_action = action_type
                detected_keyword = keyword
                break
        if detected_action:
            break
    
    if not detected_action:
        return None, None
    
    # Enhanced detection for segments
    if detected_action == 'segment':
        return detect_segment_creation_intent(query, query_lower)
    
    return detected_action, detected_keyword


def detect_segment_creation_intent(query, query_lower):
    """
    Detect detailed segment creation intent from user query.
    
    Args:
        query (str): Original user query
        query_lower (str): Lowercase version of query
        
    Returns:
        tuple: (action_type, intent_details) where intent_details is a dict
    """
    intent_details = {
        'action_type': 'segment',
        'target_audience': None,
        'conditions': [],
        'geographic': None,
        'behavioral': [],
        'device': None,
        'time_based': None,
        'custom_variables': [],
        'intent_confidence': 'medium'
    }
    
    # Detect target audience
    audience_patterns = {
        'visitors': ['visitors', 'users', 'people', 'audience', 'customers'],
        'visits': ['visits', 'sessions', 'trips'],
        'hits': ['hits', 'page views', 'clicks', 'interactions']
    }
    
    for audience_type, patterns in audience_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            intent_details['target_audience'] = audience_type
            break
    
    # Default to visitors if no specific audience mentioned
    if not intent_details['target_audience']:
        intent_details['target_audience'] = 'visitors'
    
    # Detect geographic targeting
    geo_patterns = {
        'country': ['country', 'nation', 'usa', 'united states', 'us', 'canada', 'uk', 'germany'],
        'city': ['city', 'town', 'new york', 'london', 'toronto', 'berlin'],
        'state': ['state', 'province', 'california', 'texas', 'ontario'],
        'zip': ['zip', 'postal', 'postcode', 'area code']
    }
    
    for geo_type, patterns in geo_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            intent_details['geographic'] = geo_type
            break
    
    # Detect device targeting
    device_patterns = {
        'mobile': ['mobile', 'phone', 'smartphone', 'ios', 'android'],
        'desktop': ['desktop', 'computer', 'pc', 'mac', 'laptop'],
        'tablet': ['tablet', 'ipad', 'android tablet']
    }
    
    for device_type, patterns in device_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            intent_details['device'] = device_type
            break
    
    # Detect behavioral conditions
    behavioral_patterns = {
        'page_views': ['page views', 'pages', 'pageviews', 'page count'],
        'time_on_site': ['time on site', 'session duration', 'visit length', 'dwell time'],
        'bounce_rate': ['bounce', 'bounce rate', 'single page'],
        'conversion': ['conversion', 'purchase', 'goal', 'objective', 'target'],
        'cart': ['cart', 'shopping cart', 'basket', 'add to cart'],
        'checkout': ['checkout', 'payment', 'purchase funnel']
    }
    
    for behavior_type, patterns in behavioral_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            intent_details['behavioral'].append(behavior_type)
    
    # Detect time-based targeting
    time_patterns = {
        'day_of_week': ['weekday', 'weekend', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
        'time_of_day': ['morning', 'afternoon', 'evening', 'night', 'business hours'],
        'seasonal': ['seasonal', 'holiday', 'christmas', 'black friday', 'summer', 'winter']
    }
    
    for time_type, patterns in time_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            intent_details['time_based'] = time_type
            break
    
    # Detect custom variables (eVar, prop, etc.)
    custom_var_patterns = ['evar', 'prop', 'variable', 'custom', 'attribute']
    if any(pattern in query_lower for pattern in custom_var_patterns):
        intent_details['custom_variables'].append('custom_variable')
    
    # Set confidence level based on detected information
    detected_count = sum([
        1 if intent_details['geographic'] else 0,
        1 if intent_details['device'] else 0,
        len(intent_details['behavioral']),
        1 if intent_details['time_based'] else 0,
        len(intent_details['custom_variables'])
    ])
    
    if detected_count >= 3:
        intent_details['intent_confidence'] = 'high'
    elif detected_count >= 1:
        intent_details['intent_confidence'] = 'medium'
    else:
        intent_details['intent_confidence'] = 'low'
    
    return 'segment', intent_details


def generate_segment_suggestions(intent_details):
    """
    Generate segment creation suggestions based on detected intent.
    
    Args:
        intent_details (dict): Intent details from detect_segment_creation_intent
        
    Returns:
        dict: Suggestions for segment creation
    """
    suggestions = {
        'segment_name': '',
        'segment_description': '',
        'recommended_rules': [],
        'confidence': intent_details.get('intent_confidence', 'low'),
        'next_steps': []
    }
    
    # Build segment name based on detected intent
    name_parts = []
    
    if intent_details.get('device'):
        name_parts.append(f"{intent_details['device'].title()} Users")
    
    if intent_details.get('geographic'):
        if intent_details['geographic'] == 'country':
            name_parts.append("from Specific Country")
        elif intent_details['geographic'] == 'city':
            name_parts.append("from Specific City")
        elif intent_details['geographic'] == 'state':
            name_parts.append("from Specific State")
    
    if intent_details.get('behavioral'):
        for behavior in intent_details['behavioral']:
            if behavior == 'page_views':
                name_parts.append("with High Page Views")
            elif behavior == 'time_on_site':
                name_parts.append("with Long Session Duration")
            elif behavior == 'conversion':
                name_parts.append("who Converted")
            elif behavior == 'cart':
                name_parts.append("who Added to Cart")
    
    if intent_details.get('time_based'):
        if intent_details['time_based'] == 'day_of_week':
            name_parts.append("on Weekends")
        elif intent_details['time_based'] == 'time_of_day':
            name_parts.append("during Business Hours")
        elif intent_details['time_based'] == 'seasonal':
            name_parts.append("during Holiday Season")
    
    # If no specific patterns detected, use generic name
    if not name_parts:
        name_parts = ["Custom Segment"]
    
    suggestions['segment_name'] = " ".join(name_parts)
    
    # Build description
    description_parts = []
    target_audience = intent_details.get('target_audience', 'visitors')
    description_parts.append(f"Segment targeting {target_audience}")
    
    if intent_details.get('device'):
        description_parts.append(f"using {intent_details['device']} devices")
    
    if intent_details.get('geographic'):
        description_parts.append(f"from specific geographic locations")
    
    if intent_details.get('behavioral'):
        behavior_descriptions = []
        for behavior in intent_details['behavioral']:
            if behavior == 'page_views':
                behavior_descriptions.append("with high page view counts")
            elif behavior == 'time_on_site':
                behavior_descriptions.append("with long session durations")
            elif behavior == 'conversion':
                behavior_descriptions.append("who completed conversions")
            elif behavior == 'cart':
                behavior_descriptions.append("who added items to cart")
        
        if behavior_descriptions:
            description_parts.append(" ".join(behavior_descriptions))
    
    if intent_details.get('time_based'):
        if intent_details['time_based'] == 'day_of_week':
            description_parts.append("visiting on specific days of the week")
        elif intent_details['time_based'] == 'time_of_day':
            description_parts.append("visiting during specific times of day")
        elif intent_details['time_based'] == 'seasonal':
            description_parts.append("visiting during seasonal periods")
    
    suggestions['segment_description'] = " ".join(description_parts) + "."
    
    # Generate recommended rules
    rules = []
    
    # Device rule
    if intent_details.get('device'):
        if intent_details['device'] == 'mobile':
            rules.append({
                'func': 'streq',
                'name': 'variables/device_type',
                'val': 'Mobile'
            })
        elif intent_details['device'] == 'desktop':
            rules.append({
                'func': 'streq',
                'name': 'variables/device_type',
                'val': 'Desktop'
            })
        elif intent_details['device'] == 'tablet':
            rules.append({
                'func': 'streq',
                'name': 'variables/device_type',
                'val': 'Tablet'
            })
    
    # Geographic rule (placeholder)
    if intent_details.get('geographic'):
        rules.append({
            'func': 'streq',
            'name': 'variables/geocountry',
            'val': 'Specific Country'
        })
    
    # Behavioral rules
    if intent_details.get('behavioral'):
        for behavior in intent_details['behavioral']:
            if behavior == 'page_views':
                rules.append({
                    'func': 'gt',
                    'name': 'variables/pageviews',
                    'val': 5
                })
            elif behavior == 'time_on_site':
                rules.append({
                    'func': 'gt',
                    'name': 'variables/time_on_site',
                    'val': 600  # 10 minutes in seconds
                })
    
    suggestions['recommended_rules'] = rules
    
    # Generate next steps
    next_steps = []
    
    if intent_details.get('intent_confidence') == 'low':
        next_steps.append("Clarify the specific targeting criteria")
        next_steps.append("Specify geographic location if needed")
        next_steps.append("Define behavioral thresholds")
    
    if intent_details.get('geographic') == 'country':
        next_steps.append("Specify the target country")
    
    if intent_details.get('geographic') == 'city':
        next_steps.append("Specify the target city")
    
    if intent_details.get('geographic') == 'state':
        next_steps.append("Specify the target state/province")
    
    if intent_details.get('behavioral'):
        for behavior in intent_details['behavioral']:
            if behavior == 'page_views':
                next_steps.append("Specify the minimum page view count")
            elif behavior == 'time_on_site':
                next_steps.append("Specify the minimum session duration")
    
    if not next_steps:
        next_steps.append("Review the suggested segment configuration")
        next_steps.append("Customize segment name and description if needed")
        next_steps.append("Confirm segment creation")
    
    suggestions['next_steps'] = next_steps
    
    return suggestions


def generate_adobe_url(source_name):
    """Generate Adobe Experience League URL based on source name"""
    # Remove .txt extension if present
    if source_name.endswith('.txt'):
        source_name = source_name[:-4]
    
    # Remove en_docs_ prefix if present
    if source_name.startswith('en_docs_'):
        source_name = source_name[8:]
    
    # Base URL for Adobe Experience League
    base_url = "https://experienceleague.adobe.com/en/docs"
    
    # Common patterns for URL generation
    if source_name.startswith('analytics_'):
        return f"{base_url}/analytics/{source_name.replace('analytics_', '')}"
    elif source_name.startswith('customer-journey-analytics'):
        return f"{base_url}/customer-journey-analytics/{source_name.replace('customer-journey-analytics', '')}"
    elif source_name.startswith('analytics-platform'):
        return f"{base_url}/analytics-platform/{source_name.replace('analytics-platform_', '')}"
    elif source_name.startswith('analytics-learn'):
        return f"{base_url}/analytics-learn/{source_name.replace('analytics-learn_', '')}"
    elif source_name.startswith('blueprints-learn'):
        return f"{base_url}/blueprints-learn/{source_name.replace('blueprints-learn_', '')}"
    elif source_name.startswith('certification'):
        return f"{base_url}/certification/{source_name.replace('certification_', '')}"
    elif source_name.startswith('experience-cloud-kcs'):
        return f"{base_url}/experience-cloud-kcs/{source_name.replace('experience-cloud-kcs_', '')}"
    elif source_name.startswith('home-tutorials'):
        return f"{base_url}/home-tutorials"
    elif source_name.startswith('release-notes'):
        return f"{base_url}/release-notes/{source_name.replace('release-notes_', '')}"
    elif source_name.startswith('browse_'):
        return f"{base_url}/browse/{source_name.replace('browse_', '')}"
    else:
        # Fallback to base analytics URL
        return "https://experienceleague.adobe.com/en/docs/analytics"
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

def handle_segment_creation_workflow(prompt, action_details):
    """
    Handle the segment creation workflow when a user wants to create a segment.
    
    Args:
        prompt (str): The user's original query
        action_details (dict): Detected intent details
    """
    st.markdown("---")
    st.header("🔧 Segment Creation Workflow")
    st.info(f"I detected you want to create a segment! Let me help you with that.")
    
    # Display detected intent
    if isinstance(action_details, dict):
        st.subheader("📊 Detected Intent")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Target Audience", action_details.get('target_audience', 'visitors').title())
            if action_details.get('device'):
                st.metric("Device Type", action_details['device'].title())
        
        with col2:
            if action_details.get('geographic'):
                st.metric("Geographic", action_details['geographic'].title())
            if action_details.get('time_based'):
                st.metric("Time-based", action_details['time_based'].replace('_', ' ').title())
        
        # Generate suggestions
        suggestions = generate_segment_suggestions(action_details)
        
        st.subheader("💡 Suggested Configuration")
        st.info(f"**Suggested Name:** {suggestions['segment_name']}")
        st.info(f"**Suggested Description:** {suggestions['segment_description']}")
        st.info(f"**Recommended Rules:** {len(suggestions['recommended_rules'])} rules")
        
        # Show next steps
        st.subheader("🔄 Next Steps")
        for i, step in enumerate(suggestions['next_steps'], 1):
            st.markdown(f"{i}. {step}")
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Start Segment Builder", type="primary"):
                # Store the intent details in session state for the segment builder
                st.session_state.segment_intent = {
                    'prompt': prompt,
                    'action_details': action_details,
                    'suggestions': suggestions
                }
                # Redirect to segment builder
                st.switch_page("segment_builder.py")
        
        with col2:
            if st.button("💬 Ask More Questions", type="secondary"):
                st.info("Feel free to ask more questions about Adobe Analytics or other topics!")
    
    else:
        st.error("❌ Unable to parse segment creation intent. Please try rephrasing your request.")
        st.info("💡 Example: 'Create a segment for mobile users from California'")


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
                # Show knowledge base status
                adobe_docs_count = len(list(Path("./adobe_docs").glob("*.txt")))
                stackoverflow_docs_count = len(list(Path("./stackoverflow_docs").glob("*.txt")))
                total_docs = adobe_docs_count + stackoverflow_docs_count
                
                if stackoverflow_docs_count > 0:
                    st.info(f"📚 Knowledge Base: {adobe_docs_count} Adobe docs, {stackoverflow_docs_count} SO docs")
                else:
                    st.info(f"📚 Knowledge Base: {adobe_docs_count} Adobe docs")
            
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
            
            # Display create action button for user messages if detected
            if message["role"] == "user" and "create_action" in message:
                action_info = message["create_action"]
                action_type = action_info["type"]
                if st.button(f"📋 Help Create {action_type.title()}", key=f"create_{action_type}_{len(st.session_state.messages)}"):
                    st.success(f"🎉 Let's create a {action_type}! This feature is coming soon.")
            
            # Display sources for assistant messages if available
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 View Sources", expanded=False):
                    st.write("**The answer was generated based on the following documents:**")
                    # Categorize sources
                    adobe_sources, stackoverflow_sources = categorize_sources(message["sources"])
                    
                    # Show source summary
                    if adobe_sources and stackoverflow_sources:
                        st.success("✅ Answer combines official Adobe documentation and community solutions")
                        st.info(f"📖 Adobe Docs: {len(adobe_sources)} | 💬 Stack Overflow: {len(stackoverflow_sources)}")
                    elif stackoverflow_sources:
                        st.warning("💬 Answer based on community solutions from Stack Overflow")
                        st.info(f"💬 Stack Overflow: {len(stackoverflow_sources)} sources")
                    else:
                        st.success("📖 Answer based on official Adobe documentation")
                        st.info(f"📖 Adobe Docs: {len(adobe_sources)} sources")
                    
                    st.write(f"**Debug: Found {len(message["sources"])} sources")
                    for idx, src in enumerate(message["sources"]):
                        st.write(f"  {idx+1}. {src}")
                    st.write("**Detailed sources:**")
                    for i, source in enumerate(message["sources"], 1):
                        # Add source type indicator
                        if source.startswith('stackoverflow_'):
                            source_icon = "💬"
                            source_type = "Stack Overflow"
                        else:
                            source_icon = "📖"
                            source_type = "Adobe Docs"
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
                            # Analytics Core Documentation
                            "en_docs_analytics_admin_home": "https://experienceleague.adobe.com/en/docs/analytics/admin/home",
                            "en_docs_analytics_analyze_admin-overview_analytics-overview": "https://experienceleague.adobe.com/en/docs/analytics/analyze/admin-overview/analytics-overview",
                            "en_docs_analytics_analyze_home": "https://experienceleague.adobe.com/en/docs/analytics/analyze/home",
                            "en_docs_analytics_components_calculated-metrics_cm-overview": "https://experienceleague.adobe.com/en/docs/analytics/components/calculated-metrics/cm-overview",
                            "en_docs_analytics_components_home": "https://experienceleague.adobe.com/en/docs/analytics/components/home",
                            "en_docs_analytics_components_segmentation_seg-overview": "https://experienceleague.adobe.com/en/docs/analytics/components/segmentation/seg-overview",
                            "en_docs_analytics_export_home": "https://experienceleague.adobe.com/en/docs/analytics/export/home",
                            "en_docs_analytics_implementation_home": "https://experienceleague.adobe.com/en/docs/analytics/implementation/home",
                            "en_docs_analytics_import_home": "https://experienceleague.adobe.com/en/docs/analytics/import/home",
                            "en_docs_analytics_integration_home": "https://experienceleague.adobe.com/en/docs/analytics/integration/home",
                            "en_docs_analytics_release-notes_doc-updates": "https://experienceleague.adobe.com/en/docs/analytics/release-notes/doc-updates",
                            "en_docs_analytics_release-notes_latest": "https://experienceleague.adobe.com/en/docs/analytics/release-notes/latest",
                            "en_docs_analytics_technotes_home": "https://experienceleague.adobe.com/en/docs/analytics/technotes/home",
                            
                            # Analytics Platform and CJA
                            "en_docs_analytics-platform_using_cja-overview_cja-b2c-overview_data-analysis-ai": "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-overview/cja-b2c-overview/data-analysis-ai",
                            "en_docs_analytics-platform_using_cja-workspace_attribution_algorithmic": "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-workspace/attribution/algorithmic",
                            "en_docs_analytics-platform_using_cja-workspace_attribution_best-practices": "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-workspace/attribution/best-practices",
                            "en_docs_analytics-platform_using_cja-workspace_attribution_models": "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-workspace/attribution/models",
                            "en_docs_analytics-platform_using_cja-workspace_attribution_overview": "https://experienceleague.adobe.com/en/docs/analytics-platform/using/cja-workspace/attribution/overview",
                            
                            # Customer Journey Analytics
                            "en_docs_customer-journey-analytics": "https://experienceleague.adobe.com/en/docs/customer-journey-analytics",
                            "en_docs_customer-journey-analytics-learn_tutorials_analysis-workspace_workspace-projects_analysis-workspace-overview": "https://experienceleague.adobe.com/en/docs/customer-journey-analytics-learn/tutorials/analysis-workspace/workspace-projects/analysis-workspace-overview",
                            "en_docs_customer-journey-analytics-learn_tutorials_cja-basics_what-is-customer-journey-analytics": "https://experienceleague.adobe.com/en/docs/customer-journey-analytics-learn/tutorials/cja-basics/what-is-customer-journey-analytics",
                            "en_docs_customer-journey-analytics-learn_tutorials_overview": "https://experienceleague.adobe.com/en/docs/customer-journey-analytics-learn/tutorials/overview",
                            
                            # Analytics Learn Tutorials
                            "en_docs_analytics-learn_tutorials_administration_key-admin-skills_translating-adobe-analytics-technical-language": "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/administration/key-admin-skills/translating-adobe-analytics-technical-language",
                            "en_docs_analytics-learn_tutorials_analysis-use-cases_setting-up-in-market-zip-code-analysis-use-case": "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/analysis-use-cases/setting-up-in-market-zip-code-analysis-use-case",
                            "en_docs_analytics-learn_tutorials_analysis-workspace_building-freeform-tables_row-and-column-settings-in-freeform-tables": "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/analysis-workspace/building-freeform-tables/row-and-column-settings-in-freeform-tables",
                            "en_docs_analytics-learn_tutorials_exporting_report-builder_upgrade-and-reschedule-workbooks": "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/exporting/report-builder/upgrade-and-reschedule-workbooks",
                            "en_docs_analytics-learn_tutorials_overview": "https://experienceleague.adobe.com/en/docs/analytics-learn/tutorials/overview",
                            
                            # Analytics Admin Tools
                            "en_docs_analytics_admin_admin-tools_manage-report-suites_edit-report-suite_report-suite-general_processing-rules_pr-copy": "https://experienceleague.adobe.com/en/docs/analytics/admin/admin-tools/manage-report-suites/edit-report-suite/report-suite-general/processing-rules/pr-copy",
                            "en_docs_analytics_admin_admin-tools_manage-report-suites_edit-report-suite_report-suite-general_processing-rules_pr-interface": "https://experienceleague.adobe.com/en/docs/analytics/admin/admin-tools/manage-report-suites/edit-report-suite/report-suite-general/processing-rules/pr-interface",
                            "en_docs_analytics_admin_admin-tools_manage-report-suites_edit-report-suite_report-suite-general_processing-rules_pr-use-cases": "https://experienceleague.adobe.com/en/docs/analytics/admin/admin-tools/manage-report-suites/edit-report-suite/report-suite-general/processing-rules/pr-use-cases",
                            
                            # Analytics Implementation
                            "en_docs_analytics_implementation_aep-edge_hit-types": "https://experienceleague.adobe.com/en/docs/analytics/implementation/aep-edge/hit-types",
                            
                            # Blueprints and Architecture
                            "en_docs_blueprints-learn_architecture_architecture-overview_experience-cloud": "https://experienceleague.adobe.com/en/docs/blueprints-learn/architecture/architecture-overview/experience-cloud",
                            "en_docs_blueprints-learn_architecture_architecture-overview_platform-applications": "https://experienceleague.adobe.com/en/docs/blueprints-learn/architecture/architecture-overview/platform-applications",
                            "en_docs_blueprints-learn_architecture_customer-journey-analytics_cja-ajo": "https://experienceleague.adobe.com/en/docs/blueprints-learn/architecture/customer-journey-analytics/cja-ajo",
                            "en_docs_blueprints-learn_architecture_customer-journey-analytics_cja-rtcdp": "https://experienceleague.adobe.com/en/docs/blueprints-learn/architecture/customer-journey-analytics/cja-rtcdp",
                            
                            # Certification
                            "en_docs_certification_program_technical-certifications_aa_aa-overview": "https://experienceleague.adobe.com/en/docs/certification/program/technical-certifications/aa/aa-overview",
                            "en_docs_certification_program_technical-certifications_aem_aem-overview": "https://experienceleague.adobe.com/en/docs/certification/program/technical-certifications/aem/aem-overview",
                            
                            # Knowledge Base Articles
                            "en_docs_experience-cloud-kcs_kbarticles_ka-25262": "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-25262",
                            "en_docs_experience-cloud-kcs_kbarticles_ka-26568": "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-26568",
                            "en_docs_experience-cloud-kcs_kbarticles_ka-26635": "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-26635",
                            "en_docs_experience-cloud-kcs_kbarticles_ka-26946": "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-26946",
                            "en_docs_experience-cloud-kcs_kbarticles_ka-16598": "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-16598",
                            "en_docs_experience-cloud-kcs_kbarticles_ka-17254": "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-17254",
                            "en_docs_experience-cloud-kcs_kbarticles_ka-17580": "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-17580",
                            "en_docs_experience-cloud-kcs_kbarticles_ka-20022": "https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-20022",
                            
                            # Home Tutorials and Documentation
                            "en_docs_home-tutorials": "https://experienceleague.adobe.com/en/docs/home-tutorials",
                            "en_docs_release-notes_experience-cloud_current": "https://experienceleague.adobe.com/en/docs/release-notes/experience-cloud/current",
                            
                            # Browse Pages
                            "en_browse_analytics": "https://experienceleague.adobe.com/en/browse/analytics",
                            "en_browse_advertising": "https://experienceleague.adobe.com/en/browse/advertising",
                            "en_browse_audience-manager": "https://experienceleague.adobe.com/en/browse/audience-manager",
                            "en_browse_campaign": "https://experienceleague.adobe.com/en/browse/campaign",
                            "en_browse_commerce": "https://experienceleague.adobe.com/en/browse/commerce",
                            "en_browse_creative-cloud-for-enterprise": "https://experienceleague.adobe.com/en/browse/creative-cloud-for-enterprise",
                            "en_browse_customer-journey-analytics": "https://experienceleague.adobe.com/en/browse/customer-journey-analytics",
                            "en_browse_document-cloud": "https://experienceleague.adobe.com/en/browse/document-cloud",
                            "en_browse_dynamic-media-classic": "https://experienceleague.adobe.com/en/browse/dynamic-media-classic",
                            "en_browse_experience-cloud-administration-and-interface-services": "https://experienceleague.adobe.com/en/browse/experience-cloud-administration-and-interface-services",
                            "en_browse_experience-manager": "https://experienceleague.adobe.com/en/browse/experience-manager",
                            "en_browse_experience-platform": "https://experienceleague.adobe.com/en/browse/experience-platform",
                            "en_browse_experience-platform_data-collection": "https://experienceleague.adobe.com/en/browse/experience-platform/data-collection",
                            "en_browse_genstudio-for-performance-marketing": "https://experienceleague.adobe.com/en/browse/genstudio-for-performance-marketing",
                            "en_browse_journey-optimizer": "https://experienceleague.adobe.com/en/browse/journey-optimizer",
                            "en_browse_journey-optimizer-b2b-edition": "https://experienceleague.adobe.com/en/browse/journey-optimizer-b2b-edition",
                            "en_browse_learning-manager": "https://experienceleague.adobe.com/en/browse/learning-manager",
                            "en_browse_marketo-engage": "https://experienceleague.adobe.com/en/browse/marketo-engage",
                            "en_browse_mix-modeler": "https://experienceleague.adobe.com/en/browse/mix-modeler",
                            "en_browse_pass": "https://experienceleague.adobe.com/en/browse/pass",
                            "en_browse_real-time-customer-data-platform": "https://experienceleague.adobe.com/en/browse/real-time-customer-data-platform",
                            "en_browse_target": "https://experienceleague.adobe.com/en/browse/target",
                            "en_browse_workfront": "https://experienceleague.adobe.com/en/browse/workfront",
                            
                            # Legacy mapping for old filenames
                            "docs_analytics_implementation_home": "https://experienceleague.adobe.com/en/docs/analytics/implementation/home"
                        }
                        
                        # Get the appropriate URL for this source
                        # Stack Overflow URL handling
                        if source_name.startswith("stackoverflow_"):
                            # Extract question ID from filename
                            parts = source_name.split("_")
                            if len(parts) >= 2:
                                try:
                                    question_id = parts[1]
                                    doc_url = f"https://stackoverflow.com/questions/{question_id}"
                                except:
                                    doc_url = "https://stackoverflow.com/questions"
                            else:
                                doc_url = "https://stackoverflow.com/questions"
                        else:
                            # Adobe documentation URL handling
                            # Use the original source name (without .txt extension) for exact matching
                            source_key = source_name  # This is already cleaned (no .txt extension)
                            
                            # Try exact match first in the mapping
                            doc_url = url_mapping.get(source_key, None)
                            
                            # If no exact match, try with en_docs_ prefix
                            if doc_url is None:
                                source_key_with_prefix = f"en_docs_{source_key}"
                                doc_url = url_mapping.get(source_key_with_prefix, None)
                            
                            # If still no match, try partial matching
                            if doc_url is None:
                                for key, url in url_mapping.items():
                                    # Remove en_docs_ prefix from key for comparison
                                    clean_key = key.replace('en_docs_', '') if key.startswith('en_docs_') else key
                                    if clean_key == source_key or source_key in clean_key or clean_key in source_key:
                                        doc_url = url
                                        break
                            
                            # If still no match, generate URL dynamically
                            if doc_url is None:
                                doc_url = generate_adobe_url(source)  # Use original source name

                            # Fallback to base URL if no match found
                            if doc_url is None:
                                doc_url = base_url

                        # Create clickable link that opens in new window
                        st.markdown(f"**{i}.** {source_icon} [{source_name}]({doc_url}) ({source_type})", help=f"Click to open {source_name} in a new window")
    

    
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
            
                    # Check for create actions and store in message
        action_type, action_details = detect_create_action(prompt)
        
        # Add user message to chat history
        user_message = {"role": "user", "content": prompt}
        if action_type:
            user_message["create_action"] = {"type": action_type, "details": action_details}
        st.session_state.messages.append(user_message)
        
        # Update usage statistics
        st.session_state.usage_stats["total_questions"] += 1
        st.session_state.usage_stats["last_question_time"] = time.time()
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Handle segment creation workflow
        if action_type == 'segment':
            handle_segment_creation_workflow(prompt, action_details)
            return  # Skip the regular QA flow for segment creation
        
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
                        
                        # Check if response has Stack Overflow sources
                        has_stackoverflow = False
                        if "source_documents" in response:
                            sources = [doc.metadata.get('source', 'Unknown') for doc in response["source_documents"]]
                            has_stackoverflow = has_stackoverflow_sources(sources)
                        
                        # Add source indicator to response
                        if has_stackoverflow:
                            st.info("💬 This response includes community solutions from Stack Overflow")
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