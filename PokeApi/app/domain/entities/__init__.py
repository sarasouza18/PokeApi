# app/domain/entities/__init__.py
"""
Domain entities representing core business objects

Contains:
- Post: Represents a social media post (berry)
- Comment: Represents a comment on a post (flavor)
"""

from .post import Post
from .comment import Comment

__all__ = ['Post', 'Comment']