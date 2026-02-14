"""Tests for get_note_from_pipedrive tool."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.tools.note_get_tool import get_note_from_pipedrive
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
    notes_client.get_note = AsyncMock()

    pipedrive_client = MagicMock()
    pipedrive_client.notes = notes_client

    ctx = MagicMock()
    ctx.request_context.lifespan_context.pipedrive_client = pipedrive_client

    return ctx


class TestGetNoteTool:
    """Tests for get_note_from_pipedrive tool."""

    @pytest.mark.asyncio
    async def test_get_note_success(self, mock_context):
        """Test successfully retrieving a note."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.get_note.return_value = {
            "id": 123,
            "content": "Test note",
            "deal_id": 456,
            "user_id": 1,
            "add_time": "2024-01-15 10:30:00"
        }

        result = await get_note_from_pipedrive(mock_context, note_id="123")

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["id"] == 123
        assert response["data"]["content"] == "Test note"

        mock_context.request_context.lifespan_context.pipedrive_client.notes.get_note.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_get_note_invalid_id(self, mock_context):
        """Test error handling for invalid note ID."""
        result = await get_note_from_pipedrive(mock_context, note_id="invalid")

        response = json.loads(result)
        assert response["success"] is False
        assert "note_id" in response["error"]

    @pytest.mark.asyncio
    async def test_get_note_api_error(self, mock_context):
        """Test handling of API errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.get_note.side_effect = PipedriveAPIError(
            "Note not found", status_code=404
        )

        result = await get_note_from_pipedrive(mock_context, note_id="123")

        response = json.loads(result)
        assert response["success"] is False
        assert "Pipedrive API error" in response["error"]

    @pytest.mark.asyncio
    async def test_get_note_unexpected_error(self, mock_context):
        """Test handling of unexpected errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.get_note.side_effect = Exception("Unexpected error")

        result = await get_note_from_pipedrive(mock_context, note_id="123")

        response = json.loads(result)
        assert response["success"] is False
        assert "Unexpected error" in response["error"]
