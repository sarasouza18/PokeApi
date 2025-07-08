# app/infrastructure/persistence/dynamodb_post_repository.py
import os
import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
from app.domain.entities.post import Post
from app.domain.interfaces.repositories.ipost_repository import IPostRepository
from app.infrastructure.config.database import get_dynamodb_resource

class DynamoDBPostRepository(IPostRepository):
    def __init__(self, table_name: str = None):
        self.dynamodb = get_dynamodb_resource()
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE_POSTS', 'Posts')
        self.table = self.dynamodb.Table(self.table_name)

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