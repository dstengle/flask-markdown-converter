"""
Flask application factory module.
"""
import os
from flask import Flask
from app.middleware.auth import api_key_required
from app.utils.logging import configure_logging


def create_app(test_config=None):
    """
    Create and configure the Flask application.

    Args:
        test_config (dict, optional): Test configuration to override default config.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        API_KEYS=os.environ.get("API_KEYS", "test-key").split(","),
        MAX_CONTENT_LENGTH=1 * 1024 * 1024,  # 1MB max request size
    )

    # Load instance config if it exists
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Configure logging
    configure_logging(app)

    # Register API routes
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)

    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return {"status": "healthy"}

    return app