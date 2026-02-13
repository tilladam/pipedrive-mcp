import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from mcp.server.fastmcp import Context
from pipedrive.api.features.deals.tools.deal_label_list_tool import list_deal_labels_from_pipedrive
from pipedrive.api.features.deals.tools.deal_label_create_tool import create_deal_label_in_pipedrive
from pipedrive.api.pipedrive_api_error import PipedriveAPIError


@pytest.fixture
def mock_pipedrive_client():
    deals_client = AsyncMock()

    deals_client.get_deal_labels.return_value = [
        {"id": 1, "label": "Hot"},
        {"id": 2, "label": "Warm"},
        {"id": 3, "label": "Cold"},
    ]

    deals_client.create_deal_label.return_value = {
        "id": 4,
        "label": "Enterprise",
    }

    client = MagicMock()
    client.deals = deals_client
    return client


class TestListDealLabelsTool:
    @pytest.mark.asyncio
    async def test_list_labels_success(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await list_deal_labels_from_pipedrive(ctx=mock_ctx)
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert len(result_data["data"]) == 3
        assert result_data["data"][0]["label"] == "Hot"
        assert result_data["data"][2]["id"] == 3

    @pytest.mark.asyncio
    async def test_list_labels_empty(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.deals.get_deal_labels.return_value = []

        result = await list_deal_labels_from_pipedrive(ctx=mock_ctx)
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"] == []

    @pytest.mark.asyncio
    async def test_list_labels_api_error(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.deals.get_deal_labels.side_effect = PipedriveAPIError(
            message="API Error", status_code=500, response_data={"error": "Server error"}
        )

        result = await list_deal_labels_from_pipedrive(ctx=mock_ctx)
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "API Error" in result_data["error"]


class TestCreateDealLabelTool:
    @pytest.mark.asyncio
    async def test_create_label_success(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await create_deal_label_in_pipedrive(ctx=mock_ctx, label="Enterprise")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"]["id"] == 4
        assert result_data["data"]["label"] == "Enterprise"
        mock_pipedrive_client.deals.create_deal_label.assert_called_once_with(label="Enterprise")

    @pytest.mark.asyncio
    async def test_create_label_empty_name(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await create_deal_label_in_pipedrive(ctx=mock_ctx, label="")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "required" in result_data["error"].lower()
        mock_pipedrive_client.deals.create_deal_label.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_label_too_long(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await create_deal_label_in_pipedrive(ctx=mock_ctx, label="x" * 256)
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "255" in result_data["error"]
        mock_pipedrive_client.deals.create_deal_label.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_label_strips_whitespace(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await create_deal_label_in_pipedrive(ctx=mock_ctx, label="  Enterprise  ")
        result_data = json.loads(result)

        assert result_data["success"] is True
        mock_pipedrive_client.deals.create_deal_label.assert_called_once_with(label="Enterprise")

    @pytest.mark.asyncio
    async def test_create_label_api_error(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.deals.create_deal_label.side_effect = PipedriveAPIError(
            message="Forbidden", status_code=403, response_data={"error": "Insufficient permissions"}
        )

        result = await create_deal_label_in_pipedrive(ctx=mock_ctx, label="Enterprise")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "Forbidden" in result_data["error"]

    @pytest.mark.asyncio
    async def test_create_label_empty_response(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.deals.create_deal_label.return_value = {}

        result = await create_deal_label_in_pipedrive(ctx=mock_ctx, label="Enterprise")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "empty response" in result_data["error"].lower()
