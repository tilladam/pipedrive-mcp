from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from pipedrive.api.features.tool_decorator import tool


@tool("pipelines")
async def get_stage_from_pipedrive(
    ctx: Context,
    id_str: str,
) -> str:
    """Gets the details of a specific stage from Pipedrive CRM.

    Retrieves a single stage by its ID, including its name, pipeline association,
    deal probability, and deal rot settings.

    Format requirements:
        - id_str: Stage ID as a string (required, will be converted to integer).
          Example: "1"

    Example:
        get_stage_from_pipedrive(id_str="3")

    Args:
        ctx: Context object containing the Pipedrive client
        id_str: ID of the stage to retrieve (required)

    Returns:
        JSON string containing success status and stage data with fields:
        id, name, pipeline_id, order_nr, deal_probability, is_deal_rot_enabled,
        days_to_rotten, add_time, update_time.
    """
    logger.debug(
        f"Tool 'get_stage_from_pipedrive' ENTERED with raw args: id_str='{id_str}'"
    )

    if not id_str:
        return format_tool_response(False, error_message="Stage ID is required")

    stage_id, id_error = convert_id_string(id_str, "stage_id")
    if id_error:
        return format_tool_response(False, error_message=id_error)

    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        stage_data = await client.pipelines.get_stage(stage_id=stage_id)

        if not stage_data:
            return format_tool_response(
                False, error_message=f"Stage with ID {stage_id} not found"
            )

        logger.info(f"Successfully retrieved stage with ID: {stage_id}")
        return format_tool_response(True, data=stage_data)

    except PipedriveAPIError as e:
        logger.error(
            f"PipedriveAPIError in 'get_stage_from_pipedrive' for ID {stage_id}: {str(e)}"
        )
        return format_tool_response(False, error_message=str(e), data=e.response_data)
    except Exception as e:
        logger.exception(
            f"Unexpected error in 'get_stage_from_pipedrive' for ID {stage_id}: {str(e)}"
        )
        return format_tool_response(False, error_message=f"An unexpected error occurred: {str(e)}")
