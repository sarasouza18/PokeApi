# app/domain/interfaces/__init__.py
"""
Interfaces defining contracts between layers

Contains:
- repositories: Data access interfaces
- services: External service interfaces
"""

from .repositories import IPostRepository, ICommentRepository
from .services import IPokeAPIService, IProcessingService

__all__ = [
    'IPostRepository',
    'ICommentRepository',
    'IPokeAPIService',
    'IProcessingService'
]