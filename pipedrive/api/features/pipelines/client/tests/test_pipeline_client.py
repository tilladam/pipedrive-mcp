import pytest
from unittest.mock import AsyncMock

from pipedrive.api.features.pipelines.client.pipeline_client import PipelineClient


@pytest.mark.asyncio
class TestPipelineClient:
    """Tests for the PipelineClient"""

    def setup_method(self):
        self.base_client = AsyncMock()
        self.client = PipelineClient(self.base_client)

    async def test_list_pipelines(self):
        self.base_client.request.return_value = {
            "success": True,
            "data": [
                {"id": 1, "name": "Sales Pipeline"},
                {"id": 2, "name": "Support Pipeline"},
            ],
            "additional_data": {"next_cursor": "abc123"},
        }

        pipelines, next_cursor = await self.client.list_pipelines(limit=50)

        self.base_client.request.assert_called_once_with(
            "GET", "/pipelines", query_params={"limit": 50}
        )
        assert len(pipelines) == 2
        assert pipelines[0]["name"] == "Sales Pipeline"
        assert next_cursor == "abc123"

    async def test_list_pipelines_with_sorting(self):
        self.base_client.request.return_value = {
            "success": True,
            "data": [{"id": 2, "name": "B"}, {"id": 1, "name": "A"}],
            "additional_data": {},
        }

        pipelines, next_cursor = await self.client.list_pipelines(
            limit=100, sort_by="id", sort_direction="desc"
        )

        self.base_client.request.assert_called_once_with(
            "GET",
            "/pipelines",
            query_params={"limit": 100, "sort_by": "id", "sort_direction": "desc"},
        )
        assert len(pipelines) == 2
        assert next_cursor is None

    async def test_list_pipelines_empty(self):
        self.base_client.request.return_value = {
            "success": True,
            "data": None,
            "additional_data": {},
        }

        pipelines, next_cursor = await self.client.list_pipelines()

        assert pipelines == []
        assert next_cursor is None

    async def test_get_pipeline(self):
        self.base_client.request.return_value = {
            "success": True,
            "data": {
                "id": 1,
                "name": "Sales Pipeline",
                "order_nr": 1,
                "is_deal_probability_enabled": True,
            },
        }

        result = await self.client.get_pipeline(pipeline_id=1)

        self.base_client.request.assert_called_once_with(
            "GET", "/pipelines/1"
        )
        assert result["id"] == 1
        assert result["name"] == "Sales Pipeline"

    async def test_list_stages(self):
        self.base_client.request.return_value = {
            "success": True,
            "data": [
                {"id": 1, "name": "Qualified", "pipeline_id": 1, "order_nr": 1},
                {"id": 2, "name": "Proposal", "pipeline_id": 1, "order_nr": 2},
            ],
            "additional_data": {"next_cursor": "def456"},
        }

        stages, next_cursor = await self.client.list_stages(pipeline_id=1)

        self.base_client.request.assert_called_once_with(
            "GET",
            "/stages",
            query_params={"limit": 100, "pipeline_id": 1},
        )
        assert len(stages) == 2
        assert stages[0]["name"] == "Qualified"
        assert next_cursor == "def456"

    async def test_list_stages_all_pipelines(self):
        self.base_client.request.return_value = {
            "success": True,
            "data": [
                {"id": 1, "name": "Stage A", "pipeline_id": 1},
                {"id": 5, "name": "Stage B", "pipeline_id": 2},
            ],
            "additional_data": {},
        }

        stages, next_cursor = await self.client.list_stages()

        self.base_client.request.assert_called_once_with(
            "GET", "/stages", query_params={"limit": 100}
        )
        assert len(stages) == 2

    async def test_list_stages_with_sorting(self):
        self.base_client.request.return_value = {
            "success": True,
            "data": [{"id": 1, "name": "First"}],
            "additional_data": {},
        }

        stages, _ = await self.client.list_stages(
            pipeline_id=1, sort_by="order_nr", sort_direction="asc"
        )

        self.base_client.request.assert_called_once_with(
            "GET",
            "/stages",
            query_params={
                "limit": 100,
                "pipeline_id": 1,
                "sort_by": "order_nr",
                "sort_direction": "asc",
            },
        )

    async def test_get_stage(self):
        self.base_client.request.return_value = {
            "success": True,
            "data": {
                "id": 3,
                "name": "Negotiation",
                "pipeline_id": 1,
                "order_nr": 3,
                "deal_probability": 75,
                "is_deal_rot_enabled": False,
            },
        }

        result = await self.client.get_stage(stage_id=3)

        self.base_client.request.assert_called_once_with(
            "GET", "/stages/3"
        )
        assert result["id"] == 3
        assert result["name"] == "Negotiation"
        assert result["pipeline_id"] == 1
