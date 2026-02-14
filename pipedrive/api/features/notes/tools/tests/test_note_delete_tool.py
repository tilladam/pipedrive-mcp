"""Tests for delete_note_from_pipedrive tool."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.tools.note_delete_tool import delete_note_from_pipedrive
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
    notes_client.delete_note = AsyncMock()

    pipedrive_client = MagicMock()
    pipedrive_client.notes = notes_client

    ctx = MagicMock()
    ctx.request_context.lifespan_context.pipedrive_client = pipedrive_client

    return ctx


class TestDeleteNoteTool:
    """Tests for delete_note_from_pipedrive tool."""

    @pytest.mark.asyncio
    async def test_delete_note_success(self, mock_context):
        """Test successfully deleting a note."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.delete_note.return_value = {
            "id": 123
        }

        result = await delete_note_from_pipedrive(mock_context, note_id="123")

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["id"] == 123

        mock_context.request_context.lifespan_context.pipedrive_client.notes.delete_note.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_delete_note_invalid_id(self, mock_context):
        """Test error handling for invalid note ID."""
        result = await delete_note_from_pipedrive(mock_context, note_id="invalid")

        response = json.loads(result)
        assert response["success"] is False
        assert "note_id" in response["error"]

    @pytest.mark.asyncio
    async def test_delete_note_api_error(self, mock_context):
        """Test handling of API errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.delete_note.side_effect = PipedriveAPIError(
            "Note not found", status_code=404
        )

        result = await delete_note_from_pipedrive(mock_context, note_id="123")

        response = json.loads(result)
        assert response["success"] is False
        assert "Pipedrive API error" in response["error"]

    @pytest.mark.asyncio
    async def test_delete_note_unexpected_error(self, mock_context):
        """Test handling of unexpected errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.delete_note.side_effect = Exception("Unexpected error")

        result = await delete_note_from_pipedrive(mock_context, note_id="123")

        response = json.loads(result)
        assert response["success"] is False
        assert "Unexpected error" in response["error"]
