# Flask JSON-to-Markdown Conversion Service Specification

## Overview
A Flask-based web service that provides webhook endpoints to accept various types of JSON input and return Markdown output. The system is structured to support multiple conversion types through a unified API pattern, with the initial implementation focused on Google Calendar data. This service acts as an intermediary that transforms structured data into human-readable Markdown format for easy display or sharing.

## System Requirements

### Functional Requirements
1. Accept JSON payloads via HTTP POST requests
2. Implement a nested API structure to handle different types of JSON-to-Markdown conversions
3. Use Jinja2 templates for generating Markdown from structured data
4. Support configurable preprocessors for data transformation before template rendering
5. Load conversion configurations from YAML files
6. All configuration should be loaded from the server side based on the path parameter
7. Support Google Calendar API data conversion to Markdown for MVP
8. Return Markdown output with appropriate HTTP status codes
9. Require API key authentication via header for all endpoints
10. Log all requests and responses for monitoring and debugging

### Technical Requirements
1. **Framework**: Flask 2.0+
2. **Python Version**: Python 3.9+
3. **Template Engine**: Jinja2
4. **Configuration Format**: YAML
5. **Authentication**: API key via header
6. **Data Validation**: Pydantic or JSON Schema
7. **Testing Framework**: pytest

## API Endpoints

The API follows a nested structure to handle different types of JSON-to-Markdown conversions within the same service.

### POST /api/v1/convert/{format}
Converts JSON input to Markdown output using the specified format.

**Headers:**
```
X-API-Key: your_api_key
Content-Type: application/json
```

**Path Parameters:**
- `format`: The conversion format (e.g., "calendar")

**Request Format:**
```json
[
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
      "self": true
    },
    "organizer": {
      "email": "user@example.com",
      "self": true
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
      "useDefault": false
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
  // Additional calendar events...
]
```

**Response Format:**
```
Status: 200 OK
Content-Type: text/markdown

# Markdown content generated from the template
```

### GET /api/v1/formats
Returns information about all supported conversion formats.

**Headers:**
```
X-API-Key: your_api_key
```

**Response Format:**
```
Status: 200 OK
Content-Type: application/json

{
  "formats": [
    {
      "id": "calendar",
      "name": "Calendar",
      "description": "Google Calendar data to Markdown",
      "templates": [
        {
          "id": "standard",
          "name": "Standard Format",
          "description": "Detailed calendar view with events grouped by day",
          "default": true
        },
        {
          "id": "compact",
          "name": "Compact Format",
          "description": "Condensed calendar view with minimal details",
          "default": false
        }
      ],
      "preprocessors": [
        {
          "id": "sort_events",
          "name": "Sort Events",
          "description": "Sort events by start date and time",
          "default": true
        },
        // Additional preprocessors...
      ]
    },
    // Additional formats...
  ]
}
```

### GET /api/v1/formats/{format}
Returns detailed information about a specific conversion format.

**Headers:**
```
X-API-Key: your_api_key
```

**Path Parameters:**
- `format`: The conversion format (e.g., "calendar", "tasks", "notes")

**Response Format:**
```
Status: 200 OK
Content-Type: application/json

{
  "id": "calendar",
  "name": "Calendar",
  "description": "Google Calendar data to Markdown",
  "templates": [
    {
      "id": "standard",
      "name": "Standard Format",
      "description": "Detailed calendar view with events grouped by day",
      "default": true,
      "sample": "# Calendar Events\n\n## February 27, 2025\n\n- **Home** - Work from home\n  - All day event\n  - Status: Confirmed"
    },
    // Additional templates...
  ],
  "preprocessors": [
    {
      "id": "sort_events",
      "name": "Sort Events",
      "description": "Sort events by start date and time",
      "default": true,
      "parameters": [
        {
          "name": "sortOrder",
          "type": "string",
          "description": "Sort order (asc or desc)",
          "default": "asc",
          "required": false
        }
      ]
    },
    // Additional preprocessors...
  ],
  "options": [
    {
      "name": "timezone",
      "type": "string",
      "description": "Timezone for date/time formatting",
      "default": "UTC",
      "required": false
    },
    // Additional options...
  ],
  "schema": {
    // JSON Schema for the expected data structure
  }
}
```

### GET /api/v1/health
Health check endpoint to verify service status.

**Headers:**
```
X-API-Key: your_api_key
```

**Response Format:**
```
Status: 200 OK
Content-Type: application/json

{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "10d 4h 30m",
  "memoryUsage": "24.5MB"
}
```

## Error Handling

| Error Condition | HTTP Status Code | Response |
|-----------------|------------------|----------|
| Invalid JSON    | 400 Bad Request  | Error message explaining the issue |
| Missing required fields | 400 Bad Request | Error message listing missing fields |
| Empty data | 200 OK | Markdown indicating no content found |
| Malformed data | 400 Bad Request | Error message explaining the specific issue |
| Template not found | 400 Bad Request | Error message with details about the template |
| Format not supported | 400 Bad Request | Error message listing supported formats |
| Server error    | 500 Internal Server Error | Generic error message |

The system should gracefully handle incomplete or malformed data when possible, rather than rejecting the entire payload for minor issues.

### Security Considerations

### Authentication and Authorization
1. API key authentication via header
   - Header format: `X-API-Key: {api_key}`
   - Keys should be stored securely using environment variables
   - Keys should be rotatable without service disruption
2. All endpoints must require valid API key
3. Implement API key validation middleware that runs on all requests
4. Return 401 Unauthorized for missing or invalid API keys

### Input Validation and Sanitization
1. Validate all incoming JSON against a schema
2. Sanitize any potentially dangerous input
3. Implement strict type checking for all parameters
4. Set reasonable size limits for request payloads (e.g., max 1MB)

### HTTP Support
1. Support both HTTP and HTTPS connections
2. No redirection from HTTP to HTTPS required
3. Implement basic HTTP security headers where applicable

### Additional Protections
1. Implement basic HTTP security headers:
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
2. Log security-relevant events (authentication failures)

## Template-Driven Conversion Architecture

### Template Configuration
1. All conversions will be driven by Jinja2 templates
2. Templates should be stored in a structured directory:
   ```
   templates/
   ├── calendar/
   │   ├── standard.md.j2
   │   └── compact.md.j2
   ├── tasks/
   │   ├── standard.md.j2
   │   └── by_priority.md.j2
   └── notes/
       ├── standard.md.j2
       └── brief.md.j2
   ```
3. Template configuration should be defined in YAML files:
   ```
   templates/
   ├── config/
       ├── calendar.yaml
       ├── tasks.yaml
       └── notes.yaml
   ```

### Template Configuration Format
```yaml
# Example template configuration for calendar
name: calendar
description: "Google Calendar data to Markdown"
templates:
  - id: standard
    name: "Standard Format"
    description: "Detailed calendar view with events grouped by day"
    file: "calendar/standard.md.j2"
    default: true
  - id: compact
    name: "Compact Format"
    description: "Condensed calendar view with minimal details"
    file: "calendar/compact.md.j2"
preprocessors:
  - id: sort_events
    name: "Sort Events"
    description: "Sort events by start date and time"
    function: "sort_events_by_datetime"
    default: true
  - id: group_by_date
    name: "Group by Date"
    description: "Group events by date"
    function: "group_events_by_date"
    default: true
  - id: clean_descriptions
    name: "Clean Descriptions"
    description: "Remove HTML and normalize formatting in descriptions"
    function: "clean_event_descriptions"
    default: false
```

### Preprocessor Framework
1. Preprocessors should be modular Python functions registered in the system
2. They receive the input data and return a transformed version
3. Multiple preprocessors can be chained in the order specified in the request
4. Default preprocessors can be defined in the configuration
5. Clients can specify which preprocessors to use in the request

### Jinja2 Template Features
1. Templates should support full Jinja2 syntax including:
   - Loops and conditionals
   - Filters and macros
   - Template inheritance
2. Custom filters should be available for:
   - Date and time formatting
   - Text manipulation (truncation, highlights, etc.)
   - HTML to Markdown conversion
   - List formatting

## Project Structure
```
flask-markdown-converter/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── config.py             # Configuration settings
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py           # API key authentication middleware
│   │   └── validation.py     # Request validation middleware
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py         # API route definitions
│   │   └── convert.py        # Main conversion handler
│   ├── templates/            # Jinja2 templates
│   │   ├── calendar/
│   │   │   ├── standard.md.j2
│   │   │   └── compact.md.j2
│   │   ├── tasks/
│   │   │   ├── standard.md.j2
│   │   │   └── by_priority.md.j2
│   │   └── notes/
│   │       ├── standard.md.j2
│   │       └── brief.md.j2
│   ├── config/               # Format configuration files
│   │   ├── formats/
│   │   │   ├── calendar.yaml
│   │   │   ├── tasks.yaml
│   │   │   └── notes.yaml
│   │   └── schemas/          # JSON schemas for validation
│   │       ├── calendar.json
│   │       ├── tasks.json
│   │       └── notes.json
│   ├── models/
│   │   ├── __init__.py
│   │   └── request_models.py # Pydantic models for request validation
│   ├── preprocessors/        # Data preprocessors
│   │   ├── __init__.py
│   │   ├── registry.py       # Preprocessor registration
│   │   ├── calendar.py       # Calendar-specific preprocessors
│   │   ├── tasks.py          # Task-specific preprocessors
│   │   └── notes.py          # Notes-specific preprocessors
│   └── utils/
│       ├── __init__.py
│       ├── template.py       # Template loading and rendering
│       ├── jinja_filters.py  # Custom Jinja2 filters
│       ├── date_utils.py     # Date formatting utilities
│       └── logging.py        # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Test fixtures
│   ├── test_api/
│   │   ├── __init__.py
│   │   └── test_convert.py   # API endpoint tests
│   ├── test_preprocessors/
│   │   ├── __init__.py
│   │   ├── test_calendar.py
│   │   ├── test_tasks.py
│   │   └── test_notes.py
│   └── test_templates/
│       ├── __init__.py
│       ├── test_calendar_templates.py
│       ├── test_tasks_templates.py
│       └── test_notes_templates.py
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Development, Testing, and Deployment

### Development Guidelines
1. Use virtual environments for isolated dependency management
2. Follow PEP 8 style guide and use Black for code formatting
3. Use type hints throughout the codebase for better IDE support and documentation
4. Document all functions, classes, and modules with comprehensive docstrings
5. Keep functions small and focused on a single responsibility
6. Use descriptive variable and function names
7. Implement proper error handling with custom exceptions
8. Follow the Flask application factory pattern for better testing and configuration

### Testing Requirements
1. Write unit tests for all preprocessors
2. Create integration tests for API endpoints
3. Implement template tests to verify rendering output
4. Test with various input data formats and edge cases
5. Validate error handling with malformed inputs
6. Ensure at least 85% code coverage

### Testing Strategy
1. **Unit Tests**: Test individual components in isolation
   - Preprocessor functions
   - Template rendering
   - Configuration loading
   - Auth middleware
2. **Integration Tests**: Test components working together
   - API endpoints with test client
   - End-to-end conversion flow
3. **Template Tests**: Verify template rendering with known inputs
   - Compare rendered output against expected Markdown
   - Test with various data structures

### Deployment Strategy
1. **Containerization**:
   - Provide basic Dockerfile for the application
   - Docker Compose for local development and testing

2. **Configuration Management**:
   - Use environment variables for runtime configuration
   - Support for basic environment configurations (dev, prod)
   - Keep secrets separate from code and config

3. **Monitoring and Logging**:
   - Basic structured logging
   - Simple health check endpoint

## Performance Considerations

This service is designed for low-volume usage, so performance optimizations aren't necessary for the MVP:

1. No template caching required for MVP
2. Appropriate error handling for timeouts and connection issues
3. Simple logging for troubleshooting issues if they arise

The service should be able to handle multiple concurrent requests, but scaling is not a requirement for MVP.

## Extensibility Requirements
1. Plugin architecture for adding new preprocessors
2. Support for adding new templates without code changes
3. API versioning to support future enhancements
4. Configurable logging to integrate with various monitoring systems

## Example Formats and Use Cases

### Calendar Format (MVP)
- Google Calendar events to Markdown summaries
- Group events by day, week, or month
- Highlight all-day events vs. time-specific events
- Include or exclude details like attendees, locations, etc.

### Future Potential Formats (Post-MVP)
- Task List Format
  - Convert task lists to Markdown checklists
  - Group by status, priority, or due date

- Notes Format
  - Convert structured notes to Markdown documents
  - Include metadata like tags and creation dates

- Additional Potential Formats
  - Meeting minutes to structured Markdown
  - Project status reports
  - Issue trackers
  - Documentation systems
