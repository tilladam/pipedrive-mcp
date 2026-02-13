import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from mcp.server.fastmcp import Context
from pipedrive.api.features.users.tools.user_get_tool import get_user_from_pipedrive
from pipedrive.api.pipedrive_api_error import PipedriveAPIError


@pytest.fixture
def mock_pipedrive_client():
    """Create a mock PipedriveClient for testing"""
    users_client = AsyncMock()

    users_client.get_user.return_value = {
        "id": 42,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "active_flag": True,
        "role_id": 1,
        "icon_url": None,
    }

    client = MagicMock()
    client.users = users_client

    return client


class TestGetUserTool:
    @pytest.mark.asyncio
    async def test_get_user_success(self, mock_pipedrive_client):
        """Test successful user retrieval"""
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await get_user_from_pipedrive(
            ctx=mock_ctx,
            id_str="42",
        )

        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"]["id"] == 42
        assert result_data["data"]["name"] == "Jane Smith"
        assert result_data["data"]["email"] == "jane@example.com"

        mock_pipedrive_client.users.get_user.assert_called_once_with(user_id=42)

    @pytest.mark.asyncio
    async def test_get_user_invalid_id(self, mock_pipedrive_client):
        """Test error handling with invalid ID input"""
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await get_user_from_pipedrive(
            ctx=mock_ctx,
            id_str="not_a_number",
        )

        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "user_id must be a numeric string" in result_data["error"]
        mock_pipedrive_client.users.get_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_empty_id(self, mock_pipedrive_client):
        """Test error handling with empty ID"""
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await get_user_from_pipedrive(
            ctx=mock_ctx,
            id_str="",
        )

        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "User ID is required" in result_data["error"]
        mock_pipedrive_client.users.get_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, mock_pipedrive_client):
        """Test handling when user is not found"""
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.users.get_user.return_value = {}

        result = await get_user_from_pipedrive(
            ctx=mock_ctx,
            id_str="999",
        )

        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "User with ID 999 not found" in result_data["error"]

    @pytest.mark.asyncio
    async def test_get_user_api_error(self, mock_pipedrive_client):
        """Test handling of API errors"""
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        api_error = PipedriveAPIError(
            message="API Error",
            status_code=404,
            error_info="User not found",
            response_data={"error": "The requested user does not exist"},
        )
        mock_pipedrive_client.users.get_user.side_effect = api_error

        result = await get_user_from_pipedrive(
            ctx=mock_ctx,
            id_str="42",
        )

        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "API Error" in result_data["error"]
        assert result_data["data"]["error"] == "The requested user does not exist"
