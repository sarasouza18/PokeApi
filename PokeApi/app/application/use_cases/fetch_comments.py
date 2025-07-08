# app/application/use_cases/fetch_comments.py
from typing import List
from app.domain.entities.post import Post
from app.domain.entities.comment import Comment
from app.domain.interfaces.services import IPokeAPIService
from app.domain.interfaces.repositories import ICommentRepository
from app.domain.exceptions import ServiceError, RepositoryError

class FetchAndStoreCommentsUseCase:
    """
    Use case for fetching comments for a specific post and storing them
    Follows Open/Closed Principle - can be extended without modifying existing code
    """
    
    def __init__(
        self,
        pokeapi_service: IPokeAPIService,
        comment_repository: ICommentRepository
    ):
        self.pokeapi_service = pokeapi_service
        self.comment_repository = comment_repository

    def execute(self, post: Post) -> List[Comment]:
        """
        Executes the use case:
        1. Fetches comments for the given post
        2. Stores them in the repository
        3. Returns the list of saved comments
        
        Args:
            post: The Post entity to fetch comments for
            
        Raises:
            ServiceError: If there's an issue with the PokeAPI service
            RepositoryError: If there's an issue with the repository
        """
        try:
            # Fetch from external service
            comments = self.pokeapi_service.fetch_comments_for_post(post)
            
            # Store in repository
            saved_comments = []
            for comment in comments:
                if self.comment_repository.save(comment):
                    saved_comments.append(comment)
            
            return saved_comments
            
        except ServiceError as e:
            raise ServiceError(f"Failed to fetch comments for post {post.id}: {str(e)}")
        except RepositoryError as e:
            raise RepositoryError(f"Failed to store comments for post {post.id}: {str(e)}")
        except Exception as e:
            raise ServiceError(f"Unexpected error in FetchAndStoreCommentsUseCase: {str(e)}")