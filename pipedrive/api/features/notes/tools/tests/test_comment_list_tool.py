"""Tests for list_comments_on_note_in_pipedrive tool."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.tools.comment_list_tool import list_comments_on_note_in_pipedrive
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.features.tool_registry import registry


@pytest.fixture(autouse=True)
def enable_notes_feature():
    """Enable the notes feature for all tests."""
    from pipedrive.api.features.notes import notes_tool_registry
    registry.enable_feature("notes")
    yield


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    notes_client = MagicMock()
    notes_client.comments = MagicMock()
    notes_client.comments.list_comments = AsyncMock()

    pipedrive_client = MagicMock()
    pipedrive_client.notes = notes_client

    ctx = MagicMock()
    ctx.request_context.lifespan_context.pipedrive_client = pipedrive_client

    return ctx


class TestListCommentsTool:
    """Tests for list_comments_on_note_in_pipedrive tool."""

    @pytest.mark.asyncio
    async def test_list_comments_default(self, mock_context):
        """Test listing comments with default parameters."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.list_comments.return_value = (
            [
                {"id": 1, "content": "Comment 1"},
                {"id": 2, "content": "Comment 2"},
            ],
            False,
        )

        result = await list_comments_on_note_in_pipedrive(
            mock_context, note_id="123"
        )

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["count"] == 2
        assert response["data"]["has_more"] is False
        assert len(response["data"]["comments"]) == 2

        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.list_comments.assert_called_once_with(
            note_id=123, start=0, limit=100
        )

    @pytest.mark.asyncio
    async def test_list_comments_with_pagination(self, mock_context):
        """Test listing comments with pagination parameters."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.list_comments.return_value = (
            [{"id": i} for i in range(50)],
            True,
        )

        result = await list_comments_on_note_in_pipedrive(
            mock_context, note_id="123", start=50, limit=50
        )

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["count"] == 50
        assert response["data"]["has_more"] is True
        assert response["data"]["pagination"]["start"] == 50
        assert response["data"]["pagination"]["limit"] == 50

        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.list_comments.assert_called_once_with(
            note_id=123, start=50, limit=50
        )

    @pytest.mark.asyncio
    async def test_list_comments_invalid_note_id(self, mock_context):
        """Test error handling for invalid note ID."""
        result = await list_comments_on_note_in_pipedrive(
            mock_context, note_id="invalid"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "note_id" in response["error"]

    @pytest.mark.asyncio
    async def test_list_comments_invalid_start(self, mock_context):
        """Test error for negative start parameter."""
        result = await list_comments_on_note_in_pipedrive(
            mock_context, note_id="123", start=-1
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "start must be non-negative" in response["error"]

    @pytest.mark.asyncio
    async def test_list_comments_invalid_limit(self, mock_context):
        """Test error for invalid limit parameter."""
        result = await list_comments_on_note_in_pipedrive(
            mock_context, note_id="123", limit=0
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "limit must be between 1 and 500" in response["error"]

        result = await list_comments_on_note_in_pipedrive(
            mock_context, note_id="123", limit=1000
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "limit must be between 1 and 500" in response["error"]

    @pytest.mark.asyncio
    async def test_list_comments_api_error(self, mock_context):
        """Test handling of API errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.list_comments.side_effect = PipedriveAPIError(
            "Note not found", status_code=404
        )

        result = await list_comments_on_note_in_pipedrive(
            mock_context, note_id="123"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Pipedrive API error" in response["error"]

    @pytest.mark.asyncio
    async def test_list_comments_unexpected_error(self, mock_context):
        """Test handling of unexpected errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.list_comments.side_effect = Exception(
            "Something went wrong"
        )

        result = await list_comments_on_note_in_pipedrive(
            mock_context, note_id="123"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Unexpected error" in response["error"]
