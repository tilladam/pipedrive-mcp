from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from pipedrive.api.features.tool_decorator import tool


@tool("deals")
async def list_deal_labels_from_pipedrive(ctx: Context) -> str:
    """Lists all available deal labels from Pipedrive CRM.

    Retrieves the complete list of deal labels configured in your Pipedrive account.
    Deal labels are used to categorize and visually distinguish deals. Each label has
    a numeric ID that can be used when creating or updating deals via the label field.

    Format requirements:
        No parameters required.

    Example:
        list_deal_labels_from_pipedrive()

    Args:
        ctx: Context object containing the Pipedrive client

    Returns:
        JSON string containing success status and a list of deal labels.
        Each label contains id (integer) and label (display name).
    """
    logger.debug("Tool 'list_deal_labels_from_pipedrive' ENTERED")

    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        labels = await client.deals.get_deal_labels()

        logger.info(f"Successfully retrieved {len(labels)} deal labels")
        return format_tool_response(True, data=labels)

    except PipedriveAPIError as e:
        logger.error(
            f"PipedriveAPIError in 'list_deal_labels_from_pipedrive': {str(e)}"
        )
        return format_tool_response(False, error_message=str(e), data=e.response_data)
    except Exception as e:
        logger.exception(
            f"Unexpected error in 'list_deal_labels_from_pipedrive': {str(e)}"
        )
        return format_tool_response(False, error_message=f"An unexpected error occurred: {str(e)}")
