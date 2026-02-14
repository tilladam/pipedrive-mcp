"""Tool for retrieving a note from Pipedrive."""
from mcp.server.fastmcp import Context
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from log_config import logger


@tool("notes")
async def get_note_from_pipedrive(ctx: Context, note_id: str) -> str:
    """Retrieve a single note from Pipedrive by ID.

    Fetches the complete details of a specific note including its content,
    attachments, and metadata.

    Format requirements:
    - note_id: Numeric string or integer (e.g., "123")

    Usage example:
    get_note_from_pipedrive(note_id="123")

    Args:
        note_id: The ID of the note to retrieve

    Returns:
        JSON string with success status and note data, or error message
    """
    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        # Convert note_id to integer
        note_id_int, error = convert_id_string(note_id, "note_id")
        if error:
            return format_tool_response(False, error_message=error)

        # Get the note
        note_data = await client.notes.get_note(note_id_int)

        return format_tool_response(
            success=True,
            data=note_data
        )

    except PipedriveAPIError as e:
        error_msg = f"Pipedrive API error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error retrieving note: {str(e)}"
        logger.exception(error_msg)
        return format_tool_response(False, error_message=error_msg)
