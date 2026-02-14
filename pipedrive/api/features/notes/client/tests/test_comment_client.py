"""Tests for CommentClient."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.client.comment_client import CommentClient


@pytest.fixture
def mock_base_client():
    """Create a mock base client."""
    client = MagicMock()
    client.request = AsyncMock()
    return client


@pytest.fixture
def comment_client(mock_base_client):
    """Create a CommentClient with mocked base client."""
    return CommentClient(mock_base_client)


class TestCommentClient:
    """Tests for CommentClient."""

    @pytest.mark.asyncio
    async def test_add_comment(self, comment_client, mock_base_client):
        """Test adding a comment to a note."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 1,
                "content": "Great note!",
                "note_id": 123,
                "user_id": 5,
            }
        }

        result = await comment_client.add_comment(note_id=123, content="Great note!")

        mock_base_client.request.assert_called_once_with(
            "POST",
            "/notes/123/comments",
            json_payload={"content": "Great note!"},
            version="v1",
        )
        assert result["id"] == 1
        assert result["content"] == "Great note!"

    @pytest.mark.asyncio
    async def test_get_comment(self, comment_client, mock_base_client):
        """Test retrieving a comment by ID."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 1,
                "content": "A comment",
                "note_id": 123,
            }
        }

        result = await comment_client.get_comment(note_id=123, comment_id=1)

        mock_base_client.request.assert_called_once_with(
            "GET",
            "/notes/123/comments/1",
            version="v1",
        )
        assert result["id"] == 1
        assert result["content"] == "A comment"

    @pytest.mark.asyncio
    async def test_update_comment(self, comment_client, mock_base_client):
        """Test updating a comment."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 1,
                "content": "Updated comment",
                "note_id": 123,
            }
        }

        result = await comment_client.update_comment(
            note_id=123, comment_id=1, content="Updated comment"
        )

        mock_base_client.request.assert_called_once_with(
            "PUT",
            "/notes/123/comments/1",
            json_payload={"content": "Updated comment"},
            version="v1",
        )
        assert result["content"] == "Updated comment"

    @pytest.mark.asyncio
    async def test_delete_comment(self, comment_client, mock_base_client):
        """Test deleting a comment."""
        mock_base_client.request.return_value = {
            "data": {"id": 1}
        }

        result = await comment_client.delete_comment(note_id=123, comment_id=1)

        mock_base_client.request.assert_called_once_with(
            "DELETE",
            "/notes/123/comments/1",
            version="v1",
        )
        assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_list_comments(self, comment_client, mock_base_client):
        """Test listing comments on a note."""
        mock_base_client.request.return_value = {
            "data": [
                {"id": 1, "content": "Comment 1"},
                {"id": 2, "content": "Comment 2"},
            ],
            "additional_data": {
                "pagination": {
                    "more_items_in_collection": False
                }
            },
        }

        comments, has_more = await comment_client.list_comments(note_id=123)

        mock_base_client.request.assert_called_once_with(
            "GET",
            "/notes/123/comments",
            query_params={"start": 0, "limit": 100},
            version="v1",
        )
        assert len(comments) == 2
        assert has_more is False

    @pytest.mark.asyncio
    async def test_list_comments_with_pagination(self, comment_client, mock_base_client):
        """Test listing comments with pagination."""
        mock_base_client.request.return_value = {
            "data": [{"id": i} for i in range(50)],
            "additional_data": {
                "pagination": {
                    "more_items_in_collection": True
                }
            },
        }

        comments, has_more = await comment_client.list_comments(
            note_id=123, start=50, limit=50
        )

        mock_base_client.request.assert_called_once_with(
            "GET",
            "/notes/123/comments",
            query_params={"start": 50, "limit": 50},
            version="v1",
        )
        assert len(comments) == 50
        assert has_more is True
