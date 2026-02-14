"""Tool for deleting a comment on a note from Pipedrive."""
from mcp.server.fastmcp import Context
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from log_config import logger


@tool("notes")
async def delete_comment_on_note_from_pipedrive(
    ctx: Context,
    note_id: str,
    comment_id: str,
) -> str:
    """Delete a comment on a note from Pipedrive.

    Permanently removes a comment from a note. This action cannot be undone.

    Format requirements:
    - note_id: Numeric string or integer (e.g., "123")
    - comment_id: Numeric string or integer (e.g., "456")

    Usage example:
    delete_comment_on_note_from_pipedrive(note_id="123", comment_id="456")

    Args:
        note_id: The ID of the parent note

        comment_id: The ID of the comment to delete

    Returns:
        JSON string with success status and deletion confirmation, or error message
    """
    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        note_id_int, error = convert_id_string(note_id, "note_id")
        if error:
            return format_tool_response(False, error_message=error)

        comment_id_int, error = convert_id_string(comment_id, "comment_id")
        if error:
            return format_tool_response(False, error_message=error)

        result = await client.notes.comments.delete_comment(
            note_id=note_id_int,
            comment_id=comment_id_int,
        )

        return format_tool_response(success=True, data=result)

    except PipedriveAPIError as e:
        error_msg = f"Pipedrive API error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error deleting comment: {str(e)}"
        logger.exception(error_msg)
        return format_tool_response(False, error_message=error_msg)
