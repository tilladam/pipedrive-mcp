"""Tool for updating a comment on a note in Pipedrive."""
from mcp.server.fastmcp import Context
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from log_config import logger


@tool("notes")
async def update_comment_on_note_in_pipedrive(
    ctx: Context,
    note_id: str,
    comment_id: str,
    content: str,
) -> str:
    """Update a comment on a note in Pipedrive.

    Updates the content of an existing comment on a note.

    Format requirements:
    - note_id: Numeric string or integer (e.g., "123")
    - comment_id: Numeric string or integer (e.g., "456")
    - content: Non-empty text string

    Usage example:
    update_comment_on_note_in_pipedrive(
        note_id="123",
        comment_id="456",
        content="Updated comment text."
    )

    Args:
        note_id: The ID of the parent note

        comment_id: The ID of the comment to update

        content: The new text content of the comment

    Returns:
        JSON string with success status and updated comment data, or error message
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

        if not content or not content.strip():
            return format_tool_response(False, error_message="Comment content cannot be empty")

        result = await client.notes.comments.update_comment(
            note_id=note_id_int,
            comment_id=comment_id_int,
            content=content,
        )

        return format_tool_response(success=True, data=result)

    except PipedriveAPIError as e:
        error_msg = f"Pipedrive API error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error updating comment: {str(e)}"
        logger.exception(error_msg)
        return format_tool_response(False, error_message=error_msg)
