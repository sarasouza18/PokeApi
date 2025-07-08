import os
import logging
from typing import List, Optional
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from app.domain.entities.post import Post
from app.domain.interfaces.repositories.ipost_repository import IPostRepository
from app.infrastructure.config.database import get_dynamodb_resource

# Configure logger for this module
logger = logging.getLogger(__name__)

class DynamoDBPostRepository(IPostRepository):
    """
    DynamoDB implementation of the Post repository.
    Handles all CRUD operations for Post entities in DynamoDB.
    
    Attributes:
        dynamodb: Boto3 DynamoDB resource
        table_name: Name of the DynamoDB table
        table: Reference to the DynamoDB table
    """
    
    def __init__(self, table_name: str = None, endpoint_url: str = None):
        """
        Initializes the DynamoDB connection and target table.
        
        Args:
            table_name: Optional custom table name
            endpoint_url: Optional endpoint URL (for local testing)
        """
        self.dynamodb = get_dynamodb_resource(endpoint_url=endpoint_url)
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE_POSTS', 'Posts')
        self.table = self.dynamodb.Table(self.table_name)
        
        logger.info(f"Initialized repository for table: {self.table_name}")

    def save(self, post: Post) -> bool:
        """
        Saves a Post entity to DynamoDB with automatic type conversion.
        
        Args:
            post: Post entity to be saved
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            item = self._convert_post_to_item(post)
            logger.debug(f"Attempting to save item: {item}")
            
            self.table.put_item(Item=item)
            logger.info(f"Post saved successfully with ID: {item['id']}")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'ValidationException':
                logger.error(f"Validation error when saving post. Item: {item}. Error: {str(e)}")
            else:
                logger.error(f"DynamoDB error when saving post: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error when saving post: {str(e)}", exc_info=True)
            return False

    def get_by_id(self, post_id: str) -> Optional[Post]:
        """
        Retrieves a Post by its ID.
        
        Args:
            post_id: The Post ID (must be string-compatible)
            
        Returns:
            Optional[Post]: The Post entity if found, None otherwise
        """
        try:
            if not isinstance(post_id, str):
                logger.warning(f"Invalid type for post_id: {type(post_id)}. Converting to string.")
                post_id = str(post_id)
                
            response = self.table.get_item(Key={'id': post_id})
            
            if 'Item' not in response:
                logger.info(f"Post not found for ID: {post_id}")
                return None
                
            return Post(**response['Item'])
            
        except ClientError as e:
            logger.error(f"Error fetching post ID {post_id}: {str(e)}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error when fetching post: {str(e)}", exc_info=True)
            return None

    def get_all(self) -> List[Post]:
        """
        Retrieves all Posts from the table.
        
        Returns:
            List[Post]: List of Post entities
        """
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            
            logger.info(f"Found {len(items)} posts")
            return [Post(**item) for item in items]
            
        except ClientError as e:
            logger.error(f"Error fetching all posts: {str(e)}")
            return []
            
        except Exception as e:
            logger.error(f"Unexpected error when fetching posts: {str(e)}", exc_info=True)
            return []

    def _convert_post_to_item(self, post: Post) -> dict:
        """
        Converts a Post entity to a DynamoDB-compatible dictionary.
        
        Args:
            post: Post entity to convert
            
        Returns:
            dict: DynamoDB-compatible item dictionary
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        item = post.to_dict()
        
        # Ensure ID is string type (DynamoDB requirement)
        if 'id' not in item:
            raise ValueError("Post must contain an 'id' field")
        item['id'] = str(item['id'])
            
        # Convert other required fields to string if needed
        required_string_fields = ['title', 'content']
        for field in required_string_fields:
            if field in item and not isinstance(item[field], str):
                item[field] = str(item[field])
                
        return item