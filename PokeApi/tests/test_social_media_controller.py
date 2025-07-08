# tests/test_social_media_controller.py
import pytest
from unittest.mock import MagicMock
from app.presentation.controllers.social_media_controller import SocialMediaController

@pytest.fixture
def controller():
    return SocialMediaController(
        post_repository=MagicMock(),
        comment_repository=MagicMock(),
        pokeapi_service=MagicMock(),
        processing_service=MagicMock()
    )

def test_execute_pipeline_success(controller):
    post = MagicMock(id="post123", to_dict=lambda: {"id": "post123"})
    comment = MagicMock(id="cmt456", to_dict=lambda: {"id": "cmt456"})

    controller.pokeapi_service.fetch_and_transform_posts.return_value = [post]
    controller.pokeapi_service.fetch_comments_for_post.return_value = [comment]
    controller.post_repository.save.return_value = True
    controller.comment_repository.save.return_value = True
    controller.processing_service.process_post.return_value = True
    controller.processing_service.process_comment.return_value = True

    result = controller.execute_pipeline()
    assert result["status"] == "completed"
    assert result["stats"]["posts_processed"] == 1
    assert result["stats"]["comments_processed"] == 1
