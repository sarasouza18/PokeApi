# app/application/use_cases/process_comment.py
from typing import Optional, Dict
from app.domain.interfaces.services import IProcessingService
from app.domain.exceptions import ServiceError

class ProcessCommentUseCase:
    """
    Use case for processing comment data through an external service
    Follows Interface Segregation Principle with focused single method
    """
    
    def __init__(self, processing_service: IProcessingService):
        self.processing_service = processing_service

    def execute(self, comment_data: Dict) -> Optional[Dict]:
        """
        Processes comment data through the configured processing service
        
        Args:
            comment_data: Dictionary containing comment data to process
            
        Returns:
            Optional[Dict]: Processed data if successful, None otherwise
            
        Raises:
            ServiceError: If processing fails after retries
        """
        try:
            return self.processing_service.process_comment(comment_data)
        except Exception as e:
            raise ServiceError(f"Failed to process comment {comment_data.get('id')}: {str(e)}")