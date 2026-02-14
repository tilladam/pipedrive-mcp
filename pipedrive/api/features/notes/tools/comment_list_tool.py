"""Tool for listing comments on a note from Pipedrive."""
from typing import Optional
from mcp.server.fastmcp import Context
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from log_config import logger


@tool("notes")
async def list_comments_on_note_in_pipedrive(
    ctx: Context,
    note_id: str,
    start: Optional[int] = 0,
    limit: Optional[int] = 100,
) -> str:
    """List comments on a note from Pipedrive.

    Retrieves a paginated list of comments on a specific note.

    Format requirements:
    - note_id: Numeric string or integer (e.g., "123")
    - start: Non-negative integer for pagination offset
    - limit: Positive integer (max 500)

    Usage example:
    list_comments_on_note_in_pipedrive(note_id="123", start=0, limit=50)

    Args:
        note_id: The ID of the note to list comments for

        start: Pagination offset (default 0)

        limit: Number of items to return (default 100, max 500)

    Returns:
        JSON string with success status, list of comments, and pagination info
    """
    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        note_id_int, error = convert_id_string(note_id, "note_id")
        if error:
            return format_tool_response(False, error_message=error)

        if start < 0:
            return format_tool_response(False, error_message="start must be non-negative")

        if limit <= 0 or limit > 500:
            return format_tool_response(False, error_message="limit must be between 1 and 500")

        comments, has_more = await client.notes.comments.list_comments(
            note_id=note_id_int,
            start=start,
            limit=limit,
        )

        return format_tool_response(
            success=True,
            data={
                "comments": comments,
                "count": len(comments),
                "has_more": has_more,
                "pagination": {
                    "start": start,
                    "limit": limit,
                    "has_more": has_more,
                },
            },
        )

    except PipedriveAPIError as e:
        error_msg = f"Pipedrive API error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error listing comments: {str(e)}"
        logger.exception(error_msg)
        return format_tool_response(False, error_message=error_msg)
