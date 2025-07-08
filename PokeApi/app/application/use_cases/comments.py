from typing import List
from app.domain.entities.post import Post
from app.domain.entities.comment import Comment
from app.domain.interfaces.services import IPokeAPIService
from app.domain.interfaces.repositories import ICommentRepository

class FetchAndStoreCommentsUseCase:
    def __init__(
        self,
        pokeapi_service: IPokeAPIService,
        comment_repository: ICommentRepository
    ):
        self.pokeapi_service = pokeapi_service
        self.comment_repository = comment_repository

    def execute(self, post: Post) -> List[Comment]:
        comments = self.pokeapi_service.fetch_comments_for_post(post)
        saved_comments = []
        
        for comment in comments:
            if self.comment_repository.save(comment):
                saved_comments.append(comment)
        
        return saved_comments