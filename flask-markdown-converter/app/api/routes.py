"""
API route definitions.
"""
import logging
from flask import Blueprint, jsonify, request, current_app
from app.middleware.auth import api_key_required
from app.middleware.validation import validate_json, log_request_middleware
from app.api.convert import convert_to_markdown, get_format_info, get_all_formats

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/health", methods=["GET"])
@api_key_required
def health():
    """
    Health check endpoint to verify service status.
    
    Returns:
        JSON response with service health information.
    """
    import time
    import os
    import psutil
    
    # Get process info
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # Calculate uptime
    uptime_seconds = time.time() - process.create_time()
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    
    uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m"
    
    # Get version from package or config
    version = getattr(current_app, "version", "1.0.0")
    
    return jsonify({
        "status": "healthy",
        "version": version,
        "uptime": uptime_str,
        "memoryUsage": f"{memory_info.rss / (1024 * 1024):.1f}MB"
    })


@api_bp.route("/convert/<format>", methods=["POST"])
@api_key_required
@log_request_middleware
@validate_json
def convert(format):
    """
    Convert JSON input to Markdown output using the specified format.
    
    Args:
        format: The conversion format (e.g., "calendar").
        
    Returns:
        Markdown content or error message.
    """
    # Get JSON data from request
    data = request.get_json()
    
    # Get query parameters
    template_id = request.args.get("template", "standard")
    preprocessors = request.args.getlist("preprocessor")
    
    try:
        # Convert data to markdown
        markdown_content = convert_to_markdown(
            format=format,
            data=data,
            template_id=template_id,
            preprocessors=preprocessors
        )
        
        # Return markdown content
        return markdown_content, 200, {"Content-Type": "text/markdown"}
    
    except ValueError as e:
        logger.warning(f"Conversion error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/formats", methods=["GET"])
@api_key_required
def formats():
    """
    Returns information about all supported conversion formats.
    
    Returns:
        JSON response with format information.
    """
    try:
        formats_info = get_all_formats()
        return jsonify({"formats": formats_info})
    
    except Exception as e:
        logger.error(f"Error retrieving formats: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/formats/<format>", methods=["GET"])
@api_key_required
def format_info(format):
    """
    Returns detailed information about a specific conversion format.
    
    Args:
        format: The conversion format (e.g., "calendar").
        
    Returns:
        JSON response with detailed format information.
    """
    try:
        format_details = get_format_info(format)
        
        if not format_details:
            return jsonify({"error": f"Format '{format}' not found"}), 404
            
        return jsonify(format_details)
    
    except Exception as e:
        logger.error(f"Error retrieving format info: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({"error": "Method not allowed"}), 405


@api_bp.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(error)}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500