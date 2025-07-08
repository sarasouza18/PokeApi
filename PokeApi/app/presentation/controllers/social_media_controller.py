# app/presentation/controllers/social_media_controller.py
import logging
from typing import List, Dict, Any
from app.domain.entities.post import Post
from app.domain.entities.comment import Comment
from app.domain.interfaces.repositories import IPostRepository, ICommentRepository
from app.domain.interfaces.services import IPokeAPIService, IProcessingService
from app.presentation.error_handling.error_handler import ErrorHandler
from app.infrastructure.search.opensearch_service import OpenSearchService  # ➕ Import OpenSearch

logger = logging.getLogger(__name__)

class SocialMediaController:
    """
    Main controller for social media operations that:
    - Orchestrates the data pipeline
    - Coordinates between services and repositories
    - Handles errors at the presentation layer
    """

    def __init__(
        self,
        post_repository: IPostRepository,
        comment_repository: ICommentRepository,
        pokeapi_service: IPokeAPIService,
        processing_service: IProcessingService
    ):
        self.post_repository = post_repository
        self.comment_repository = comment_repository
        self.pokeapi_service = pokeapi_service
        self.processing_service = processing_service
        self.opensearch_service = OpenSearchService()  # ➕ Instância de OpenSearch

    def execute_pipeline(self) -> Dict[str, Any]:
        """
        Execute the complete data processing pipeline with error handling
        
        Returns:
            Dictionary containing either:
            - Success response with statistics, or
            - Error response if pipeline fails
        """
        @ErrorHandler.wrap_endpoint
        def _execute():
            return self._execute_pipeline_internal()
            
        return _execute()

    def _execute_pipeline_internal(self) -> Dict[str, Any]:
        """
        Internal implementation of the pipeline execution
        """
        logger.info("Starting social media data pipeline")
        
        posts = self._fetch_and_store_posts()
        stats = {
            'posts_processed': 0,
            'comments_processed': 0,
            'post_errors': [],
            'comment_errors': []
        }
        
        for post in posts:
            post_result = self._process_post(post)
            if post_result['status'] == 'processed':
                stats['posts_processed'] += 1
            else:
                stats['post_errors'].append(post_result)
            
            comments = self._fetch_and_store_comments(post)
            for comment in comments:
                comment_result = self._process_comment(comment)
                if comment_result['status'] == 'processed':
                    stats['comments_processed'] += 1
                else:
                    stats['comment_errors'].append(comment_result)
        
        logger.info("Pipeline execution completed")
        return {
            'status': 'completed',
            'stats': stats
        }

    def _fetch_and_store_posts(self) -> List[Post]:
        """Fetch posts from PokeAPI and store in repository"""
        logger.debug("Fetching posts from PokeAPI")
        posts = self.pokeapi_service.fetch_and_transform_posts()
        saved_posts = []
        
        for post in posts:
            if self.post_repository.save(post):
                saved_posts.append(post)
                logger.debug(f"Saved post: {post.id}")
        
        logger.info(f"Saved {len(saved_posts)} posts")
        return saved_posts

    def _process_post(self, post: Post) -> Dict[str, Any]:
        """Process post data through the processing service"""
        logger.debug(f"Processing post {post.id}")
        result = self.processing_service.process_post(post.to_dict())

        if result:
            logger.debug(f"Successfully processed post {post.id}")

            try:
                self.opensearch_service.index_post(post.id, post.to_dict())
                logger.info(f"✅ Post {post.id} indexed in OpenSearch")
            except Exception as e:
                logger.warning(f"⚠️ Failed to index post {post.id}: {str(e)}")

            return {'post_id': post.id, 'status': 'processed'}

        return {'post_id': post.id, 'status': 'failed'}

    def _fetch_and_store_comments(self, post: Post) -> List[Comment]:
        """Fetch comments for a post and store in repository"""
        logger.debug(f"Fetching comments for post {post.id}")
        comments = self.pokeapi_service.fetch_comments_for_post(post)
        saved_comments = []
        
        for comment in comments:
            if self.comment_repository.save(comment):
                saved_comments.append(comment)
                logger.debug(f"Saved comment: {comment.id}")
        
        logger.info(f"Saved {len(saved_comments)} comments for post {post.id}")
        return saved_comments

    def _process_comment(self, comment: Comment) -> Dict[str, Any]:
        """Process comment data through the processing service"""
        logger.debug(f"Processing comment {comment.id}")
        result = self.processing_service.process_comment(comment.to_dict())
        if result:
            logger.debug(f"Successfully processed comment {comment.id}")
            return {'comment_id': comment.id, 'status': 'processed'}
        return {'comment_id': comment.id, 'status': 'failed'}
