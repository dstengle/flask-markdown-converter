# Flask JSON-to-Markdown Conversion Service

A Flask-based web service that provides webhook endpoints to accept various types of JSON input and return Markdown output. The system is structured to support multiple conversion types through a unified API pattern, with the initial implementation focused on Google Calendar data.

## Features

- Convert JSON data to Markdown using configurable templates
- Support for Google Calendar data conversion
- Multiple template formats (standard, compact)
- Configurable preprocessors for data transformation
- API key authentication
- Comprehensive error handling
- Extensible architecture for adding new formats

## Requirements

- Python 3.9+
- Poetry (for dependency management)
- Flask 2.0+
- Jinja2
- PyYAML
- Pydantic

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/flask-markdown-converter.git
   cd flask-markdown-converter
   ```

2. Build and run with Docker Compose:
   ```
   docker-compose up --build
   ```

The service will be available at http://localhost:5000.

### Using Poetry (Recommended for Development)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/flask-markdown-converter.git
   cd flask-markdown-converter
   ```

2. Install dependencies with Poetry:
   ```
   poetry install
   ```

3. Activate the Poetry virtual environment:
   ```
   poetry shell
   ```

4. Set environment variables:
   ```
   export FLASK_APP=app
   export FLASK_ENV=development
   export API_KEYS=your-api-key-1,your-api-key-2
   export SECRET_KEY=your-secret-key
   ```

5. Run the application:
   ```
   flask run
   ```

The service will be available at http://localhost:5000.

### Manual Installation (Legacy)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/flask-markdown-converter.git
   cd flask-markdown-converter
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```
   export FLASK_APP=app
   export FLASK_ENV=development
   export API_KEYS=your-api-key-1,your-api-key-2
   export SECRET_KEY=your-secret-key
   ```

5. Run the application:
   ```
   flask run
   ```

The service will be available at http://localhost:5000.

## API Usage

### Authentication

All API endpoints require an API key, which should be provided in the `X-API-Key` header.

### Convert JSON to Markdown

**Endpoint:** `POST /api/v1/convert/{format}`

**Headers:**
```
X-API-Key: your_api_key
Content-Type: application/json
```

**Path Parameters:**
- `format`: The conversion format (e.g., "calendar")

**Query Parameters:**
- `template`: (Optional) The template to use (e.g., "standard", "compact"). Defaults to "standard".
- `preprocessor`: (Optional, can be specified multiple times) Preprocessors to apply to the data.

**Example Request:**
```bash
curl -X POST \
  http://localhost:5000/api/v1/convert/calendar \
  -H 'X-API-Key: your_api_key' \
  -H 'Content-Type: application/json' \
  -d '[
    {
      "id": "8dgs7j1qaq4uvk1m94aitnu5fs_20250227",
      "summary": "Home",
      "start": {
        "date": "2025-02-27"
      },
      "end": {
        "date": "2025-02-28"
      },
      "eventType": "workingLocation",
      "workingLocationProperties": {
        "type": "homeOffice",
        "homeOffice": {}
      }
    }
  ]'
```

**Example Response:**
```markdown
# Calendar Events

## February 27, 2025

- **Home**
  - All day event
  - Working Location: Home Office
```

### Get Available Formats

**Endpoint:** `GET /api/v1/formats`

**Headers:**
```
X-API-Key: your_api_key
```

**Example Request:**
```bash
curl -X GET \
  http://localhost:5000/api/v1/formats \
  -H 'X-API-Key: your_api_key'
```

### Get Format Details

**Endpoint:** `GET /api/v1/formats/{format}`

**Headers:**
```
X-API-Key: your_api_key
```

**Path Parameters:**
- `format`: The conversion format (e.g., "calendar")

**Example Request:**
```bash
curl -X GET \
  http://localhost:5000/api/v1/formats/calendar \
  -H 'X-API-Key: your_api_key'
```

### Health Check

**Endpoint:** `GET /api/v1/health`

**Headers:**
```
X-API-Key: your_api_key
```

**Example Request:**
```bash
curl -X GET \
  http://localhost:5000/api/v1/health \
  -H 'X-API-Key: your_api_key'
```

## Development

### Project Structure

```
flask-markdown-converter/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── config.py             # Configuration settings
│   ├── middleware/           # Authentication and validation middleware
│   ├── api/                  # API routes and conversion handlers
│   ├── templates/            # Jinja2 templates
│   ├── config/               # Format configurations and schemas
│   ├── models/               # Pydantic models for validation
│   ├── preprocessors/        # Data preprocessors
│   └── utils/                # Utility functions
├── tests/                    # Test suite
├── pyproject.toml            # Poetry configuration
├── poetry.lock               # Poetry lock file
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # This file
```

### Running Tests

1. Install development dependencies with Poetry:
   ```
   poetry install --with dev
   ```

2. Run tests:
   ```
   poetry run pytest
   ```

3. Run tests with coverage:
   ```
   poetry run pytest --cov=app
   ```

## Extending the Service

### Adding a New Format

1. Create a new template file in `app/templates/{format}/standard.md.j2`
2. Create a format configuration in `app/config/formats/{format}.yaml`
3. Create a JSON schema in `app/config/schemas/{format}.json`
4. Implement any necessary preprocessors in `app/preprocessors/{format}.py`

### Using Jinja2 Extensions

The application uses a centralized Jinja2 environment creation system that allows for consistent configuration of extensions across the application.

#### Enabling Extensions

To enable Jinja2 extensions:

1. Edit the `JINJA_EXTENSIONS` list in `app/config.py`:

   ```python
   # In app/config.py
   class DevelopmentConfig(Config):
       """Development configuration."""
       
       DEBUG = True
       LOG_LEVEL = "DEBUG"
       
       # Enable Jinja2 extensions
       JINJA_EXTENSIONS = [
           "jinja2.ext.loopcontrols",  # Adds break/continue to loops
           "jinja2.ext.do",            # Adds do expression
           # Add other extensions as needed
       ]
   ```

2. The extensions will be automatically loaded when the Jinja2 environment is created.

#### Available Extensions

Some useful built-in Jinja2 extensions include:

- `jinja2.ext.loopcontrols`: Adds `break` and `continue` statements to loops
- `jinja2.ext.do`: Adds the `do` expression for executing statements without output
- `jinja2.ext.debug`: Adds a `{% debug %}` tag to dump the current context
- `jinja2.ext.i18n`: Adds internationalization support

#### Creating Custom Extensions

You can also create and use custom Jinja2 extensions:

1. Create your extension class in a new file (e.g., `app/utils/jinja_extensions.py`)
2. Add the full import path to the `JINJA_EXTENSIONS` list in your configuration

For more information on creating Jinja2 extensions, see the [Jinja2 documentation](https://jinja.palletsprojects.com/en/3.0.x/extensions/).

## License

This project is licensed under the MIT License - see the LICENSE file for details.