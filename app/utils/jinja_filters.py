"""
Custom Jinja2 filters for template rendering.
"""
import re
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import html

from jinja2 import Environment

logger = logging.getLogger(__name__)


def format_date(value: Union[str, datetime, date], format_str: str = "%B %d, %Y") -> str:
    """
    Format a date string or datetime object.
    
    Args:
        value: Date string (ISO format) or datetime object.
        format_str: Format string for strftime.
        
    Returns:
        Formatted date string.
    """
    if not value:
        return ""
    
    if isinstance(value, str):
        try:
            # Try parsing as ISO date
            if "T" in value:
                # Has time component
                # Replace Z with +00:00 for fromisoformat compatibility
                value = value.replace("Z", "+00:00")
                dt = datetime.fromisoformat(value)
            else:
                # Date only
                dt = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return value
    elif isinstance(value, (datetime, date)):
        dt = value
    else:
        return str(value)
    
    return dt.strftime(format_str)


def format_time(value: Union[str, datetime], format_str: str = "%I:%M %p") -> str:
    """
    Format a time string or datetime object.
    
    Args:
        value: Time string (ISO format) or datetime object.
        format_str: Format string for strftime.
        
    Returns:
        Formatted time string.
    """
    if not value:
        return ""
    
    if isinstance(value, str):
        try:
            # Try parsing as ISO datetime
            # Replace Z with +00:00 for fromisoformat compatibility
            value = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(value)
        except ValueError:
            return value
    elif isinstance(value, datetime):
        dt = value
    else:
        return str(value)
    
    return dt.strftime(format_str)


def html_to_markdown(value: str) -> str:
    """
    Convert HTML to Markdown.
    
    Args:
        value: HTML string.
        
    Returns:
        Markdown string.
    """
    if not value:
        return ""
    
    # Unescape HTML entities
    text = html.unescape(value)
    
    # Convert <strong>, <b> to **
    text = re.sub(r'<(?:strong|b)>(.*?)</(?:strong|b)>', r'**\1**', text)
    
    # Convert <em>, <i> to *
    text = re.sub(r'<(?:em|i)>(.*?)</(?:em|i)>', r'*\1*', text)
    
    # Convert <a href="...">...</a> to [text](url)
    text = re.sub(r'<a href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text)
    
    # Convert <h1> to # 
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', text)
    
    # Convert <h2> to ## 
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text)
    
    # Convert <h3> to ### 
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text)
    
    # Convert <ul><li> to -
    text = re.sub(r'<ul[^>]*>(.*?)</ul>', lambda m: re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', m.group(1)), text)
    
    # Convert <ol><li> to 1.
    text = re.sub(r'<ol[^>]*>(.*?)</ol>', lambda m: re.sub(r'<li[^>]*>(.*?)</li>', r'1. \1\n', m.group(1)), text)
    
    # Convert <br> to newline
    text = re.sub(r'<br[^>]*>', '\n', text)
    
    # Convert <p> to newline
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text)
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def truncate(value: str, length: int = 100, ellipsis: str = "...") -> str:
    """
    Truncate a string to a specified length.
    
    Args:
        value: String to truncate.
        length: Maximum length.
        ellipsis: String to append if truncated.
        
    Returns:
        Truncated string.
    """
    if not value:
        return ""
    
    if len(value) <= length:
        return value
    
    return value[:length] + ellipsis


def format_list(value: List[Any], separator: str = ", ", last_separator: str = " and ") -> str:
    """
    Format a list as a string with separators.
    
    Args:
        value: List to format.
        separator: Separator between items.
        last_separator: Separator before the last item.
        
    Returns:
        Formatted string.
    """
    if not value:
        return ""
    
    if len(value) == 1:
        return str(value[0])
    
    if len(value) == 2:
        return f"{value[0]}{last_separator}{value[1]}"
    
    return separator.join(str(item) for item in value[:-1]) + last_separator + str(value[-1])


def register_filters(env: Environment) -> None:
    """
    Register custom filters with a Jinja2 environment.
    
    Args:
        env: Jinja2 Environment.
    """
    env.filters["format_date"] = format_date
    env.filters["format_time"] = format_time
    env.filters["html_to_markdown"] = html_to_markdown
    env.filters["truncate"] = truncate
    env.filters["format_list"] = format_list
    env.filters['dict_add'] = lambda d, key, value: d.update({key: value}) or d