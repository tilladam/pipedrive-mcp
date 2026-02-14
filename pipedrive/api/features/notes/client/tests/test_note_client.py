"""Tests for NoteClient."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.client.note_client import NoteClient
from pydantic import ValidationError


@pytest.fixture
def mock_base_client():
    """Create a mock base client."""
    client = MagicMock()
    client.request = AsyncMock()
    return client


@pytest.fixture
def note_client(mock_base_client):
    """Create a NoteClient with mocked base client."""
    return NoteClient(mock_base_client)


class TestNoteClient:
    """Tests for NoteClient."""

    @pytest.mark.asyncio
    async def test_create_note(self, note_client, mock_base_client):
        """Test creating a note."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 123,
                "content": "Test note",
                "deal_id": 456,
                "user_id": 1
            }
        }

        result = await note_client.create_note(
            content="Test note",
            deal_id=456,
            user_id=1
        )

        # Verify request was made with correct parameters
        mock_base_client.request.assert_called_once()
        call_args = mock_base_client.request.call_args

        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/notes"
        assert call_args[1]["version"] == "v1"
        assert call_args[1]["json_payload"]["content"] == "Test note"
        assert call_args[1]["json_payload"]["deal_id"] == 456

        # Verify result
        assert result["id"] == 123
        assert result["content"] == "Test note"

    @pytest.mark.asyncio
    async def test_create_note_with_lead(self, note_client, mock_base_client):
        """Test creating a note attached to a lead."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 123,
                "content": "Lead note",
                "lead_id": "abc-123-def"
            }
        }

        result = await note_client.create_note(
            content="Lead note",
            lead_id="abc-123-def"
        )

        call_args = mock_base_client.request.call_args
        assert call_args[1]["json_payload"]["lead_id"] == "abc-123-def"
        assert result["lead_id"] == "abc-123-def"

    @pytest.mark.asyncio
    async def test_create_note_with_pinning(self, note_client, mock_base_client):
        """Test creating a pinned note."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 123,
                "content": "Pinned note",
                "deal_id": 456,
                "pinned_to_deal_flag": 1
            }
        }

        result = await note_client.create_note(
            content="Pinned note",
            deal_id=456,
            pinned_to_deal_flag=1
        )

        call_args = mock_base_client.request.call_args
        assert call_args[1]["json_payload"]["pinned_to_deal_flag"] == 1

    @pytest.mark.asyncio
    async def test_create_note_validation_error(self, note_client):
        """Test that validation errors are raised for invalid data."""
        # No entity attachment
        with pytest.raises(ValidationError, match="must be attached to exactly one entity"):
            await note_client.create_note(content="Test note")

        # Multiple entities
        with pytest.raises(ValidationError, match="can only be attached to one entity"):
            await note_client.create_note(
                content="Test note",
                deal_id=123,
                person_id=456
            )

    @pytest.mark.asyncio
    async def test_get_note(self, note_client, mock_base_client):
        """Test retrieving a note by ID."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 123,
                "content": "Retrieved note",
                "deal_id": 456
            }
        }

        result = await note_client.get_note(123)

        mock_base_client.request.assert_called_once_with(
            "GET",
            "/notes/123",
            version="v1"
        )
        assert result["id"] == 123
        assert result["content"] == "Retrieved note"

    @pytest.mark.asyncio
    async def test_update_note(self, note_client, mock_base_client):
        """Test updating a note."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 123,
                "content": "Updated content",
                "deal_id": 456
            }
        }

        result = await note_client.update_note(
            note_id=123,
            content="Updated content"
        )

        call_args = mock_base_client.request.call_args
        assert call_args[0][0] == "PUT"
        assert call_args[0][1] == "/notes/123"
        assert call_args[1]["version"] == "v1"
        assert call_args[1]["json_payload"]["content"] == "Updated content"

        assert result["content"] == "Updated content"

    @pytest.mark.asyncio
    async def test_update_note_change_entity(self, note_client, mock_base_client):
        """Test updating note to attach to different entity."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 123,
                "content": "Note",
                "person_id": 789
            }
        }

        result = await note_client.update_note(
            note_id=123,
            person_id=789
        )

        call_args = mock_base_client.request.call_args
        assert call_args[1]["json_payload"]["person_id"] == 789

    @pytest.mark.asyncio
    async def test_update_note_no_fields(self, note_client):
        """Test that update without fields raises ValueError."""
        with pytest.raises(ValueError, match="At least one field must be provided"):
            await note_client.update_note(note_id=123)

    @pytest.mark.asyncio
    async def test_delete_note(self, note_client, mock_base_client):
        """Test deleting a note."""
        mock_base_client.request.return_value = {
            "data": {
                "id": 123
            }
        }

        result = await note_client.delete_note(123)

        mock_base_client.request.assert_called_once_with(
            "DELETE",
            "/notes/123",
            version="v1"
        )
        assert result["id"] == 123

    @pytest.mark.asyncio
    async def test_list_notes(self, note_client, mock_base_client):
        """Test listing notes."""
        mock_base_client.request.return_value = {
            "data": [
                {"id": 1, "content": "Note 1"},
                {"id": 2, "content": "Note 2"}
            ],
            "additional_data": {
                "pagination": {
                    "more_items_in_collection": True
                }
            }
        }

        notes, has_more = await note_client.list_notes()

        mock_base_client.request.assert_called_once()
        call_args = mock_base_client.request.call_args

        assert call_args[0][0] == "GET"
        assert call_args[0][1] == "/notes"
        assert call_args[1]["version"] == "v1"
        assert call_args[1]["params"]["start"] == 0
        assert call_args[1]["params"]["limit"] == 100

        assert len(notes) == 2
        assert has_more is True

    @pytest.mark.asyncio
    async def test_list_notes_with_filters(self, note_client, mock_base_client):
        """Test listing notes with filters."""
        mock_base_client.request.return_value = {
            "data": [{"id": 1, "content": "Filtered note"}],
            "additional_data": {
                "pagination": {
                    "more_items_in_collection": False
                }
            }
        }

        notes, has_more = await note_client.list_notes(
            deal_id=456,
            user_id=1,
            pinned_to_deal_flag=1,
            start=10,
            limit=50,
            sort="add_time",
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        call_args = mock_base_client.request.call_args
        params = call_args[1]["params"]

        assert params["deal_id"] == 456
        assert params["user_id"] == 1
        assert params["pinned_to_deal_flag"] == 1
        assert params["start"] == 10
        assert params["limit"] == 50
        assert params["sort"] == "add_time"
        assert params["start_date"] == "2024-01-01"
        assert params["end_date"] == "2024-12-31"

        assert len(notes) == 1
        assert has_more is False

    @pytest.mark.asyncio
    async def test_list_notes_pagination(self, note_client, mock_base_client):
        """Test pagination in list notes."""
        mock_base_client.request.return_value = {
            "data": [{"id": i} for i in range(100)],
            "additional_data": {
                "pagination": {
                    "more_items_in_collection": True
                }
            }
        }

        notes, has_more = await note_client.list_notes(start=100, limit=100)

        call_args = mock_base_client.request.call_args
        assert call_args[1]["params"]["start"] == 100
        assert call_args[1]["params"]["limit"] == 100
        assert has_more is True
