"""Tool for deleting notes from Pipedrive."""
from mcp.server.fastmcp import Context
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from log_config import logger


@tool("notes")
async def delete_note_from_pipedrive(ctx: Context, note_id: str) -> str:
    """Delete a note from Pipedrive.

    Permanently removes a note from Pipedrive. This action cannot be undone.

    Format requirements:
    - note_id: Numeric string or integer (e.g., "123")

    Usage example:
    delete_note_from_pipedrive(note_id="123")

    Args:
        note_id: The ID of the note to delete

    Returns:
        JSON string with success status and deletion confirmation, or error message
    """
    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        # Convert note_id to integer
        note_id_int, error = convert_id_string(note_id, "note_id")
        if error:
            return format_tool_response(False, error_message=error)

        # Delete the note
        result = await client.notes.delete_note(note_id_int)

        return format_tool_response(
            success=True,
            data=result
        )

    except PipedriveAPIError as e:
        error_msg = f"Pipedrive API error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error deleting note: {str(e)}"
        logger.exception(error_msg)
        return format_tool_response(False, error_message=error_msg)
