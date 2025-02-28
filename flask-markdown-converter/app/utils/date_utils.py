"""
Date formatting utilities.
"""
import logging
from typing import Optional, Union, Dict, Any
from datetime import datetime, date, timedelta
import pytz

logger = logging.getLogger(__name__)


def parse_iso_datetime(date_str: str) -> Optional[datetime]:
    """
    Parse an ISO 8601 datetime string.
    
    Args:
        date_str: ISO 8601 datetime string.
        
    Returns:
        Datetime object or None if parsing fails.
    """
    if not date_str:
        return None
    
    try:
        # Replace Z with +00:00 for fromisoformat compatibility
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        
        return datetime.fromisoformat(date_str)
    except ValueError:
        logger.warning(f"Failed to parse ISO datetime: {date_str}")
        return None


def parse_iso_date(date_str: str) -> Optional[date]:
    """
    Parse an ISO 8601 date string.
    
    Args:
        date_str: ISO 8601 date string (YYYY-MM-DD).
        
    Returns:
        Date object or None if parsing fails.
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logger.warning(f"Failed to parse ISO date: {date_str}")
        return None


def format_datetime(dt: Union[datetime, str], format_str: str = "%B %d, %Y %I:%M %p", timezone: str = "UTC") -> str:
    """
    Format a datetime object or ISO datetime string.
    
    Args:
        dt: Datetime object or ISO datetime string.
        format_str: Format string for strftime.
        timezone: Timezone name for conversion.
        
    Returns:
        Formatted datetime string.
    """
    if isinstance(dt, str):
        dt = parse_iso_datetime(dt)
        if not dt:
            return ""
    
    if not isinstance(dt, datetime):
        return ""
    
    try:
        # Convert to specified timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.UTC)
        
        target_tz = pytz.timezone(timezone)
        dt = dt.astimezone(target_tz)
        
        return dt.strftime(format_str)
    except Exception as e:
        logger.warning(f"Error formatting datetime: {str(e)}")
        return ""


def format_date(d: Union[date, datetime, str], format_str: str = "%B %d, %Y") -> str:
    """
    Format a date object, datetime object, or ISO date string.
    
    Args:
        d: Date object, datetime object, or ISO date string.
        format_str: Format string for strftime.
        
    Returns:
        Formatted date string.
    """
    if isinstance(d, str):
        # Try parsing as ISO date first
        parsed_date = parse_iso_date(d)
        if parsed_date:
            d = parsed_date
        else:
            # Try parsing as ISO datetime
            parsed_dt = parse_iso_datetime(d)
            if parsed_dt:
                d = parsed_dt.date()
            else:
                return ""
    
    if isinstance(d, datetime):
        d = d.date()
    
    if not isinstance(d, date):
        return ""
    
    try:
        return d.strftime(format_str)
    except Exception as e:
        logger.warning(f"Error formatting date: {str(e)}")
        return ""


def get_date_range(start_date: Union[date, datetime, str], end_date: Union[date, datetime, str]) -> str:
    """
    Get a formatted date range string.
    
    Args:
        start_date: Start date.
        end_date: End date.
        
    Returns:
        Formatted date range string.
    """
    # Parse dates if they are strings
    if isinstance(start_date, str):
        start_date = parse_iso_date(start_date) or parse_iso_datetime(start_date)
    
    if isinstance(end_date, str):
        end_date = parse_iso_date(end_date) or parse_iso_datetime(end_date)
    
    # Convert datetime to date if needed
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Handle invalid dates
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        return ""
    
    # For all-day events, end date is exclusive, so subtract one day
    if end_date > start_date:
        end_date = end_date - timedelta(days=1)
    
    # Format the date range
    if start_date == end_date:
        return format_date(start_date)
    else:
        return f"{format_date(start_date)} - {format_date(end_date)}"


def is_all_day_event(event: Dict[str, Any]) -> bool:
    """
    Check if an event is an all-day event.
    
    Args:
        event: Event dictionary.
        
    Returns:
        True if the event is an all-day event, False otherwise.
    """
    start = event.get("start", {})
    return "date" in start and "dateTime" not in start