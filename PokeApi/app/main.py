# app/main.py
import os
from app.infrastructure.persistence.dynamodb_repositories import (
    DynamoDBPostRepository,
    DynamoDBCommentRepository
)
from app.infrastructure.external.pokeapi_service import PokeAPIService
from app.infrastructure.external.processing_service import ProcessingService
from app.infrastructure.external.dead_letter_queue import DeadLetterQueue
from app.application.use_cases.posts import FetchAndStorePostsUseCase
from app.application.use_cases.comments import FetchAndStoreCommentsUseCase
from app.application.use_cases.processing import ProcessPostUseCase, ProcessCommentUseCase
from app.presentation.controllers.social_media_controller import SocialMediaController

def configure_container():
    # Initialize infrastructure components
    post_repository = DynamoDBPostRepository()
    comment_repository = DynamoDBCommentRepository()
    dlq = DeadLetterQueue()
    pokeapi_service = PokeAPIService()
    processing_service = ProcessingService(dlq)
    
    # Initialize use cases
    fetch_posts_use_case = FetchAndStorePostsUseCase(pokeapi_service, post_repository)
    fetch_comments_use_case = FetchAndStoreCommentsUseCase(pokeapi_service, comment_repository)
    process_post_use_case = ProcessPostUseCase(processing_service)
    process_comment_use_case = ProcessCommentUseCase(processing_service)
    
    # Initialize controller
    controller = SocialMediaController(
        fetch_posts_use_case,
        fetch_comments_use_case,
        process_post_use_case,
        process_comment_use_case
    )
    
    return controller

if __name__ == "__main__":
    controller = configure_container()
    controller.run_data_pipeline()