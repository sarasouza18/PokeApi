import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any

class DeadLetterQueue:
    def __init__(self, queue_url: str = None):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url or os.getenv('DLQ_QUEUE_URL')
        
    def add_failed_item(self, item_type: str, item_data: Dict[str, Any]):
        if not self.queue_url:
            print("No DLQ configured, skipping failed item")
            return
            
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
        except Exception as e:
            print(f"Failed to send message to DLQ: {e}")