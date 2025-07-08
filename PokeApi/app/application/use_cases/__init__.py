# app/application/use_cases/__init__.py
"""
Application use cases (interactors)

Contains:
- FetchAndStorePostsUseCase: Gets and stores posts from PokeAPI
- FetchAndStoreCommentsUseCase: Gets and stores comments for posts
- ProcessPostUseCase: Processes post data
- ProcessCommentUseCase: Processes comment data
"""

from .fetch_posts import FetchAndStorePostsUseCase
from .fetch_comments import FetchAndStoreCommentsUseCase
from .process_post import ProcessPostUseCase
from .process_comment import ProcessCommentUseCase

__all__ = [
    'FetchAndStorePostsUseCase',
    'FetchAndStoreCommentsUseCase',
    'ProcessPostUseCase',
    'ProcessCommentUseCase'
]