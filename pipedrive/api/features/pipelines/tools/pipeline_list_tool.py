from typing import Optional

from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from pipedrive.api.features.tool_decorator import tool


@tool("pipelines")
async def list_pipelines_from_pipedrive(
    ctx: Context,
    limit: Optional[str] = "100",
    cursor: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = None,
) -> str:
    """Lists all pipelines from the Pipedrive CRM.

    Retrieves a paginated list of all pipelines configured in Pipedrive.
    Pipelines represent the sales processes that deals move through.

    Format requirements:
        - limit: Number of results per page as a string, max "500" (default: "100")
        - cursor: Pagination cursor from a previous response's next_cursor field
        - sort_by: Field to sort by - "id", "update_time", or "add_time"
        - sort_direction: Sort direction - "asc" or "desc"

    Example:
        list_pipelines_from_pipedrive()

    Args:
        ctx: Context object containing the Pipedrive client
        limit: Maximum number of pipelines to return per page (default "100")
        cursor: Pagination cursor for fetching the next page
        sort_by: Field to sort results by
        sort_direction: Direction to sort results

    Returns:
        JSON string containing success status and a list of pipelines with fields:
        id, name, order_nr, is_deal_probability_enabled, add_time, update_time.
        Includes next_cursor for pagination if more results exist.
    """
    logger.debug(
        f"Tool 'list_pipelines_from_pipedrive' ENTERED with raw args: "
        f"limit='{limit}', cursor='{cursor}', sort_by='{sort_by}', sort_direction='{sort_direction}'"
    )

    # Sanitize
    limit = None if limit == "" else limit
    cursor = None if cursor == "" else cursor
    sort_by = None if sort_by == "" else sort_by
    sort_direction = None if sort_direction == "" else sort_direction

    # Convert limit
    limit_int = 100
    if limit is not None:
        limit_id, limit_error = convert_id_string(limit, "limit")
        if limit_error:
            return format_tool_response(False, error_message=limit_error)
        limit_int = min(limit_id, 500)

    # Validate sort_by
    if sort_by and sort_by not in ("id", "update_time", "add_time"):
        return format_tool_response(
            False,
            error_message=f"Invalid sort_by value: '{sort_by}'. Must be one of: id, update_time, add_time",
        )

    # Validate sort_direction
    if sort_direction and sort_direction not in ("asc", "desc"):
        return format_tool_response(
            False,
            error_message=f"Invalid sort_direction: '{sort_direction}'. Must be 'asc' or 'desc'",
        )

    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        pipelines, next_cursor = await client.pipelines.list_pipelines(
            limit=limit_int,
            cursor=cursor,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

        result = {"pipelines": pipelines, "next_cursor": next_cursor}
        logger.info(f"Successfully listed {len(pipelines)} pipelines")
        return format_tool_response(True, data=result)

    except PipedriveAPIError as e:
        logger.error(f"PipedriveAPIError in 'list_pipelines_from_pipedrive': {str(e)}")
        return format_tool_response(False, error_message=str(e), data=e.response_data)
    except Exception as e:
        logger.exception(f"Unexpected error in 'list_pipelines_from_pipedrive': {str(e)}")
        return format_tool_response(False, error_message=f"An unexpected error occurred: {str(e)}")
