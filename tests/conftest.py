"""
Test fixtures for the Flask application.
"""
import os
import json
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create the app with test config
    app = create_app({
        'TESTING': True,
        'API_KEYS': ['test-api-key'],
    })
    
    # Return the app for testing
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Authentication headers for API requests."""
    return {
        'X-API-Key': 'test-api-key',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def calendar_event_data():
    """Sample calendar event data for testing."""
    return [
        {
            "id": "8dgs7j1qaq4uvk1m94aitnu5fs_20250227",
            "summary": "Home",
            "start": {
                "date": "2025-02-27"
            },
            "end": {
                "date": "2025-02-28"
            },
            "creator": {
                "email": "user@example.com",
                "self": True
            },
            "organizer": {
                "email": "user@example.com",
                "self": True
            },
            "created": "2022-11-28T16:33:07.000Z",
            "updated": "2024-01-25T16:49:15.544Z",
            "etag": "\"3412402711088000\"",
            "eventType": "workingLocation",
            "htmlLink": "https://www.google.com/calendar/event?eid=...",
            "iCalUID": "8dgs7j1qaq4uvk1m94aitnu5fs@google.com",
            "kind": "calendar#event",
            "originalStartTime": {
                "date": "2025-02-27"
            },
            "recurringEventId": "8dgs7j1qaq4uvk1m94aitnu5fs",
            "reminders": {
                "useDefault": False
            },
            "sequence": 0,
            "status": "confirmed",
            "transparency": "transparent",
            "visibility": "public",
            "workingLocationProperties": {
                "type": "homeOffice",
                "homeOffice": {}
            }
        },
        {
            "id": "9fht8k2rbr5vwl2n05bjuov6gt_20250228",
            "summary": "Office",
            "start": {
                "date": "2025-02-28"
            },
            "end": {
                "date": "2025-03-01"
            },
            "creator": {
                "email": "user@example.com",
                "self": True
            },
            "organizer": {
                "email": "user@example.com",
                "self": True
            },
            "created": "2022-11-28T16:33:07.000Z",
            "updated": "2024-01-25T16:49:15.544Z",
            "eventType": "workingLocation",
            "status": "confirmed",
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
            "id": "7cfs6i0pap3tuk0l83zismt4er_20250227T140000Z",
            "summary": "Team Meeting",
            "description": "Weekly team sync meeting",
            "start": {
                "dateTime": "2025-02-27T14:00:00Z",
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": "2025-02-27T15:00:00Z",
                "timeZone": "UTC"
            },
            "attendees": [
                {
                    "email": "user@example.com",
                    "self": True,
                    "responseStatus": "accepted"
                },
                {
                    "email": "colleague1@example.com",
                    "responseStatus": "accepted"
                },
                {
                    "email": "colleague2@example.com",
                    "responseStatus": "tentative"
                }
            ],
            "status": "confirmed"
        }
    ]