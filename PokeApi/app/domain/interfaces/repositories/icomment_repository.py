from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.comment import Comment

class ICommentRepository(ABC):
    @abstractmethod
    def save(self, comment: Comment) -> bool:
        pass

    @abstractmethod
    def get_by_post_id(self, post_id: int) -> List[Comment]:
        pass