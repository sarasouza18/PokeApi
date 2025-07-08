import os
import json
import logging
import boto3
from typing import Dict, Any, Optional
from datetime import datetime
from botocore.config import Config
from pathlib import Path

logger = logging.getLogger(__name__)

class DeadLetterQueue:
    def __init__(self, queue_url: str = None, region_name: str = None):
        """
        Dead Letter Queue implementation with SQS backend and local fallback.
        
        Args:
            queue_url: SQS queue URL (optional, falls back to DLQ_QUEUE_URL env var)
            region_name: AWS region (optional, falls back to AWS_DEFAULT_REGION env var)
        """
        self.queue_url = queue_url or os.getenv('DLQ_QUEUE_URL')
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self._fallback_path = Path(os.getenv('DLQ_FALLBACK_PATH', '/tmp/dlq_fallback'))
        self._client = None
        
        # Ensure fallback directory exists
        self._fallback_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized DLQ with queue: {self.queue_url or 'FALLBACK ONLY'}")

    @property
    def client(self):
        """Lazy-loaded SQS client with retry configuration"""
        if self._client is None and self.queue_url:
            self._client = boto3.client(
                'sqs',
                region_name=self.region_name,
                config=Config(
                    retries={
                        'max_attempts': 3,
                        'mode': 'standard'
                    }
                )
            )
        return self._client

    def add_failed_item(self, item_type: str, item_data: Dict[str, Any]) -> bool:
        """
        Add a failed item to the DLQ with automatic fallback to local storage.
        
        Args:
            item_type: Type of the failed item (e.g., 'post', 'comment')
            item_data: The item data to store
            
        Returns:
            bool: True if successfully queued (or fallback succeeded), False otherwise
        """
        message = {
            'type': item_type,
            'data': item_data,
            'timestamp': datetime.utcnow().isoformat(),
            'retry_count': 0,
            'source': 'processing_service'
        }

        # Try SQS first if configured
        if self.queue_url and self.client:
            try:
                response = self.client.send_message(
                    QueueUrl=self.queue_url,
                    MessageBody=json.dumps(message),
                    MessageAttributes={
                        'ItemType': {
                            'DataType': 'String',
                            'StringValue': item_type
                        }
                    }
                )
                logger.debug(f"Successfully sent to DLQ: {item_type} {message.get('timestamp')}")
                return True
            except Exception as e:
                logger.warning(f"SQS DLQ failed: {str(e)}. Attempting fallback...")

        # Fallback to local storage
        try:
            fallback_file = self._fallback_path / f"{item_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(fallback_file, 'w') as f:
                json.dump(message, f)
            logger.warning(f"Used fallback DLQ storage: {fallback_file}")
            return True
        except Exception as e:
            logger.error(f"DLQ fallback also failed: {str(e)}")
            return False

    def get_fallback_items(self) -> list:
        """Retrieve items from local fallback storage"""
        items = []
        for file in self._fallback_path.glob('*.json'):
            try:
                with open(file) as f:
                    items.append(json.load(f))
            except Exception as e:
                logger.error(f"Error reading fallback file {file}: {str(e)}")
        return items