from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from pipedrive.api.features.tool_decorator import tool


@tool("users")
async def get_user_from_pipedrive(
    ctx: Context,
    id_str: str,
) -> str:
    """Gets the details of a specific user from Pipedrive CRM.

    This tool retrieves information about a Pipedrive user by their ID.
    Useful for resolving user IDs (e.g. owner_id on deals, persons, etc.)
    to user names and email addresses.

    Format requirements:
        - id_str: User ID as a string (required, will be converted to integer).
          Example: "123"

    Example:
        get_user_from_pipedrive(
            id_str="123"
        )

    Args:
        ctx: Context object containing the Pipedrive client
        id_str: ID of the user to retrieve (required)

    Returns:
        JSON string containing success status and user data or error message.
        When successful, the response includes fields such as:
        - id: User's unique identifier
        - name: User's full name
        - email: User's email address
        - active_flag: Whether the user is active
        - role_id: ID of the user's role
        - icon_url: URL of the user's avatar
    """
    logger.debug(
        f"Tool 'get_user_from_pipedrive' ENTERED with raw args: id_str='{id_str}'"
    )

    if not id_str:
        error_msg = "User ID is required"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    user_id, id_error = convert_id_string(id_str, "user_id")
    if id_error:
        logger.error(id_error)
        return format_tool_response(False, error_message=id_error)

    try:
        user_data = await pd_mcp_ctx.pipedrive_client.users.get_user(
            user_id=user_id,
        )

        if not user_data:
            logger.warning(f"User with ID {user_id} not found")
            return format_tool_response(
                False, error_message=f"User with ID {user_id} not found"
            )

        logger.info(f"Successfully retrieved user with ID: {user_id}")
        return format_tool_response(True, data=user_data)

    except PipedriveAPIError as e:
        logger.error(
            f"PipedriveAPIError in tool 'get_user_from_pipedrive' for ID {user_id}: {str(e)} - Response Data: {e.response_data}"
        )
        return format_tool_response(False, error_message=str(e), data=e.response_data)
    except Exception as e:
        logger.exception(
            f"Unexpected error in tool 'get_user_from_pipedrive' for ID {user_id}: {str(e)}"
        )
        return format_tool_response(
            False, error_message=f"An unexpected error occurred: {str(e)}"
        )
