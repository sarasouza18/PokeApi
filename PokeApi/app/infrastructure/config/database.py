# app/infrastructure/config/database.py
import os
import boto3

def get_dynamodb_resource(endpoint_url: str = None):
    return boto3.resource(
        'dynamodb',
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test'),
        endpoint_url=endpoint_url
    )
