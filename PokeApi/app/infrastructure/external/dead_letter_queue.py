# app/infrastructure/external/dead_letter_queue.py
import os
import boto3
from typing import Dict, Any
from datetime import datetime
import json

class DeadLetterQueue:
    def __init__(self, queue_url: str = None, region_name: str = None):
        # Configure AWS client with explicit credentials and region
        self.sqs = boto3.client(
            'sqs',
            region_name=region_name or os.getenv('AWS_DEFAULT_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.queue_url = queue_url or os.getenv('DLQ_QUEUE_URL')

    def add_failed_item(self, item_type: str, item_data: Dict[str, Any]):
        if not self.queue_url:
            raise ValueError("DLQ queue URL not configured")
        
        try:
            message = {
                'type': item_type,
                'data': item_data,
                'timestamp': datetime.utcnow().isoformat(),
                'retry_count': 0
            }
            
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message)
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send message to DLQ: {str(e)}")