"""
Tests for the convert API endpoint.
"""
import json
import pytest


def test_convert_endpoint_requires_auth(client):
    """Test that the convert endpoint requires authentication."""
    response = client.post('/api/v1/convert/calendar')
    assert response.status_code == 401
    assert b'API key is required' in response.data


def test_convert_endpoint_requires_valid_auth(client):
    """Test that the convert endpoint requires a valid API key."""
    headers = {
        'X-API-Key': 'invalid-key',
        'Content-Type': 'application/json'
    }
    response = client.post('/api/v1/convert/calendar', headers=headers)
    assert response.status_code == 401
    assert b'Invalid API key' in response.data


def test_convert_endpoint_requires_json(client, auth_headers):
    """Test that the convert endpoint requires JSON content."""
    response = client.post('/api/v1/convert/calendar', headers={
        'X-API-Key': auth_headers['X-API-Key']
    })
    assert response.status_code == 400
    assert b'Request must be JSON' in response.data


def test_convert_endpoint_with_empty_data(client, auth_headers):
    """Test that the convert endpoint handles empty data."""
    response = client.post(
        '/api/v1/convert/calendar',
        headers=auth_headers,
        json=[]
    )
    assert response.status_code == 200
    assert b'No calendar events found' in response.data


def test_convert_endpoint_with_invalid_format(client, auth_headers, calendar_event_data):
    """Test that the convert endpoint validates the format."""
    response = client.post(
        '/api/v1/convert/invalid_format',
        headers=auth_headers,
        json=calendar_event_data
    )
    assert response.status_code == 400
    assert b'Format not supported' in response.data


def test_convert_endpoint_with_missing_data(client, auth_headers):
    """Test that the convert endpoint validates required data fields."""
    invalid_data = {
        "events": [
            {"title": "Test Event"} # missing required fields like date
        ]
    }
    response = client.post(
        '/api/v1/convert/calendar',
        headers=auth_headers, 
        json=invalid_data
    )
    assert response.status_code == 400
    assert b'Schema validation' in response.data

def test_convert_endpoint_rejects_preprocessors_parameter(client, auth_headers, calendar_event_data):
    """Test that the convert endpoint rejects the preprocessors parameter."""
    response = client.post(
        '/api/v1/convert/calendar?preprocessors=sort_by_date',
        headers=auth_headers,
        json=calendar_event_data
    )
    assert response.status_code == 400
    assert b'preprocessors parameter is no longer supported' in response.data

def test_convert_endpoint_without_headers(client):
    """Test that the convert endpoint requires headers."""
    response = client.post('/api/v1/convert/calendar')
    assert response.status_code == 401

def test_convert_endpoint_malformed_json(client, auth_headers):
    """Test handling of malformed JSON data."""
    response = client.post(
        '/api/v1/convert/calendar',
        headers=auth_headers,
        data='{invalid json',
        content_type='application/json'
    )
    assert response.status_code == 400
    assert b'Invalid JSON' in response.data


def test_convert_calendar_standard_template(client, auth_headers, calendar_event_data):
    """Test converting calendar data with the standard template."""
    response = client.post(
        '/api/v1/convert/calendar',
        headers=auth_headers,
        json=calendar_event_data
    )
    assert response.status_code == 200
    assert response.content_type == 'text/markdown'
    
    # Check for expected content in the markdown
    markdown = response.data.decode('utf-8')
    assert '# Calendar Events' in markdown
    assert '## February 27, 2025' in markdown
    assert '**Home**' in markdown
    assert '**Team Meeting**' in markdown
    assert 'Weekly team sync meeting' in markdown


def test_convert_calendar_compact_template(client, auth_headers, calendar_event_data):
    """Test converting calendar data with the compact template."""
    response = client.post(
        '/api/v1/convert/calendar?template=compact',
        headers=auth_headers,
        json=calendar_event_data
    )
    assert response.status_code == 200
    assert response.content_type == 'text/markdown'
    
    # Check for expected content in the markdown
    markdown = response.data.decode('utf-8')
    assert '# Calendar Events (Compact)' in markdown
    assert '## February 27, 2025' in markdown
    assert '[All day] **Home**' in markdown
    assert '**Team Meeting**' in markdown  # Time format may vary based on locale settings


def test_formats_endpoint(client, auth_headers):
    """Test the formats endpoint."""
    response = client.get('/api/v1/formats', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'formats' in data
    
    # Check that calendar format is included
    calendar_format = next((f for f in data['formats'] if f['id'] == 'calendar'), None)
    assert calendar_format is not None
    assert calendar_format['name'] == 'Calendar'
    assert 'templates' in calendar_format
    assert 'preprocessors' in calendar_format


def test_format_info_endpoint(client, auth_headers):
    """Test the format info endpoint."""
    response = client.get('/api/v1/formats/calendar', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['id'] == 'calendar'
    assert data['name'] == 'Calendar'
    assert 'templates' in data
    assert 'preprocessors' in data
    assert 'options' in data
    assert 'schema' in data


def test_format_info_endpoint_invalid_format(client, auth_headers):
    """Test the format info endpoint with an invalid format."""
    response = client.get('/api/v1/formats/invalid_format', headers=auth_headers)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data


def test_health_endpoint(client, auth_headers):
    """Test the health endpoint."""
    response = client.get('/api/v1/health', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['status'] == 'healthy'
    assert 'version' in data
    assert 'uptime' in data
    assert 'memoryUsage' in data