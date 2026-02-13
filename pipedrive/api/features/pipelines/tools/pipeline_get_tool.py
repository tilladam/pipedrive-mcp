from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from pipedrive.api.features.tool_decorator import tool


@tool("pipelines")
async def get_pipeline_from_pipedrive(
    ctx: Context,
    id_str: str,
) -> str:
    """Gets the details of a specific pipeline from Pipedrive CRM.

    Retrieves a single pipeline by its ID, including its name, ordering,
    and whether deal probability is enabled.

    Format requirements:
        - id_str: Pipeline ID as a string (required, will be converted to integer).
          Example: "1"

    Example:
        get_pipeline_from_pipedrive(id_str="1")

    Args:
        ctx: Context object containing the Pipedrive client
        id_str: ID of the pipeline to retrieve (required)

    Returns:
        JSON string containing success status and pipeline data with fields:
        id, name, order_nr, is_deal_probability_enabled, add_time, update_time.
    """
    logger.debug(
        f"Tool 'get_pipeline_from_pipedrive' ENTERED with raw args: id_str='{id_str}'"
    )

    if not id_str:
        return format_tool_response(False, error_message="Pipeline ID is required")

    pipeline_id, id_error = convert_id_string(id_str, "pipeline_id")
    if id_error:
        return format_tool_response(False, error_message=id_error)

    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        pipeline_data = await client.pipelines.get_pipeline(pipeline_id=pipeline_id)

        if not pipeline_data:
            return format_tool_response(
                False, error_message=f"Pipeline with ID {pipeline_id} not found"
            )

        logger.info(f"Successfully retrieved pipeline with ID: {pipeline_id}")
        return format_tool_response(True, data=pipeline_data)

    except PipedriveAPIError as e:
        logger.error(
            f"PipedriveAPIError in 'get_pipeline_from_pipedrive' for ID {pipeline_id}: {str(e)}"
        )
        return format_tool_response(False, error_message=str(e), data=e.response_data)
    except Exception as e:
        logger.exception(
            f"Unexpected error in 'get_pipeline_from_pipedrive' for ID {pipeline_id}: {str(e)}"
        )
        return format_tool_response(False, error_message=f"An unexpected error occurred: {str(e)}")
