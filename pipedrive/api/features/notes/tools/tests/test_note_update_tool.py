"""Tests for update_note_in_pipedrive tool."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.tools.note_update_tool import update_note_in_pipedrive
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
    notes_client.update_note = AsyncMock()

    pipedrive_client = MagicMock()
    pipedrive_client.notes = notes_client

    ctx = MagicMock()
    ctx.request_context.lifespan_context.pipedrive_client = pipedrive_client

    return ctx


class TestUpdateNoteTool:
    """Tests for update_note_in_pipedrive tool."""

    @pytest.mark.asyncio
    async def test_update_note_content(self, mock_context):
        """Test updating note content."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.return_value = {
            "id": 123,
            "content": "Updated content",
            "deal_id": 456
        }

        result = await update_note_in_pipedrive(
            mock_context,
            note_id="123",
            content="Updated content"
        )

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["content"] == "Updated content"

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.call_args.kwargs
        assert call_kwargs["note_id"] == 123
        assert call_kwargs["content"] == "Updated content"

    @pytest.mark.asyncio
    async def test_update_note_change_entity(self, mock_context):
        """Test changing note attachment to different entity."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.return_value = {
            "id": 123,
            "content": "Note",
            "person_id": 789
        }

        result = await update_note_in_pipedrive(
            mock_context,
            note_id="123",
            person_id="789"
        )

        response = json.loads(result)
        assert response["success"] is True

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.call_args.kwargs
        assert call_kwargs["person_id"] == 789

    @pytest.mark.asyncio
    async def test_update_note_toggle_pinning(self, mock_context):
        """Test toggling note pinning."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.return_value = {
            "id": 123,
            "content": "Note",
            "deal_id": 456,
            "pinned_to_deal_flag": 1
        }

        result = await update_note_in_pipedrive(
            mock_context,
            note_id="123",
            pinned=True
        )

        response = json.loads(result)
        assert response["success"] is True

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.call_args.kwargs
        # When pinned=True and no entity specified, all flags should be set
        assert call_kwargs["pinned_to_deal_flag"] == 1

    @pytest.mark.asyncio
    async def test_update_note_unpin(self, mock_context):
        """Test unpinning a note."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.return_value = {
            "id": 123,
            "content": "Note",
            "deal_id": 456,
            "pinned_to_deal_flag": 0
        }

        result = await update_note_in_pipedrive(
            mock_context,
            note_id="123",
            pinned=False
        )

        response = json.loads(result)
        assert response["success"] is True

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.call_args.kwargs
        assert call_kwargs["pinned_to_deal_flag"] == 0

    @pytest.mark.asyncio
    async def test_update_note_invalid_id(self, mock_context):
        """Test error handling for invalid note ID."""
        result = await update_note_in_pipedrive(
            mock_context,
            note_id="invalid",
            content="Test"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "note_id" in response["error"]

    @pytest.mark.asyncio
    async def test_update_note_api_error(self, mock_context):
        """Test handling of API errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.side_effect = PipedriveAPIError(
            "Note not found", status_code=404
        )

        result = await update_note_in_pipedrive(
            mock_context,
            note_id="123",
            content="Updated"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Pipedrive API error" in response["error"]

    @pytest.mark.asyncio
    async def test_update_note_value_error(self, mock_context):
        """Test handling of ValueError from client."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.side_effect = ValueError(
            "At least one field must be provided for update"
        )

        result = await update_note_in_pipedrive(
            mock_context,
            note_id="123"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Validation error" in response["error"]

    @pytest.mark.asyncio
    async def test_update_note_multiple_fields(self, mock_context):
        """Test updating multiple fields at once."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.return_value = {
            "id": 123,
            "content": "New content",
            "person_id": 789,
            "pinned_to_person_flag": 1
        }

        result = await update_note_in_pipedrive(
            mock_context,
            note_id="123",
            content="New content",
            person_id="789",
            pinned=True
        )

        response = json.loads(result)
        assert response["success"] is True

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.update_note.call_args.kwargs
        assert call_kwargs["content"] == "New content"
        assert call_kwargs["person_id"] == 789
        assert call_kwargs["pinned_to_person_flag"] == 1
