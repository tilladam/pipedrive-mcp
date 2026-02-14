"""Tests for list_notes_in_pipedrive tool."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from pipedrive.api.features.notes.tools.note_list_tool import list_notes_in_pipedrive
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
    notes_client.list_notes = AsyncMock()

    pipedrive_client = MagicMock()
    pipedrive_client.notes = notes_client

    ctx = MagicMock()
    ctx.request_context.lifespan_context.pipedrive_client = pipedrive_client

    return ctx


class TestListNotesTool:
    """Tests for list_notes_in_pipedrive tool."""

    @pytest.mark.asyncio
    async def test_list_notes_default(self, mock_context):
        """Test listing notes with default parameters."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.return_value = (
            [
                {"id": 1, "content": "Note 1"},
                {"id": 2, "content": "Note 2"}
            ],
            False
        )

        result = await list_notes_in_pipedrive(mock_context)

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["count"] == 2
        assert response["data"]["has_more"] is False
        assert len(response["data"]["notes"]) == 2

        mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_notes_with_deal_filter(self, mock_context):
        """Test listing notes filtered by deal."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.return_value = (
            [{"id": 1, "content": "Deal note", "deal_id": 456}],
            False
        )

        result = await list_notes_in_pipedrive(mock_context, deal_id="456")

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["count"] == 1

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.call_args.kwargs
        assert call_kwargs["deal_id"] == 456

    @pytest.mark.asyncio
    async def test_list_notes_with_pagination(self, mock_context):
        """Test listing notes with pagination."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.return_value = (
            [{"id": i} for i in range(50)],
            True
        )

        result = await list_notes_in_pipedrive(
            mock_context,
            start=50,
            limit=50
        )

        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["count"] == 50
        assert response["data"]["has_more"] is True
        assert response["data"]["pagination"]["start"] == 50
        assert response["data"]["pagination"]["limit"] == 50

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.call_args.kwargs
        assert call_kwargs["start"] == 50
        assert call_kwargs["limit"] == 50

    @pytest.mark.asyncio
    async def test_list_notes_with_sort(self, mock_context):
        """Test listing notes with sorting."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.return_value = (
            [{"id": 1}, {"id": 2}],
            False
        )

        result = await list_notes_in_pipedrive(
            mock_context,
            sort="-update_time"
        )

        response = json.loads(result)
        assert response["success"] is True

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.call_args.kwargs
        assert call_kwargs["sort"] == "-update_time"

    @pytest.mark.asyncio
    async def test_list_notes_with_date_range(self, mock_context):
        """Test listing notes with date range filter."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.return_value = (
            [{"id": 1}],
            False
        )

        result = await list_notes_in_pipedrive(
            mock_context,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        response = json.loads(result)
        assert response["success"] is True

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.call_args.kwargs
        assert call_kwargs["start_date"] == "2024-01-01"
        assert call_kwargs["end_date"] == "2024-12-31"

    @pytest.mark.asyncio
    async def test_list_notes_pinned_only(self, mock_context):
        """Test listing only pinned notes."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.return_value = (
            [{"id": 1, "deal_id": 456, "pinned_to_deal_flag": 1}],
            False
        )

        result = await list_notes_in_pipedrive(
            mock_context,
            deal_id="456",
            pinned_only=True
        )

        response = json.loads(result)
        assert response["success"] is True

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.call_args.kwargs
        assert call_kwargs["pinned_to_deal_flag"] == 1

    @pytest.mark.asyncio
    async def test_list_notes_invalid_start(self, mock_context):
        """Test error for negative start parameter."""
        result = await list_notes_in_pipedrive(mock_context, start=-1)

        response = json.loads(result)
        assert response["success"] is False
        assert "start must be non-negative" in response["error"]

    @pytest.mark.asyncio
    async def test_list_notes_invalid_limit(self, mock_context):
        """Test error for invalid limit parameter."""
        result = await list_notes_in_pipedrive(mock_context, limit=0)

        response = json.loads(result)
        assert response["success"] is False
        assert "limit must be between 1 and 500" in response["error"]

        result = await list_notes_in_pipedrive(mock_context, limit=1000)

        response = json.loads(result)
        assert response["success"] is False
        assert "limit must be between 1 and 500" in response["error"]

    @pytest.mark.asyncio
    async def test_list_notes_invalid_sort(self, mock_context):
        """Test error for invalid sort field."""
        result = await list_notes_in_pipedrive(mock_context, sort="invalid_field")

        response = json.loads(result)
        assert response["success"] is False
        assert "Invalid sort field" in response["error"]

    @pytest.mark.asyncio
    async def test_list_notes_api_error(self, mock_context):
        """Test handling of API errors."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.side_effect = PipedriveAPIError(
            "API Error", status_code=500
        )

        result = await list_notes_in_pipedrive(mock_context)

        response = json.loads(result)
        assert response["success"] is False
        assert "Pipedrive API error" in response["error"]

    @pytest.mark.asyncio
    async def test_list_notes_multiple_filters(self, mock_context):
        """Test listing notes with multiple filters."""
        mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.return_value = (
            [{"id": 1}],
            False
        )

        result = await list_notes_in_pipedrive(
            mock_context,
            deal_id="456",
            user_id="5",
            pinned_only=True,
            start=0,
            limit=25,
            sort="add_time"
        )

        response = json.loads(result)
        assert response["success"] is True

        call_kwargs = mock_context.request_context.lifespan_context.pipedrive_client.notes.list_notes.call_args.kwargs
        assert call_kwargs["deal_id"] == 456
        assert call_kwargs["user_id"] == 5
        assert call_kwargs["pinned_to_deal_flag"] == 1
        assert call_kwargs["limit"] == 25
        assert call_kwargs["sort"] == "add_time"
