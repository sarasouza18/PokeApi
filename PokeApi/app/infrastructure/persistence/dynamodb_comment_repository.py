import os
import boto3
from botocore.exceptions import ClientError
from typing import List
from app.domain.entities.comment import Comment
from app.domain.interfaces.repositories.icomment_repository import ICommentRepository
from app.infrastructure.config.database import get_dynamodb_resource

class DynamoDBCommentRepository(ICommentRepository):
    def __init__(self, table_name: str = None):
        self.dynamodb = get_dynamodb_resource()
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE_COMMENTS', 'Comments')
        self.table = self.dynamodb.Table(self.table_name)

    def save(self, comment: Comment) -> bool:
        try:
            self.table.put_item(Item=comment.to_dict())
            return True
        except ClientError as e:
            print(f"Error saving comment: {e}")
            return False

    def get_by_post_id(self, post_id: int) -> List[Comment]:
        try:
            response = self.table.query(
                IndexName='post_id-index',
                KeyConditionExpression='post_id = :post_id',
                ExpressionAttributeValues={':post_id': post_id}
            )
            return [
                Comment(
                    id=item['id'],
                    post_id=item['post_id'],
                    flavor=item['flavor'],
                    potency=item['potency'],
                    raw_data=item['raw_data'],
                    created_at=item['created_at']
                ) for item in response.get('Items', [])
            ]
        except ClientError as e:
            print(f"Error getting comments: {e}")
            return []