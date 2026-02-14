"""Tool for updating notes in Pipedrive."""
from typing import Optional
from mcp.server.fastmcp import Context
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from log_config import logger


@tool("notes")
async def update_note_in_pipedrive(
    ctx: Context,
    note_id: str,
    content: Optional[str] = None,
    lead_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    person_id: Optional[str] = None,
    org_id: Optional[str] = None,
    project_id: Optional[str] = None,
    pinned: Optional[bool] = None,
) -> str:
    """Update an existing note in Pipedrive.

    Updates the content, changes the entity attachment, or toggles pinning
    status. At least one field must be provided for update.

    Format requirements:
    - note_id: Numeric string or integer (required)
    - content: HTML string (optional)
    - lead_id: UUID string (optional, e.g., "abc-123-def")
    - Other entity IDs: Numeric strings or integers (optional)

    Usage example:
    update_note_in_pipedrive(
        note_id="123",
        content="<p>Updated meeting notes with action items.</p>",
        pinned=True
    )

    Args:
        note_id: The ID of the note to update
        content: New HTML-formatted note content
        lead_id: New lead UUID to attach note to
        deal_id: New deal ID to attach note to
        person_id: New person ID to attach note to
        org_id: New organization ID to attach note to
        project_id: New project ID to attach note to
        pinned: Whether to pin the note to the entity

    Returns:
        JSON string with success status and updated note data, or error message
    """
    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        # Convert note_id to integer
        note_id_int, error = convert_id_string(note_id, "note_id")
        if error:
            return format_tool_response(False, error_message=error)

        # Sanitize empty strings to None
        lead_id = lead_id.strip() if lead_id and lead_id.strip() else None
        deal_id_str = deal_id.strip() if deal_id and deal_id.strip() else None
        person_id_str = person_id.strip() if person_id and person_id.strip() else None
        org_id_str = org_id.strip() if org_id and org_id.strip() else None
        project_id_str = project_id.strip() if project_id and project_id.strip() else None

        # Convert numeric IDs
        deal_id_int = None
        person_id_int = None
        org_id_int = None
        project_id_int = None

        if deal_id_str:
            deal_id_int, error = convert_id_string(deal_id_str, "deal_id")
            if error:
                return format_tool_response(False, error_message=error)

        if person_id_str:
            person_id_int, error = convert_id_string(person_id_str, "person_id")
            if error:
                return format_tool_response(False, error_message=error)

        if org_id_str:
            org_id_int, error = convert_id_string(org_id_str, "org_id")
            if error:
                return format_tool_response(False, error_message=error)

        if project_id_str:
            project_id_int, error = convert_id_string(project_id_str, "project_id")
            if error:
                return format_tool_response(False, error_message=error)

        # Determine pinning flags based on entity type if pinned is set
        pinned_to_lead_flag = None
        pinned_to_deal_flag = None
        pinned_to_person_flag = None
        pinned_to_organization_flag = None
        pinned_to_project_flag = None

        if pinned is not None:
            pin_value = 1 if pinned else 0
            # Determine which entity is being updated
            if lead_id:
                pinned_to_lead_flag = pin_value
            elif deal_id_int:
                pinned_to_deal_flag = pin_value
            elif person_id_int:
                pinned_to_person_flag = pin_value
            elif org_id_int:
                pinned_to_organization_flag = pin_value
            elif project_id_int:
                pinned_to_project_flag = pin_value
            else:
                # If no entity is being changed, we need to get current note to determine entity
                # For now, we'll set all flags to the same value
                # The API will ignore irrelevant flags
                pinned_to_lead_flag = pin_value
                pinned_to_deal_flag = pin_value
                pinned_to_person_flag = pin_value
                pinned_to_organization_flag = pin_value
                pinned_to_project_flag = pin_value

        # Update the note
        updated_note = await client.notes.update_note(
            note_id=note_id_int,
            content=content,
            lead_id=lead_id,
            deal_id=deal_id_int,
            person_id=person_id_int,
            org_id=org_id_int,
            project_id=project_id_int,
            pinned_to_lead_flag=pinned_to_lead_flag,
            pinned_to_deal_flag=pinned_to_deal_flag,
            pinned_to_person_flag=pinned_to_person_flag,
            pinned_to_organization_flag=pinned_to_organization_flag,
            pinned_to_project_flag=pinned_to_project_flag,
        )

        return format_tool_response(
            success=True,
            data=updated_note
        )

    except ValueError as e:
        error_msg = f"Validation error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except PipedriveAPIError as e:
        error_msg = f"Pipedrive API error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error updating note: {str(e)}"
        logger.exception(error_msg)
        return format_tool_response(False, error_message=error_msg)
