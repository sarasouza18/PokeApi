import os
import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
from app.domain.entities.post import Post
from app.domain.entities.comment import Comment
from app.domain.interfaces.repositories import IPostRepository, ICommentRepository

class DynamoDBPostRepository(IPostRepository):
    def __init__(self, table_name: str = None):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name or os.getenv('DYNAMODB_TABLE_POSTS', 'Posts'))

    def save(self, post: Post) -> bool:
        try:
            self.table.put_item(Item=post.to_dict())
            return True
        except ClientError as e:
            print(f"Error saving post: {e}")
            return False

    def get_by_id(self, post_id: int) -> Optional[Post]:
        try:
            response = self.table.get_item(Key={'id': post_id})
            if 'Item' in response:
                item = response['Item']
                return Post(
                    id=item['id'],
                    name=item['name'],
                    growth_time=item['growth_time'],
                    max_harvest=item['max_harvest'],
                    natural_gift_power=item['natural_gift_power'],
                    size=item['size'],
                    smoothness=item['smoothness'],
                    soil_dryness=item['soil_dryness'],
                    raw_data=item['raw_data'],
                    created_at=item['created_at']
                )
            return None
        except ClientError as e:
            print(f"Error getting post: {e}")
            return None

    def get_all(self) -> List[Post]:
        try:
            response = self.table.scan()
            return [
                Post(
                    id=item['id'],
                    name=item['name'],
                    growth_time=item['growth_time'],
                    max_harvest=item['max_harvest'],
                    natural_gift_power=item['natural_gift_power'],
                    size=item['size'],
                    smoothness=item['smoothness'],
                    soil_dryness=item['soil_dryness'],
                    raw_data=item['raw_data'],
                    created_at=item['created_at']
                ) for item in response.get('Items', [])
            ]
        except ClientError as e:
            print(f"Error getting all posts: {e}")
            return []

class DynamoDBCommentRepository(ICommentRepository):
    def __init__(self, table_name: str = None):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name or os.getenv('DYNAMODB_TABLE_COMMENTS', 'Comments'))

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