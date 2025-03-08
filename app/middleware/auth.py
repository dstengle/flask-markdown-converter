"""
Authentication middleware for API key validation.
"""
from functools import wraps
from flask import request, current_app, jsonify, g
import logging

logger = logging.getLogger(__name__)


def api_key_required(f):
    """
    Decorator to require a valid API key for route access.
    
    Args:
        f: The function to decorate.
        
    Returns:
        The decorated function that checks for a valid API key.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            logger.warning("API request missing API key")
            return jsonify({"error": "API key is required"}), 401
        
        if api_key not in current_app.config["API_KEYS"]:
            logger.warning(f"Invalid API key used: {api_key[:4]}...")
            return jsonify({"error": "Invalid API key"}), 401
        
        # Store API key in g for potential future use
        g.api_key = api_key
        
        return f(*args, **kwargs)
    
    return decorated_function


def apply_auth_middleware(app):
    """
    Apply authentication middleware to the Flask application.
    
    Args:
        app: The Flask application instance.
    """
    @app.before_request
    def authenticate():
        # Skip authentication for health check endpoint
        if request.path == "/health":
            return None
            
        # All other endpoints require authentication
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            logger.warning("API request missing API key")
            return jsonify({"error": "API key is required"}), 401
        
        if api_key not in app.config["API_KEYS"]:
            logger.warning(f"Invalid API key used: {api_key[:4]}...")
            return jsonify({"error": "Invalid API key"}), 401
        
        # Store API key in g for potential future use
        g.api_key = api_key