# app/domain/exceptions/service_exceptions.py
from http import HTTPStatus
from typing import Any, Dict, Optional

class ServiceError(Exception):
    """Base exception for service layer errors"""
    def __init__(
        self,
        message: str = "Service error occurred",
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

class NotFoundError(ServiceError):
    """Resource not found exception"""
    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        message: Optional[str] = None
    ):
        if not message:
            message = f"{resource_type} with id {resource_id} not found"
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            details={
                'resource_type': resource_type,
                'resource_id': resource_id
            }
        )

class ValidationError(ServiceError):
    """Data validation exception"""
    def __init__(
        self,
        field: str,
        reason: str,
        message: Optional[str] = None
    ):
        if not message:
            message = f"Validation failed for field {field}: {reason}"
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            details={
                'field': field,
                'reason': reason
            }
        )

class RateLimitError(ServiceError):
    """Rate limiting exception"""
    def __init__(
        self,
        service_name: str,
        retry_after: int,
        message: Optional[str] = None
    ):
        if not message:
            message = f"Rate limit exceeded for {service_name}"
        super().__init__(
            message=message,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            details={
                'service_name': service_name,
                'retry_after': retry_after
            }
        )