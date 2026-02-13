from typing import Any, Dict, List, Optional, Tuple

from log_config import logger
from pipedrive.api.base_client import BaseClient


class PipelineClient:
    """Client for Pipedrive Pipelines and Stages API endpoints (v2)"""

    def __init__(self, base_client: BaseClient):
        self.base_client = base_client

    async def list_pipelines(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        List all pipelines.

        Args:
            limit: Max items per page (max 500)
            cursor: Pagination cursor
            sort_by: Field to sort by (id, update_time, add_time)
            sort_direction: Sort direction (asc, desc)

        Returns:
            Tuple of (list of pipeline dicts, next_cursor or None)
        """
        logger.info("PipelineClient: Listing pipelines")

        params: Dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if sort_by:
            params["sort_by"] = sort_by
        if sort_direction:
            params["sort_direction"] = sort_direction

        response_data = await self.base_client.request(
            "GET", "/pipelines", query_params=params
        )

        pipelines = response_data.get("data", []) or []
        next_cursor = (
            response_data.get("additional_data", {}).get("next_cursor")
        )

        logger.info(f"PipelineClient: Retrieved {len(pipelines)} pipelines")
        return pipelines, next_cursor

    async def get_pipeline(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Get a single pipeline by ID.

        Args:
            pipeline_id: The ID of the pipeline

        Returns:
            Dictionary containing pipeline data
        """
        logger.info(f"PipelineClient: Fetching pipeline with ID {pipeline_id}")

        response_data = await self.base_client.request(
            "GET", f"/pipelines/{pipeline_id}"
        )

        pipeline_data = response_data.get("data", {})
        logger.info(f"PipelineClient: Successfully retrieved pipeline {pipeline_id}")
        return pipeline_data

    async def list_stages(
        self,
        pipeline_id: Optional[int] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        List stages, optionally filtered by pipeline.

        Args:
            pipeline_id: Filter stages for a specific pipeline
            limit: Max items per page (max 500)
            cursor: Pagination cursor
            sort_by: Field to sort by (id, update_time, add_time, order_nr)
            sort_direction: Sort direction (asc, desc)

        Returns:
            Tuple of (list of stage dicts, next_cursor or None)
        """
        logger.info(
            f"PipelineClient: Listing stages"
            + (f" for pipeline {pipeline_id}" if pipeline_id else "")
        )

        params: Dict[str, Any] = {"limit": limit}
        if pipeline_id:
            params["pipeline_id"] = pipeline_id
        if cursor:
            params["cursor"] = cursor
        if sort_by:
            params["sort_by"] = sort_by
        if sort_direction:
            params["sort_direction"] = sort_direction

        response_data = await self.base_client.request(
            "GET", "/stages", query_params=params
        )

        stages = response_data.get("data", []) or []
        next_cursor = (
            response_data.get("additional_data", {}).get("next_cursor")
        )

        logger.info(f"PipelineClient: Retrieved {len(stages)} stages")
        return stages, next_cursor

    async def get_stage(self, stage_id: int) -> Dict[str, Any]:
        """
        Get a single stage by ID.

        Args:
            stage_id: The ID of the stage

        Returns:
            Dictionary containing stage data
        """
        logger.info(f"PipelineClient: Fetching stage with ID {stage_id}")

        response_data = await self.base_client.request(
            "GET", f"/stages/{stage_id}"
        )

        stage_data = response_data.get("data", {})
        logger.info(f"PipelineClient: Successfully retrieved stage {stage_id}")
        return stage_data
