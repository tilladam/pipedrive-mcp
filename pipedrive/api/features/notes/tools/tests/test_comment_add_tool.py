"""Tests for add_comment_to_note_in_pipedrive tool."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.tools.comment_add_tool import add_comment_to_note_in_pipedrive
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
    notes_client.comments.add_comment = AsyncMock()

    pipedrive_client = MagicMock()
    pipedrive_client.notes = notes_client

    ctx = MagicMock()
    ctx.request_context.lifespan_context.pipedrive_client = pipedrive_client

    return ctx


class TestAddCommentTool:
    """Tests for add_comment_to_note_in_pipedrive tool."""

    @pytest.mark.asyncio
    async def test_add_comment_success(self, mock_context):
        """Test successfully adding a comment."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.add_comment.return_value = {
            "id": 1,
            "content": "Great note!",
            "note_id": 123,
            "user_id": 5,
        }

        result = await add_comment_to_note_in_pipedrive(
            mock_context, note_id="123", content="Great note!"
        )

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["id"] == 1
        assert response["data"]["content"] == "Great note!"

        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.add_comment.assert_called_once_with(
            note_id=123, content="Great note!"
        )

    @pytest.mark.asyncio
    async def test_add_comment_invalid_note_id(self, mock_context):
        """Test error handling for invalid note ID."""
        result = await add_comment_to_note_in_pipedrive(
            mock_context, note_id="invalid", content="Test"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "note_id" in response["error"]

    @pytest.mark.asyncio
    async def test_add_comment_empty_content(self, mock_context):
        """Test error handling for empty content."""
        result = await add_comment_to_note_in_pipedrive(
            mock_context, note_id="123", content=""
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "empty" in response["error"]

    @pytest.mark.asyncio
    async def test_add_comment_whitespace_content(self, mock_context):
        """Test error handling for whitespace-only content."""
        result = await add_comment_to_note_in_pipedrive(
            mock_context, note_id="123", content="   "
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "empty" in response["error"]

    @pytest.mark.asyncio
    async def test_add_comment_api_error(self, mock_context):
        """Test handling of API errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.add_comment.side_effect = PipedriveAPIError(
            "Note not found", status_code=404
        )

        result = await add_comment_to_note_in_pipedrive(
            mock_context, note_id="123", content="Test"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Pipedrive API error" in response["error"]

    @pytest.mark.asyncio
    async def test_add_comment_unexpected_error(self, mock_context):
        """Test handling of unexpected errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.comments.add_comment.side_effect = Exception(
            "Something went wrong"
        )

        result = await add_comment_to_note_in_pipedrive(
            mock_context, note_id="123", content="Test"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Unexpected error" in response["error"]
