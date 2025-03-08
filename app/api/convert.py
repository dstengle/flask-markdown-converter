"""
Main conversion handler for JSON to Markdown.
"""
import os
import yaml
import json
import logging
from typing import Dict, List, Any, Optional, Union

from flask import current_app
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.preprocessors.registry import get_preprocessor
from app.utils.template import render_template
from app.utils.jinja_filters import register_filters

logger = logging.getLogger(__name__)


def load_format_config(format_id: str) -> Optional[Dict[str, Any]]:
    """
    Load format configuration from YAML file.
    
    Args:
        format_id: The format identifier.
        
    Returns:
        Dict containing format configuration or None if not found.
    """
    config_dir = current_app.config.get("CONFIG_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "config"))
    config_path = os.path.join(config_dir, "formats", f"{format_id}.yaml")
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logger.warning(f"Format configuration not found: {format_id}")
        return None
    except Exception as e:
        logger.error(f"Error loading format configuration: {str(e)}")
        raise ValueError(f"Error loading format configuration: {str(e)}")


def get_all_formats() -> List[Dict[str, Any]]:
    """
    Get information about all supported conversion formats.
    
    Returns:
        List of format information dictionaries.
    """
    config_dir = current_app.config.get("CONFIG_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "config"))
    formats_dir = os.path.join(config_dir, "formats")
    
    formats = []
    
    try:
        for filename in os.listdir(formats_dir):
            if filename.endswith(".yaml"):
                format_id = filename[:-5]  # Remove .yaml extension
                format_config = load_format_config(format_id)
                
                if format_config:
                    # Extract relevant information for the formats endpoint
                    format_info = {
                        "id": format_id,
                        "name": format_config.get("name", format_id),
                        "description": format_config.get("description", ""),
                        "templates": [
                            {
                                "id": template["id"],
                                "name": template["name"],
                                "description": template.get("description", ""),
                                "default": template.get("default", False)
                            }
                            for template in format_config.get("templates", [])
                        ],
                        "preprocessors": [
                            {
                                "id": preprocessor["id"],
                                "name": preprocessor["name"],
                                "description": preprocessor.get("description", ""),
                                "default": preprocessor.get("default", False)
                            }
                            for preprocessor in format_config.get("preprocessors", [])
                        ]
                    }
                    formats.append(format_info)
    
    except Exception as e:
        logger.error(f"Error retrieving formats: {str(e)}")
        raise
    
    return formats


def get_format_info(format_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific conversion format.
    
    Args:
        format_id: The format identifier.
        
    Returns:
        Dict containing detailed format information or None if not found.
    """
    format_config = load_format_config(format_id)
    
    if not format_config:
        return None
    
    # Load schema if available
    schema = None
    config_dir = current_app.config.get("CONFIG_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "config"))
    schema_path = os.path.join(config_dir, "schemas", f"{format_id}.json")
    
    try:
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema = json.load(f)
    except Exception as e:
        logger.warning(f"Error loading schema for {format_id}: {str(e)}")
    
    # Build detailed format information
    format_info = {
        "id": format_id,
        "name": format_config.get("name", format_id),
        "description": format_config.get("description", ""),
        "templates": [
            {
                "id": template["id"],
                "name": template["name"],
                "description": template.get("description", ""),
                "default": template.get("default", False),
                "sample": template.get("sample", "")
            }
            for template in format_config.get("templates", [])
        ],
        "preprocessors": [
            {
                "id": preprocessor["id"],
                "name": preprocessor["name"],
                "description": preprocessor.get("description", ""),
                "default": preprocessor.get("default", False),
                "parameters": preprocessor.get("parameters", [])
            }
            for preprocessor in format_config.get("preprocessors", [])
        ],
        "options": format_config.get("options", []),
        "schema": schema
    }
    
    return format_info


def apply_preprocessors(data: Any, format_id: str, preprocessor_ids: Optional[List[str]] = None) -> Any:
    """
    Apply preprocessors to the input data.
    
    Args:
        data: The input data to process.
        format_id: The format identifier.
        preprocessor_ids: List of preprocessor IDs to apply. If None, use default preprocessors.
        
    Returns:
        Processed data.
    """
    format_config = load_format_config(format_id)
    
    if not format_config:
        raise ValueError(f"Format not found: {format_id}")
    
    # If no preprocessors specified, use default ones
    if preprocessor_ids is None:
        preprocessor_ids = [
            p["id"] for p in format_config.get("preprocessors", [])
            if p.get("default", False)
        ]
    
    # Apply each preprocessor in sequence
    processed_data = data
    for preprocessor_id in preprocessor_ids:
        # Find preprocessor config
        preprocessor_config = next(
            (p for p in format_config.get("preprocessors", []) if p["id"] == preprocessor_id),
            None
        )
        
        if not preprocessor_config:
            logger.warning(f"Preprocessor not found: {preprocessor_id}")
            continue
        
        # Get preprocessor function
        function_name = preprocessor_config.get("function")
        if not function_name:
            logger.warning(f"No function specified for preprocessor: {preprocessor_id}")
            continue
        
        preprocessor_func = get_preprocessor(function_name)
        if not preprocessor_func:
            logger.warning(f"Preprocessor function not found: {function_name}")
            continue
        
        # Apply preprocessor
        try:
            processed_data = preprocessor_func(processed_data)
            logger.debug(f"Applied preprocessor: {preprocessor_id}")
        except Exception as e:
            logger.error(f"Error applying preprocessor {preprocessor_id}: {str(e)}")
            raise ValueError(f"Error in preprocessor {preprocessor_id}: {str(e)}")
    
    return processed_data


def convert_to_markdown(
    format: str,
    data: Any,
    template_id: str = "standard",
    preprocessors: Optional[List[str]] = None
) -> str:
    """
    Convert JSON data to Markdown using the specified format and template.
    
    Args:
        format: The conversion format (e.g., "calendar").
        data: The input data to convert.
        template_id: The template ID to use for conversion.
        preprocessors: List of preprocessor IDs to apply.
        
    Returns:
        Markdown content as a string.
    """
    # Load format configuration
    format_config = load_format_config(format)
    
    if not format_config:
        raise ValueError(f"Format not supported: {format}")
    
    # Find template configuration
    template_config = next(
        (t for t in format_config.get("templates", []) if t["id"] == template_id),
        None
    )
    
    if not template_config:
        # If template not found, try to use the default template
        template_config = next(
            (t for t in format_config.get("templates", []) if t.get("default", False)),
            None
        )
        
        if not template_config:
            raise ValueError(f"Template not found: {template_id}")
    
    # Apply preprocessors
    processed_data = apply_preprocessors(data, format, preprocessors)
    
    # Render template
    template_path = template_config.get("file")
    if not template_path:
        raise ValueError(f"Template file not specified for {template_id}")
    
    try:
        markdown_content = render_template(template_path, {"data": processed_data})
        return markdown_content
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        raise ValueError(f"Error rendering template: {str(e)}")