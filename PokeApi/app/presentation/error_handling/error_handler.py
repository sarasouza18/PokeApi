# app/presentation/error_handling/error_handler.py
import logging
from functools import wraps
from http import HTTPStatus
from typing import Dict, Any, Type, Callable, Optional
from app.domain.exceptions import (
    RepositoryError,
    ServiceError,
    NotFoundError,
    ValidationError,
    RateLimitError
)

logger = logging.getLogger(__name__)

class ErrorHandler:
    """
    Centralized error handling component that:
    - Logs errors appropriately
    - Transforms domain exceptions to presentation-layer responses
    - Provides decorators for error handling
    """
    
    ERROR_MAPPING: Dict[Type[Exception], Dict[str, Any]] = {
        RepositoryError: {
            'status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'type': 'repository_error'
        },
        ServiceError: {
            'status_code': HTTPStatus.BAD_GATEWAY,
            'type': 'service_error'
        },
        NotFoundError: {
            'status_code': HTTPStatus.NOT_FOUND,
            'type': 'not_found'
        },
        ValidationError: {
            'status_code': HTTPStatus.BAD_REQUEST,
            'type': 'validation_error'
        },
        RateLimitError: {
            'status_code': HTTPStatus.TOO_MANY_REQUESTS,
            'type': 'rate_limit_error'
        }
    }

    @classmethod
    def wrap_endpoint(cls, func: Callable) -> Callable:
        """
        Decorator for API endpoints that provides standardized error handling
        
        Args:
            func: The endpoint function to wrap
            
        Returns:
            Wrapped function with error handling
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_response = cls.handle_error(e)
                cls.log_error(e, f"endpoint_{func.__name__}")
                return error_response
        return wrapper

    @classmethod
    def handle_error(cls, error: Exception) -> Dict[str, Any]:
        """
        Transforms an exception into an appropriate error response
        
        Args:
            error: The exception to handle
            
        Returns:
            Dictionary containing error details and status code
        """
        error_type = type(error)
        
        if error_type in cls.ERROR_MAPPING:
            mapping = cls.ERROR_MAPPING[error_type]
            return {
                'status_code': mapping['status_code'],
                'error': {
                    'type': mapping['type'],
                    'message': str(error),
                    'details': getattr(error, 'details', None)
                }
            }
        
        # Default case for unhandled exceptions
        logger.error("Unhandled exception", exc_info=True)
        return {
            'status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'error': {
                'type': 'internal_server_error',
                'message': 'An unexpected error occurred',
                'details': None
            }
        }

    @classmethod
    def log_error(cls, error: Exception, context: Optional[str] = None) -> None:
        """
        Standardized error logging with context
        
        Args:
            error: The exception to log
            context: Additional context about where the error occurred
        """
        error_type = type(error).__name__
        context_msg = f" in {context}" if context else ""
        
        logger.error(
            f"{error_type} occurred{context_msg}: {str(error)}",
            exc_info=True,
            extra={
                'error_type': error_type,
                'context': context,
                'details': getattr(error, 'details', None)
            }
        )