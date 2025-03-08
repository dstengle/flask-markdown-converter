"""
Tests for calendar templates.
"""
import os
import pytest
from jinja2 import FileSystemLoader

from app.utils.template import create_jinja_environment


@pytest.fixture
def template_env():
    """Create a Jinja2 environment for testing templates."""
    # Get the path to the templates directory
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                               "app", "templates")
    
    # Create Jinja2 environment using the central function
    env = create_jinja_environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,  # Different from production for testing purposes
        trim_blocks=True,
        lstrip_blocks=True,
        extensions=[]  # No extensions for testing
    )
    
    # Add dict_add filter for testing
    env.filters['dict_add'] = lambda d, key, value: d.update({key: value}) or d
    
    return env


@pytest.fixture
def calendar_event_data():
    """Sample calendar event data for testing."""
    return [
        {
            "id": "event1",
            "summary": "All-day Event",
            "start": {
                "date": "2025-02-26"
            },
            "end": {
                "date": "2025-02-27"
            },
            "status": "confirmed",
            "eventType": "workingLocation",
            "workingLocationProperties": {
                "type": "homeOffice",
                "homeOffice": {}
            }
        },
        {
            "id": "event2",
            "summary": "Time-specific Event",
            "description": "This is a test event with a description",
            "location": "Conference Room A",
            "start": {
                "dateTime": "2025-02-27T10:00:00Z",
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": "2025-02-27T11:00:00Z",
                "timeZone": "UTC"
            },
            "status": "confirmed",
            "attendees": [
                {
                    "email": "user@example.com",
                    "self": True
                },
                {
                    "email": "colleague@example.com"
                }
            ]
        }
    ]


def test_standard_template(template_env, calendar_event_data):
    """Test the standard calendar template."""
    template = template_env.get_template("calendar/standard.md.j2")
    result = template.render(data=calendar_event_data)
    
    # Check that the template renders correctly
    assert "# Calendar Events" in result
    
    # Check for the first event (all-day)
    assert "## February 26, 2025" in result
    assert "**All-day Event**" in result
    assert "All day event" in result
    assert "Status: Confirmed" in result
    assert "Working Location: Home Office" in result
    
    # Check for the second event (time-specific)
    assert "## February 27, 2025" in result
    assert "**Time-specific Event**" in result
    assert "10:00 AM - 11:00 AM" in result
    assert "Location: Conference Room A" in result
    assert "Description: This is a test event with a description" in result
    assert "Attendees: user@example.com, colleague@example.com" in result


def test_compact_template(template_env, calendar_event_data):
    """Test the compact calendar template."""
    template = template_env.get_template("calendar/compact.md.j2")
    result = template.render(data=calendar_event_data)
    
    # Check that the template renders correctly
    assert "# Calendar Events (Compact)" in result
    
    # Check for the first event (all-day)
    assert "## February 26, 2025" in result
    assert "[All day] **All-day Event** (Home)" in result
    
    # Check for the second event (time-specific)
    assert "## February 27, 2025" in result
    assert "[10:00 AM] **Time-specific Event**" in result


def test_templates_with_empty_data(template_env):
    """Test templates with empty data."""
    # Standard template
    standard_template = template_env.get_template("calendar/standard.md.j2")
    standard_result = standard_template.render(data=[])
    assert "# Calendar Events" in standard_result
    assert "No calendar events found" in standard_result
    
    # Compact template
    compact_template = template_env.get_template("calendar/compact.md.j2")
    compact_result = compact_template.render(data=[])
    assert "# Calendar Events (Compact)" in compact_result
    assert "No calendar events found" in compact_result


def test_templates_with_missing_fields(template_env):
    """Test templates with events missing optional fields."""
    events = [
        {
            "id": "event1",
            "start": {
                "date": "2025-02-26"
            },
            "end": {
                "date": "2025-02-27"
            }
            # Missing summary, status, etc.
        }
    ]
    
    # Standard template
    standard_template = template_env.get_template("calendar/standard.md.j2")
    standard_result = standard_template.render(data=events)
    assert "# Calendar Events" in standard_result
    assert "## February 26, 2025" in standard_result
    assert "**Untitled Event**" in standard_result
    
    # Compact template
    compact_template = template_env.get_template("calendar/compact.md.j2")
    compact_result = compact_template.render(data=events)
    assert "# Calendar Events (Compact)" in compact_result
    assert "## February 26, 2025" in compact_result
    assert "[All day] **Untitled Event**" in compact_result