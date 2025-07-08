# app/infrastructure/config/__init__.py
"""
Configuration utilities for infrastructure

Contains:
- database: Database connection utilities
"""

from .database import get_dynamodb_resource

__all__ = ['get_dynamodb_resource']