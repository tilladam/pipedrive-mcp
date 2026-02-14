"""Tool for listing notes from Pipedrive."""
from typing import Optional
from mcp.server.fastmcp import Context
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from log_config import logger


@tool("notes")
async def list_notes_in_pipedrive(
    ctx: Context,
    user_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    person_id: Optional[str] = None,
    org_id: Optional[str] = None,
    lead_id: Optional[str] = None,
    pinned_only: Optional[bool] = None,
    start: Optional[int] = 0,
    limit: Optional[int] = 100,
    sort: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    """List notes from Pipedrive with optional filters.

    Retrieves a list of notes with support for filtering by entity, user,
    pinning status, and date range. Results are paginated.

    Format requirements:
    - Entity IDs: Numeric strings or integers (except lead_id which is UUID)
    - start: Non-negative integer for pagination offset
    - limit: Positive integer (max 500)
    - sort: Field name like "add_time", "update_time" (prefix with "-" for descending)
    - start_date, end_date: ISO date format (YYYY-MM-DD)

    Usage example:
    list_notes_in_pipedrive(
        deal_id="123",
        pinned_only=True,
        start=0,
        limit=50,
        sort="-update_time"
    )

    Args:
        user_id: Filter by user ID
        deal_id: Filter by deal ID
        person_id: Filter by person ID
        org_id: Filter by organization ID
        lead_id: Filter by lead UUID
        pinned_only: Filter to show only pinned notes
        start: Pagination offset (default 0)
        limit: Number of items to return (default 100, max 500)
        sort: Sort field (e.g., "add_time", "-update_time")
        start_date: Filter by creation date start (YYYY-MM-DD)
        end_date: Filter by creation date end (YYYY-MM-DD)

    Returns:
        JSON string with success status, list of notes, and pagination info
    """
    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        # Sanitize and convert IDs
        user_id_int = None
        deal_id_int = None
        person_id_int = None
        org_id_int = None
        lead_id_str = None

        if user_id:
            user_id_int, error = convert_id_string(user_id, "user_id")
            if error:
                return format_tool_response(False, error_message=error)

        if deal_id:
            deal_id_int, error = convert_id_string(deal_id, "deal_id")
            if error:
                return format_tool_response(False, error_message=error)

        if person_id:
            person_id_int, error = convert_id_string(person_id, "person_id")
            if error:
                return format_tool_response(False, error_message=error)

        if org_id:
            org_id_int, error = convert_id_string(org_id, "org_id")
            if error:
                return format_tool_response(False, error_message=error)

        if lead_id:
            lead_id_str = lead_id.strip()

        # Validate pagination parameters
        if start < 0:
            return format_tool_response(False, error_message="start must be non-negative")

        if limit <= 0 or limit > 500:
            return format_tool_response(False, error_message="limit must be between 1 and 500")

        # Validate sort parameter
        valid_sort_fields = ["add_time", "update_time", "-add_time", "-update_time"]
        if sort and sort not in valid_sort_fields:
            return format_tool_response(
                False,
                error_message=f"Invalid sort field. Must be one of: {', '.join(valid_sort_fields)}"
            )

        # Determine pinning flags if pinned_only is set
        pinned_to_lead_flag = None
        pinned_to_deal_flag = None
        pinned_to_person_flag = None
        pinned_to_organization_flag = None

        if pinned_only:
            # Set flag based on which entity filter is active
            if lead_id_str:
                pinned_to_lead_flag = 1
            elif deal_id_int:
                pinned_to_deal_flag = 1
            elif person_id_int:
                pinned_to_person_flag = 1
            elif org_id_int:
                pinned_to_organization_flag = 1

        # List notes
        notes, has_more = await client.notes.list_notes(
            user_id=user_id_int,
            deal_id=deal_id_int,
            person_id=person_id_int,
            org_id=org_id_int,
            lead_id=lead_id_str,
            pinned_to_lead_flag=pinned_to_lead_flag,
            pinned_to_deal_flag=pinned_to_deal_flag,
            pinned_to_person_flag=pinned_to_person_flag,
            pinned_to_organization_flag=pinned_to_organization_flag,
            start=start,
            limit=limit,
            sort=sort,
            start_date=start_date,
            end_date=end_date,
        )

        return format_tool_response(
            success=True,
            data={
                "notes": notes,
                "count": len(notes),
                "has_more": has_more,
                "pagination": {
                    "start": start,
                    "limit": limit,
                    "has_more": has_more
                }
            }
        )

    except PipedriveAPIError as e:
        error_msg = f"Pipedrive API error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error listing notes: {str(e)}"
        logger.exception(error_msg)
        return format_tool_response(False, error_message=error_msg)
