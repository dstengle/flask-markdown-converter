"""
Application configuration settings.
"""
import os
from typing import List, Dict, Any


class Config:
    """Base configuration."""
    
    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")
    DEBUG = False
    TESTING = False
    
    # API settings
    API_KEYS: List[str] = os.environ.get("API_KEYS", "test-key").split(",")
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB max request size
    
    # Template settings
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
    CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
    JINJA_EXTENSIONS: List[str] = ['jinja2.ext.loopcontrols']  # Default: no extensions
    
    # Logging settings
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    
    # Example of enabling Jinja2 extensions in development
    # Uncomment to enable the loop controls extension
    # JINJA_EXTENSIONS = ["jinja2.ext.loopcontrols"]
    LOG_LEVEL = "DEBUG"


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""
    
    # Use strong secret key in production
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    # In production, API keys should be set via environment variables
    API_KEYS = os.environ.get("API_KEYS", "").split(",")


# Configuration dictionary
config_by_name: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

# Default to development configuration
default_config = config_by_name[os.environ.get("FLASK_ENV", "development")]