# app/infrastructure/external/__init__.py
"""
External service implementations and utilities

Contains:
- PokeAPIService: PokeAPI implementation
- ProcessingService: Data processing implementation
- CircuitBreaker: Circuit breaker pattern
- DeadLetterQueue: Dead letter queue implementation
"""

from .pokeapi_service import PokeAPIService
from .processing_service import ProcessingService
from .circuit_breaker import CircuitBreaker
from .dead_letter_queue import DeadLetterQueue

__all__ = [
    'PokeAPIService',
    'ProcessingService',
    'CircuitBreaker',
    'DeadLetterQueue'
]