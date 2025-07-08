# app/infrastructure/external/processing_service.py
import requests
import os
from typing import Dict, Optional
from app.domain.interfaces.services.iprocessing_service import IProcessingService
from app.infrastructure.external.dead_letter_queue import DeadLetterQueue

class ProcessingService(IProcessingService):
    def __init__(self, dlq: DeadLetterQueue = None):
        self.dlq = dlq or DeadLetterQueue()
        self.processing_endpoint = os.getenv('PROCESSING_ENDPOINT', 'https://httpbin.org/post')

    def process_post(self, post_data: Dict) -> Optional[Dict]:
        try:
            response = requests.post(self.processing_endpoint, json=post_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error processing post {post_data.get('id')}: {e}")
            self.dlq.add_failed_item('post', post_data)
            return None

    def process_comment(self, comment_data: Dict) -> Optional[Dict]:
        try:
            response = requests.post(self.processing_endpoint, json=comment_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error processing comment {comment_data.get('id')}: {e}")
            self.dlq.add_failed_item('comment', comment_data)
            return None