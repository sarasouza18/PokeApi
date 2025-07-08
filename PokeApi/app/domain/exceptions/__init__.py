# app/domain/exceptions/__init__.py
"""
Domain-specific exceptions module
"""

class RepositoryError(Exception):
    """Base exception for repository operations"""
    def __init__(self, message: str = "Repository error occurred", details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

class ServiceError(Exception):
    """Base exception for service operations"""
    def __init__(self, message: str = "Service error occurred", details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

class NotFoundError(RepositoryError):
    """Resource not found exception"""
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with id {resource_id} not found"
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "error_type": "not_found"
        }
        super().__init__(message, details)

class ValidationError(ServiceError):
    """Data validation exception"""
    def __init__(self, field: str, reason: str):
        message = f"Validation failed for field '{field}': {reason}"
        details = {
            "field": field,
            "reason": reason,
            "error_type": "validation"
        }
        super().__init__(message, details)

class RateLimitError(ServiceError):
    """Rate limiting exception"""
    def __init__(self, service_name: str, retry_after: int = 60):
        message = f"Rate limit exceeded for {service_name}"
        details = {
            "service_name": service_name,
            "retry_after": retry_after,
            "error_type": "rate_limit"
        }
        super().__init__(message, details)

__all__ = [
    'RepositoryError',
    'ServiceError',
    'NotFoundError',
    'ValidationError',
    'RateLimitError'
]