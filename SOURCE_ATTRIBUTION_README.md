# Source Attribution System for RAG Chatbot

A comprehensive source attribution system designed specifically for RAG (Retrieval-Augmented Generation) chatbots, with built-in support for Adobe Experience League documentation, Stack Overflow content, and generic web sources.

## 🎯 Features

### ✨ **Core Capabilities**
- **Automatic Source Type Detection**: Identifies Stack Overflow, Adobe docs, and generic web sources
- **License Compliance**: Handles CC BY-SA 4.0 (Stack Overflow) and Adobe proprietary licensing
- **Multiple Output Formats**: Plain text, Markdown, and detailed attribution formats
- **Bulk Processing**: Generate attributions for multiple sources simultaneously
- **Compliance Validation**: Ensures proper attribution requirements are met
- **Export Functionality**: JSON, Markdown, and plain text export options

### 🔒 **License Compliance**
- **Stack Overflow (CC BY-SA 4.0)**: Proper author attribution and license notice
- **Adobe Documentation**: Adobe Inc. attribution and proprietary license handling
- **Generic Web Sources**: Flexible attribution for external content
- **Compliance Monitoring**: Track and report attribution compliance status

### 🚀 **Integration Ready**
- **FastAPI Integration**: Complete API endpoints for attribution services
- **Modular Design**: Easy to integrate with existing chatbot systems
- **Type Hints**: Full Python type annotations for better development experience
- **Error Handling**: Comprehensive error handling and logging

## 📦 Installation

### Prerequisites
```bash
python >= 3.8
pip >= 21.0
```

### Install Dependencies
```bash
pip install fastapi uvicorn pydantic
```

### Project Structure
```
ChatBotAdobe/
├── source_attributor.py          # Main attribution system
├── test_source_attributor.py     # Comprehensive test suite
├── fastapi_integration_example.py # FastAPI integration example
├── SOURCE_ATTRIBUTION_README.md  # This file
└── requirements.txt              # Python dependencies
```

## 🚀 Quick Start

### Basic Usage
```python
from source_attributor import SourceAttributor, quick_attribution

# Quick attribution for a single source
attribution = quick_attribution("stackoverflow_12345_question", "markdown")
print(attribution)

# Full attribution system
attributor = SourceAttributor()
metadata = attributor.extract_metadata_from_source("en_docs_analytics_implementation_home")
attribution = attributor.generate_attribution(metadata, "detailed")
print(attribution.attribution_markdown)
```

### FastAPI Integration
```bash
# Start the FastAPI server
python fastapi_integration_example.py

# Or with uvicorn
uvicorn fastapi_integration_example:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Usage Examples

### 1. **Single Source Attribution**
```python
from source_attributor import SourceAttributor

attributor = SourceAttributor()

# Extract metadata from source
metadata = attributor.extract_metadata_from_source("stackoverflow_12345_how_to_implement_adobe_analytics")

# Generate attribution in different formats
plain_attribution = attributor.generate_attribution(metadata, "plain_text")
markdown_attribution = attributor.generate_attribution(metadata, "markdown")
detailed_attribution = attributor.generate_attribution(metadata, "detailed")

print(f"Plain: {plain_attribution.attribution_text}")
print(f"Markdown: {markdown_attribution.attribution_markdown}")
print(f"Detailed: {detailed_attribution.attribution_markdown}")
```

### 2. **Bulk Attribution Generation**
```python
# Multiple sources
sources = [
    "stackoverflow_12345_how_to_implement_adobe_analytics",
    "en_docs_analytics_implementation_home",
    "en_browse_analytics"
]

# Generate attributions for all sources
attributions = attributor.generate_bulk_attribution(sources, "markdown")

# Process results
for attribution in attributions:
    print(f"Source: {attribution.source_metadata.title}")
    print(f"Attribution: {attribution.attribution_markdown}")
    print(f"Compliance: {attribution.compliance_status}")
    print("---")
```

### 3. **Export Attribution Reports**
```python
# Generate attributions
attributions = attributor.generate_bulk_attribution(sources)

# Export in different formats
json_report = attributor.export_attribution_report(attributions, "json")
markdown_report = attributor.export_attribution_report(attributions, "markdown")
text_report = attributor.export_attribution_report(attributions, "plain_text")

# Save reports to files
with open("attribution_report.json", "w") as f:
    f.write(json_report)

with open("attribution_report.md", "w") as f:
    f.write(markdown_report)
```

### 4. **Compliance Validation**
```python
# Validate individual source compliance
metadata = attributor.extract_metadata_from_source("stackoverflow_12345_question")
compliance_status, warnings, errors = attributor._validate_attribution_compliance(metadata)

print(f"Compliance Status: {compliance_status}")
if warnings:
    print(f"Warnings: {warnings}")
if errors:
    print(f"Errors: {errors}")
```

## 🌐 FastAPI Endpoints

### **Core Endpoints**

#### `POST /chat`
Process chat queries with source attribution
```json
{
  "query": "How do I implement Adobe Analytics?",
  "include_sources": true,
  "attribution_format": "markdown",
  "max_sources": 3
}
```

#### `POST /attribution`
Generate attributions for multiple sources
```json
{
  "sources": [
    "stackoverflow_12345_question",
    "en_docs_analytics_implementation"
  ],
  "format_type": "markdown",
  "include_compliance": true
}
```

#### `GET /sources/validate?source={source_id}`
Validate compliance for a single source

#### `GET /sources/types`
Get supported source types and requirements

### **Demo Endpoints**

#### `GET /demo/quick-attribution?source={source_id}`
Quick attribution demo

#### `GET /demo/source-metadata?source={source_id}`
Source metadata extraction demo

## 🔧 Configuration

### **Source Type Patterns**
The system automatically detects source types using regex patterns:

```python
source_patterns = {
    SourceType.STACK_OVERFLOW: [
        r'stackoverflow\.com',
        r'stackoverflow_',
        r'Stack Overflow'
    ],
    SourceType.ADOBE_DOCS: [
        r'experienceleague\.adobe\.com',
        r'en_docs_',
        r'adobe_docs'
    ],
    SourceType.GENERIC_WEB: [
        r'http[s]?://',
        r'www\.',
        r'\.com'
    ]
}
```

### **Attribution Templates**
Customizable templates for different source types:

```python
attribution_templates = {
    SourceType.STACK_OVERFLOW: {
        "plain_text": "{title} by {author} on Stack Overflow ({license}) - {url}",
        "markdown": "[{title}]({url}) by {author} on Stack Overflow ({license})",
        "detailed": "**Source:** {title}\n**Author:** {author}\n**Platform:** Stack Overflow\n**License:** {license}\n**URL:** {url}"
    }
}
```

### **License Requirements**
Configurable license-specific requirements:

```python
license_requirements = {
    LicenseType.CC_BY_SA_4_0: {
        "requires_attribution": True,
        "required_fields": ["title", "author", "url", "license"],
        "license_text": "Creative Commons Attribution-ShareAlike 4.0 International License",
        "notice": "This content is licensed under CC BY-SA 4.0. You must attribute the original author and indicate if changes were made."
    }
}
```

## 🧪 Testing

### **Run Tests**
```bash
# Run all tests
python -m pytest test_source_attributor.py -v

# Run specific test
python test_source_attributor.py TestSourceAttributor.test_source_type_identification

# Run with demo
python test_source_attributor.py
```

### **Test Coverage**
The test suite covers:
- ✅ Source type identification
- ✅ Metadata extraction
- ✅ Attribution generation
- ✅ License compliance validation
- ✅ Bulk processing
- ✅ Export functionality
- ✅ Error handling
- ✅ Integration scenarios

## 🔌 Integration with Existing Systems

### **Streamlit Integration**
```python
# In your Streamlit app
from source_attributor import SourceAttributor

attributor = SourceAttributor()

# When displaying sources
for source in sources:
    metadata = attributor.extract_metadata_from_source(source)
    attribution = attributor.generate_attribution(metadata, "markdown")
    
    st.markdown(f"**Source:** {attribution.attribution_markdown}")
    if attribution.license_notice:
        st.info(attribution.license_notice)
```

### **LangChain Integration**
```python
# In your LangChain chain
from source_attributor import SourceAttributor

class AttributionChain:
    def __init__(self):
        self.attributor = SourceAttributor()
    
    def process_with_attribution(self, query, sources):
        # Process query with sources
        result = self.llm_chain.run(query=query, context=sources)
        
        # Generate attributions
        attributions = self.attributor.generate_bulk_attribution(sources)
        
        # Add attributions to result
        result["attributions"] = attributions
        return result
```

### **Custom Source Types**
```python
# Extend for custom source types
class CustomSourceAttributor(SourceAttributor):
    def __init__(self):
        super().__init__()
        
        # Add custom source type
        self.source_patterns[SourceType.CUSTOM] = [
            r'custom_source_pattern',
            r'my_domain\.com'
        ]
        
        # Add custom attribution template
        self.attribution_templates[SourceType.CUSTOM] = {
            "plain_text": "Custom: {title} - {url}",
            "markdown": "**Custom:** [{title}]({url})"
        }
```

## 📊 Compliance Monitoring

### **Compliance Statuses**
- **`compliant`**: All requirements met
- **`compliant_with_warnings`**: Requirements met but with warnings
- **`non_compliant`**: Requirements not met
- **`not_required`**: Attribution not required
- **`error`**: Processing error occurred

### **Compliance Reports**
```python
# Generate compliance summary
compliance_summary = {
    "total_sources": 5,
    "compliant": 3,
    "compliant_with_warnings": 1,
    "non_compliant": 1,
    "overall_status": "needs_attention"
}
```

## 🚀 Performance Considerations

### **Caching**
```python
# Use Streamlit caching for repeated calls
@st.cache_resource
def get_attributor():
    return SourceAttributor()

# Cache metadata extraction
@st.cache_data
def get_source_metadata(source_id):
    attributor = get_attributor()
    return attributor.extract_metadata_from_source(source_id)
```

### **Bulk Processing**
```python
# Process multiple sources efficiently
attributions = attributor.generate_bulk_attribution(sources, "markdown")

# Export in batches for large datasets
batch_size = 100
for i in range(0, len(attributions), batch_size):
    batch = attributions[i:i + batch_size]
    report = attributor.export_attribution_report(batch, "json")
    # Process batch report
```

## 🔒 Security and Best Practices

### **Input Validation**
```python
# Validate source identifiers
def validate_source_id(source_id: str) -> bool:
    if not source_id or len(source_id) > 500:
        return False
    # Add additional validation as needed
    return True
```

### **Error Handling**
```python
try:
    attribution = attributor.generate_attribution(metadata, "markdown")
except ValueError as e:
    logger.error(f"Attribution generation failed: {e}")
    # Handle gracefully
    attribution = generate_fallback_attribution(metadata)
```

### **Logging**
```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log attribution operations
logger.info(f"Generated attribution for source: {source_id}")
logger.warning(f"Compliance warning: {warning}")
logger.error(f"Attribution error: {error}")
```

## 📈 Monitoring and Analytics

### **Usage Metrics**
```python
# Track attribution usage
attribution_metrics = {
    "total_requests": 0,
    "sources_processed": 0,
    "compliance_violations": 0,
    "processing_time_avg": 0.0
}

# Update metrics
def update_metrics(attributions, processing_time):
    attribution_metrics["total_requests"] += 1
    attribution_metrics["sources_processed"] += len(attributions)
    attribution_metrics["processing_time_avg"] = (
        (attribution_metrics["processing_time_avg"] * (attribution_metrics["total_requests"] - 1) + processing_time) /
        attribution_metrics["total_requests"]
    )
```

## 🆘 Troubleshooting

### **Common Issues**

#### **Source Type Not Detected**
```python
# Check source patterns
print(attributor.source_patterns)

# Add custom pattern
attributor.source_patterns[SourceType.CUSTOM].append(r'your_pattern')
```

#### **Attribution Generation Fails**
```python
# Check metadata
metadata = attributor.extract_metadata_from_source(source)
print(f"Metadata: {metadata}")

# Validate manually
compliance_status, warnings, errors = attributor._validate_attribution_compliance(metadata)
print(f"Compliance: {compliance_status}, Warnings: {warnings}, Errors: {errors}")
```

#### **License Compliance Issues**
```python
# Check license requirements
license_info = attributor.license_requirements.get(metadata.license_type, {})
print(f"License requirements: {license_info}")

# Verify required fields
for field in metadata.attribution_required_fields:
    value = getattr(metadata, field, None)
    print(f"{field}: {value}")
```

### **Debug Mode**
```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
source_type = attributor.identify_source_type("test_source")
print(f"Detected type: {source_type}")

metadata = attributor.extract_metadata_from_source("test_source")
print(f"Generated metadata: {metadata}")
```

## 🤝 Contributing

### **Adding New Source Types**
1. Extend the `SourceType` enum
2. Add patterns to `source_patterns`
3. Create attribution templates
4. Define license requirements
5. Add tests

### **Adding New License Types**
1. Extend the `LicenseType` enum
2. Add requirements to `license_requirements`
3. Update validation logic
4. Add tests

### **Code Style**
- Follow PEP 8 guidelines
- Use type hints throughout
- Add comprehensive docstrings
- Include error handling
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Adobe Experience League** for documentation access
- **Stack Overflow** for community content
- **Creative Commons** for CC BY-SA 4.0 license
- **FastAPI** for the excellent web framework
- **Pydantic** for data validation

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Check the test examples for usage patterns
- Review the FastAPI integration example
- Run the test suite to verify functionality

---

**Happy Attributing! 🎉**
