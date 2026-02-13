import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from mcp.server.fastmcp import Context
from pipedrive.api.features.pipelines.tools.pipeline_list_tool import list_pipelines_from_pipedrive
from pipedrive.api.features.pipelines.tools.pipeline_get_tool import get_pipeline_from_pipedrive
from pipedrive.api.features.pipelines.tools.stage_list_tool import list_stages_from_pipedrive
from pipedrive.api.features.pipelines.tools.stage_get_tool import get_stage_from_pipedrive
from pipedrive.api.pipedrive_api_error import PipedriveAPIError


@pytest.fixture
def mock_pipedrive_client():
    pipelines_client = AsyncMock()

    pipelines_client.list_pipelines.return_value = (
        [
            {"id": 1, "name": "Sales Pipeline", "order_nr": 1},
            {"id": 2, "name": "Support Pipeline", "order_nr": 2},
        ],
        None,
    )

    pipelines_client.get_pipeline.return_value = {
        "id": 1,
        "name": "Sales Pipeline",
        "order_nr": 1,
        "is_deal_probability_enabled": True,
    }

    pipelines_client.list_stages.return_value = (
        [
            {"id": 1, "name": "Qualified", "pipeline_id": 1, "order_nr": 1},
            {"id": 2, "name": "Proposal", "pipeline_id": 1, "order_nr": 2},
        ],
        None,
    )

    pipelines_client.get_stage.return_value = {
        "id": 3,
        "name": "Negotiation",
        "pipeline_id": 1,
        "order_nr": 3,
        "deal_probability": 75,
    }

    client = MagicMock()
    client.pipelines = pipelines_client
    return client


class TestListPipelinesTool:
    @pytest.mark.asyncio
    async def test_list_pipelines_success(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await list_pipelines_from_pipedrive(ctx=mock_ctx)
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert len(result_data["data"]["pipelines"]) == 2
        assert result_data["data"]["pipelines"][0]["name"] == "Sales Pipeline"
        assert result_data["data"]["next_cursor"] is None

    @pytest.mark.asyncio
    async def test_list_pipelines_with_sorting(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await list_pipelines_from_pipedrive(
            ctx=mock_ctx, sort_by="id", sort_direction="desc"
        )
        result_data = json.loads(result)

        assert result_data["success"] is True
        mock_pipedrive_client.pipelines.list_pipelines.assert_called_once_with(
            limit=100, cursor=None, sort_by="id", sort_direction="desc"
        )

    @pytest.mark.asyncio
    async def test_list_pipelines_invalid_sort_by(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await list_pipelines_from_pipedrive(ctx=mock_ctx, sort_by="invalid")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "sort_by" in result_data["error"]

    @pytest.mark.asyncio
    async def test_list_pipelines_invalid_sort_direction(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await list_pipelines_from_pipedrive(ctx=mock_ctx, sort_direction="up")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "sort_direction" in result_data["error"]

    @pytest.mark.asyncio
    async def test_list_pipelines_api_error(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.pipelines.list_pipelines.side_effect = PipedriveAPIError(
            message="API Error", status_code=500, response_data={"error": "Server error"}
        )

        result = await list_pipelines_from_pipedrive(ctx=mock_ctx)
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "API Error" in result_data["error"]


class TestGetPipelineTool:
    @pytest.mark.asyncio
    async def test_get_pipeline_success(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await get_pipeline_from_pipedrive(ctx=mock_ctx, id_str="1")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"]["id"] == 1
        assert result_data["data"]["name"] == "Sales Pipeline"
        mock_pipedrive_client.pipelines.get_pipeline.assert_called_once_with(pipeline_id=1)

    @pytest.mark.asyncio
    async def test_get_pipeline_invalid_id(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await get_pipeline_from_pipedrive(ctx=mock_ctx, id_str="abc")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "pipeline_id" in result_data["error"]

    @pytest.mark.asyncio
    async def test_get_pipeline_empty_id(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await get_pipeline_from_pipedrive(ctx=mock_ctx, id_str="")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "required" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_get_pipeline_not_found(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.pipelines.get_pipeline.return_value = {}

        result = await get_pipeline_from_pipedrive(ctx=mock_ctx, id_str="999")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "not found" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_get_pipeline_api_error(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.pipelines.get_pipeline.side_effect = PipedriveAPIError(
            message="Not found", status_code=404, response_data={"error": "Pipeline not found"}
        )

        result = await get_pipeline_from_pipedrive(ctx=mock_ctx, id_str="1")
        result_data = json.loads(result)

        assert result_data["success"] is False


class TestListStagesTool:
    @pytest.mark.asyncio
    async def test_list_stages_success(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await list_stages_from_pipedrive(ctx=mock_ctx, pipeline_id_str="1")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert len(result_data["data"]["stages"]) == 2
        assert result_data["data"]["stages"][0]["name"] == "Qualified"
        mock_pipedrive_client.pipelines.list_stages.assert_called_once_with(
            pipeline_id=1, limit=100, cursor=None, sort_by=None, sort_direction=None
        )

    @pytest.mark.asyncio
    async def test_list_stages_all_pipelines(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await list_stages_from_pipedrive(ctx=mock_ctx)
        result_data = json.loads(result)

        assert result_data["success"] is True
        mock_pipedrive_client.pipelines.list_stages.assert_called_once_with(
            pipeline_id=None, limit=100, cursor=None, sort_by=None, sort_direction=None
        )

    @pytest.mark.asyncio
    async def test_list_stages_invalid_pipeline_id(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await list_stages_from_pipedrive(ctx=mock_ctx, pipeline_id_str="abc")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "pipeline_id" in result_data["error"]

    @pytest.mark.asyncio
    async def test_list_stages_invalid_sort_by(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await list_stages_from_pipedrive(ctx=mock_ctx, sort_by="invalid")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "sort_by" in result_data["error"]

    @pytest.mark.asyncio
    async def test_list_stages_api_error(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.pipelines.list_stages.side_effect = PipedriveAPIError(
            message="API Error", status_code=500, response_data={"error": "Server error"}
        )

        result = await list_stages_from_pipedrive(ctx=mock_ctx)
        result_data = json.loads(result)

        assert result_data["success"] is False


class TestGetStageTool:
    @pytest.mark.asyncio
    async def test_get_stage_success(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await get_stage_from_pipedrive(ctx=mock_ctx, id_str="3")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"]["id"] == 3
        assert result_data["data"]["name"] == "Negotiation"
        mock_pipedrive_client.pipelines.get_stage.assert_called_once_with(stage_id=3)

    @pytest.mark.asyncio
    async def test_get_stage_invalid_id(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await get_stage_from_pipedrive(ctx=mock_ctx, id_str="abc")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "stage_id" in result_data["error"]

    @pytest.mark.asyncio
    async def test_get_stage_empty_id(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        result = await get_stage_from_pipedrive(ctx=mock_ctx, id_str="")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "required" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_get_stage_not_found(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.pipelines.get_stage.return_value = {}

        result = await get_stage_from_pipedrive(ctx=mock_ctx, id_str="999")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "not found" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_get_stage_api_error(self, mock_pipedrive_client):
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.request_context.lifespan_context.pipedrive_client = mock_pipedrive_client

        mock_pipedrive_client.pipelines.get_stage.side_effect = PipedriveAPIError(
            message="Not found", status_code=404, response_data={"error": "Stage not found"}
        )

        result = await get_stage_from_pipedrive(ctx=mock_ctx, id_str="3")
        result_data = json.loads(result)

        assert result_data["success"] is False
