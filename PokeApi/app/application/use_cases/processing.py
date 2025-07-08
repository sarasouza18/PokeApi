from typing import Optional, Dict
from app.domain.interfaces.services import IProcessingService

class ProcessPostUseCase:
    def __init__(self, processing_service: IProcessingService):
        self.processing_service = processing_service

    def execute(self, post_data: Dict) -> Optional[Dict]:
        return self.processing_service.process_post(post_data)

class ProcessCommentUseCase:
    def __init__(self, processing_service: IProcessingService):
        self.processing_service = processing_service

    def execute(self, comment_data: Dict) -> Optional[Dict]:
        return self.processing_service.process_comment(comment_data)