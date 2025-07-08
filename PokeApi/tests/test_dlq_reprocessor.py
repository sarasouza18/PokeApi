# tests/test_dlq_reprocessor.py
import pytest
from unittest.mock import patch, MagicMock
from app.infrastructure.workers import dlq_reprocessor

@patch("app.infrastructure.workers.dlq_reprocessor.sqs")
@patch("app.infrastructure.workers.dlq_reprocessor.processor")
@patch("app.infrastructure.workers.dlq_reprocessor.post_repo")
def test_process_success(mock_repo, mock_processor, mock_sqs):
    mock_post = MagicMock()
    mock_post.to_dict.return_value = {"id": "123", "content": "example"}
    mock_repo.get.return_value = mock_post
    mock_processor.process_post.return_value = {"ok": True}

    payload = {"id": "123", "content": "example"}
    result = dlq_reprocessor.process_message("post", payload)

    assert result is True
