import os
import logging
from typing import List
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from app.domain.entities.comment import Comment
from app.domain.interfaces.repositories.icomment_repository import ICommentRepository
from app.infrastructure.config.database import get_dynamodb_resource

logger = logging.getLogger(__name__)

class DynamoDBCommentRepository(ICommentRepository):
    def __init__(self, table_name: str = None, endpoint_url: str = None):
        self.dynamodb = get_dynamodb_resource(endpoint_url=endpoint_url)
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE_COMMENTS', 'Comments')
        self.table = self.dynamodb.Table(self.table_name)
        logger.info(f"Initialized repository for table: {self.table_name}")

    def save(self, comment: Comment) -> bool:
        try:
            item = self._adapt_comment_structure(comment)
            logger.debug(f"Saving adapted comment: {item}")
            
            self.table.put_item(Item=item)
            return True
            
        except ValueError as e:
            logger.warning(f"Validation error: {e}. Comment data: {comment.__dict__}")
            return False
        except ClientError as e:
            logger.error(f"DynamoDB error saving comment: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving comment: {e}", exc_info=True)
            return False

    def get_by_post_id(self, post_id: str) -> List[Comment]:
        try:
            response = self.table.query(
                IndexName='post_id-index',
                KeyConditionExpression=Key('post_id').eq(str(post_id)),
            )
            return [Comment(**item) for item in response.get('Items', [])]
        except Exception as e:
            logger.error(f"Error getting comments: {e}")
            return []

    def _adapt_comment_structure(self, comment: Comment) -> dict:
        """
        Adapts comment structure handling both dict and string flavor data.
        Preserves original dictionaries while converting other fields to strings.
        """
        item = comment.to_dict()
        
        # Validate required fields
        if 'id' not in item:
            raise ValueError("Comment must have an 'id' field")
        if 'post_id' not in item:
            raise ValueError("Comment must have a 'post_id' field")
        
        # Convert IDs to strings
        item['id'] = str(item['id'])
        item['post_id'] = str(item['post_id'])
        
        # Generate content from flavor data if missing
        if 'content' not in item:
            flavor_data = item.get('flavor')
            potency = item.get('potency', 0)
            
            if isinstance(flavor_data, dict):
                item['content'] = f"{flavor_data.get('name', 'unknown')} (potency: {potency})"
            elif isinstance(flavor_data, str):
                item['content'] = f"{flavor_data} (potency: {potency})"
            else:
                item['content'] = f"Berry flavor (potency: {potency})"
        
        # Convert non-dict fields to strings
        for key in item:
            if not isinstance(item[key], (str, dict)):
                item[key] = str(item[key])
                
        return item