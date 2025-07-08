from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from app.domain.entities.post import Post
from app.domain.entities.comment import Comment

class IPokeAPIService(ABC):
    @abstractmethod
    def get_all_posts(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_post_details(self, post_id: int) -> Optional[Dict]:
        pass

    @abstractmethod
    def fetch_and_transform_posts(self) -> List[Post]:
        pass

    @abstractmethod
    def fetch_comments_for_post(self, post: Post) -> List[Comment]:
        pass

class IProcessingService(ABC):
    @abstractmethod
    def process_post(self, post_data: Dict) -> Optional[Dict]:
        pass

    @abstractmethod
    def process_comment(self, comment_data: Dict) -> Optional[Dict]:
        pass