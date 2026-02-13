from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from pipedrive.api.features.tool_decorator import tool


@tool("deals")
async def create_deal_label_in_pipedrive(
    ctx: Context,
    label: str,
) -> str:
    """Creates a new deal label in Pipedrive CRM.

    Adds a new label option that can be applied to deals. After creation,
    the returned ID can be used to tag deals via the label field when
    creating or updating deals.

    Format requirements:
        - label: The display name for the new label (1-255 characters, required).
          Example: "Enterprise"

    Example:
        create_deal_label_in_pipedrive(label="Enterprise")

    Args:
        ctx: Context object containing the Pipedrive client
        label: Display name for the new deal label (required)

    Returns:
        JSON string containing success status and the created label with id and label fields.
    """
    logger.debug(
        f"Tool 'create_deal_label_in_pipedrive' ENTERED with raw args: label='{label}'"
    )

    if not label or not label.strip():
        return format_tool_response(False, error_message="Label name is required and cannot be empty")

    if len(label) > 255:
        return format_tool_response(
            False, error_message="Label name must be 255 characters or fewer"
        )

    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        created_label = await client.deals.create_deal_label(label=label.strip())

        if not created_label:
            return format_tool_response(
                False, error_message="Label was not created — empty response from API"
            )

        logger.info(f"Successfully created deal label '{label}' with ID: {created_label.get('id')}")
        return format_tool_response(True, data=created_label)

    except PipedriveAPIError as e:
        logger.error(
            f"PipedriveAPIError in 'create_deal_label_in_pipedrive': {str(e)}"
        )
        return format_tool_response(False, error_message=str(e), data=e.response_data)
    except ValueError as e:
        logger.error(f"Validation error in 'create_deal_label_in_pipedrive': {str(e)}")
        return format_tool_response(False, error_message=str(e))
    except Exception as e:
        logger.exception(
            f"Unexpected error in 'create_deal_label_in_pipedrive': {str(e)}"
        )
        return format_tool_response(False, error_message=f"An unexpected error occurred: {str(e)}")
