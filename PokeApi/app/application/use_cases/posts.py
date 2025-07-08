from typing import List, Optional
from app.domain.entities.post import Post
from app.domain.interfaces.services import IPokeAPIService
from app.domain.interfaces.repositories import IPostRepository

class FetchAndStorePostsUseCase:
    def __init__(
        self,
        pokeapi_service: IPokeAPIService,
        post_repository: IPostRepository
    ):
        self.pokeapi_service = pokeapi_service
        self.post_repository = post_repository

    def execute(self) -> List[Post]:
        posts = self.pokeapi_service.fetch_and_transform_posts()
        saved_posts = []
        
        for post in posts:
            if self.post_repository.save(post):
                saved_posts.append(post)
        
        return saved_posts