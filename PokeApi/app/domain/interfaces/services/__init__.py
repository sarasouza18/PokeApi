# app/domain/interfaces/services/__init__.py
"""
Service interfaces for external integrations

Contains:
- IPokeAPIService: Interface for PokeAPI integration
- IProcessingService: Interface for data processing
"""

from .ipokeapi_service import IPokeAPIService
from .iprocessing_service import IProcessingService

__all__ = ['IPokeAPIService', 'IProcessingService']