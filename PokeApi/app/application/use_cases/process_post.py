# app/application/use_cases/process_post.py
from typing import Optional, Dict
from app.domain.interfaces.services import IProcessingService
from app.domain.exceptions import ServiceError

class ProcessPostUseCase:
    """
    Use case for processing post data through an external service
    Implements Dependency Inversion Principle by depending on abstraction (IProcessingService)
    """
    
    def __init__(self, processing_service: IProcessingService):
        self.processing_service = processing_service

    def execute(self, post_data: Dict) -> Optional[Dict]:
        """
        Processes post data through the configured processing service
        
        Args:
            post_data: Dictionary containing post data to process
            
        Returns:
            Optional[Dict]: Processed data if successful, None otherwise
            
        Raises:
            ServiceError: If processing fails after retries
        """
        try:
            return self.processing_service.process_post(post_data)
        except Exception as e:
            raise ServiceError(f"Failed to process post {post_data.get('id')}: {str(e)}")