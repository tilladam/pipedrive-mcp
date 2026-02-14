"""Tool for creating notes in Pipedrive."""
from typing import Optional
from mcp.server.fastmcp import Context
from pipedrive.api.features.tool_decorator import tool
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from pydantic import ValidationError
from log_config import logger


@tool("notes")
async def create_note_in_pipedrive(
    ctx: Context,
    content: str,
    lead_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    person_id: Optional[str] = None,
    org_id: Optional[str] = None,
    project_id: Optional[str] = None,
    user_id: Optional[str] = None,
    pinned: Optional[bool] = None,
) -> str:
    """Create a new note in Pipedrive.

    Creates an HTML-formatted note and attaches it to exactly one entity
    (lead, deal, person, organization, or project).

    Format requirements:
    - content: HTML string (max ~100KB)
    - entity IDs: Must provide exactly ONE of: lead_id, deal_id, person_id, org_id, or project_id
    - lead_id: UUID string (e.g., "abc-123-def")
    - All other IDs: Numeric strings or integers

    Usage example:
    create_note_in_pipedrive(
        content="<p>Meeting went well. Customer interested in premium plan.</p>",
        deal_id="123",
        user_id="5",
        pinned=True
    )

    Args:
        content: HTML-formatted note content (required)
        lead_id: UUID of the lead to attach note to
        deal_id: ID of the deal to attach note to
        person_id: ID of the person to attach note to
        org_id: ID of the organization to attach note to
        project_id: ID of the project to attach note to
        user_id: ID of the user who will own the note
        pinned: Whether to pin the note to the entity (default: False)

    Returns:
        JSON string with success status and created note data, or error message
    """
    try:
        pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context
        client = pd_mcp_ctx.pipedrive_client

        # Sanitize empty strings to None
        lead_id = lead_id.strip() if lead_id and lead_id.strip() else None
        deal_id_str = deal_id.strip() if deal_id and deal_id.strip() else None
        person_id_str = person_id.strip() if person_id and person_id.strip() else None
        org_id_str = org_id.strip() if org_id and org_id.strip() else None
        project_id_str = project_id.strip() if project_id and project_id.strip() else None
        user_id_str = user_id.strip() if user_id and user_id.strip() else None

        # Convert numeric IDs
        deal_id_int = None
        person_id_int = None
        org_id_int = None
        project_id_int = None
        user_id_int = None

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

        if user_id_str:
            user_id_int, error = convert_id_string(user_id_str, "user_id")
            if error:
                return format_tool_response(False, error_message=error)

        # Determine pinning flag based on entity type
        pinned_to_lead_flag = None
        pinned_to_deal_flag = None
        pinned_to_person_flag = None
        pinned_to_organization_flag = None
        pinned_to_project_flag = None

        if pinned:
            if lead_id:
                pinned_to_lead_flag = 1
            elif deal_id_int:
                pinned_to_deal_flag = 1
            elif person_id_int:
                pinned_to_person_flag = 1
            elif org_id_int:
                pinned_to_organization_flag = 1
            elif project_id_int:
                pinned_to_project_flag = 1

        # Create the note
        created_note = await client.notes.create_note(
            content=content,
            lead_id=lead_id,
            deal_id=deal_id_int,
            person_id=person_id_int,
            org_id=org_id_int,
            project_id=project_id_int,
            user_id=user_id_int,
            pinned_to_lead_flag=pinned_to_lead_flag,
            pinned_to_deal_flag=pinned_to_deal_flag,
            pinned_to_person_flag=pinned_to_person_flag,
            pinned_to_organization_flag=pinned_to_organization_flag,
            pinned_to_project_flag=pinned_to_project_flag,
        )

        return format_tool_response(
            success=True,
            data=created_note
        )

    except ValidationError as e:
        error_msg = f"Validation error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except PipedriveAPIError as e:
        error_msg = f"Pipedrive API error: {str(e)}"
        logger.error(error_msg)
        return format_tool_response(False, error_message=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error creating note: {str(e)}"
        logger.exception(error_msg)
        return format_tool_response(False, error_message=error_msg)
