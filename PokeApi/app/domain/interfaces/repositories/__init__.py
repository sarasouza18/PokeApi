# app/domain/interfaces/repositories/__init__.py
"""
Repository interfaces for data access

Contains:
- IPostRepository: Interface for post data access
- ICommentRepository: Interface for comment data access
"""

from .ipost_repository import IPostRepository
from .icomment_repository import ICommentRepository

__all__ = ['IPostRepository', 'ICommentRepository']