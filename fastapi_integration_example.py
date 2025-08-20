#!/usr/bin/env python3
"""
FastAPI Integration Example for SourceAttributor

This module demonstrates how to integrate the SourceAttributor class with FastAPI endpoints
for the RAG chatbot, showing proper attribution handling and license compliance.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn

from source_attributor import (
    SourceAttributor,
    SourceMetadata,
    AttributionResult,
    SourceType,
    LicenseType
)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot with Source Attribution",
    description="FastAPI integration example for SourceAttributor class",
    version="1.0.0"
)

# Initialize SourceAttributor
attributor = SourceAttributor()


# Pydantic models for API requests/responses
class ChatRequest(BaseModel):
    """Request model for chat queries"""
    query: str = Field(..., description="User's question or query")
    include_sources: bool = Field(True, description="Whether to include source attribution")
    attribution_format: str = Field("markdown", description="Attribution format (plain_text, markdown, detailed)")
    max_sources: int = Field(3, description="Maximum number of sources to return")


class SourceInfo(BaseModel):
    """Model for source information"""
    title: str
    url: str
    source_type: str
    license_type: str
    attribution_text: str
    attribution_markdown: str
    compliance_status: str
    warnings: List[str] = []
    errors: List[str] = []


class ChatResponse(BaseModel):
    """Response model for chat queries"""
    answer: str
    sources: List[SourceInfo] = []
    attribution_summary: Optional[str] = None
    compliance_report: Optional[Dict[str, Any]] = None
    processing_time: float


class AttributionRequest(BaseModel):
    """Request model for attribution generation"""
    sources: List[str] = Field(..., description="List of source identifiers")
    format_type: str = Field("markdown", description="Output format (json, markdown, plain_text)")
    include_compliance: bool = Field(True, description="Whether to include compliance information")


class AttributionResponse(BaseModel):
    """Response model for attribution generation"""
    attributions: List[SourceInfo]
    report: str
    compliance_summary: Dict[str, Any]
    export_formats: Dict[str, str]


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RAG Chatbot with Source Attribution API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "Process chat queries with source attribution",
            "/attribution": "Generate attributions for sources",
            "/sources/validate": "Validate source compliance",
            "/sources/types": "Get supported source types",
            "/health": "Health check endpoint"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    """
    Process chat queries with comprehensive source attribution.
    
    This endpoint demonstrates how to integrate source attribution into a RAG chatbot
    response, ensuring proper licensing compliance and attribution formatting.
    """
    import time
    start_time = time.time()
    
    try:
        # Simulate RAG processing (replace with your actual RAG logic)
        # In a real implementation, this would call your vector database and LLM
        answer = f"Here's the answer to your question: '{request.query}'. "
        answer += "This response is based on multiple sources including Adobe documentation and community solutions."
        
        # Simulate source retrieval (replace with your actual source extraction)
        simulated_sources = [
            "stackoverflow_12345_how_to_implement_adobe_analytics",
            "en_docs_analytics_implementation_home",
            "en_browse_analytics"
        ]
        
        sources = []
        if request.include_sources:
            # Generate attributions for sources
            attributions = attributor.generate_bulk_attribution(
                simulated_sources, 
                request.attribution_format
            )
            
            # Convert to API response format
            for attr in attributions:
                source_info = SourceInfo(
                    title=attr.source_metadata.title,
                    url=attr.source_metadata.url,
                    source_type=attr.source_metadata.source_type.value,
                    license_type=attr.source_metadata.license_type.value,
                    attribution_text=attr.attribution_text,
                    attribution_markdown=attr.attribution_markdown,
                    compliance_status=attr.compliance_status,
                    warnings=attr.warnings,
                    errors=attr.errors
                )
                sources.append(source_info)
        
        # Generate attribution summary
        attribution_summary = None
        if sources:
            if request.attribution_format == "markdown":
                attribution_summary = "**Sources:**\n" + "\n".join([
                    f"- {source.attribution_markdown}" for source in sources
                ])
            else:
                attribution_summary = "Sources:\n" + "\n".join([
                    f"- {source.attribution_text}" for source in sources
                ])
        
        # Generate compliance report
        compliance_report = None
        if sources:
            compliant_count = sum(1 for s in sources if s.compliance_status == "compliant")
            warnings_count = sum(1 for s in sources if s.compliance_status == "compliant_with_warnings")
            errors_count = sum(1 for s in sources if s.compliance_status in ["non_compliant", "error"])
            
            compliance_report = {
                "total_sources": len(sources),
                "compliant": compliant_count,
                "compliant_with_warnings": warnings_count,
                "non_compliant": errors_count,
                "overall_status": "compliant" if errors_count == 0 else "needs_attention"
            }
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            answer=answer,
            sources=sources[:request.max_sources],
            attribution_summary=attribution_summary,
            compliance_report=compliance_report,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/attribution", response_model=AttributionResponse)
async def generate_attributions(request: AttributionRequest):
    """
    Generate comprehensive attributions for multiple sources.
    
    This endpoint demonstrates bulk attribution generation with multiple output formats
    and compliance reporting.
    """
    try:
        # Generate attributions
        attributions = attributor.generate_bulk_attribution(
            request.sources, 
            "markdown"  # Use markdown for internal processing
        )
        
        # Convert to API response format
        source_infos = []
        for attr in attributions:
            source_info = SourceInfo(
                title=attr.source_metadata.title,
                url=attr.source_metadata.url,
                source_type=attr.source_metadata.source_type.value,
                license_type=attr.source_metadata.license_type.value,
                attribution_text=attr.attribution_text,
                attribution_markdown=attr.attribution_markdown,
                compliance_status=attr.compliance_status,
                warnings=attr.warnings,
                errors=attr.errors
            )
            source_infos.append(source_info)
        
        # Generate report in requested format
        report = attributor.export_attribution_report(attributions, request.format_type)
        
        # Generate compliance summary
        compliance_summary = {
            "total_sources": len(attributions),
            "by_source_type": {},
            "by_license_type": {},
            "by_compliance_status": {}
        }
        
        for attr in attributions:
            # Count by source type
            source_type = attr.source_metadata.source_type.value
            compliance_summary["by_source_type"][source_type] = \
                compliance_summary["by_source_type"].get(source_type, 0) + 1
            
            # Count by license type
            license_type = attr.source_metadata.license_type.value
            compliance_summary["by_license_type"][license_type] = \
                compliance_summary["by_license_type"].get(license_type, 0) + 1
            
            # Count by compliance status
            status = attr.compliance_status
            compliance_summary["by_compliance_status"][status] = \
                compliance_summary["by_compliance_status"].get(status, 0) + 1
        
        # Generate export formats
        export_formats = {}
        for format_type in ["json", "markdown", "plain_text"]:
            try:
                export_formats[format_type] = attributor.export_attribution_report(
                    attributions, format_type
                )
            except Exception as e:
                export_formats[format_type] = f"Error generating {format_type}: {str(e)}"
        
        return AttributionResponse(
            attributions=source_infos,
            report=report,
            compliance_summary=compliance_summary,
            export_formats=export_formats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attribution generation failed: {str(e)}")


@app.get("/sources/validate")
async def validate_source_compliance(source: str = Query(..., description="Source identifier to validate")):
    """
    Validate compliance for a single source.
    
    This endpoint demonstrates individual source validation and compliance checking.
    """
    try:
        # Extract metadata and validate
        metadata = attributor.extract_metadata_from_source(source)
        compliance_status, warnings, errors = attributor._validate_attribution_compliance(metadata)
        
        # Generate attribution for reference
        attribution = attributor.generate_attribution(metadata, "detailed")
        
        return {
            "source": source,
            "metadata": {
                "title": metadata.title,
                "url": metadata.url,
                "source_type": metadata.source_type.value,
                "license_type": metadata.license_type.value,
                "requires_attribution": metadata.requires_attribution
            },
            "compliance": {
                "status": compliance_status,
                "warnings": warnings,
                "errors": errors,
                "required_fields": metadata.attribution_required_fields
            },
            "attribution": {
                "text": attribution.attribution_text,
                "markdown": attribution.attribution_markdown,
                "license_notice": attribution.license_notice
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Source validation failed: {str(e)}")


@app.get("/sources/types")
async def get_supported_source_types():
    """Get information about supported source types and their requirements."""
    return {
        "supported_source_types": [
            {
                "type": source_type.value,
                "description": f"Sources from {source_type.value.replace('_', ' ').title()}",
                "license_requirements": attributor.license_requirements.get(
                    attributor.license_requirements.get(source_type.value, {}).get("license_type", LicenseType.UNKNOWN),
                    {}
                )
            }
            for source_type in SourceType
        ],
        "license_types": [
            {
                "type": license_type.value,
                "description": attributor.license_requirements.get(license_type, {}).get("license_text", "Unknown license"),
                "requires_attribution": attributor.license_requirements.get(license_type, {}).get("requires_attribution", False)
            }
            for license_type in LicenseType
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "RAG Chatbot with Source Attribution",
        "version": "1.0.0",
        "attributor_status": "initialized"
    }


# Utility endpoints for testing and debugging

@app.get("/demo/quick-attribution")
async def quick_attribution_demo(source: str = Query(..., description="Source identifier")):
    """Quick attribution demo endpoint."""
    try:
        from source_attributor import quick_attribution
        attribution_text = quick_attribution(source, "plain_text")
        return {"source": source, "attribution": attribution_text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Quick attribution failed: {str(e)}")


@app.get("/demo/source-metadata")
async def source_metadata_demo(source: str = Query(..., description="Source identifier")):
    """Source metadata extraction demo endpoint."""
    try:
        metadata = attributor.extract_metadata_from_source(source)
        return {
            "source": source,
            "metadata": {
                "title": metadata.title,
                "url": metadata.url,
                "source_type": metadata.source_type.value,
                "license_type": metadata.license_type.value,
                "requires_attribution": metadata.requires_attribution,
                "attribution_required_fields": metadata.attribution_required_fields
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Metadata extraction failed: {str(e)}")


# Error handlers

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler for expected errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


# Example usage and integration notes

"""
Integration Notes:

1. **Chat Endpoint Integration**:
   - The /chat endpoint shows how to integrate source attribution into your RAG responses
   - Replace the simulated RAG logic with your actual vector database queries and LLM calls
   - The attribution is automatically generated for all sources used in the response

2. **Source Attribution**:
   - The /attribution endpoint provides bulk attribution generation
   - Supports multiple output formats (JSON, Markdown, Plain Text)
   - Includes comprehensive compliance reporting

3. **Compliance Monitoring**:
   - The /sources/validate endpoint helps monitor individual source compliance
   - Use this for debugging and ensuring proper attribution

4. **FastAPI Features Used**:
   - Pydantic models for request/response validation
   - Query parameters for flexible API usage
   - Proper error handling with HTTPException
   - Global exception handlers for robustness

5. **Production Considerations**:
   - Add authentication and rate limiting
   - Implement caching for frequently requested attributions
   - Add logging and monitoring
   - Consider async processing for bulk operations
   - Add input validation and sanitization

6. **Testing the Integration**:
   - Run the FastAPI server: uvicorn fastapi_integration_example:app --reload
   - Test endpoints with the interactive docs at /docs
   - Use the demo endpoints for quick testing
"""

if __name__ == "__main__":
    # Run the FastAPI server
    print("🚀 Starting FastAPI server with Source Attribution...")
    print("📚 API Documentation available at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("🎯 Demo endpoints available for testing")
    
    uvicorn.run(
        "fastapi_integration_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
