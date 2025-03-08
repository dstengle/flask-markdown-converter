"""
Tests for calendar preprocessors.
"""
import pytest
from datetime import datetime
from app.preprocessors.calendar import (
    sort_events_by_datetime,
    group_events_by_date,
    clean_event_descriptions,
    add_formatted_dates,
    extract_working_location
)


def test_sort_events_by_datetime():
    """Test sorting events by datetime."""
    events = [
        {
            "id": "event3",
            "start": {"dateTime": "2025-02-27T15:00:00Z"}
        },
        {
            "id": "event1",
            "start": {"date": "2025-02-26"}
        },
        {
            "id": "event2",
            "start": {"dateTime": "2025-02-27T10:00:00Z"}
        }
    ]
    
    # Test ascending sort (default)
    sorted_events = sort_events_by_datetime(events)
    assert sorted_events[0]["id"] == "event1"
    assert sorted_events[1]["id"] == "event2"
    assert sorted_events[2]["id"] == "event3"
    
    # Test descending sort
    sorted_events_desc = sort_events_by_datetime(events, sort_order="desc")
    assert sorted_events_desc[0]["id"] == "event3"
    assert sorted_events_desc[1]["id"] == "event2"
    assert sorted_events_desc[2]["id"] == "event1"


def test_sort_events_by_datetime_handles_invalid_dates():
    """Test that sort_events_by_datetime handles invalid dates gracefully."""
    events = [
        {
            "id": "event1",
            "start": {"dateTime": "2025-02-27T15:00:00Z"}
        },
        {
            "id": "event2",
            "start": {"dateTime": "invalid-date"}
        },
        {
            "id": "event3",
            "start": {}
        }
    ]
    
    sorted_events = sort_events_by_datetime(events)
    # The invalid dates should be sorted to the beginning (datetime.min)
    assert sorted_events[0]["id"] in ["event2", "event3"]
    assert sorted_events[1]["id"] in ["event2", "event3"]
    assert sorted_events[2]["id"] == "event1"


def test_group_events_by_date():
    """Test grouping events by date."""
    events = [
        {
            "id": "event1",
            "start": {"date": "2025-02-26"}
        },
        {
            "id": "event2",
            "start": {"dateTime": "2025-02-27T10:00:00Z"}
        },
        {
            "id": "event3",
            "start": {"dateTime": "2025-02-27T15:00:00Z"}
        }
    ]
    
    grouped_events = group_events_by_date(events)
    assert "2025-02-26" in grouped_events
    assert "2025-02-27" in grouped_events
    assert len(grouped_events["2025-02-26"]) == 1
    assert len(grouped_events["2025-02-27"]) == 2
    assert grouped_events["2025-02-26"][0]["id"] == "event1"
    assert grouped_events["2025-02-27"][0]["id"] == "event2"
    assert grouped_events["2025-02-27"][1]["id"] == "event3"


def test_group_events_by_date_handles_invalid_dates():
    """Test that group_events_by_date handles invalid dates gracefully."""
    events = [
        {
            "id": "event1",
            "start": {"dateTime": "2025-02-27T15:00:00Z"}
        },
        {
            "id": "event2",
            "start": {"dateTime": "invalid-date"}
        },
        {
            "id": "event3",
            "start": {}
        }
    ]
    
    grouped_events = group_events_by_date(events)
    assert "2025-02-27" in grouped_events
    assert len(grouped_events["2025-02-27"]) == 1
    assert grouped_events["2025-02-27"][0]["id"] == "event1"
    # Invalid dates should be skipped
    assert len(grouped_events) == 1


def test_clean_event_descriptions():
    """Test cleaning HTML from event descriptions."""
    events = [
        {
            "id": "event1",
            "description": "<p>This is a <strong>test</strong> description with <a href='https://example.com'>link</a>.</p>"
        },
        {
            "id": "event2",
            "description": "Plain text description"
        },
        {
            "id": "event3",
            "description": None
        },
        {
            "id": "event4"
            # No description field
        }
    ]
    
    cleaned_events = clean_event_descriptions(events)
    assert cleaned_events[0]["description"] == "This is a test description with link."
    assert cleaned_events[1]["description"] == "Plain text description"
    assert cleaned_events[2]["description"] == ""
    assert "description" not in cleaned_events[3]


def test_add_formatted_dates():
    """Test adding formatted dates to events."""
    events = [
        {
            "id": "event1",
            "start": {"date": "2025-02-26"},
            "end": {"date": "2025-02-27"}
        },
        {
            "id": "event2",
            "start": {"dateTime": "2025-02-27T10:00:00Z"},
            "end": {"dateTime": "2025-02-27T11:00:00Z"}
        }
    ]
    
    formatted_events = add_formatted_dates(events)
    
    # All-day event
    assert formatted_events[0]["formatted_start_date"] == "February 26, 2025"
    assert formatted_events[0]["formatted_end_date"] == "February 26, 2025"
    assert formatted_events[0]["is_all_day"] is True
    
    # Time-specific event
    assert formatted_events[1]["formatted_start_date"] == "February 27, 2025"
    assert formatted_events[1]["formatted_start_time"] == "10:00 AM"
    assert formatted_events[1]["formatted_end_date"] == "February 27, 2025"
    assert formatted_events[1]["formatted_end_time"] == "11:00 AM"
    assert formatted_events[1]["is_all_day"] is False


def test_extract_working_location():
    """Test extracting working location information."""
    events = [
        {
            "id": "event1",
            "eventType": "workingLocation",
            "workingLocationProperties": {
                "type": "homeOffice",
                "homeOffice": {}
            }
        },
        {
            "id": "event2",
            "eventType": "workingLocation",
            "workingLocationProperties": {
                "type": "officeLocation",
                "officeLocation": {
                    "buildingId": "Building A",
                    "floorId": "Floor 3",
                    "deskId": "Desk 42"
                }
            }
        },
        {
            "id": "event3",
            "eventType": "workingLocation",
            "workingLocationProperties": {
                "type": "customLocation",
                "customLocation": {
                    "label": "Coffee Shop"
                }
            }
        },
        {
            "id": "event4",
            "eventType": "normal"
            # Not a working location event
        }
    ]
    
    processed_events = extract_working_location(events)
    
    assert processed_events[0]["working_location"] == "Home Office"
    assert processed_events[1]["working_location"] == "Office - Building: Building A, Floor: Floor 3, Desk: Desk 42"
    assert processed_events[2]["working_location"] == "Coffee Shop"
    assert "working_location" not in processed_events[3]