import pytest
import requests
from unittest.mock import MagicMock, patch
from app.infrastructure.external.processing_service import ProcessingService
from app.infrastructure.external.dead_letter_queue import DeadLetterQueue

@pytest.fixture
def mock_dlq():
    return MagicMock(spec=DeadLetterQueue)

@pytest.fixture
def service(mock_dlq):
    return ProcessingService(dlq=mock_dlq, endpoint="http://mocked-endpoint.com")

def test_process_post_success(service):
    with patch.object(service, '_make_request', return_value={"status": "ok"}) as mock_request:
        post_data = {"id": "123", "content": "Test post"}
        result = service.process_post(post_data)
        assert result == {"status": "ok"}
        mock_request.assert_called_once_with(post_data)

def test_process_post_failure_sends_to_dlq(service, mock_dlq):
    with patch.object(service, '_make_request', side_effect=Exception("Mocked failure")):
        post_data = {"id": "123", "content": "Test post"}
        result = service.process_post(post_data)
        assert result is None
        mock_dlq.add_failed_item.assert_called_once_with("post", post_data)

def test_process_comment_success(service):
    with patch.object(service, '_make_request', return_value={"status": "ok"}) as mock_request:
        comment_data = {"id": "456", "content": "Test comment"}
        result = service.process_comment(comment_data)
        assert result == {"status": "ok"}
        mock_request.assert_called_once_with(comment_data)

def test_process_comment_failure_sends_to_dlq(service, mock_dlq):
    with patch.object(service, '_make_request', side_effect=Exception("Mocked failure")):
        comment_data = {"id": "456", "content": "Test comment"}
        result = service.process_comment(comment_data)
        assert result is None
        mock_dlq.add_failed_item.assert_called_once_with("comment", comment_data)
def test_successful_process_post(service, mock_dlq):
    data = {"id": "123", "content": "test"}

    with patch("app.infrastructure.external.processing_service.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"result": "ok"}
        mock_post.return_value.raise_for_status.return_value = None

        result = service.process_post(data)

    assert result == {"result": "ok"}
    mock_dlq.add_failed_item.assert_not_called()

def test_failed_process_post_sends_to_dlq(service, mock_dlq):
    data = {"id": "123", "content": "fail"}

    with patch("app.infrastructure.external.processing_service.requests.post", side_effect=Exception("Boom")):
        result = service.process_post(data)

    assert result is None
    mock_dlq.add_failed_item.assert_called_once_with("post", data)

def test_retry_on_transient_failure(service):
    data = {"id": "789", "content": "retry"}

    call_tracker = {"attempts": 0}

    def flaky_request(*args, **kwargs):
        call_tracker["attempts"] += 1
        if call_tracker["attempts"] < 3:
            raise requests.exceptions.RequestException("Temporary error")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"result": "recovered"}
        return mock_resp

    with patch("app.infrastructure.external.processing_service.requests.post", side_effect=flaky_request):
        result = service.process_post(data)

    assert result == {"result": "recovered"}
    assert call_tracker["attempts"] == 3