import requests
import os
import logging
from typing import Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.domain.interfaces.services.iprocessing_service import IProcessingService
from app.infrastructure.external.dead_letter_queue import DeadLetterQueue

logger = logging.getLogger(__name__)


class ProcessingService(IProcessingService):
    def __init__(self, dlq: DeadLetterQueue = None, endpoint: Optional[str] = None):
        """
        Initialize processing service with configurable endpoint and dead letter queue.
        
        Args:
            dlq: Dead letter queue instance for failed items
            endpoint: Processing endpoint URL
        """
        self.dlq = dlq or DeadLetterQueue()
        self.processing_endpoint = endpoint or os.getenv('PROCESSING_ENDPOINT', 'https://httpbin.org/post')
        self.timeout = int(os.getenv('PROCESSING_TIMEOUT', '5'))  # seconds

        logger.info(f"🚀 ProcessingService initialized with endpoint: {self.processing_endpoint}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        reraise=True
    )
    def _make_request(self, data: Dict) -> Dict:
        """Internal method to handle the actual HTTP request with retry logic"""
        try:
            response = requests.post(
                self.processing_endpoint,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Request failed for item {data.get('id')}: {str(e)}")
            raise

    def process_post(self, post_data: Dict) -> Optional[Dict]:
        """
        Process a post through the external service.
        
        Args:
            post_data: Post data to process
            
        Returns:
            Processed result or None if failed
        """
        item_id = post_data.get("id", "unknown")
        try:
            result = self._make_request(post_data)
            logger.info(f"✅ Post {item_id} processed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to process post {item_id}: {str(e)}")
            self._send_to_dlq("post", post_data)
            return None

    def process_comment(self, comment_data: Dict) -> Optional[Dict]:
        """
        Process a comment through the external service.
        
        Args:
            comment_data: Comment data to process
            
        Returns:
            Processed result or None if failed
        """
        item_id = comment_data.get("id", "unknown")
        try:
            result = self._make_request(comment_data)
            logger.info(f"✅ Comment {item_id} processed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to process comment {item_id}: {str(e)}")
            self._send_to_dlq("comment", comment_data)
            return None

    def _send_to_dlq(self, item_type: str, payload: Dict) -> None:
        """
        Wraps and sends failed item to the dead letter queue.
        
        Args:
            item_type: 'post' or 'comment'
            payload: failed item data
        """
        try:
            self.dlq.add_failed_item(item_type, payload)
            logger.info(f"📦 Sent {item_type} {payload.get('id', 'unknown')} to DLQ")
        except Exception as e:
            logger.error(f"🔥 Failed to enqueue {item_type} to DLQ: {str(e)}")
