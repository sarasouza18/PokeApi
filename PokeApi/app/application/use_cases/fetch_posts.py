# app/application/use_cases/fetch_posts.py
from typing import List
from app.domain.entities.post import Post
from app.domain.interfaces.services import IPokeAPIService
from app.domain.interfaces.repositories import IPostRepository
from app.domain.exceptions import ServiceError, RepositoryError

class FetchAndStorePostsUseCase:
    """
    Use case for fetching posts from PokeAPI and storing them in the repository
    Implements the Single Responsibility Principle by handling only post fetching and storage
    """
    
    def __init__(
        self,
        pokeapi_service: IPokeAPIService,
        post_repository: IPostRepository
    ):
        self.pokeapi_service = pokeapi_service
        self.post_repository = post_repository

    def execute(self) -> List[Post]:
        """
        Executes the use case:
        1. Fetches posts from PokeAPI
        2. Stores them in the repository
        3. Returns the list of saved posts
        
        Raises:
            ServiceError: If there's an issue with the PokeAPI service
            RepositoryError: If there's an issue with the repository
        """
        try:
            # Fetch from external service
            posts = self.pokeapi_service.fetch_and_transform_posts()
            
            # Store in repository
            saved_posts = []
            for post in posts:
                if self.post_repository.save(post):
                    saved_posts.append(post)
            
            return saved_posts
            
        except ServiceError as e:
            raise ServiceError(f"Failed to fetch posts: {str(e)}")
        except RepositoryError as e:
            raise RepositoryError(f"Failed to store posts: {str(e)}")
        except Exception as e:
            raise ServiceError(f"Unexpected error in FetchAndStorePostsUseCase: {str(e)}")