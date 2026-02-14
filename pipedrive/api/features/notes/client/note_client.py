"""Client for interacting with Pipedrive Notes API (v1 only)."""
from typing import Dict, List, Optional, Tuple, Any
from pipedrive.api.base_client import BaseClient
from pipedrive.api.features.notes.models.note import Note


class NoteClient:
    """Client for Pipedrive Notes API.

    Notes are only available in API v1, so all requests must specify version="v1".
    """

    def __init__(self, base_client: BaseClient):
        """Initialize the NoteClient.

        Args:
            base_client: The base HTTP client for API requests
        """
        self.base_client = base_client

    async def create_note(
        self,
        content: str,
        lead_id: Optional[str] = None,
        deal_id: Optional[int] = None,
        person_id: Optional[int] = None,
        org_id: Optional[int] = None,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None,
        pinned_to_lead_flag: Optional[int] = None,
        pinned_to_deal_flag: Optional[int] = None,
        pinned_to_person_flag: Optional[int] = None,
        pinned_to_organization_flag: Optional[int] = None,
        pinned_to_project_flag: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new note in Pipedrive.

        Args:
            content: HTML-formatted note content (required)
            lead_id: UUID of the lead to attach note to
            deal_id: ID of the deal to attach note to
            person_id: ID of the person to attach note to
            org_id: ID of the organization to attach note to
            project_id: ID of the project to attach note to
            user_id: ID of the user who will own the note
            pinned_to_lead_flag: Pin to lead (0 or 1)
            pinned_to_deal_flag: Pin to deal (0 or 1)
            pinned_to_person_flag: Pin to person (0 or 1)
            pinned_to_organization_flag: Pin to organization (0 or 1)
            pinned_to_project_flag: Pin to project (0 or 1)

        Returns:
            Dictionary containing the created note data

        Raises:
            PipedriveAPIError: If the API request fails
            ValidationError: If the note data is invalid
        """
        # Create Note model for validation
        note = Note(
            content=content,
            lead_id=lead_id,
            deal_id=deal_id,
            person_id=person_id,
            org_id=org_id,
            project_id=project_id,
            user_id=user_id,
            pinned_to_lead_flag=pinned_to_lead_flag,
            pinned_to_deal_flag=pinned_to_deal_flag,
            pinned_to_person_flag=pinned_to_person_flag,
            pinned_to_organization_flag=pinned_to_organization_flag,
            pinned_to_project_flag=pinned_to_project_flag,
        )

        # Convert to API payload
        payload = note.to_api_dict(exclude_none=True)

        # Make API request (v1 only)
        response = await self.base_client.request(
            "POST",
            "/notes",
            json_payload=payload,
            version="v1"
        )

        return response.get("data", {})

    async def get_note(self, note_id: int) -> Dict[str, Any]:
        """Retrieve a single note by ID.

        Args:
            note_id: The ID of the note to retrieve

        Returns:
            Dictionary containing the note data

        Raises:
            PipedriveAPIError: If the API request fails
        """
        response = await self.base_client.request(
            "GET",
            f"/notes/{note_id}",
            version="v1"
        )

        return response.get("data", {})

    async def update_note(
        self,
        note_id: int,
        content: Optional[str] = None,
        lead_id: Optional[str] = None,
        deal_id: Optional[int] = None,
        person_id: Optional[int] = None,
        org_id: Optional[int] = None,
        project_id: Optional[int] = None,
        pinned_to_lead_flag: Optional[int] = None,
        pinned_to_deal_flag: Optional[int] = None,
        pinned_to_person_flag: Optional[int] = None,
        pinned_to_organization_flag: Optional[int] = None,
        pinned_to_project_flag: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update an existing note.

        Args:
            note_id: The ID of the note to update
            content: New HTML-formatted note content
            lead_id: New lead UUID to attach note to
            deal_id: New deal ID to attach note to
            person_id: New person ID to attach note to
            org_id: New organization ID to attach note to
            project_id: New project ID to attach note to
            pinned_to_lead_flag: Pin to lead (0 or 1)
            pinned_to_deal_flag: Pin to deal (0 or 1)
            pinned_to_person_flag: Pin to person (0 or 1)
            pinned_to_organization_flag: Pin to organization (0 or 1)
            pinned_to_project_flag: Pin to project (0 or 1)

        Returns:
            Dictionary containing the updated note data

        Raises:
            PipedriveAPIError: If the API request fails
            ValueError: If no fields are provided for update
        """
        # Build payload with only provided fields
        payload = {}

        if content is not None:
            payload["content"] = content
        if lead_id is not None:
            payload["lead_id"] = lead_id
        if deal_id is not None:
            payload["deal_id"] = deal_id
        if person_id is not None:
            payload["person_id"] = person_id
        if org_id is not None:
            payload["org_id"] = org_id
        if project_id is not None:
            payload["project_id"] = project_id
        if pinned_to_lead_flag is not None:
            payload["pinned_to_lead_flag"] = pinned_to_lead_flag
        if pinned_to_deal_flag is not None:
            payload["pinned_to_deal_flag"] = pinned_to_deal_flag
        if pinned_to_person_flag is not None:
            payload["pinned_to_person_flag"] = pinned_to_person_flag
        if pinned_to_organization_flag is not None:
            payload["pinned_to_organization_flag"] = pinned_to_organization_flag
        if pinned_to_project_flag is not None:
            payload["pinned_to_project_flag"] = pinned_to_project_flag

        if not payload:
            raise ValueError("At least one field must be provided for update")

        # Make API request (v1 only)
        response = await self.base_client.request(
            "PUT",
            f"/notes/{note_id}",
            json_payload=payload,
            version="v1"
        )

        return response.get("data", {})

    async def delete_note(self, note_id: int) -> Dict[str, Any]:
        """Delete a note.

        Args:
            note_id: The ID of the note to delete

        Returns:
            Dictionary containing deletion confirmation

        Raises:
            PipedriveAPIError: If the API request fails
        """
        response = await self.base_client.request(
            "DELETE",
            f"/notes/{note_id}",
            version="v1"
        )

        return response.get("data", {})

    async def list_notes(
        self,
        user_id: Optional[int] = None,
        deal_id: Optional[int] = None,
        person_id: Optional[int] = None,
        org_id: Optional[int] = None,
        lead_id: Optional[str] = None,
        pinned_to_lead_flag: Optional[int] = None,
        pinned_to_deal_flag: Optional[int] = None,
        pinned_to_person_flag: Optional[int] = None,
        pinned_to_organization_flag: Optional[int] = None,
        start: int = 0,
        limit: int = 100,
        sort: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """List notes with optional filters.

        Notes use offset-based pagination (start/limit), not cursor-based.

        Args:
            user_id: Filter by user ID
            deal_id: Filter by deal ID
            person_id: Filter by person ID
            org_id: Filter by organization ID
            lead_id: Filter by lead UUID
            pinned_to_lead_flag: Filter by pinned to lead (0 or 1)
            pinned_to_deal_flag: Filter by pinned to deal (0 or 1)
            pinned_to_person_flag: Filter by pinned to person (0 or 1)
            pinned_to_organization_flag: Filter by pinned to organization (0 or 1)
            start: Pagination offset (default 0)
            limit: Number of items to return (default 100)
            sort: Sort field (e.g., "add_time", "update_time")
            start_date: Filter by creation date (YYYY-MM-DD)
            end_date: Filter by creation date (YYYY-MM-DD)

        Returns:
            Tuple of (list of note dictionaries, has_more boolean)

        Raises:
            PipedriveAPIError: If the API request fails
        """
        # Build query parameters
        params = {
            "start": start,
            "limit": limit,
        }

        if user_id is not None:
            params["user_id"] = user_id
        if deal_id is not None:
            params["deal_id"] = deal_id
        if person_id is not None:
            params["person_id"] = person_id
        if org_id is not None:
            params["org_id"] = org_id
        if lead_id is not None:
            params["lead_id"] = lead_id
        if pinned_to_lead_flag is not None:
            params["pinned_to_lead_flag"] = pinned_to_lead_flag
        if pinned_to_deal_flag is not None:
            params["pinned_to_deal_flag"] = pinned_to_deal_flag
        if pinned_to_person_flag is not None:
            params["pinned_to_person_flag"] = pinned_to_person_flag
        if pinned_to_organization_flag is not None:
            params["pinned_to_organization_flag"] = pinned_to_organization_flag
        if sort:
            params["sort"] = sort
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        # Make API request (v1 only)
        response = await self.base_client.request(
            "GET",
            "/notes",
            params=params,
            version="v1"
        )

        notes_list = response.get("data", [])
        additional_data = response.get("additional_data", {})
        pagination = additional_data.get("pagination", {})
        has_more = pagination.get("more_items_in_collection", False)

        return notes_list, has_more
