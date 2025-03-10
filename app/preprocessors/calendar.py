"""
Calendar-specific preprocessors.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import re
from collections import defaultdict

from app.preprocessors.registry import register_preprocessor

logger = logging.getLogger(__name__)


@register_preprocessor("sort_events_by_datetime")
def sort_events_by_datetime(events: List[Dict[str, Any]], sort_order: str = "asc") -> List[Dict[str, Any]]:
    """
    Sort events by start date and time.
    
    Args:
        events: List of calendar events.
        sort_order: Sort order, either "asc" or "desc".
        
    Returns:
        Sorted list of events.
    """
    def get_event_datetime(event):
        """Extract datetime from event for sorting."""
        start = event.get("start")
        if not isinstance(start, dict):
            return datetime.min
        
        # Handle all-day events (date only)
        if "date" in start:
            try:
                return datetime.strptime(start["date"], "%Y-%m-%d").replace(tzinfo=None)
            except (ValueError, TypeError):
                return datetime.min
        
        # Handle events with specific times
        elif "dateTime" in start:
            try:
                # Handle ISO 8601 format with timezone
                dt_str = start["dateTime"]
                # Replace Z with +00:00 for fromisoformat compatibility
                dt_str = dt_str.replace("Z", "+00:00")
                return datetime.fromisoformat(dt_str).replace(tzinfo=None)
            except (ValueError, TypeError):
                return datetime.min
        
        return datetime.min
    
    # Sort events
    sorted_events = sorted(events, key=get_event_datetime, reverse=(sort_order.lower() == "desc"))
    
    return sorted_events


@register_preprocessor("group_events_by_date")
def group_events_by_date(events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group events by date.
    
    Args:
        events: List of calendar events.
        
    Returns:
        Dictionary with dates as keys and lists of events as values.
    """
    grouped_events = defaultdict(list)
    
    for event in events:
        start = event.get("start")
        if not isinstance(start, dict):
            logger.warning(f"Invalid start format: {start}")
            continue
        
        # Get the date string
        date_str = None
        
        # Handle all-day events
        if "date" in start:
            date_str = start["date"]
        
        # Handle events with specific times
        elif "dateTime" in start:
            try:
                # Handle ISO 8601 format with timezone
                dt_str = start["dateTime"]
                # Replace Z with +00:00 for fromisoformat compatibility
                dt_str = dt_str.replace("Z", "+00:00")
                dt = datetime.fromisoformat(dt_str)
                date_str = dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                logger.warning(f"Invalid dateTime format: {start.get('dateTime')}")
                continue
        
        if date_str:
            grouped_events[date_str].append(event)
    
    return dict(grouped_events)


@register_preprocessor("clean_event_descriptions")
def clean_event_descriptions(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean HTML and normalize formatting in event descriptions.
    
    Args:
        events: List of calendar events.
        
    Returns:
        List of events with cleaned descriptions.
    """
    def clean_html(html_text):
        """Remove HTML tags from text."""
        if not html_text:
            return ""
        
        # Simple HTML tag removal
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        
        # Replace HTML entities
        clean_text = clean_text.replace('&nbsp;', ' ')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&quot;', '"')
        clean_text = clean_text.replace('&#39;', "'")
        
        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    # Process each event
    for event in events:
        if "description" in event:
            event["description"] = clean_html(event["description"])
    
    return events


@register_preprocessor("add_formatted_dates")
def add_formatted_dates(events: List[Dict[str, Any]], date_format: str = "%B %d, %Y") -> List[Dict[str, Any]]:
    """
    Add formatted date strings to events.
    
    Args:
        events: List of calendar events.
        date_format: Date format string.
        
    Returns:
        List of events with formatted dates.
    """
    for event in events:
        start = event.get("start", {})
        end = event.get("end", {})
        
        # Process start date
        if "date" in start:
            try:
                dt = datetime.strptime(start["date"], "%Y-%m-%d")
                event["formatted_start_date"] = dt.strftime(date_format)
                event["is_all_day"] = True
            except (ValueError, TypeError):
                event["formatted_start_date"] = start["date"]
                event["is_all_day"] = True
        
        elif "dateTime" in start:
            try:
                # Handle ISO 8601 format with timezone
                dt_str = start["dateTime"]
                # Replace Z with +00:00 for fromisoformat compatibility
                dt_str = dt_str.replace("Z", "+00:00")
                dt = datetime.fromisoformat(dt_str)
                event["formatted_start_date"] = dt.strftime(date_format)
                event["formatted_start_time"] = dt.strftime("%I:%M %p")
                event["is_all_day"] = False
            except (ValueError, TypeError):
                event["formatted_start_date"] = start["dateTime"]
                event["is_all_day"] = False
        
        # Process end date
        if "date" in end:
            try:
                dt = datetime.strptime(end["date"], "%Y-%m-%d")
                # Subtract one day for all-day events (end date is exclusive)
                dt = dt.replace(day=dt.day - 1)
                event["formatted_end_date"] = dt.strftime(date_format)
            except (ValueError, TypeError):
                event["formatted_end_date"] = end["date"]
        
        elif "dateTime" in end:
            try:
                # Handle ISO 8601 format with timezone
                dt_str = end["dateTime"]
                # Replace Z with +00:00 for fromisoformat compatibility
                dt_str = dt_str.replace("Z", "+00:00")
                dt = datetime.fromisoformat(dt_str)
                event["formatted_end_date"] = dt.strftime(date_format)
                event["formatted_end_time"] = dt.strftime("%I:%M %p")
            except (ValueError, TypeError):
                event["formatted_end_date"] = end["dateTime"]
    
    return events


@register_preprocessor("extract_working_location")
def extract_working_location(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract and format working location information.
    
    Args:
        events: List of calendar events.
        
    Returns:
        List of events with extracted working location.
    """
    for event in events:
        if event.get("eventType") == "workingLocation":
            props = event.get("workingLocationProperties", {})
            location_type = props.get("type")
            
            if location_type == "homeOffice":
                event["working_location"] = "Home Office"
            elif location_type == "officeLocation":
                office_details = props.get("officeLocation", {})
                building = office_details.get("buildingId", "")
                floor = office_details.get("floorId", "")
                desk = office_details.get("deskId", "")
                
                location_parts = []
                if building:
                    location_parts.append(f"Building: {building}")
                if floor:
                    location_parts.append(f"Floor: {floor}")
                if desk:
                    location_parts.append(f"Desk: {desk}")
                
                event["working_location"] = "Office - " + ", ".join(location_parts) if location_parts else "Office"
            elif location_type == "customLocation":
                custom_details = props.get("customLocation", {})
                event["working_location"] = custom_details.get("label", "Custom Location")
            else:
                event["working_location"] = "Unknown"
    
    return events