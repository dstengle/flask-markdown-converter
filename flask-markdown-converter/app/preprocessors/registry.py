"""
Preprocessor registration and management.
"""
import logging
from typing import Dict, Callable, Any, Optional

logger = logging.getLogger(__name__)

# Registry to store preprocessor functions
_preprocessor_registry: Dict[str, Callable] = {}


def register_preprocessor(name: str):
    """
    Decorator to register a preprocessor function.
    
    Args:
        name: The name of the preprocessor function.
        
    Returns:
        Decorator function.
    """
    def decorator(func: Callable):
        _preprocessor_registry[name] = func
        logger.debug(f"Registered preprocessor: {name}")
        return func
    
    return decorator


def get_preprocessor(name: str) -> Optional[Callable]:
    """
    Get a preprocessor function by name.
    
    Args:
        name: The name of the preprocessor function.
        
    Returns:
        The preprocessor function or None if not found.
    """
    return _preprocessor_registry.get(name)


def list_preprocessors() -> Dict[str, Callable]:
    """
    List all registered preprocessors.
    
    Returns:
        Dictionary of preprocessor names and functions.
    """
    return _preprocessor_registry.copy()