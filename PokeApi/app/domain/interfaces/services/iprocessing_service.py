from abc import ABC, abstractmethod
from typing import Dict, Optional

class IProcessingService(ABC):
    @abstractmethod
    def process_post(self, post_data: Dict) -> Optional[Dict]:
        pass

    @abstractmethod
    def process_comment(self, comment_data: Dict) -> Optional[Dict]:
        pass