"""
Template loading and rendering utilities.
"""
import os
import logging
from typing import Dict, Any, Optional, Union, List

from flask import current_app
from jinja2 import Environment, FileSystemLoader, select_autoescape, BaseLoader

from app.utils.jinja_filters import register_filters

logger = logging.getLogger(__name__)


def create_jinja_environment(
    loader: BaseLoader,
    autoescape: Union[bool, List[str]] = select_autoescape(['html', 'xml']),
    trim_blocks: bool = True,
    lstrip_blocks: bool = True,
    extensions: Optional[List[str]] = ['jinja2.ext.loopcontrols'],
    **kwargs
) -> Environment:
    """
    Create and configure a Jinja2 environment with consistent settings.
    
    This is the central function for creating Jinja2 environments throughout the application.
    
    Args:
        loader: The template loader to use.
        autoescape: Autoescape setting (True/False or list of extensions to autoescape).
        trim_blocks: Whether to trim blocks.
        lstrip_blocks: Whether to strip leading whitespace from blocks.
        extensions: List of Jinja2 extensions to enable.
        **kwargs: Additional keyword arguments to pass to the Environment constructor.
        
    Returns:
        Configured Jinja2 Environment.
    """
    # Set default extensions if none provided
    if extensions is None:
        extensions = ['jinja2.ext.loopcontrols']
    extensions = ['jinja2.ext.loopcontrols']
    
    print (f"Creating Jinja2 environment with extensions: {extensions}")
    
    # Create Jinja2 environment with provided settings
    env = Environment(
        loader=loader,
        autoescape=autoescape,
        trim_blocks=trim_blocks,
        lstrip_blocks=lstrip_blocks,
        extensions=extensions,
        **kwargs
    )
    
    # Register custom filters
    register_filters(env)
    
    return env


def get_template_environment() -> Environment:
    """
    Create and configure a Jinja2 environment for the Flask application.
    
    Returns:
        Configured Jinja2 Environment.
    """
    # Get template directory from config or use default
    template_dir = current_app.config.get(
        "TEMPLATE_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    )
    
    # Get any configured extensions
    extensions = current_app.config.get("JINJA_EXTENSIONS", [])
    
    # Create Jinja2 environment using the central function
    return create_jinja_environment(
        loader=FileSystemLoader(template_dir),
        extensions=extensions
    )


def render_template(template_path: str, context: Dict[str, Any]) -> str:
    """
    Render a template with the given context.
    
    Args:
        template_path: Path to the template file (relative to template directory).
        context: Dictionary of variables to pass to the template.
        
    Returns:
        Rendered template as a string.
    """
    try:
        env = get_template_environment()
        template = env.get_template(template_path)
        return template.render(**context)
    except Exception as e:
        logger.error(f"Error rendering template {template_path}: {str(e)}")
        raise ValueError(f"Template rendering error: {str(e)}")


def get_template_path(format_id: str, template_id: str) -> Optional[str]:
    """
    Get the path to a template file.
    
    Args:
        format_id: Format identifier.
        template_id: Template identifier.
        
    Returns:
        Path to the template file or None if not found.
    """
    # Get template directory from config or use default
    template_dir = current_app.config.get(
        "TEMPLATE_DIR", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    )
    
    # Check if template exists
    template_path = os.path.join(format_id, f"{template_id}.md.j2")
    full_path = os.path.join(template_dir, template_path)
    
    if os.path.exists(full_path):
        return template_path
    
    return None