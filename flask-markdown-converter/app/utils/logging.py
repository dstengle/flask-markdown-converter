"""
Logging configuration.
"""
import logging
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import traceback

from flask import Flask, Request


def configure_logging(app: Flask) -> None:
    """
    Configure logging for the Flask application.
    
    Args:
        app: Flask application instance.
    """
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"))
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure app logger
    logger = logging.getLogger('app')
    logger.setLevel(log_level)
    
    # Add handler if not already added
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(handler)
    
    app.logger.info(f"Logging configured with level: {app.config.get('LOG_LEVEL', 'INFO')}")


def log_request(request: Request) -> None:
    """
    Log details of an HTTP request.
    
    Args:
        request: Flask request object.
    """
    logger = logging.getLogger('app.request')
    
    # Create log entry
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string,
        'content_type': request.content_type,
        'content_length': request.content_length,
    }
    
    # Add query parameters if present
    if request.args:
        log_entry['query_params'] = dict(request.args)
    
    # Add headers (excluding sensitive ones)
    headers = {}
    for key, value in request.headers:
        if key.lower() not in ('authorization', 'x-api-key', 'cookie'):
            headers[key] = value
    
    if headers:
        log_entry['headers'] = headers
    
    # Log as JSON
    logger.info(f"Request: {json.dumps(log_entry)}")


def log_response(status_code: int, response_data: Any, duration_ms: float) -> None:
    """
    Log details of an HTTP response.
    
    Args:
        status_code: HTTP status code.
        response_data: Response data.
        duration_ms: Request duration in milliseconds.
    """
    logger = logging.getLogger('app.response')
    
    # Create log entry
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'status_code': status_code,
        'duration_ms': duration_ms,
    }
    
    # Add response data summary
    if isinstance(response_data, dict):
        log_entry['response_keys'] = list(response_data.keys())
    elif isinstance(response_data, list):
        log_entry['response_length'] = len(response_data)
    elif isinstance(response_data, str):
        log_entry['response_length'] = len(response_data)
    
    # Log as JSON
    logger.info(f"Response: {json.dumps(log_entry)}")


def log_error(error: Exception, request: Optional[Request] = None) -> None:
    """
    Log details of an error.
    
    Args:
        error: Exception object.
        request: Flask request object (optional).
    """
    logger = logging.getLogger('app.error')
    
    # Create log entry
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc(),
    }
    
    # Add request details if available
    if request:
        log_entry['method'] = request.method
        log_entry['path'] = request.path
        log_entry['remote_addr'] = request.remote_addr
    
    # Log as JSON
    logger.error(f"Error: {json.dumps(log_entry)}")