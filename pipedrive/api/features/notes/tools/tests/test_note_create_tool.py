"""Tests for create_note_in_pipedrive tool."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.tools.note_create_tool import create_note_in_pipedrive
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.features.tool_registry import registry
from pydantic import ValidationError


@pytest.fixture(autouse=True)
def enable_notes_feature():
    """Enable the notes feature for all tests."""
    # Register and enable feature before tests
    from pipedrive.api.features.notes import notes_tool_registry
    registry.enable_feature("notes")
    yield
    # Clean up after tests if needed


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    notes_client = MagicMock()
    notes_client.create_note = AsyncMock()

    pipedrive_client = MagicMock()
    pipedrive_client.notes = notes_client

    ctx = MagicMock()
    ctx.request_context.lifespan_context.pipedrive_client = pipedrive_client

    return ctx


class TestCreateNoteTool:
    """Tests for create_note_in_pipedrive tool."""

    @pytest.mark.asyncio
    async def test_create_note_with_deal(self, mock_context):
        """Test creating a note attached to a deal."""
        mock_context.pipedrive_client.notes.create_note.return_value = {
            "id": 123,
            "content": "Test note",
            "deal_id": 456
        }

        result = await create_note_in_pipedrive(
            mock_context,
            content="Test note",
            deal_id="456"
        )

        # Parse JSON response
        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["id"] == 123

        # Verify client was called correctly
        mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.assert_called_once()
        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.call_args.kwargs
        assert call_kwargs["content"] == "Test note"
        assert call_kwargs["deal_id"] == 456

    @pytest.mark.asyncio
    async def test_create_note_with_person(self, mock_context):
        """Test creating a note attached to a person."""
        mock_context.pipedrive_client.notes.create_note.return_value = {
            "id": 789,
            "content": "Person note",
            "person_id": 123
        }

        result = await create_note_in_pipedrive(
            mock_context,
            content="Person note",
            person_id="123"
        )

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["person_id"] == 123

    @pytest.mark.asyncio
    async def test_create_note_with_lead(self, mock_context):
        """Test creating a note attached to a lead."""
        mock_context.pipedrive_client.notes.create_note.return_value = {
            "id": 999,
            "content": "Lead note",
            "lead_id": "abc-123-def"
        }

        result = await create_note_in_pipedrive(
            mock_context,
            content="Lead note",
            lead_id="abc-123-def"
        )

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["lead_id"] == "abc-123-def"

    @pytest.mark.asyncio
    async def test_create_note_with_pinning(self, mock_context):
        """Test creating a pinned note."""
        mock_context.pipedrive_client.notes.create_note.return_value = {
            "id": 123,
            "content": "Pinned note",
            "deal_id": 456,
            "pinned_to_deal_flag": 1
        }

        result = await create_note_in_pipedrive(
            mock_context,
            content="Pinned note",
            deal_id="456",
            pinned=True
        )

        response = json.loads(result)
        assert response["success"] is True

        # Verify pinning flag was set
        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.call_args.kwargs
        assert call_kwargs["pinned_to_deal_flag"] == 1

    @pytest.mark.asyncio
    async def test_create_note_with_user(self, mock_context):
        """Test creating a note with specific user."""
        mock_context.pipedrive_client.notes.create_note.return_value = {
            "id": 123,
            "content": "User note",
            "deal_id": 456,
            "user_id": 5
        }

        result = await create_note_in_pipedrive(
            mock_context,
            content="User note",
            deal_id="456",
            user_id="5"
        )

        response = json.loads(result)
        assert response["success"] is True

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.call_args.kwargs
        assert call_kwargs["user_id"] == 5

    @pytest.mark.asyncio
    async def test_create_note_invalid_deal_id(self, mock_context):
        """Test error handling for invalid deal ID."""
        result = await create_note_in_pipedrive(
            mock_context,
            content="Test note",
            deal_id="invalid"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "deal_id" in response["error"]

    @pytest.mark.asyncio
    async def test_create_note_validation_error(self, mock_context):
        """Test handling of validation errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.side_effect = ValidationError.from_exception_data(
            "Note",
            [{"type": "value_error", "loc": ("content",), "msg": "Note content cannot be empty", "input": ""}]
        )

        result = await create_note_in_pipedrive(
            mock_context,
            content="Test",
            deal_id="123"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Validation error" in response["error"]

    @pytest.mark.asyncio
    async def test_create_note_api_error(self, mock_context):
        """Test handling of API errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.side_effect = PipedriveAPIError(
            "API Error", status_code=400
        )

        result = await create_note_in_pipedrive(
            mock_context,
            content="Test note",
            deal_id="123"
        )

        response = json.loads(result)
        assert response["success"] is False
        assert "Pipedrive API error" in response["error"]

    @pytest.mark.asyncio
    async def test_create_note_html_content(self, mock_context):
        """Test creating note with HTML content."""
        html_content = "<p>This is <strong>bold</strong> text</p>"
        mock_context.pipedrive_client.notes.create_note.return_value = {
            "id": 123,
            "content": html_content,
            "deal_id": 456
        }

        result = await create_note_in_pipedrive(
            mock_context,
            content=html_content,
            deal_id="456"
        )

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["content"] == html_content

    @pytest.mark.asyncio
    async def test_create_note_sanitize_empty_strings(self, mock_context):
        """Test that empty strings are sanitized to None."""
        mock_context.pipedrive_client.notes.create_note.return_value = {
            "id": 123,
            "content": "Test",
            "deal_id": 456
        }

        result = await create_note_in_pipedrive(
            mock_context,
            content="Test",
            deal_id="456",
            person_id="",  # Empty string should be converted to None
            user_id="  "   # Whitespace only should be converted to None
        )

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.create_note.call_args.kwargs
        assert call_kwargs["person_id"] is None
        assert call_kwargs["user_id"] is None
