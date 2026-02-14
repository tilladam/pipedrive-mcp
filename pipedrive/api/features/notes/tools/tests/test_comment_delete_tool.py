"""Tests for delete_comment_on_note_from_pipedrive tool."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.tools.comment_delete_tool import delete_comment_on_note_from_pipedrive
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
    notes_client.comments.delete_comment = AsyncMock()

    pipedrive_client = MagicMock()
    pipedrive_client.notes = notes_client

    ctx = MagicMock()
    ctx.request_context.lifespan_context.pipedrive_client = pipedrive_client

    return ctx


class TestDeleteCommentTool:
    """Tests for delete_comment_on_note_from_pipedrive tool."""

    @pytest.mark.asyncio
    async def test_delete_comment_success(self, mock_context):
        """Test successfully deleting a comment."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.delete_comment.return_value = {
            "id": 1,
        }

        result = await delete_comment_on_note_from_pipedrive(
            mock_context, note_id="123", comment_id="1"
        )

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["id"] == 1

        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.delete_comment.assert_called_once_with(
            note_id=123, comment_id=1
        )

    @pytest.mark.asyncio
    async def test_delete_comment_invalid_note_id(self, mock_context):
        """Test error handling for invalid note ID."""
        result = await delete_comment_on_note_from_pipedrive(
            mock_context, note_id="invalid", comment_id="1"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "note_id" in response["error"]

    @pytest.mark.asyncio
    async def test_delete_comment_invalid_comment_id(self, mock_context):
        """Test error handling for invalid comment ID."""
        result = await delete_comment_on_note_from_pipedrive(
            mock_context, note_id="123", comment_id="invalid"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "comment_id" in response["error"]

    @pytest.mark.asyncio
    async def test_delete_comment_api_error(self, mock_context):
        """Test handling of API errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.delete_comment.side_effect = PipedriveAPIError(
            "Comment not found", status_code=404
        )

        result = await delete_comment_on_note_from_pipedrive(
            mock_context, note_id="123", comment_id="1"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Pipedrive API error" in response["error"]

    @pytest.mark.asyncio
    async def test_delete_comment_unexpected_error(self, mock_context):
        """Test handling of unexpected errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.delete_comment.side_effect = Exception(
            "Something went wrong"
        )

        result = await delete_comment_on_note_from_pipedrive(
            mock_context, note_id="123", comment_id="1"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Unexpected error" in response["error"]
