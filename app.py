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
from langchain_anthropic import ChatAnthropic
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import json

# Import source attribution system
try:
    from source_attributor import SourceAttributor, quick_attribution, SourceType
    SOURCE_ATTRIBUTION_AVAILABLE = True
except ImportError:
    SOURCE_ATTRIBUTION_AVAILABLE = False
    st.warning("⚠️ Source attribution system not available. Install source_attributor.py")

# Import segment creator system
try:
    from segment_creator import segment_creator
    SEGMENT_CREATOR_AVAILABLE = True
except ImportError:
    SEGMENT_CREATOR_AVAILABLE = False
    st.warning("⚠️ Segment creator system not available. Install segment_creator.py")


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

def generate_source_attributions(sources, format_type="markdown"):
    """Generate proper attributions for sources using the attribution system"""
    if not SOURCE_ATTRIBUTION_AVAILABLE:
        return []
    
    try:
        attributor = SourceAttributor()
        attributions = attributor.generate_bulk_attribution(sources, format_type)
        return attributions
    except Exception as e:
        st.error(f"Error generating attributions: {str(e)}")
        return []

def get_simple_attributions(sources):
    """Get simple attributions with links and license text only"""
    if not SOURCE_ATTRIBUTION_AVAILABLE:
        return []
    
    try:
        attributor = SourceAttributor()
        attributions = attributor.generate_bulk_attribution(sources, "markdown")
        return attributions
    except Exception as e:
        st.error(f"Error generating attributions: {str(e)}")
        return []

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
        'calculated metrics': ['calculated metrics', 'calculated metric', 'metric', 'metrics', 'kpi'],
        'workspace': ['workspace', 'analysis workspace', 'project', 'analysis'],
        'report': ['report', 'reports', 'reporting'],
        'alert': ['alert', 'alerts', 'notification'],
        'filter': ['filter', 'filters', 'filtering'],
        'visualization': ['visualization', 'chart', 'charts', 'graph', 'plot'],
        'segment': ['segment', 'segments', 'audience', 'cohort', 'user group', 'visitor group']
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
    
    
    return detected_action, detected_keyword


def detect_segment_intent_with_claude(query, claude_llm=None):
    """
    Use Anthropic Claude to detect and understand segment creation intent.
    
    Args:
        query (str): User's segment creation request
        claude_llm: Anthropic Claude LLM instance
        
    Returns:
        dict: Enhanced intent details with Claude's analysis
    """
    if not claude_llm:
        return None
    
    try:
        prompt = f"""Analyze this user request for Adobe Analytics segment creation:
"{query}"

Extract and return a JSON object with the following structure:
{{
    "target_audience": "visitors|visits|hits",
    "conditions": ["list of conditions mentioned"],
    "business_context": "business goal or use case",
    "geographic": "country|state|city|zip or null",
    "device": "mobile|desktop|tablet or null",
    "behavioral": ["page_views", "time_on_site", "conversion", "cart", etc.],
    "time_based": "day_of_week|time_of_day|seasonal or null",
    "custom_variables": ["any custom variables mentioned"],
    "confidence": "high|medium|low",
    "complexity": "simple|moderate|complex",
    "business_value": "explanation of business value",
    "recommended_approach": "suggested approach for this segment"
}}

Focus on:
1. Understanding the business context and goals
2. Identifying all conditions and filters
3. Assessing complexity and confidence
4. Providing business value insights
5. Suggesting the best approach

Return only valid JSON, no additional text."""

        response = claude_llm.invoke(prompt)
        
        # Parse Claude's response
        import json
        try:
            claude_analysis = json.loads(response.content.strip())
            
            # Convert to our standard format
            intent_details = {
                'action_type': 'segment',
                'target_audience': claude_analysis.get('target_audience', 'visitors'),
                'conditions': claude_analysis.get('conditions', []),
                'business_context': claude_analysis.get('business_context', ''),
                'geographic': claude_analysis.get('geographic'),
                'behavioral': claude_analysis.get('behavioral', []),
                'device': claude_analysis.get('device'),
                'time_based': claude_analysis.get('time_based'),
                'custom_variables': claude_analysis.get('custom_variables', []),
                'intent_confidence': claude_analysis.get('confidence', 'medium'),
                'complexity': claude_analysis.get('complexity', 'simple'),
                'business_value': claude_analysis.get('business_value', ''),
                'recommended_approach': claude_analysis.get('recommended_approach', ''),
                'claude_enhanced': True
            }
            
            return intent_details
            
        except json.JSONDecodeError:
            # Fallback if Claude returns invalid JSON
            return None
            
    except Exception as e:
        print(f"Error in Claude intent detection: {e}")
        return None

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
    Now enhanced to use vector database for better suggestions.
    
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
    
    # Try to get relevant segment examples from vector database
    relevant_examples = []
    try:
        vectorstore = load_knowledge_base()
        if vectorstore:
            # Create a search query based on intent
            search_query = ""
            if intent_details.get('device'):
                search_query += f"{intent_details['device']} "
            if intent_details.get('geographic'):
                search_query += f"{intent_details['geographic']} "
            if intent_details.get('behavioral'):
                for behavior in intent_details['behavioral']:
                    search_query += f"{behavior} "
            
            if search_query.strip():
                # Search for relevant examples
                results = vectorstore.similarity_search(search_query.strip(), k=3)
                for result in results:
                    if result.metadata.get('type') == 'segment_example':
                        relevant_examples.append(result.metadata)
            else:
                # Generic search for segment examples
                results = vectorstore.similarity_search("Adobe Analytics segment examples", k=3)
                for result in results:
                    if result.metadata.get('type') == 'segment_example':
                        relevant_examples.append(result.metadata)
    except Exception as e:
        print(f"Warning: Could not load relevant examples: {e}")
    
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
    
    # Generate recommended rules based on relevant examples or defaults
    rules = []
    
    # Device rule - use valid Adobe Analytics variables
    if intent_details.get('device'):
        if intent_details['device'] == 'mobile':
            rules.append({
                'func': 'streq',
                'name': 'variables/evar1',  # Use evar1 for device type
                'val': 'Mobile',
                'str': 'Mobile'
            })
        elif intent_details['device'] == 'desktop':
            rules.append({
                'func': 'streq',
                'name': 'variables/evar1',  # Use evar1 for device type
                'val': 'Desktop',
                'str': 'Desktop'
            })
        elif intent_details['device'] == 'tablet':
            rules.append({
                'func': 'streq',
                'name': 'variables/evar1',  # Use evar1 for device type
                'val': 'Tablet',
                'str': 'Tablet'
            })
    
    # Geographic rule - now smarter based on examples
    if intent_details.get('geographic'):
        # Look for relevant geographic examples
        geographic_example = None
        for example in relevant_examples:
            if 'geocountry' in str(example.get('description', '')).lower():
                geographic_example = example
                break
        
        if geographic_example:
            # Use the example's geographic variable
            rules.append({
                'func': 'streq',
                'name': 'variables/geocountry',
                'val': 'Specific Country',  # User will specify
                'str': 'Specific Country'
            })
        else:
            # Default geographic rule
            rules.append({
                'func': 'streq',
                'name': 'variables/geocountry',
                'val': 'Specific Country',
                'str': 'Specific Country'
            })
    
    # Behavioral rules - use valid Adobe Analytics variables
    if intent_details.get('behavioral'):
        for behavior in intent_details['behavioral']:
            if behavior == 'page_views':
                rules.append({
                    'func': 'gt',
                    'name': 'metrics/pageviews',  # Page views are metrics, not variables
                    'val': 5
                })
            elif behavior == 'time_on_site':
                rules.append({
                    'func': 'gt',
                    'name': 'metrics/timeonsite',  # Time on site is a metric, not a variable
                    'val': 600  # 10 minutes in seconds
                })
    
    suggestions['recommended_rules'] = rules
    
    # Add relevant examples to suggestions if found
    if relevant_examples:
        suggestions['relevant_examples'] = relevant_examples[:2]  # Limit to 2 examples
    
    # Generate next steps
    next_steps = []
    
    if intent_details.get('intent_confidence') == 'low':
        next_steps.append("Clarify the specific targeting criteria")
        next_steps.append("Specify geographic location if needed")
        next_steps.append("Define behavioral thresholds")
    
    if intent_details.get('geographic') == 'country':
        next_steps.append("Specify the target country (e.g., New Zealand, United States)")
    
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

def generate_segment_definition(query, intent_details, claude_llm=None):
    """
    Generate comprehensive segment definition using Claude.
    
    Args:
        query (str): User's original query
        intent_details (dict): Detected intent details
        claude_llm: Anthropic Claude LLM instance
        
    Returns:
        dict: Definition content with explanation
    """
    if not claude_llm:
        return {
            'title': 'Segment Definition',
            'content': 'Segment definition generation requires Anthropic Claude.',
            'business_value': 'Please use Anthropic Claude for enhanced segment definitions.',
            'best_practices': [],
            'limitations': []
        }
    
    try:
        prompt = f"""User wants to create this Adobe Analytics segment: "{query}"

Detected intent details: {intent_details}

Provide a comprehensive definition and explanation in the following JSON format:
{{
    "title": "Clear, descriptive title for this segment type",
    "content": "Detailed explanation of what this segment captures and measures",
    "business_value": "Why this segment is valuable for business analysis",
    "use_cases": ["list of specific business use cases"],
    "best_practices": ["list of best practices for this segment type"],
    "limitations": ["potential limitations or considerations"],
    "related_segments": ["suggestions for related segments"],
    "data_requirements": "what data is needed for this segment"
}}

Focus on:
1. Clear, educational explanation
2. Business value and use cases
3. Adobe Analytics best practices
4. Practical considerations
5. Related segment suggestions

Return only valid JSON, no additional text."""

        response = claude_llm.invoke(prompt)
        
        # Parse Claude's response
        import json
        try:
            definition = json.loads(response.content.strip())
            return definition
            
        except json.JSONDecodeError:
            # Fallback definition
            return {
                'title': 'Segment Definition',
                'content': f'This segment will capture {intent_details.get("target_audience", "visitors")} based on the specified conditions.',
                'business_value': 'Segments help you analyze specific user groups and their behavior patterns.',
                'use_cases': ['User behavior analysis', 'Targeted marketing', 'Performance optimization'],
                'best_practices': ['Keep segments focused', 'Use clear naming conventions', 'Test segments before deployment'],
                'limitations': ['Segment performance depends on data quality', 'Complex segments may impact query performance']
            }
            
    except Exception as e:
        print(f"Error generating segment definition: {e}")
        return {
            'title': 'Segment Definition',
            'content': 'Unable to generate definition at this time.',
            'business_value': 'Please try again or use the standard segment builder.',
            'use_cases': [],
            'best_practices': [],
            'limitations': []
        }



def generate_enhanced_segment_suggestions(query, intent_details, claude_llm=None):
    """
    Generate intelligent segment suggestions using Claude.
    
    Args:
        query (str): User's original query
        intent_details (dict): Detected intent details (potentially enhanced by Claude)
        claude_llm: Anthropic Claude LLM instance
        
    Returns:
        dict: Enhanced suggestions with Claude's intelligence
    """
    if not claude_llm or not intent_details.get('claude_enhanced'):
        # Fallback to standard suggestions
        return generate_segment_suggestions(intent_details)
    
    try:
        prompt = f"""Create Adobe Analytics segment suggestions for: "{query}"

Intent Analysis: {intent_details}

Generate comprehensive segment suggestions in the following JSON format:
{{
    "segment_name": "Optimal, descriptive segment name",
    "segment_description": "Clear, detailed description of what this segment captures",
    "recommended_rules": [
        {{
            "name": "Rule name (e.g., 'Mobile Device Type')",
            "func": "Adobe Analytics function (e.g., 's.eq')",
            "value": "Rule value (e.g., 'Mobile')",
            "description": "What this rule does",
            "business_rationale": "Why this rule is important"
        }}
    ],
    "alternative_configurations": [
        {{
            "name": "Alternative segment name",
            "description": "Alternative approach description",
            "rules": ["list of alternative rules"],
            "use_case": "When to use this alternative"
        }}
    ],
    "performance_considerations": [
        "Performance tip 1",
        "Performance tip 2"
    ],
    "best_practices": [
        "Adobe Analytics best practice 1",
        "Adobe Analytics best practice 2"
    ],
    "validation_tips": [
        "How to validate this segment",
        "What to check before deploying"
    ],
    "related_segments": [
        "Related segment suggestion 1",
        "Related segment suggestion 2"
    ],
    "confidence": "high|medium|low",
    "complexity": "simple|moderate|complex"
}}

Focus on:
1. Adobe Analytics best practices and technical accuracy
2. Business context and value
3. Performance optimization
4. Practical implementation guidance
5. Alternative approaches for different use cases

Return only valid JSON, no additional text."""

        response = claude_llm.invoke(prompt)
        
        # Parse Claude's response
        import json
        try:
            claude_suggestions = json.loads(response.content.strip())
            
            # Convert to our standard format with enhancements
            enhanced_suggestions = {
                'segment_name': claude_suggestions.get('segment_name', 'Custom Segment'),
                'segment_description': claude_suggestions.get('segment_description', 'Custom segment configuration'),
                'recommended_rules': claude_suggestions.get('recommended_rules', []),
                'confidence': claude_suggestions.get('confidence', 'medium'),
                'next_steps': [
                    "Review the suggested segment configuration",
                    "Customize segment name and description if needed",
                    "Validate the segment rules",
                    "Test the segment before deployment"
                ],
                'claude_enhanced': True,
                'alternative_configurations': claude_suggestions.get('alternative_configurations', []),
                'performance_considerations': claude_suggestions.get('performance_considerations', []),
                'best_practices': claude_suggestions.get('best_practices', []),
                'validation_tips': claude_suggestions.get('validation_tips', []),
                'related_segments': claude_suggestions.get('related_segments', []),
                'complexity': claude_suggestions.get('complexity', 'simple')
            }
            
            return enhanced_suggestions
            
        except json.JSONDecodeError:
            # Fallback to standard suggestions if Claude returns invalid JSON
            print("Claude returned invalid JSON for suggestions, using fallback")
            return generate_segment_suggestions(intent_details)
            
    except Exception as e:
        print(f"Error generating enhanced suggestions: {e}")
        # Fallback to standard suggestions
        return generate_segment_suggestions(intent_details)

def generate_intelligent_rules(intent_details, claude_llm=None):
    """
    Generate intelligent segment rules using Claude.
    
    Args:
        intent_details (dict): Detected intent details (potentially enhanced by Claude)
        claude_llm: Anthropic Claude LLM instance
        
    Returns:
        dict: Intelligent rules with proper logic and values
    """
    if not claude_llm or not intent_details.get('claude_enhanced'):
        # Fallback to standard rule generation
        return generate_standard_rules(intent_details)
    
    try:
        prompt = f"""Generate Adobe Analytics segment rules for: {intent_details}

Create technically correct, performance-optimized segment rules in the following JSON format:
{{
    "rules": [
        {{
            "name": "Rule name (e.g., 'Mobile Device Type')",
            "func": "Adobe Analytics function (e.g., 's.eq', 's.gt', 's.contains')",
            "value": "Rule value (e.g., 'Mobile', '5', 'California')",
            "description": "What this rule does",
            "business_rationale": "Why this rule is important",
            "performance_impact": "low|medium|high",
            "data_requirement": "What data is needed for this rule"
        }}
    ],
    "logic_operators": [
        {{
            "position": 1,
            "operator": "AND|OR",
            "description": "Why this operator is used"
        }}
    ],
    "alternative_rules": [
        {{
            "name": "Alternative rule name",
            "description": "Alternative approach",
            "use_case": "When to use this alternative",
            "rules": ["list of alternative rules"]
        }}
    ],
    "threshold_suggestions": [
        {{
            "metric": "Metric name (e.g., 'Page Views')",
            "suggested_value": "Suggested threshold",
            "reasoning": "Why this threshold is appropriate",
            "alternatives": ["alternative threshold values"]
        }}
    ],
    "performance_optimization": [
        "Performance optimization tip 1",
        "Performance optimization tip 2"
    ],
    "validation_checks": [
        "Validation check 1",
        "Validation check 2"
    ],
    "complexity": "simple|moderate|complex",
    "estimated_performance": "fast|medium|slow"
}}

Focus on:
1. Adobe Analytics technical accuracy and valid functions
2. Appropriate threshold values based on business context
3. Performance optimization and efficient rule ordering
4. Proper AND/OR logic for complex segments
5. Alternative approaches for different use cases
6. Validation and testing considerations

Use valid Adobe Analytics functions like:
- s.eq (equals)
- s.gt (greater than)
- s.lt (less than)
- s.contains (contains)
- s.exists (exists)
- s.does-not-exist (does not exist)

Return only valid JSON, no additional text."""

        response = claude_llm.invoke(prompt)
        
        # Parse Claude's response
        import json
        try:
            claude_rules = json.loads(response.content.strip())
            
            # Convert to our standard format with enhancements
            intelligent_rules = {
                'rules': claude_rules.get('rules', []),
                'logic_operators': claude_rules.get('logic_operators', []),
                'alternative_rules': claude_rules.get('alternative_rules', []),
                'threshold_suggestions': claude_rules.get('threshold_suggestions', []),
                'performance_optimization': claude_rules.get('performance_optimization', []),
                'validation_checks': claude_rules.get('validation_checks', []),
                'complexity': claude_rules.get('complexity', 'simple'),
                'estimated_performance': claude_rules.get('estimated_performance', 'fast'),
                'claude_enhanced': True
            }
            
            return intelligent_rules
            
        except json.JSONDecodeError:
            # Fallback to standard rules if Claude returns invalid JSON
            print("Claude returned invalid JSON for rules, using fallback")
            return generate_standard_rules(intent_details)
            
    except Exception as e:
        print(f"Error generating intelligent rules: {e}")
        # Fallback to standard rules
        return generate_standard_rules(intent_details)

def generate_standard_rules(intent_details):
    """
    Generate standard segment rules as fallback.
    
    Args:
        intent_details (dict): Detected intent details
        
    Returns:
        dict: Standard rules
    """
    rules = []
    
    # Device rules
    if intent_details.get('device'):
        device = intent_details['device']
        rules.append({
            'name': f'{device.title()} Device Type',
            'func': 's.eq',
            'value': device.title(),
            'description': f'Identifies visitors using {device} devices',
            'business_rationale': f'Focus on {device} user behavior patterns',
            'performance_impact': 'low',
            'data_requirement': 'Device type data'
        })
    
    # Geographic rules
    if intent_details.get('geographic'):
        geo = intent_details['geographic']
        rules.append({
            'name': f'{geo.title()} Location',
            'func': 's.contains',
            'value': geo.title(),
            'description': f'Identifies visitors from {geo}',
            'business_rationale': f'Geographic targeting for {geo}',
            'performance_impact': 'medium',
            'data_requirement': 'Geographic data'
        })
    
    # Behavioral rules
    if intent_details.get('behavioral'):
        for behavior in intent_details['behavioral']:
            if behavior == 'page_views':
                rules.append({
                    'name': 'High Page Views',
                    'func': 's.gt',
                    'value': '5',
                    'description': 'Identifies visitors with more than 5 page views',
                    'business_rationale': 'Engaged users with high page views',
                    'performance_impact': 'medium',
                    'data_requirement': 'Page view data'
                })
            elif behavior == 'time_on_site':
                rules.append({
                    'name': 'Long Session Duration',
                    'func': 's.gt',
                    'value': '600',
                    'description': 'Identifies visitors with session duration > 10 minutes',
                    'business_rationale': 'Engaged users with long session duration',
                    'performance_impact': 'medium',
                    'data_requirement': 'Session duration data'
                })
    
    return {
        'rules': rules,
        'logic_operators': [{'position': 1, 'operator': 'AND', 'description': 'All conditions must be met'}],
        'alternative_rules': [],
        'threshold_suggestions': [],
        'performance_optimization': ['Use specific values for better performance'],
        'validation_checks': ['Test segment performance before deployment'],
        'complexity': 'simple',
        'estimated_performance': 'fast',
        'claude_enhanced': False
    }

# Page configuration
st.set_page_config(page_title="Adobe Experience League Documentation Chatbot", layout="wide", page_icon="🤖")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize page load time for other features
if "page_load_time" not in st.session_state:
    st.session_state.page_load_time = time.time()

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
def setup_direct_llm(provider="Anthropic Claude (Cloud)"):
    """Setup direct LLM without RAG"""
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
                    model_name="llama-3.1-8b-instant",
                    temperature=0.1,
                    max_tokens=4000
                )
                
                # Test the connection with a simple call
                try:
                    test_response = llm.invoke("Hello")
                    st.success("✅ Groq connection successful!")
                except Exception as groq_error:
                    if "rate limit" in str(groq_error).lower() or "quota" in str(groq_error).lower():
                        st.error("❌ Groq rate limit exceeded. Please try again later or switch to another provider.")
                    elif "unauthorized" in str(groq_error).lower() or "invalid" in str(groq_error).lower():
                        st.error("❌ Invalid Groq API key. Please check your API key.")
                    else:
                        st.error(f"❌ Groq connection error: {groq_error}")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error initializing Groq: {e}")
                return None
                
        elif provider == "Anthropic Claude (Cloud)":
            try:
                # Initialize Anthropic Claude LLM
                anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
                if not anthropic_api_key:
                    st.error("❌ Anthropic API key not found. Please add ANTHROPIC_API_KEY to Streamlit secrets.")
                    return None
                
                llm = ChatAnthropic(
                    anthropic_api_key=anthropic_api_key,
                    model_name="claude-3-5-haiku-20241022",  # Claude 3.5 Haiku - Fast and efficient # old: claude-3-5-sonnet-20241022
                    temperature=0.1,
                    max_tokens=4000
                )
                
                # Test the connection with a simple call
                try:
                    test_response = llm.invoke("Hello")

                except Exception as claude_error:
                    if "rate limit" in str(claude_error).lower() or "quota" in str(claude_error).lower():
                        st.error("❌ Anthropic rate limit exceeded. Please try again later or switch to another provider.")
                    elif "unauthorized" in str(claude_error).lower() or "invalid" in str(claude_error).lower():
                        st.error("❌ Invalid Anthropic API key. Please check your API key.")
                    else:
                        st.error(f"❌ Anthropic Claude connection error: {claude_error}")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error initializing Anthropic Claude: {e}")
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
                    st.info("💡 You can switch to 'Groq (Cloud)' or 'Anthropic Claude (Cloud)' in the sidebar for cloud-based responses.")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error initializing Ollama: {e}")
                return None
        
        return llm
    except Exception as e:
        st.error(f"❌ Error setting up direct LLM: {e}")
        return None

@st.cache_resource
def setup_qa_chain(_vectorstore, provider="Anthropic Claude (Cloud)"):
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
                    model_name="llama-3.1-8b-instant",
                    temperature=0.1
                )
                
                # Test the connection with a simple call
                try:
                    test_response = llm.invoke("Hello")
                    st.success("✅ Groq connection successful!")
                except Exception as groq_error:
                    if "rate limit" in str(groq_error).lower() or "quota" in str(groq_error).lower():
                        st.error("❌ Groq rate limit exceeded. Please try again later or switch to another provider.")
                    elif "unauthorized" in str(groq_error).lower() or "invalid" in str(groq_error).lower():
                        st.error("❌ Invalid Groq API key. Please check your API key.")
                    else:
                        st.error(f"❌ Groq connection error: {groq_error}")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error initializing Groq: {e}")
                return None
                
        elif provider == "Anthropic Claude (Cloud)":
            try:
                # Initialize Anthropic Claude LLM
                anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
                if not anthropic_api_key:
                    st.error("❌ Anthropic API key not found. Please add ANTHROPIC_API_KEY to Streamlit secrets.")
                    return None
                
                llm = ChatAnthropic(
                    anthropic_api_key=anthropic_api_key,
                    model_name="claude-3-5-haiku-20241022",  # Claude 3.5 Haiku - Fast and efficient
                    temperature=0.1,
                    max_tokens=4000
                )
                
                # Test the connection with a simple call
                try:
                    test_response = llm.invoke("Hello")

                except Exception as claude_error:
                    if "rate limit" in str(claude_error).lower() or "quota" in str(claude_error).lower():
                        st.error("❌ Anthropic rate limit exceeded. Please try again later or switch to another provider.")
                    elif "unauthorized" in str(claude_error).lower() or "invalid" in str(claude_error).lower():
                        st.error("❌ Invalid Anthropic API key. Please check your API key.")
                    else:
                        st.error(f"❌ Anthropic Claude connection error: {claude_error}")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error initializing Anthropic Claude: {e}")
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
                    st.info("💡 You can switch to 'Groq (Cloud)' or 'Anthropic Claude (Cloud)' in the sidebar for cloud-based responses.")
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

def generate_direct_response_stream(question, llm, provider):
    """Generate streaming response using direct LLM approach"""
    try:
        # Create a comprehensive prompt for direct LLM
        if provider == "Anthropic Claude (Cloud)":
            direct_prompt = f"""You are an expert on Adobe Experience League solutions including Adobe Analytics, Adobe Experience Manager, Adobe Target, Customer Journey Analytics, and other Adobe Experience Cloud products.

Question: {question}

Please provide a comprehensive and accurate answer based on your knowledge of Adobe Experience League solutions. Include specific details, best practices, and implementation guidance where relevant.

Answer:"""
        else:
            direct_prompt = f"""You are a helpful assistant that answers questions about Adobe Experience League solutions.

Question: {question}

Please provide a comprehensive answer based on your knowledge of Adobe Experience League solutions. Be helpful and accurate in your response.

Answer:"""
        
        # Use streaming for faster response
        for chunk in llm.stream(direct_prompt):
            # Handle different response types properly
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
            elif isinstance(chunk, str):
                yield chunk
            elif hasattr(chunk, 'text'):
                yield chunk.text
            else:
                # Fallback: convert to string
                yield str(chunk)
                
    except Exception as e:
        yield f"Error generating direct response: {str(e)}"

def generate_direct_response(question, llm, provider):
    """Generate response using direct LLM approach (non-streaming fallback)"""
    try:
        # Create a comprehensive prompt for direct LLM
        if provider == "Anthropic Claude (Cloud)":
            direct_prompt = f"""You are an expert on Adobe Experience League solutions including Adobe Analytics, Adobe Experience Manager, Adobe Target, Customer Journey Analytics, and other Adobe Experience Cloud products.

Question: {question}

Please provide a comprehensive and accurate answer based on your knowledge of Adobe Experience League solutions. Include specific details, best practices, and implementation guidance where relevant.

Answer:"""
        else:
            direct_prompt = f"""You are a helpful assistant that answers questions about Adobe Experience League solutions.

Question: {question}

Please provide a comprehensive answer based on your knowledge of Adobe Experience League solutions. Be helpful and accurate in your response.

Answer:"""
        
        response = llm.invoke(direct_prompt)
        
        return {
            "result": response.content,
            "source_documents": [],
            "method": f"Direct {provider}"
        }
    except Exception as e:
        return {
            "result": f"Error generating direct response: {str(e)}",
            "source_documents": [],
            "method": f"Direct {provider}"
        }

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
        st.info(f"**Suggested Name:** {suggestions.get('segment_name', 'New Segment')}")
        st.info(f"**Suggested Description:** {suggestions.get('segment_description', '')}")
        st.info(f"**Recommended Rules:** {len(suggestions.get('recommended_rules', []))} rules")
        
        # Show next steps
        st.subheader("🔄 Next Steps")
        for i, step in enumerate(suggestions.get('next_steps', []), 1):
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
                # Set the current workflow step to segment builder
                st.session_state.current_workflow = 'segment_builder'
                st.rerun()
        
        with col2:
            if st.button("💬 Ask More Questions", type="secondary"):
                st.info("Feel free to ask more questions about Adobe Analytics or other topics!")
    
    else:
        st.error("❌ Unable to parse segment creation intent. Please try rephrasing your request.")
        st.info("💡 Example: 'Create a segment for mobile users from California'")


def render_segment_creation_workflow():
    """Render the segment creation workflow within the main app."""
    
    # Header for segment creation
    st.header("🚀 Creating Your Segment")
    st.caption("Executing segment creation in Adobe Analytics")
    
    # Back to segment builder button
    if st.button("← Back to Segment Builder", type="secondary"):
        st.session_state.current_workflow = 'segment_builder'
        st.rerun()
    
    # Check if we have segment configuration
    if 'segment_config' not in st.session_state:
        st.error("❌ No segment configuration found. Please go back to the segment builder.")
        return
    
    segment_config = st.session_state.segment_config
    
    # Display configuration summary
    st.subheader("📋 Configuration Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Segment Name", segment_config['name'])
        st.metric("RSID", segment_config['rsid'])
    
    with col2:
        st.metric("Target Audience", segment_config['target_audience'])
        st.metric("Rules Count", len(segment_config['rules']))
    
    # Display full configuration
    with st.expander("🔍 View Full Configuration"):
        st.json(segment_config)
    
    # Create segment button
    if st.button("🎯 Create Segment in Adobe Analytics", type="primary"):
        with st.spinner("🚀 Creating your segment in Adobe Analytics..."):
            try:
                # Import the Adobe API function
                from adobe_api import create_analytics_segment_from_json
                
                # Transform rules to proper Adobe Analytics format
                adobe_definition = {
                    "container": {
                        "type": segment_config['target_audience'],
                        "rules": segment_config['rules']
                    }
                }
                
                # Build the proper Adobe Analytics payload
                adobe_payload = {
                    "name": segment_config['name'],
                    "description": segment_config['description'],
                    "rsid": segment_config['rsid'],
                    "definition": adobe_definition
                }
                
                # Display the Adobe Analytics format
                st.subheader("🔍 Adobe Analytics Segment Format")
                st.info("This is the exact format that will be sent to Adobe Analytics:")
                st.json(adobe_payload)
                
                # Create the segment
                result = create_analytics_segment_from_json(adobe_payload)
                
                if result.get('status') == 'success':
                    st.success("🎉 Segment created successfully!")
                    
                    # Display segment details
                    segment_data = result.get('data', {})
                    st.subheader("✅ Segment Created")
                    st.json(segment_data)
                    
                    # Show segment ID
                    if 'id' in segment_data:
                        st.info(f"**Segment ID:** {segment_data['id']}")
                    
                    # Success message with prominent redirect
                    st.success("Your segment has been created in Adobe Analytics and is ready to use!")
                    
                    # Store success state
                    st.session_state.segment_created_successfully = True
                    st.session_state.created_segment_data = segment_data
                    
                    # Success completion message
                    st.balloons()  # Celebrate the success!
                    
                    # Prominent redirect section
                    st.markdown("---")
                    st.subheader("🎯 What would you like to do next?")
                    
                    # Action buttons in columns
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        if st.button("🏠 Return to Main Chat", type="primary", key="redirect_main", use_container_width=True):
                            # Clear all workflow state and redirect
                            st.session_state.current_workflow = 'chat'
                            if 'segment_intent' in st.session_state:
                                del st.session_state.segment_intent
                            if 'segment_config' in st.session_state:
                                del st.session_state.segment_config
                            if 'segment_created_successfully' in st.session_state:
                                del st.session_state.segment_created_successfully
                            if 'created_segment_data' in st.session_state:
                                del st.session_state.created_segment_data
                            st.rerun()
                    
                    with col2:
                        if st.button("📊 Create Another Segment", type="secondary", key="create_another", use_container_width=True):
                            # Go back to segment builder to create another segment
                            st.session_state.current_workflow = 'segment_builder'
                            if 'segment_config' in st.session_state:
                                del st.session_state.segment_config
                            st.rerun()
                    
                    with col3:
                        if st.button("📋 View Segment Details", type="secondary", key="view_details", use_container_width=True):
                            st.session_state.show_segment_details = True
                            st.rerun()
                    
                    # Show segment details if requested
                    if st.session_state.get('show_segment_details', False):
                        with st.expander("📋 Segment Details", expanded=True):
                            st.json(segment_data)
                            if st.button("Close Details", key="close_details"):
                                st.session_state.show_segment_details = False
                                st.rerun()
                
                else:
                    st.error("❌ Failed to create segment")
                    st.error(f"Error: {result.get('message', 'Unknown error')}")
                    
                    # Show the payload that was sent for debugging
                    st.subheader("🔍 Debug: Payload Sent")
                    st.json(adobe_payload)
                    
            except Exception as e:
                st.error("❌ Error during segment creation")
                st.error(f"Exception: {type(e).__name__}")
                st.error(f"Message: {str(e)}")
                
                # Show the payload that was attempted for debugging
                st.subheader("🔍 Debug: Payload Attempted")
                try:
                    adobe_definition = {
                        "container": {
                            "type": segment_config['target_audience'],
                            "rules": segment_config['rules']
                        }
                    }
                    adobe_payload = {
                        "name": segment_config['name'],
                        "description": segment_config['description'],
                        "rsid": segment_config['rsid'],
                        "definition": adobe_definition
                    }
                    st.json(adobe_payload)
                except:
                    st.error("Could not generate payload for debugging")
                
                # Back to segment builder button
                if st.button("← Back to Segment Builder", type="secondary"):
                    st.session_state.current_workflow = 'segment_builder'
                    st.rerun()


def render_segment_builder_workflow():
    """Render the segment builder workflow within the main app."""
    
    # Header for segment builder
    st.header("🔧 Segment Builder")
    st.caption("Create and configure your Adobe Analytics segment")
    
    # Back to main app button
    if st.button("← Back to Main Chat", type="secondary"):
        st.session_state.current_workflow = 'chat'
        st.rerun()
    
    # Check if we have segment intent data
    if 'segment_intent' not in st.session_state:
        st.error("❌ No segment creation intent found. Please go back to the main chat.")
        return
    
    intent_data = st.session_state.segment_intent
    
    # Display segment definition first (if available from Claude)
    if intent_data.get('definition') and intent_data.get('claude_enhanced'):
        st.subheader("📖 Segment Definition")
        
        definition = intent_data['definition']
        
        # Display definition in an expandable section
        with st.expander(f"🎯 {definition.get('title', 'Segment Definition')}", expanded=True):
            st.markdown(f"**What this segment captures:**")
            st.info(definition.get('content', 'No content available'))
            
            st.markdown(f"**Business Value:**")
            st.success(definition.get('business_value', 'No business value specified'))
            
            if definition.get('use_cases'):
                st.markdown(f"**Use Cases:**")
                for use_case in definition.get('use_cases', []):
                    st.markdown(f"• {use_case}")
            
            if definition.get('best_practices'):
                st.markdown(f"**Best Practices:**")
                for practice in definition.get('best_practices', []):
                    st.markdown(f"✅ {practice}")
            
            if definition.get('limitations'):
                st.markdown(f"**Considerations:**")
                for limitation in definition.get('limitations', []):
                    st.markdown(f"⚠️ {limitation}")
            
            if definition.get('related_segments'):
                st.markdown(f"**Related Segments:**")
                for related in definition.get('related_segments', []):
                    st.markdown(f"🔗 {related}")
        
        st.markdown("---")
    
    # Display detected intent
    st.subheader("📊 Detected Intent")
    
    # Show Claude enhancement indicator
    if intent_data.get('claude_enhanced'):
        st.success("🧠 Enhanced with Anthropic Claude analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Target Audience", intent_data.get('action_details', {}).get('target_audience', 'visitors').title())
        if intent_data.get('action_details', {}).get('device'):
            st.metric("Device Type", intent_data.get('action_details', {})['device'].title())
        if intent_data.get('action_details', {}).get('complexity'):
            st.metric("Complexity", intent_data.get('action_details', {})['complexity'].title())
    
    with col2:
        if intent_data.get('action_details', {}).get('geographic'):
            st.metric("Geographic", intent_data.get('action_details', {})['geographic'].title())
        if intent_data.get('action_details', {}).get('time_based'):
            st.metric("Time-based", intent_data.get('action_details', {})['time_based'].replace('_', ' ').title())
        if intent_data.get('action_details', {}).get('intent_confidence'):
            st.metric("Confidence", intent_data.get('action_details', {})['intent_confidence'].title())
    
    # Display Claude's enhanced analysis if available
    if intent_data.get('claude_enhanced'):
        enhanced_details = intent_data.get('action_details', {})
        
        if enhanced_details.get('business_context'):
            st.markdown("**🎯 Business Context:**")
            st.info(enhanced_details['business_context'])
        
        if enhanced_details.get('business_value'):
            st.markdown("**💼 Business Value:**")
            st.success(enhanced_details['business_value'])
        
        if enhanced_details.get('recommended_approach'):
            st.markdown("**🚀 Recommended Approach:**")
            st.info(enhanced_details['recommended_approach'])
        
        if enhanced_details.get('conditions'):
            st.markdown("**📋 Detected Conditions:**")
            for condition in enhanced_details['conditions']:
                st.markdown(f"• {condition}")
        
        if enhanced_details.get('behavioral'):
            st.markdown("**🎭 Behavioral Patterns:**")
            for behavior in enhanced_details['behavioral']:
                st.markdown(f"• {behavior.replace('_', ' ').title()}")
        
        if enhanced_details.get('custom_variables'):
            st.markdown("**🔧 Custom Variables:**")
            for var in enhanced_details['custom_variables']:
                st.markdown(f"• {var}")
        
        st.markdown("---")
    
    # Display relevant examples from vector database
    if 'relevant_examples' in intent_data.get('suggestions', {}) and intent_data.get('suggestions', {}).get('relevant_examples'):
        st.subheader("📚 Relevant Segment Examples")
        st.info("Based on your request, here are some relevant segment examples from our database:")
        
        for i, example in enumerate(intent_data.get('suggestions', {}).get('relevant_examples', [])):
            with st.expander(f"📋 {example.get('name', 'Example Segment')}", expanded=False):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Description:** {example.get('description', 'No description')}")
                    st.write(f"**Context:** {example.get('context', 'Not specified')}")
                    st.write(f"**Predicate Function:** {example.get('pred_func', 'Not specified')}")
                
                with col2:
                    st.write(f"**Source:** {example.get('source', 'Unknown')}")
                    if example.get('rsid'):
                        st.write(f"**RSID:** {example['rsid']}")
                
                # Show the example structure
                st.write("**Example Structure:**")
                st.code(json.dumps({
                    "name": example.get('name'),
                    "description": example.get('description'),
                    "context": example.get('context'),
                    "pred_func": example.get('pred_func')
                }, indent=2), language="json")
    
    # Display enhanced suggestions if available
    if intent_data.get('suggestions', {}).get('claude_enhanced'):
        st.subheader("🧠 Enhanced Suggestions")
        st.success("✨ Powered by Anthropic Claude for intelligent segment recommendations")
        
        suggestions = intent_data.get('suggestions', {})
        
        # Show alternative configurations
        if suggestions.get('alternative_configurations'):
            st.markdown("**🔄 Alternative Configurations:**")
            for i, alt in enumerate(suggestions['alternative_configurations'], 1):
                with st.expander(f"Option {i}: {alt.get('name', 'Alternative')}", expanded=False):
                    st.write(f"**Description:** {alt.get('description', 'No description')}")
                    st.write(f"**Use Case:** {alt.get('use_case', 'Not specified')}")
                    if alt.get('rules'):
                        st.write("**Rules:**")
                        for rule in alt['rules']:
                            st.markdown(f"• {rule}")
        
        # Show performance considerations
        if suggestions.get('performance_considerations'):
            st.markdown("**⚡ Performance Considerations:**")
            for consideration in suggestions['performance_considerations']:
                st.markdown(f"• {consideration}")
        
        # Show best practices
        if suggestions.get('best_practices'):
            st.markdown("**✅ Best Practices:**")
            for practice in suggestions['best_practices']:
                st.markdown(f"• {practice}")
        
        # Show validation tips
        if suggestions.get('validation_tips'):
            st.markdown("**🔍 Validation Tips:**")
            for tip in suggestions['validation_tips']:
                st.markdown(f"• {tip}")
        
        # Show related segments
        if suggestions.get('related_segments'):
            st.markdown("**🔗 Related Segments:**")
            for related in suggestions['related_segments']:
                st.markdown(f"• {related}")
        
        st.markdown("---")
    
    # Display intelligent rules if available
    if intent_data.get('intelligent_rules') and intent_data.get('claude_enhanced'):
        st.subheader("🧠 Intelligent Rules")
        st.success("✨ Powered by Anthropic Claude for intelligent rule generation")
        
        intelligent_rules = intent_data['intelligent_rules']
        
        # Show rules with detailed information
        if intelligent_rules.get('rules'):
            st.markdown("**📋 Generated Rules:**")
            for i, rule in enumerate(intelligent_rules['rules'], 1):
                with st.expander(f"Rule {i}: {rule.get('name', 'Unnamed Rule')}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Function:** `{rule.get('func', 'N/A')}`")
                        st.write(f"**Value:** `{rule.get('value', 'N/A')}`")
                        st.write(f"**Description:** {rule.get('description', 'No description')}")
                    
                    with col2:
                        st.write(f"**Performance Impact:** {rule.get('performance_impact', 'N/A').title()}")
                        st.write(f"**Data Requirement:** {rule.get('data_requirement', 'N/A')}")
                        st.write(f"**Business Rationale:** {rule.get('business_rationale', 'N/A')}")
        
        # Show logic operators
        if intelligent_rules.get('logic_operators'):
            st.markdown("**🔗 Logic Operators:**")
            for op in intelligent_rules['logic_operators']:
                st.markdown(f"• **{op.get('operator', 'N/A')}** - {op.get('description', 'No description')}")
        
        # Show threshold suggestions
        if intelligent_rules.get('threshold_suggestions'):
            st.markdown("**📊 Threshold Suggestions:**")
            for threshold in intelligent_rules['threshold_suggestions']:
                with st.expander(f"Threshold: {threshold.get('metric', 'Unknown Metric')}", expanded=False):
                    st.write(f"**Suggested Value:** {threshold.get('suggested_value', 'N/A')}")
                    st.write(f"**Reasoning:** {threshold.get('reasoning', 'No reasoning provided')}")
                    if threshold.get('alternatives'):
                        st.write("**Alternatives:**")
                        for alt in threshold['alternatives']:
                            st.markdown(f"• {alt}")
        
        # Show alternative rules
        if intelligent_rules.get('alternative_rules'):
            st.markdown("**🔄 Alternative Rules:**")
            for i, alt in enumerate(intelligent_rules['alternative_rules'], 1):
                with st.expander(f"Alternative {i}: {alt.get('name', 'Unnamed Alternative')}", expanded=False):
                    st.write(f"**Description:** {alt.get('description', 'No description')}")
                    st.write(f"**Use Case:** {alt.get('use_case', 'No use case specified')}")
                    if alt.get('rules'):
                        st.write("**Rules:**")
                        for rule in alt['rules']:
                            st.markdown(f"• {rule}")
        
        # Show performance optimization
        if intelligent_rules.get('performance_optimization'):
            st.markdown("**⚡ Performance Optimization:**")
            for tip in intelligent_rules['performance_optimization']:
                st.markdown(f"• {tip}")
        
        # Show validation checks
        if intelligent_rules.get('validation_checks'):
            st.markdown("**🔍 Validation Checks:**")
            for check in intelligent_rules['validation_checks']:
                st.markdown(f"• {check}")
        
        # Show complexity and performance estimates
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Complexity", intelligent_rules.get('complexity', 'N/A').title())
        with col2:
            st.metric("Estimated Performance", intelligent_rules.get('estimated_performance', 'N/A').title())
        
        st.markdown("---")
    
    # Segment configuration
    st.subheader("⚙️ Segment Configuration")
    
    # Basic information with real-time validation
    segment_name = st.text_input(
        "Segment Name",
        value=intent_data.get('suggestions', {}).get('segment_name', 'New Segment'),
        help="Enter a descriptive name for your segment",
        key="app_segment_name_input"
    )
    
    # Basic name validation
    if not segment_name or len(segment_name.strip()) < 3:
        st.error("❌ Segment name must be at least 3 characters long")
        return None
    
    segment_description = st.text_area(
        "Description",
        value=intent_data.get('suggestions', {}).get('segment_description', ''),
        help="Describe what this segment targets",
        key="app_segment_description_input"
    )
    
    rsid = st.text_input(
        "Report Suite ID (RSID)",
        value="argupaepdemo",
        help="Enter your Adobe Analytics Report Suite ID",
        key="app_segment_rsid_input"
    )
    
    # Basic RSID validation
    if not rsid or len(rsid.strip()) < 3:
        st.error("❌ RSID must be at least 3 characters long")
        return None
    
    target_audience = st.selectbox(
        "Target Audience",
        options=["visitors", "visits", "hits"],
        index=0,
        help="Select the context for your segment",
        key="app_segment_target_audience_input"
    )
    
    # Rules configuration
    st.subheader("📋 Segment Rules")
    st.info("Configure the rules that define your segment")
    
    # Dynamic rule configuration based on detected intent
    intent_details = intent_data.get('action_details', {})
    configured_rules = []
    
    # Geographic rule configuration
    if intent_details.get('geographic'):
        st.write("**🌍 Geographic Targeting**")
        if intent_details['geographic'] == 'country':
            country_input = st.text_input(
                "Target Country",
                value="New Zealand",
                help="Enter the target country (e.g., New Zealand, United States, Australia)",
                key="country_input"
            )
            if country_input:
                configured_rules.append({
                    'func': 'streq',
                    'name': 'variables/geocountry',
                    'val': country_input,
                    'str': country_input,
                    'type': 'geographic',
                    'description': f'Users from {country_input}'
                })
        
        elif intent_details['geographic'] == 'city':
            city_input = st.text_input(
                "Target City",
                help="Enter the target city",
                key="city_input"
            )
            if city_input:
                configured_rules.append({
                    'func': 'streq',
                    'name': 'variables/geocity',
                    'val': city_input,
                    'str': city_input,
                    'type': 'geographic',
                    'description': f'Users from {city_input}'
                })
        
        elif intent_details['geographic'] == 'state':
            state_input = st.text_input(
                "Target State/Province",
                help="Enter the target state or province",
                key="state_input"
            )
            if state_input:
                configured_rules.append({
                    'func': 'streq',
                    'name': 'variables/georegion',
                    'val': state_input,
                    'str': state_input,
                    'type': 'geographic',
                    'description': f'Users from {state_input}'
                })
    
    # Device rule configuration
    if intent_details.get('device'):
        st.write("**📱 Device Targeting**")
        device_options = ["Mobile", "Desktop", "Tablet"]
        device_input = st.selectbox(
            "Target Device Type",
            options=device_options,
            index=device_options.index(intent_details['device'].title()) if intent_details['device'].title() in device_options else 0,
            help="Select the target device type",
            key="device_input"
        )
        
        # Device detection method selection
        device_method = st.selectbox(
            "Device Detection Method",
            options=[
                "Custom eVar (e.g., evar1, evar2)",
                "Built-in Mobile Device Variable",
                "Mobile Device Type Variable"
            ],
            index=0,
            help="Select how device type is detected in your implementation",
            key="device_method"
        )
        
        if device_method == "Custom eVar (e.g., evar1, evar2)":
            device_evar = st.text_input(
                "Device Type eVar (e.g., evar1, evar2)",
                value="evar1",
                help="Enter the eVar that stores device type information",
                key="device_evar_input"
            )
            
            if device_input and device_evar:
                configured_rules.append({
                    'func': 'streq',
                    'name': f'variables/{device_evar}',
                    'val': device_input,
                    'str': device_input,
                    'type': 'device',
                    'description': f'Users on {device_input} devices'
                })
        
        elif device_method == "Built-in Mobile Device Variable":
            if device_input == "Mobile":
                configured_rules.append({
                    'func': 'streq',
                    'name': 'variables/mobiledevice',
                    'val': '1',
                    'str': '1',
                    'type': 'device',
                    'description': f'Users on {device_input} devices'
                })
            elif device_input == "Desktop":
                configured_rules.append({
                    'func': 'not-streq',
                    'name': 'variables/mobiledevice',
                    'val': '1',
                    'str': '1',
                    'type': 'device',
                    'description': f'Users on {device_input} devices'
                })
            else:  # Tablet
                configured_rules.append({
                    'func': 'streq',
                    'name': 'variables/mobiledevice',
                    'val': '2',
                    'str': '2',
                    'type': 'device',
                    'description': f'Users on {device_input} devices'
                })
        
        elif device_method == "Mobile Device Type Variable":
            if device_input == "Mobile":
                configured_rules.append({
                    'func': 'streq',
                    'name': 'variables/mobiledevicetype',
                    'val': 'Mobile',
                    'str': 'Mobile',
                    'type': 'device',
                    'description': f'Users on {device_input} devices'
                })
            elif device_input == "Desktop":
                configured_rules.append({
                    'func': 'streq',
                    'name': 'variables/mobiledevicetype',
                    'val': 'Desktop',
                    'str': 'Desktop',
                    'type': 'device',
                    'description': f'Users on {device_input} devices'
                })
            else:  # Tablet
                configured_rules.append({
                    'func': 'streq',
                    'name': 'variables/mobiledevicetype',
                    'val': 'Tablet',
                    'str': 'Tablet',
                    'type': 'device',
                    'description': f'Users on {device_input} devices'
                })
    
    # Behavioral rule configuration
    if intent_details.get('behavioral'):
        st.write("**📊 Behavioral Targeting**")
        
        for i, behavior in enumerate(intent_details['behavioral']):
            if behavior == 'page_views':
                page_views_threshold = st.number_input(
                    "Minimum Page Views",
                    min_value=1,
                    value=5,
                    help="Enter the minimum number of page views required",
                    key=f"page_views_{i}"
                )
                
                if page_views_threshold:
                    configured_rules.append({
                        'func': 'gt',
                        'name': 'metrics/pageviews',
                        'val': page_views_threshold,
                        'type': 'behavioral',
                        'description': f'Users with more than {page_views_threshold} page views'
                    })
            
            elif behavior == 'time_on_site':
                time_threshold = st.number_input(
                    "Minimum Session Duration (seconds)",
                    min_value=1,
                    value=600,
                    help="Enter the minimum session duration in seconds",
                    key=f"time_threshold_{i}"
                )
                
                if time_threshold:
                    configured_rules.append({
                        'func': 'gt',
                        'name': 'metrics/timeonsite',
                        'val': time_threshold,
                        'type': 'behavioral',
                        'description': f'Users with session duration > {time_threshold} seconds'
                    })
            
            elif behavior == 'conversion':
                conversion_event = st.text_input(
                    "Conversion Event Name",
                    value="purchase",
                    help="Enter the name of the conversion event (e.g., purchase, signup)",
                    key=f"conversion_event_{i}"
                )
                
                if conversion_event:
                    configured_rules.append({
                        'func': 'event-exists',
                        'evt': {
                            'func': 'event',
                            'name': f'metrics/{conversion_event}'
                        },
                        'type': 'behavioral',
                        'description': f'Users who completed {conversion_event}'
                    })
            
            elif behavior == 'cart':
                cart_event = st.text_input(
                    "Cart Event Name",
                    value="add_to_cart",
                    help="Enter the name of the cart event",
                    key=f"cart_event_{i}"
                )
                
                if cart_event:
                    configured_rules.append({
                        'func': 'event-exists',
                        'evt': {
                            'func': 'event',
                            'name': f'metrics/{cart_event}'
                        },
                        'type': 'behavioral',
                        'description': f'Users who added items to cart'
                    })
    
    # Custom eVar configuration
    if intent_details.get('custom_variables'):
        st.write("**🔧 Custom Variable Targeting**")
        
        for i, custom_var in enumerate(intent_details['custom_variables']):
            st.write(f"**Custom Variable {i+1}**")
            
            evar_name = st.text_input(
                f"eVar Name (e.g., evar1, evar2)",
                key=f"evar_name_{i}",
                help="Enter the eVar name"
            )
            
            evar_value = st.text_input(
                f"eVar Value",
                key=f"evar_value_{i}",
                help="Enter the value to match"
            )
            
            if evar_name and evar_value:
                configured_rules.append({
                    'func': 'streq',
                    'name': f'variables/{evar_name}',
                    'val': evar_value,
                    'str': evar_value,
                    'type': 'custom',
                    'description': f'Users with {evar_name} = {evar_value}'
                })
    
    # Time-based rule configuration
    if intent_details.get('time_based'):
        st.write("**⏰ Time-based Targeting**")
        
        if intent_details['time_based'] == 'day_of_week':
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_days = st.multiselect(
                "Select Days of Week",
                options=days,
                default=["Saturday", "Sunday"],
                help="Select the days of the week to target",
                key="days_of_week"
            )
            
            if selected_days:
                configured_rules.append({
                    'func': 'streq-in',
                    'name': 'variables/dayofweek',
                    'list': selected_days,
                    'type': 'time_based',
                    'description': f'Users visiting on {", ".join(selected_days)}'
                })
        
        elif intent_details['time_based'] == 'time_of_day':
            time_ranges = [
                "Early Morning (6AM-9AM)",
                "Morning (9AM-12PM)", 
                "Afternoon (12PM-5PM)",
                "Evening (5PM-9PM)",
                "Night (9PM-6AM)"
            ]
            selected_times = st.multiselect(
                "Select Time Ranges",
                options=time_ranges,
                help="Select the time ranges to target",
                key="time_ranges"
            )
            
            if selected_times:
                configured_rules.append({
                    'func': 'streq-in',
                    'name': 'variables/hourofday',
                    'list': selected_times,
                    'type': 'time_based',
                    'description': f'Users visiting during {", ".join(selected_times)}'
                })
    
    # Basic validation and preview
    if not configured_rules:
        st.warning("⚠️ Please add at least one rule to your segment")
        return None
    
    # Create segment config for preview
    segment_config = {
        'name': segment_name,
        'description': segment_description,
        'rsid': rsid,
        'target_audience': target_audience,
        'rules': configured_rules
    }
    
    # Show preview
    st.subheader("📊 Segment Preview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Name:** {segment_name}")
        st.info(f"**Description:** {segment_description}")
    
    with col2:
        st.info(f"**RSID:** {rsid}")
        st.info(f"**Target:** {target_audience}")
    
    # Show rules
    st.subheader("📋 Rules")
    for i, rule in enumerate(configured_rules, 1):
        with st.expander(f"Rule {i}: {rule.get('description', 'Custom Rule')}"):
            st.json(rule)
    
    return segment_config

def main():
    """Main Streamlit app"""
    
    # Initialize session state for workflow management
    if 'current_workflow' not in st.session_state:
        st.session_state.current_workflow = 'chat'
    
    
    # Header
    st.title("🤖 Adobe Experience League Documentation Chatbot")
    st.caption("This chatbot is powered by local open-source models and Adobe's official documentation.")
    
    
    # Sidebar for controls and information
    with st.sidebar:
        st.header("About")
        st.markdown("This POC demonstrates a chatbot built with LangChain and multiple LLM providers, powered by Adobe Experience League documentation")
        
        st.markdown("""
        **Tech Stack:**
        - **FAISS Vector Store**: For semantic search
        - **LLM Providers**: Anthropic Claude (Direct Mode), Groq (RAG Mode), Ollama (RAG Mode)
        - **Smart Mode Selection**: Automatic based on provider choice
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
            ["Anthropic Claude (Cloud)", "Groq (Cloud)", "Ollama (Local)"],
            key="llm_provider"
        )
        
        # Automatically determine response mode based on provider
        if llm_provider == "Anthropic Claude (Cloud)":
            response_mode = "Direct LLM (No RAG)"
            st.info("🧠 **Direct Mode**: Anthropic Claude uses its training data directly for comprehensive responses without document retrieval.")
        else:
            response_mode = "RAG (Adobe Docs + Stack Overflow)"
            st.info("🔍 **RAG Mode**: Uses your ingested Adobe documentation and Stack Overflow data for context-aware responses with source attribution.")
        
        
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
    
    # Welcome message for new users with close button
    if not st.session_state.messages:
        # Initialize welcome message state
        if "show_welcome" not in st.session_state:
            st.session_state.show_welcome = True
        
        if st.session_state.show_welcome:
            st.markdown("---")
            
            # Create a container for the tips box with close button
            tips_container = st.container()
            with tips_container:
                col1, col2 = st.columns([10, 1])
                
                with col1:
                    st.info("""
                    🎉 **Welcome to Adobe Experience League Documentation Chatbot!**
                    
                    **💡 Tips:**
                    - Ask questions about Adobe Experience League solutions features, implementation, or best practices
                    - Use the sidebar to quickly access common questions
                    - Multiple LLM providers available: Anthropic Claude (default, direct mode), Groq (RAG mode), Ollama (RAG mode)
                    - Automatic mode selection: Claude uses direct responses, others use RAG with Adobe docs
                    - Use reactions (👍👎💡) to provide feedback on responses
                    
                    **🚀 Getting Started:**
                    Try asking: "What is Adobe Analytics?" or "How do I implement tracking?"
                    """)
                
                with col2:
                    if st.button("❌", key="close_tips", help="Close tips"):
                        st.session_state.show_welcome = False
                        st.rerun()
    
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
                message_idx = st.session_state.messages.index(message)
                # Create unique key that includes message content hash to avoid duplicates
                message_content_hash = hash(message["content"]) % 10000
                unique_key = f"create_{action_type}_{message_idx}_{message_content_hash}"
                if st.button(f"📋 Help Create {action_type.title()}", key=unique_key):
                    if action_type == 'segment' and SEGMENT_CREATOR_AVAILABLE:
                        # Handle segment creation
                        segment_creator.handle_segment_creation_flow(message["content"])
                    else:
                        st.success(f"🎉 Let's create a {action_type}! This feature is coming soon.")
            
            # Display simple attribution for assistant messages if available
            # Skip attribution panel for Anthropic Claude
            current_provider = st.session_state.get("llm_provider", "Groq (Cloud)")
            if (message["role"] == "assistant" and "sources" in message and 
                current_provider != "Anthropic Claude (Cloud)"):
                if SOURCE_ATTRIBUTION_AVAILABLE:
                    try:
                        attributions = get_simple_attributions(message["sources"])
                        if attributions:
                            st.markdown("---")
                            st.markdown("**📚 Sources & Attribution:**")
                            for attribution in attributions:
                                st.markdown(attribution.attribution_markdown)
                                if attribution.license_notice:
                                    st.info(attribution.license_notice)
                    except Exception as e:
                        st.write(f"*Sources: {len(message['sources'])} documents used*")
                else:
                    st.write(f"*Sources: {len(message['sources'])} documents used*")
    
    # Add reaction buttons for the most recent assistant message
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        st.markdown("---")
        st.markdown("**💬 How was this response?**")
        reaction_col1, reaction_col2, reaction_col3 = st.columns([1, 1, 1])
        message_idx = len(st.session_state.messages) - 1
        # Create unique keys that include timestamp to avoid duplicates
        timestamp = int(time.time() * 1000) % 100000
        with reaction_col1:
            if st.button("👍 Helpful", key=f"thumbs_up_{message_idx}_{timestamp}", help="This response was helpful"):
                st.success("✅ Thank you for the feedback!")
        with reaction_col2:
            if st.button("👎 Not Helpful", key=f"thumbs_down_{message_idx}_{timestamp}", help="This response was not helpful"):
                st.error("❌ We'll work to improve!")
        with reaction_col3:
            if st.button("💡 Suggest", key=f"suggest_{message_idx}_{timestamp}", help="Suggest improvement"):
                st.info("💡 Thanks for the suggestion!")
    
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
    
    # If a quick test source was selected, set it as test source
    if "quick_test_source" in st.session_state and st.session_state.quick_test_source:
        # This will be handled in the attribution testing section
        pass
    
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
            
            # Check for segment requests even without explicit "create" keywords
            if not action_type and SEGMENT_CREATOR_AVAILABLE and segment_creator.detect_segment_request(prompt):
                action_type = 'segment'
                action_details = segment_creator.parse_segment_request(prompt)
            
            # Add user message to chat history
            user_message = {"role": "user", "content": prompt}
            if action_type:
                user_message["create_action"] = {"type": action_type, "details": action_details}
            st.session_state.messages.append(user_message)
            
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Start timer for response time
                        start_time = time.time()
                        
                        # Get answer with error handling based on response mode
                        try:
                            if response_mode == "RAG (Adobe Docs + Stack Overflow)":
                                # Use RAG with vector store
                                response = qa_chain.invoke({"query": prompt})
                                answer = response["result"]
                            else:
                                # Use direct LLM without RAG with streaming
                                direct_llm = setup_direct_llm(llm_provider)
                                if direct_llm is None:
                                    st.error("❌ Failed to initialize direct LLM. Please check your API keys.")
                                    st.session_state.is_processing = False
                                    st.rerun()
                                
                                # Create a placeholder for streaming response
                                message_placeholder = st.empty()
                                full_response = ""
                                
                                # Show streaming indicator
                                with st.spinner("🤖 Claude is thinking..."):
                                    try:
                                        # Stream the response
                                        for chunk in generate_direct_response_stream(prompt, direct_llm, llm_provider):
                                            if isinstance(chunk, str):
                                                full_response += chunk
                                                message_placeholder.markdown(full_response + "▌")
                                    except Exception as stream_error:
                                        # Fallback to non-streaming if streaming fails
                                        st.warning("⚠️ Streaming failed, using standard response...")
                                        response_data = generate_direct_response(prompt, direct_llm, llm_provider)
                                        full_response = response_data.get("result", "Error generating response")
                                        message_placeholder.markdown(full_response)
                                
                                # Final response without cursor
                                message_placeholder.markdown(full_response)
                                answer = full_response
                        except Exception as api_error:
                            error_message = str(api_error).lower()
                            
                            if "rate limit" in error_message or "quota" in error_message:
                                st.error("❌ Groq rate limit exceeded. Please try again later or switch to another provider.")
                                st.info("💡 You can switch to 'Anthropic Claude (Cloud)' or 'Ollama (Local)' in the sidebar to continue using the chatbot.")
                            elif "unauthorized" in error_message or "invalid" in error_message:
                                st.error("❌ Invalid Groq API key. Please check your API key in Streamlit secrets.")
                            elif "timeout" in error_message:
                                st.error("❌ Groq request timed out. Please try again.")
                            else:
                                st.error(f"❌ Error calling Groq API: {api_error}")
                            
                            # Add error message to chat history
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": "Sorry, I encountered an error while processing your request. Please try again or switch to another provider in the sidebar.",
                                "sources": []
                            })
                            
                            # Reset processing state
                            st.session_state.is_processing = False
                            st.rerun()
                        
                        # Check if response has Stack Overflow sources (only for RAG mode)
                        has_stackoverflow = False
                        if response_mode == "RAG (Adobe Docs + Stack Overflow)" and "source_documents" in response:
                            sources = [doc.metadata.get('source', 'Unknown') for doc in response["source_documents"]]
                            has_stackoverflow = has_stackoverflow_sources(sources)
                        
                        # Calculate response time
                        end_time = time.time()
                        response_time = end_time - start_time
                        
                        # Display answer with copy button
                        col1, col2 = st.columns([6, 1])
                        with col1:
                            st.markdown(answer)
                            
                            # Display integrated source attribution directly in the response
                            # Skip attribution panel for Anthropic Claude
                            current_provider = st.session_state.get("llm_provider", "Groq (Cloud)")
                            if (response_mode == "RAG (Adobe Docs + Stack Overflow)" and 
                                "source_documents" in response and 
                                current_provider != "Anthropic Claude (Cloud)"):
                                sources = [doc.metadata.get('source', 'Unknown') for doc in response["source_documents"]]
                                
                                # Generate attributions for all sources
                                if SOURCE_ATTRIBUTION_AVAILABLE and sources:
                                    try:
                                        attributor = SourceAttributor()
                                        attributions = attributor.generate_bulk_attribution(sources, "markdown")
                                        
                                        # Show attribution summary
                                        st.markdown("---")
                                        st.markdown("**📚 Sources & Attribution:**")
                                        
                                        # Count compliance
                                        compliant_count = sum(1 for attr in attributions if attr.compliance_status == "compliant")
                                        warnings_count = sum(1 for attr in attributions if attr.compliance_status == "compliant_with_warnings")
                                        non_compliant_count = sum(1 for attr in attributions if attr.compliance_status == "non_compliant")
                                        
                                        # Show compliance status
                                        if non_compliant_count == 0:
                                            st.success("✅ All sources are properly attributed")
                                        elif non_compliant_count > 0:
                                            st.warning(f"⚠️ {non_compliant_count} sources need attention for proper attribution")
                                        
                                        # Display each source with its attribution
                                        for i, (source, attribution) in enumerate(zip(sources, attributions), 1):
                                            # Use attribution metadata for source type and URL
                                            stype = attribution.source_metadata.source_type
                                            if stype == SourceType.STACK_OVERFLOW:
                                                source_icon, source_type_label = "💬", "Stack Overflow"
                                            elif stype == SourceType.ADOBE_DOCS:
                                                source_icon, source_type_label = "📖", "Adobe Docs"
                                            elif stype == SourceType.GENERIC_WEB:
                                                source_icon, source_type_label = "🌐", "Web"
                                            else:  # SourceType.UNKNOWN
                                                source_icon, source_type_label = "❓", "Unknown"
                                            doc_url = attribution.source_metadata.url
                                            
                                            # Clean up source name for display
                                            source_name = source
                                            if source_name.endswith('.txt'):
                                                source_name = source_name[:-4]
                                            if source_name.startswith('en_docs_'):
                                                source_name = source_name[8:]
                                            source_name = source_name.replace('_', ' ').title()
                                            
                                            # Display source with attribution
                                            with st.expander(f"{i}. {source_icon} {source_name} ({source_type_label})", expanded=False):
                                                # Show attribution status
                                                if attribution.compliance_status == "compliant":
                                                    st.success(f"✅ **Attribution:** {attribution.attribution_markdown}")
                                                elif attribution.compliance_status == "compliant_with_warnings":
                                                    st.warning(f"⚠️ **Attribution:** {attribution.attribution_markdown}")
                                                    if attribution.warnings:
                                                        st.caption(f"⚠️ {', '.join(attribution.warnings)}")
                                                else:
                                                    st.error(f"❌ **Attribution:** {attribution.attribution_markdown}")
                                                    if attribution.errors:
                                                        st.caption(f"❌ {', '.join(attribution.errors)}")
                                                
                                                # Show license and metadata
                                                st.caption(f"📄 License: {attribution.source_metadata.license_type.value}")
                                                st.caption(f"🔗 [View Source]({doc_url})")
                                                
                                                # Show license notice if applicable
                                                if attribution.license_notice:
                                                    st.info(attribution.license_notice)
                                        
                                        # Show overall compliance summary
                                        st.markdown("---")
                                        col1, col2, col3, col4 = st.columns(4)
                                        with col1:
                                            st.metric("Total Sources", len(sources))
                                        with col2:
                                            st.metric("✅ Compliant", compliant_count)
                                        with col3:
                                            st.metric("⚠️ Warnings", warnings_count)
                                        with col4:
                                            st.metric("❌ Non-Compliant", non_compliant_count)
                                        
                                        # Generate attribution report button
                                        message_idx = len(st.session_state.messages) - 1
                                        # Create unique key that includes timestamp to avoid duplicates
                                        timestamp = int(time.time() * 1000) % 100000
                                        unique_key = f"attribution_report_{message_idx}_{timestamp}"
                                        if st.button("📊 Generate Attribution Report", key=unique_key):
                                            try:
                                                json_report = attributor.export_attribution_report(attributions, "json")
                                                markdown_report = attributor.export_attribution_report(attributions, "markdown")
                                                
                                                # Display reports in tabs
                                                tab1, tab2 = st.tabs(["📋 JSON Report", "📝 Markdown Report"])
                                                
                                                with tab1:
                                                    st.json(json.loads(json_report))
                                                    st.download_button(
                                                        label="💾 Download JSON Report",
                                                        data=json_report,
                                                        file_name="attribution_report.json",
                                                        mime="application/json"
                                                    )
                                                
                                                with tab2:
                                                    st.markdown(markdown_report)
                                                    st.download_button(
                                                        label="💾 Download Markdown Report",
                                                        data=markdown_report,
                                                        file_name="attribution_report.md",
                                                        mime="text/markdown"
                                                    )
                                                
                                            except Exception as e:
                                                st.error(f"Error generating report: {str(e)}")
                                    
                                    except Exception as e:
                                        st.error(f"Error generating attributions: {str(e)}")
                                        # Fallback to simple source display
                                        st.markdown("---")
                                        st.markdown("**📚 Sources:**")
                                        for i, source in enumerate(sources, 1):
                                            if source.startswith('stackoverflow_'):
                                                st.info(f"{i}. 💬 {source} (Stack Overflow)")
                                            else:
                                                st.info(f"{i}. 📖 {source} (Adobe Docs)")
                                else:
                                    # Simple source display if attribution system not available
                                    st.markdown("---")
                                    st.markdown("**📚 Sources:**")
                                    for i, source in enumerate(sources, 1):
                                        if source.startswith('stackoverflow_'):
                                            st.info(f"{i}. 💬 {source} (Stack Overflow)")
                                        else:
                                            st.info(f"{i}. 📖 {source} (Adobe Docs)")
                            else:
                                # Direct mode - no source documents
                                st.markdown("---")
                                st.info("🧠 **Direct LLM Response**: This answer is generated using the LLM's training data without document retrieval.")
                            
                            # Extract and display links from source documents (only for RAG mode)
                            if response_mode == "RAG (Adobe Docs + Stack Overflow)" and "source_documents" in response:
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
                            message_idx = len(st.session_state.messages) - 1
                            # Create unique key that includes timestamp to avoid duplicates
                            timestamp = int(time.time() * 1000) % 100000
                            unique_key = f"copy_{message_idx}_{timestamp}"
                            if st.button("📋 Copy", key=unique_key, help="Copy response to clipboard"):
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
                        if response_mode == "RAG (Adobe Docs + Stack Overflow)" and "source_documents" in response:
                            for doc in response["source_documents"]:
                                sources.append(doc.metadata.get('source', 'Unknown'))
                        elif response_mode == "Direct LLM (No RAG)":
                            sources = [f"Direct {llm_provider} Response"]
                        
                        # Add assistant response to chat history with sources
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer,
                            "sources": sources
                        })
                        
                        
                        # Reset processing state after successful response
                        st.session_state.is_processing = False
                        
                        
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