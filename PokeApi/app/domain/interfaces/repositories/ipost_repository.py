from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.post import Post

class IPostRepository(ABC):
    @abstractmethod
    def save(self, post: Post) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, post_id: int) -> Optional[Post]:
        pass

    @abstractmethod
    def get_all(self) -> List[Post]:
        pass