# app/infrastructure/persistence/__init__.py
"""
Persistence implementations for data access

Contains:
- DynamoDBPostRepository: DynamoDB implementation for posts
- DynamoDBCommentRepository: DynamoDB implementation for comments
"""

from .dynamodb_post_repository import DynamoDBPostRepository
from .dynamodb_comment_repository import DynamoDBCommentRepository

__all__ = ['DynamoDBPostRepository', 'DynamoDBCommentRepository']