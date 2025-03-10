"""
Request validation middleware.
"""
import json
import logging
import os
from functools import wraps
from typing import Dict, Any, Optional, Callable, Type

from flask import request, jsonify, current_app
from pydantic import BaseModel, ValidationError
from jsonschema import validate, ValidationError as JsonSchemaValidationError

from app.utils.logging import log_request

logger = logging.getLogger(__name__)


def validate_json(f):
    """
    Decorator to validate that the request contains valid JSON.
    
    Args:
        f: The function to decorate.
        
    Returns:
        The decorated function that validates JSON.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            logger.warning("Request content-type is not application/json")
            return jsonify({"error": "Request must be JSON"}), 400
        
        try:
            # Try to parse JSON
            _ = request.get_json()
        except Exception as e:
            logger.warning(f"Invalid JSON in request: {str(e)}")
            return jsonify({"error": "Invalid JSON format"}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_schema(schema_dir: str = "config/schemas"):
    """
    Decorator to validate request JSON against a JSON schema.
    
    Args:
        schema_dir: Directory containing the JSON schema files.
        
    Returns:
        Decorator function that validates against the schema.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema_dir = current_app.config.get("CONFIG_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "config/schemas"))
            schema_path = f"{schema_dir}/{request.path.strip('/').split('/')[-1]}.json"
            try:
                with open(schema_path, 'r') as schema_file:
                    schema = json.load(schema_file)
            except FileNotFoundError:
                # Continue without schema validation for formats without schema
                # The actual format validation will happen in the convert function
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Failed to load schema from {schema_path}: {str(e)}")
                return jsonify({"error": "Server configuration error"}), 500
            
            try:
                data = request.get_json()
                validate(instance=data, schema=schema)
            except JsonSchemaValidationError as e:
                logger.warning(f"Schema validation failed: {str(e.message)}")
                return jsonify({"error": f"Schema validation failed: {str(e.message)}"}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def validate_pydantic(model: Type[BaseModel]):
    """
    Decorator to validate request JSON against a Pydantic model.
    
    Args:
        model: Pydantic model class to validate against.
        
    Returns:
        Decorator function that validates against the model.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                validated_data = model(**data)
                # Add validated data to kwargs
                kwargs['validated_data'] = validated_data
            except ValidationError as e:
                logger.warning(f"Pydantic validation failed: {str(e)}")
                return jsonify({"error": f"Validation error: {str(e)}"}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def log_request_middleware(f):
    """
    Middleware to log request details.
    
    Args:
        f: The function to decorate.
        
    Returns:
        The decorated function that logs request details.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        log_request(request)
        return f(*args, **kwargs)
    
    return decorated_function