"""Tool for adding comments to notes in Pipedrive."""
from mcp.server.fastmcp import Context
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from log_config import logger


@tool("notes")
async def add_comment_to_note_in_pipedrive(
    ctx: Context,
    note_id: str,
    content: str,
) -> str:
    """Add a comment to a note in Pipedrive.

    Creates a new threaded comment on an existing note. Comments are used
    for collaborative discussions on note content.

    Format requirements:
    - note_id: Numeric string or integer (e.g., "123")
    - content: Non-empty text string

    Usage example:
    add_comment_to_note_in_pipedrive(
        note_id="123",
        content="Great observation, let's follow up on this next week."
    )

    Args:
        note_id: The ID of the note to comment on

        content: The text content of the comment

    Returns:
        JSON string with success status and created comment data, or error message
    """
    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        note_id_int, error = convert_id_string(note_id, "note_id")
        if error:
            return format_tool_response(False, error_message=error)

        if not content or not content.strip():
            return format_tool_response(False, error_message="Comment content cannot be empty")

        result = await client.notes.comments.add_comment(
            note_id=note_id_int,
            content=content,
        )

        return format_tool_response(success=True, data=result)

    except PipedriveAPIError as e:
        error_msg = f"Pipedrive API error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error adding comment: {str(e)}"
        logger.exception(error_msg)
        return format_tool_response(False, error_message=error_msg)
