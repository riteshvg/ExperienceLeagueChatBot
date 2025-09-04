#!/usr/bin/env python3
"""
Source Attribution System for RAG Chatbot

This module provides comprehensive source attribution capabilities for the Adobe Experience League
Documentation Chatbot, including proper licensing compliance and multiple output formats.

Author: RAG Chatbot Team
License: MIT
"""

import re
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Tuple
from enum import Enum
from urllib.parse import urlparse, parse_qs
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Enumeration of supported source types"""
    STACK_OVERFLOW = "stack_overflow"
    ADOBE_DOCS = "adobe_docs"
    GENERIC_WEB = "generic_web"
    UNKNOWN = "unknown"


class LicenseType(Enum):
    """Enumeration of supported license types"""
    CC_BY_SA_4_0 = "CC BY-SA 4.0"
    ADOBE_PROPRIETARY = "Adobe Proprietary"
    UNKNOWN = "Unknown"


@dataclass
class SourceMetadata:
    """Data class for storing source metadata"""
    title: str
    url: str
    source_type: SourceType
    license_type: LicenseType
    author: Optional[str] = None
    publication_date: Optional[str] = None
    last_modified: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    requires_attribution: bool = True
    attribution_required_fields: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and set default values after initialization"""
        if self.source_type == SourceType.STACK_OVERFLOW:
            self.license_type = LicenseType.CC_BY_SA_4_0
            self.requires_attribution = True
            self.attribution_required_fields = ["title", "author", "url", "license_type"]
        elif self.source_type == SourceType.ADOBE_DOCS:
            self.license_type = LicenseType.ADOBE_PROPRIETARY
            self.requires_attribution = True
            self.attribution_required_fields = ["title", "url", "license_type"]
        else:
            self.license_type = LicenseType.UNKNOWN
            self.requires_attribution = False
            self.attribution_required_fields = ["title", "url"]


@dataclass
class AttributionResult:
    """Data class for storing attribution results"""
    source_metadata: SourceMetadata
    attribution_text: str
    attribution_markdown: str
    license_notice: Optional[str] = None
    compliance_status: str = "compliant"
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class SourceAttributor:
    """
    Comprehensive source attribution system for RAG chatbot responses.
    
    This class handles source identification, metadata extraction, licensing compliance,
    and attribution formatting for various source types including Stack Overflow,
    Adobe documentation, and generic web sources.
    
    Attributes:
        source_patterns (Dict): Regex patterns for identifying source types
        license_requirements (Dict): License-specific attribution requirements
        attribution_templates (Dict): Templates for different attribution formats
    """
    
    def __init__(self):
        """Initialize the SourceAttributor with patterns and templates"""
        self.source_patterns = {
            SourceType.STACK_OVERFLOW: [
                r'stackoverflow\.com',
                r'stackoverflow_',
                r'stackoverflow',
                r'SO:',
                r'Stack Overflow'
            ],
            SourceType.ADOBE_DOCS: [
                r'experienceleague\.adobe\.com',
                r'adobe\.com',
                r'en_docs_',
                r'en_browse_',
                r'adobe_docs',
                r'Adobe',
                r'Adobe Analytics',
                r'Adobe Experience'
            ],
            SourceType.GENERIC_WEB: [
                r'http[s]?://',
                r'www\.',
                r'\.com',
                r'\.org',
                r'\.net'
            ]
        }
        
        self.license_requirements = {
            LicenseType.CC_BY_SA_4_0: {
                "requires_attribution": True,
                "required_fields": ["title", "author", "url", "license"],
                "license_text": "Creative Commons Attribution-ShareAlike 4.0 International License",
                "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
                "notice": "This content is licensed under CC BY-SA 4.0. You must attribute the original author and indicate if changes were made."
            },
            LicenseType.ADOBE_PROPRIETARY: {
                "requires_attribution": True,
                "required_fields": ["title", "url", "license"],
                "license_text": "Adobe Proprietary Documentation",
                "license_url": "https://www.adobe.com/legal/terms.html",
                "notice": "Adobe documentation is proprietary. Please refer to Adobe's terms of use for proper attribution."
            }
        }
        
        self.attribution_templates = {
            SourceType.STACK_OVERFLOW: {
                "plain_text": "{title} by {author} on Stack Overflow ({license}) - {url}",
                "markdown": "[{title}]({url}) by {author} on Stack Overflow ({license})",
                "detailed": "**Source:** {title}\n**Author:** {author}\n**Platform:** Stack Overflow\n**License:** {license}\n**URL:** {url}"
            },
            SourceType.ADOBE_DOCS: {
                "plain_text": "{title} (Adobe Inc.) - {url}",
                "markdown": "[{title}]({url}) (Adobe Inc.)",
                "detailed": "**Source:** {title}\n**Author:** Adobe Inc.\n**Platform:** Adobe Experience League\n**License:** {license_type}\n**URL:** {url}"
            },
            SourceType.GENERIC_WEB: {
                "plain_text": "{title} - {url}",
                "markdown": "[{title}]({url})",
                "detailed": "**Source:** {title}\n**URL:** {url}\n**License:** {license}"
            }
        }
    
    def identify_source_type(self, source: str) -> SourceType:
        """
        Identify the source type based on source identifier or URL.
        
        Args:
            source (str): Source identifier, filename, or URL
            
        Returns:
            SourceType: Identified source type
            
        Raises:
            ValueError: If source is empty or invalid
        """
        if not source or not isinstance(source, str):
            raise ValueError("Source must be a non-empty string")
        
        source_lower = source.lower()
        
        # Check each source type pattern
        for source_type, patterns in self.source_patterns.items():
            for pattern in patterns:
                if re.search(pattern, source_lower, re.IGNORECASE):
                    logger.info(f"Identified source type '{source_type.value}' for source: {source}")
                    return source_type
        
        # Default to generic web if no specific pattern matches
        logger.warning(f"Could not identify source type for: {source}, defaulting to generic web")
        return SourceType.GENERIC_WEB
    
    def extract_metadata_from_source(self, source: str, additional_info: Optional[Dict] = None) -> SourceMetadata:
        """
        Extract metadata from source identifier and additional information.
        
        Args:
            source (str): Source identifier or filename
            additional_info (Optional[Dict]): Additional metadata information
            
        Returns:
            SourceMetadata: Extracted source metadata
            
        Raises:
            ValueError: If source extraction fails
        """
        try:
            source_type = self.identify_source_type(source)
            
            # Initialize with defaults
            metadata = {
                "title": self._generate_title_from_source(source),
                "url": self._generate_url_from_source(source, source_type),
                "source_type": source_type,
                "license_type": None,  # Let __post_init__ set this
                "author": None,
                "publication_date": None,
                "last_modified": None,
                "description": None,
                "tags": []
            }
            
            # Override with additional info if provided
            if additional_info:
                metadata.update(additional_info)
            
            # Create and return SourceMetadata object
            return SourceMetadata(**metadata)
            
        except Exception as e:
            logger.error(f"Failed to extract metadata from source '{source}': {str(e)}")
            raise ValueError(f"Metadata extraction failed: {str(e)}")
    
    def _generate_title_from_source(self, source: str) -> str:
        """
        Generate a human-readable title from source identifier.
        
        Args:
            source (str): Source identifier or filename
            
        Returns:
            str: Generated title
        """
        if not source:
            return "Unknown Source"
        
        # Remove file extensions
        title = source.replace('.txt', '').replace('.html', '')
        
        # Handle different naming conventions
        if title.startswith('stackoverflow_'):
            # Extract question ID and create title
            parts = title.split('_')
            if len(parts) >= 2:
                try:
                    question_id = parts[1]
                    return f"Stack Overflow Question #{question_id}"
                except:
                    pass
            return "Stack Overflow Question"
        
        elif title.startswith('en_docs_'):
            # Clean up Adobe documentation titles
            title = title.replace('en_docs_', '')
            title = title.replace('_', ' ').title()
            return title
        
        elif title.startswith('en_browse_'):
            # Clean up Adobe browse page titles
            title = title.replace('en_browse_', '')
            title = title.replace('_', ' ').title()
            return title
        
        # Generic cleanup
        title = title.replace('_', ' ').replace('-', ' ')
        return title.title()
    
    def generate_url_from_source(self, source: str) -> str:
        """
        Generate URL from source identifier.
        
        This is a public method that identifies the source type and generates
        the appropriate URL using the private _generate_url_from_source method.
        
        Args:
            source (str): Source identifier
            
        Returns:
            str: Generated URL
        """
        stype = self.identify_source_type(source)
        return self._generate_url_from_source(source, stype)
    
    def _generate_url_from_source(self, source: str, source_type: SourceType) -> str:
        """
        Generate URL from source identifier based on source type.
        
        This method uses comprehensive Adobe URL generation logic for better
        support of complex Adobe documentation patterns including analytics-platform,
        customer-journey-analytics, experience-cloud-kcs, and other nested structures.
        
        Args:
            source (str): Source identifier
            source_type (SourceType): Identified source type
            
        Returns:
            str: Generated URL
        """
        if source_type == SourceType.STACK_OVERFLOW:
            # Extract question ID from filename
            if source.startswith('stackoverflow_'):
                parts = source.split('_')
                if len(parts) >= 2:
                    try:
                        question_id = parts[1]
                        return f"https://stackoverflow.com/questions/{question_id}"
                    except:
                        pass
            return "https://stackoverflow.com/questions"
        
        elif source_type == SourceType.ADOBE_DOCS:
            # Use comprehensive Adobe URL generation logic
            logger.debug(f"Using Adobe URL generation for source: {source}")
            return self._generate_adobe_url(source)
        
        # Generic fallback
        return f"https://example.com/{source}"
    

    
    def _generate_adobe_url(self, source_name: str) -> str:
        """
        Generate Adobe Experience League URL based on source name with comprehensive pattern matching.
        
        This method implements a hierarchical approach to URL generation:
        1. Identify prefix type (docs/browse/playlists/perspectives)
        2. Apply specific mapping rules for each category
        3. Use intelligent fallback by parsing source structure
        
        Args:
            source_name (str): Source filename or identifier
            
        Returns:
            str: Generated Adobe Experience League URL
            
        Supported Patterns:
        - en_docs_* → https://experienceleague.adobe.com/en/docs/*
        - en_browse_* → https://experienceleague.adobe.com/en/browse/*
        - en_playlists_* → https://experienceleague.adobe.com/en/playlists/*
        - en_perspectives_* → https://experienceleague.adobe.com/en/perspectives/*
        - docs_* → https://experienceleague.adobe.com/docs/*
        
        Special Cases:
        - experience-cloud-kcs_kbarticles_ka-{id} → /experience-cloud-kcs/kbarticles/ka-{id}
        - analytics-platform_* → /analytics-platform/*
        - customer-journey-analytics-learn_* → /customer-journey-analytics-learn/*
        - analytics-learn_* → /analytics-learn/*
        - blueprints-learn_* → /blueprints-learn/*
        - certification_* → /certification/*
        - release-notes_* → /release-notes/*
        """
        if not source_name:
            raise ValueError("source_name must be a non-empty string")
        
        # Input preprocessing: Remove .txt extension (case-insensitive)
        name_lower = source_name.lower()
        if name_lower.endswith('.txt'):
            source_name = source_name[:-4]
        
        logger.debug(f"Processing source name: {source_name}")
        
        # Handle legacy HTML suffix for docs_ prefixed files (case-insensitive)
        html_suffix = ""
        if name_lower.endswith('.html'):
            html_suffix = ".html"
            source_name = source_name[:-5]
        
        # Prefix identification and routing
        if source_name.startswith('en_docs_'):
            return self._handle_docs_prefix(source_name[8:], html_suffix)
        elif source_name.startswith('en_browse_'):
            return self._handle_browse_prefix(source_name[10:])
        elif source_name.startswith('en_playlists_'):
            return self._handle_playlists_prefix(source_name[13:])
        elif source_name.startswith('en_perspectives_'):
            return self._handle_perspectives_prefix(source_name[16:])
        elif source_name.startswith('docs_'):
            return self._handle_legacy_docs_prefix(source_name[5:], html_suffix)
        elif source_name.startswith('browse_'):
            return self._handle_browse_prefix(source_name[7:])
        else:
            # No prefix detected, try intelligent fallback
            logger.debug(f"No prefix detected for {source_name}, using intelligent fallback")
            return self._intelligent_fallback(source_name, html_suffix)
    
    def _handle_docs_prefix(self, path: str, html_suffix: str = "") -> str:
        """
        Handle en_docs_ prefix with comprehensive pattern matching.
        
        Args:
            path (str): Path after en_docs_ prefix
            html_suffix (str): HTML suffix if present
            
        Returns:
            str: Generated URL
        """
        base_url = "https://experienceleague.adobe.com/en/docs"
        
        # Special cases for complex nested paths
        # Use regex to capture the ka- ID and optionally append remaining segments
        m = re.match(r'^experience-cloud-kcs_kbarticles_(ka-[\w\-]+)(?:_(.*))?$', path)
        if m:
            kb_id = m.group(1)
            if m.group(2):
                # Convert remaining segments to path format
                converted_remainder = self._convert_underscores_to_path(m.group(2))
                return f"https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/{kb_id}/{converted_remainder}{html_suffix}"
            else:
                return f"https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/{kb_id}{html_suffix}"
        
        elif path.startswith('analytics-platform_'):
            # Handle analytics-platform paths
            clean_path = path.replace('analytics-platform_', '')
            url_path = self._convert_underscores_to_path(clean_path)
            return f"{base_url}/analytics-platform/{url_path}{html_suffix}"
        
        elif path.startswith('customer-journey-analytics-learn_'):
            # Handle customer-journey-analytics-learn paths
            clean_path = path.replace('customer-journey-analytics-learn_', '')
            url_path = self._convert_underscores_to_path(clean_path)
            return f"{base_url}/customer-journey-analytics-learn/{url_path}{html_suffix}"
        
        elif path.startswith('analytics-learn_'):
            # Handle analytics-learn paths
            clean_path = path.replace('analytics-learn_', '')
            url_path = self._convert_underscores_to_path(clean_path)
            return f"{base_url}/analytics-learn/{url_path}{html_suffix}"
        
        elif path.startswith('blueprints-learn_'):
            # Handle blueprints-learn paths
            clean_path = path.replace('blueprints-learn_', '')
            url_path = self._convert_underscores_to_path(clean_path)
            return f"{base_url}/blueprints-learn/{url_path}{html_suffix}"
        
        elif path.startswith('certification_'):
            # Handle certification paths
            clean_path = path.replace('certification_', '')
            url_path = self._convert_underscores_to_path(clean_path)
            return f"{base_url}/certification/{url_path}{html_suffix}"
        
        elif path.startswith('release-notes_'):
            # Handle release-notes paths
            clean_path = path.replace('release-notes_', '')
            url_path = self._convert_underscores_to_path(clean_path)
            return f"{base_url}/release-notes/{url_path}{html_suffix}"
        
        elif path.startswith('customer_journey_analytics_'):
            # Handle underscore variant customer_journey_analytics paths
            clean = path[len('customer_journey_analytics_'):]
            url_path = self._convert_underscores_to_path(clean)
            return f"https://experienceleague.adobe.com/en/docs/customer-journey-analytics/{url_path}{html_suffix}"
        
        elif path.startswith('customer-journey-analytics_'):
            # Handle hyphen variant customer-journey-analytics paths
            clean = path[len('customer-journey-analytics_'):]
            url_path = self._convert_underscores_to_path(clean)
            return f"https://experienceleague.adobe.com/en/docs/customer-journey-analytics/{url_path}{html_suffix}"
        
        elif path.startswith('analytics_'):
            # Handle generic analytics paths
            clean_path = path.replace('analytics_', '')
            url_path = self._convert_underscores_to_path(clean_path)
            return f"{base_url}/analytics/{url_path}{html_suffix}"
        
        else:
            # Generic path construction for docs
            url_path = self._convert_underscores_to_path(path)
            return f"{base_url}/{url_path}{html_suffix}"
    
    def _handle_browse_prefix(self, path: str) -> str:
        """
        Handle en_browse_ prefix.
        
        Args:
            path (str): Path after en_browse_ prefix
            
        Returns:
            str: Generated URL
        """
        base_url = "https://experienceleague.adobe.com/en/browse"
        url_path = self._convert_underscores_to_path(path)
        return f"{base_url}/{url_path}"
    
    def _handle_playlists_prefix(self, path: str) -> str:
        """
        Handle en_playlists_ prefix.
        
        Args:
            path (str): Path after en_playlists_ prefix
            
        Returns:
            str: Generated URL
        """
        base_url = "https://experienceleague.adobe.com/en/playlists"
        url_path = self._convert_underscores_to_path(path)
        return f"{base_url}/{url_path}"
    
    def _handle_perspectives_prefix(self, path: str) -> str:
        """
        Handle en_perspectives_ prefix.
        
        Args:
            path (str): Path after en_perspectives_ prefix
            
        Returns:
            str: Generated URL
        """
        base_url = "https://experienceleague.adobe.com/en/perspectives"
        url_path = self._convert_underscores_to_path(path)
        return f"{base_url}/{url_path}"
    
    def _handle_legacy_docs_prefix(self, path: str, html_suffix: str = "") -> str:
        """
        Handle legacy docs_ prefix.
        
        Args:
            path (str): Path after docs_ prefix
            html_suffix (str): HTML suffix if present
            
        Returns:
            str: Generated URL
        """
        base_url = "https://experienceleague.adobe.com/docs"
        url_path = self._convert_underscores_to_path(path)
        return f"{base_url}/{url_path}{html_suffix}"
    
    def _convert_underscores_to_path(self, path: str) -> str:
        """
        Convert underscores to forward slashes while preserving hyphens within segments.
        
        Args:
            path (str): Path with underscores
            
        Returns:
            str: URL path with forward slashes
        """
        if not path:
            return ""
        
        # Split on underscores and join with forward slashes
        # This preserves hyphens within each segment
        # Filter out empty segments to handle consecutive underscores
        segments = [s for s in path.split('_') if s]
        return '/'.join(segments)
    
    def _intelligent_fallback(self, source_name: str, html_suffix: str = "") -> str:
        """
        Intelligent fallback when no prefix is detected.
        
        Args:
            source_name (str): Source name without prefix
            html_suffix (str): HTML suffix if present
            
        Returns:
            str: Generated URL using intelligent fallback
        """
        logger.debug(f"Using intelligent fallback for: {source_name}")
        
        # Convert underscores to forward slashes
        url_path = self._convert_underscores_to_path(source_name)
        
        # Try to determine the most appropriate base URL based on content
        # Prioritize Customer Journey Analytics before generic Analytics
        name = source_name.lower()
        if 'customer-journey-analytics' in name or 'customer_journey_analytics' in name:
            base_url = 'https://experienceleague.adobe.com/en/docs/customer-journey-analytics'
        elif 'analytics' in name:
            base_url = 'https://experienceleague.adobe.com/en/docs/analytics'
        else:
            base_url = 'https://experienceleague.adobe.com/en/docs'
        
        return f"{base_url}/{url_path}{html_suffix}"
    
    def generate_attribution(self, source_metadata: SourceMetadata, format_type: str = "plain_text") -> AttributionResult:
        """
        Generate attribution for a given source with specified format.
        
        Args:
            source_metadata (SourceMetadata): Source metadata object
            format_type (str): Desired format type (plain_text, markdown, detailed)
            
        Returns:
            AttributionResult: Complete attribution result
            
        Raises:
            ValueError: If attribution generation fails
        """
        try:
            # Validate required fields
            compliance_status, warnings, errors = self._validate_attribution_compliance(source_metadata)
            
            # Get appropriate template
            template = self.attribution_templates.get(source_metadata.source_type, {})
            if not template:
                raise ValueError(f"No attribution template found for source type: {source_metadata.source_type}")
            
            # Generate attribution text
            attribution_text = self._format_attribution(template.get(format_type, template["plain_text"]), source_metadata)
            attribution_markdown = self._format_attribution(template.get(format_type, template.get("markdown", template["plain_text"])), source_metadata)
            
            # Generate license notice if required
            license_notice = None
            if source_metadata.requires_attribution and source_metadata.license_type != LicenseType.UNKNOWN:
                license_notice = self._generate_license_notice(source_metadata.license_type)
            
            return AttributionResult(
                source_metadata=source_metadata,
                attribution_text=attribution_text,
                attribution_markdown=attribution_markdown,
                license_notice=license_notice,
                compliance_status=compliance_status,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Failed to generate attribution for source '{source_metadata.title}': {str(e)}")
            raise ValueError(f"Attribution generation failed: {str(e)}")
    
    def _format_attribution(self, template: str, metadata: SourceMetadata) -> str:
        """
        Format attribution using template and metadata.
        
        Args:
            template (str): Attribution template string
            metadata (SourceMetadata): Source metadata
            
        Returns:
            str: Formatted attribution text
        """
        # Prepare formatting variables
        format_vars = {
            "title": metadata.title,
            "url": metadata.url,
            "author": metadata.author or "Unknown Author",
            "license": metadata.license_type.value,
            "license_type": metadata.license_type.value,
            "source_type": metadata.source_type.value,
            "date": metadata.publication_date or "Unknown Date"
        }
        
        # Format the template
        try:
            return template.format(**format_vars)
        except KeyError as e:
            logger.warning(f"Template formatting failed for key {e}, using fallback")
            return f"{metadata.title} - {metadata.url}"
    
    def _validate_attribution_compliance(self, metadata: SourceMetadata) -> Tuple[str, List[str], List[str]]:
        """
        Validate attribution compliance for a given source.
        
        Args:
            metadata (SourceMetadata): Source metadata to validate
            
        Returns:
            Tuple[str, List[str], List[str]]: Compliance status, warnings, and errors
        """
        warnings = []
        errors = []
        
        if not metadata.requires_attribution:
            return "not_required", warnings, errors
        
        # Check required fields
        for field in metadata.attribution_required_fields:
            if not getattr(metadata, field, None):
                if field == "author" and metadata.source_type == SourceType.ADOBE_DOCS:
                    # Adobe docs don't always have individual authors
                    continue
                errors.append(f"Required field '{field}' is missing")
        
        # Check license compliance
        if metadata.license_type == LicenseType.CC_BY_SA_4_0:
            if not metadata.author:
                warnings.append("CC BY-SA 4.0 license requires author attribution")
        
        # Determine compliance status
        if errors:
            compliance_status = "non_compliant"
        elif warnings:
            compliance_status = "compliant_with_warnings"
        else:
            compliance_status = "compliant"
        
        return compliance_status, warnings, errors
    
    def _generate_license_notice(self, license_type: LicenseType) -> str:
        """
        Generate license notice text for a given license type.
        
        Args:
            license_type (LicenseType): License type
            
        Returns:
            str: License notice text
        """
        license_info = self.license_requirements.get(license_type, {})
        return license_info.get("notice", f"License: {license_type.value}")
    
    def generate_bulk_attribution(self, sources: List[Union[str, SourceMetadata]], format_type: str = "plain_text") -> List[AttributionResult]:
        """
        Generate attributions for multiple sources.
        
        Args:
            sources (List[Union[str, SourceMetadata]]): List of sources or source metadata
            format_type (str): Desired format type
            
        Returns:
            List[AttributionResult]: List of attribution results
        """
        results = []
        
        for source in sources:
            try:
                if isinstance(source, str):
                    metadata = self.extract_metadata_from_source(source)
                else:
                    metadata = source
                
                attribution = self.generate_attribution(metadata, format_type)
                results.append(attribution)
                
            except Exception as e:
                logger.error(f"Failed to generate attribution for source: {str(e)}")
                # Create error result
                error_metadata = SourceMetadata(
                    title="Error Processing Source",
                    url="",
                    source_type=SourceType.UNKNOWN,
                    license_type=LicenseType.UNKNOWN
                )
                error_result = AttributionResult(
                    source_metadata=error_metadata,
                    attribution_text=f"Error: {str(e)}",
                    attribution_markdown=f"**Error:** {str(e)}",
                    compliance_status="error",
                    errors=[str(e)]
                )
                results.append(error_result)
        
        return results
    
    def export_attribution_report(self, attributions: List[AttributionResult], format_type: str = "json") -> str:
        """
        Export attribution results in various formats.
        
        Args:
            attributions (List[AttributionResult]): List of attribution results
            format_type (str): Export format (json, markdown, plain_text)
            
        Returns:
            str: Exported attribution report
        """
        if format_type == "json":
            return self._export_json(attributions)
        elif format_type == "markdown":
            return self._export_markdown(attributions)
        elif format_type == "plain_text":
            return self._export_plain_text(attributions)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_json(self, attributions: List[AttributionResult]) -> str:
        """Export attributions as JSON string"""
        export_data = []
        for attr in attributions:
            export_data.append({
                "title": attr.source_metadata.title,
                "url": attr.source_metadata.url,
                "source_type": attr.source_metadata.source_type.value,
                "license": attr.source_metadata.license_type.value,
                "attribution_text": attr.attribution_text,
                "attribution_markdown": attr.attribution_markdown,
                "compliance_status": attr.compliance_status,
                "warnings": attr.warnings,
                "errors": attr.errors
            })
        
        return json.dumps(export_data, indent=2)
    
    def _export_markdown(self, attributions: List[AttributionResult]) -> str:
        """Export attributions as Markdown string"""
        markdown_lines = ["# Source Attribution Report", ""]
        
        for i, attr in enumerate(attributions, 1):
            markdown_lines.append(f"## {i}. {attr.source_metadata.title}")
            markdown_lines.append(f"**URL:** {attr.source_metadata.url}")
            markdown_lines.append(f"**Source Type:** {attr.source_metadata.source_type.value}")
            markdown_lines.append(f"**License:** {attr.source_metadata.license_type.value}")
            markdown_lines.append(f"**Attribution:** {attr.attribution_markdown}")
            markdown_lines.append(f"**Compliance:** {attr.compliance_status}")
            
            if attr.warnings:
                markdown_lines.append(f"**Warnings:** {', '.join(attr.warnings)}")
            if attr.errors:
                markdown_lines.append(f"**Errors:** {', '.join(attr.errors)}")
            
            markdown_lines.append("")
        
        return "\n".join(markdown_lines)
    
    def _export_plain_text(self, attributions: List[AttributionResult]) -> str:
        """Export attributions as plain text string"""
        text_lines = ["SOURCE ATTRIBUTION REPORT", "=" * 50, ""]
        
        for i, attr in enumerate(attributions, 1):
            text_lines.append(f"{i}. {attr.source_metadata.title}")
            text_lines.append(f"   URL: {attr.source_metadata.url}")
            text_lines.append(f"   Source Type: {attr.source_metadata.source_type.value}")
            text_lines.append(f"   License: {attr.source_metadata.license_type.value}")
            text_lines.append(f"   Attribution: {attr.attribution_text}")
            text_lines.append(f"   Compliance: {attr.compliance_status}")
            
            if attr.warnings:
                text_lines.append(f"   Warnings: {', '.join(attr.warnings)}")
            if attr.errors:
                text_lines.append(f"   Errors: {', '.join(attr.errors)}")
            
            text_lines.append("")
        
        return "\n".join(text_lines)


# Utility functions for easy integration
def create_source_attributor() -> SourceAttributor:
    """Factory function to create a SourceAttributor instance"""
    return SourceAttributor()


def quick_attribution(source: str, format_type: str = "plain_text") -> str:
    """
    Quick attribution generation for a single source.
    
    Args:
        source (str): Source identifier
        format_type (str): Desired format type
        
    Returns:
        str: Attribution text
    """
    try:
        attributor = SourceAttributor()
        metadata = attributor.extract_metadata_from_source(source)
        attribution = attributor.generate_attribution(metadata, format_type)
        return attribution.attribution_text
    except Exception as e:
        logger.error(f"Quick attribution failed: {str(e)}")
        return f"Error generating attribution: {str(e)}"


if __name__ == "__main__":
    # Example usage and testing
    def test_source_attributor():
        """Test the SourceAttributor class functionality"""
        print("🧪 Testing SourceAttributor class...")
        
        # Create attributor instance
        attributor = SourceAttributor()
        
        # Test sources
        test_sources = [
            "stackoverflow_12345_how_to_implement_adobe_analytics",
            "en_docs_analytics_implementation_home",
            "en_browse_analytics",
            "generic_web_source"
        ]
        
        print("\n📚 Testing source identification:")
        for source in test_sources:
            source_type = attributor.identify_source_type(source)
            print(f"  {source} -> {source_type.value}")
        
        print("\n🔍 Testing metadata extraction:")
        for source in test_sources:
            try:
                metadata = attributor.extract_metadata_from_source(source)
                print(f"  {source}:")
                print(f"    Title: {metadata.title}")
                print(f"    URL: {metadata.url}")
                print(f"    Type: {metadata.source_type.value}")
                print(f"    License: {metadata.license_type.value}")
            except Exception as e:
                print(f"  Error processing {source}: {str(e)}")
        
        print("\n📝 Testing attribution generation:")
        for source in test_sources:
            try:
                metadata = attributor.extract_metadata_from_source(source)
                attribution = attributor.generate_attribution(metadata, "plain_text")
                print(f"  {source}: {attribution.attribution_text}")
            except Exception as e:
                print(f"  Error generating attribution for {source}: {str(e)}")
        
        print("\n✅ SourceAttributor test completed!")
    
    # Run tests
    test_source_attributor()
