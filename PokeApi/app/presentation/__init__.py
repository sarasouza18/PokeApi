# app/presentation/__init__.py
"""
Presentation layer containing interface adapters

Exposes:
- Controllers: SocialMediaController
- ErrorHandlers: ErrorHandler
"""

from .controllers import SocialMediaController
from .error_handling import ErrorHandler

__all__ = ['SocialMediaController', 'ErrorHandler']