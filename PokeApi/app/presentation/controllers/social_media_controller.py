# app/presentation/controllers/social_media_controller.py
from typing import List
from app.domain.entities.post import Post
from app.domain.entities.comment import Comment
from app.application.use_cases.posts import FetchAndStorePostsUseCase
from app.application.use_cases.comments import FetchAndStoreCommentsUseCase
from app.application.use_cases.processing import ProcessPostUseCase, ProcessCommentUseCase

class SocialMediaController:
    def __init__(
        self,
        fetch_posts_use_case: FetchAndStorePostsUseCase,
        fetch_comments_use_case: FetchAndStoreCommentsUseCase,
        process_post_use_case: ProcessPostUseCase,
        process_comment_use_case: ProcessCommentUseCase
    ):
        self.fetch_posts_use_case = fetch_posts_use_case
        self.fetch_comments_use_case = fetch_comments_use_case
        self.process_post_use_case = process_post_use_case
        self.process_comment_use_case = process_comment_use_case

    def run_data_pipeline(self) -> None:
        print("Starting data pipeline...")
        
        # Step 1: Fetch and store posts
        posts = self.fetch_posts_use_case.execute()
        print(f"Fetched and stored {len(posts)} posts")
        
        # Step 2: Process posts and fetch/store comments
        for post in posts:
            # Process the post
            processed_data = self.process_post_use_case.execute(post.to_dict())
            if processed_data:
                print(f"Processed post: {post.id}")
            
            # Fetch and store comments for this post
            comments = self.fetch_comments_use_case.execute(post)
            print(f"Fetched and stored {len(comments)} comments for post {post.id}")
            
            # Process each comment
            for comment in comments:
                processed_data = self.process_comment_use_case.execute(comment.to_dict())
                if processed_data:
                    print(f"Processed comment: {comment.id}")
        
        print("Data pipeline completed successfully.")