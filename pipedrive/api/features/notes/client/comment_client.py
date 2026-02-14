"""Client for interacting with Pipedrive Note Comments API (v1 only)."""
from typing import Dict, List, Tuple, Any
from pipedrive.api.base_client import BaseClient


class CommentClient:
    """Client for Pipedrive Note Comments API.

    Comments are sub-resources of notes, accessible via /notes/{note_id}/comments.
    """

    def __init__(self, base_client: BaseClient):
        """Initialize the CommentClient.

        Args:
            base_client: The base HTTP client for API requests
        """
        self.base_client = base_client

    async def add_comment(self, note_id: int, content: str) -> Dict[str, Any]:
        """Add a comment to a note.

        Args:
            note_id: The ID of the note to comment on
            content: The comment text content

        Returns:
            Dictionary containing the created comment data

        Raises:
            PipedriveAPIError: If the API request fails
        """
        response = await self.base_client.request(
            "POST",
            f"/notes/{note_id}/comments",
            json_payload={"content": content},
            version="v1",
        )

        return response.get("data", {})

    async def get_comment(self, note_id: int, comment_id: int) -> Dict[str, Any]:
        """Retrieve a single comment by ID.

        Args:
            note_id: The ID of the parent note
            comment_id: The ID of the comment to retrieve

        Returns:
            Dictionary containing the comment data

        Raises:
            PipedriveAPIError: If the API request fails
        """
        response = await self.base_client.request(
            "GET",
            f"/notes/{note_id}/comments/{comment_id}",
            version="v1",
        )

        return response.get("data", {})

    async def update_comment(
        self, note_id: int, comment_id: int, content: str
    ) -> Dict[str, Any]:
        """Update an existing comment.

        Args:
            note_id: The ID of the parent note
            comment_id: The ID of the comment to update
            content: The new comment text content

        Returns:
            Dictionary containing the updated comment data

        Raises:
            PipedriveAPIError: If the API request fails
        """
        response = await self.base_client.request(
            "PUT",
            f"/notes/{note_id}/comments/{comment_id}",
            json_payload={"content": content},
            version="v1",
        )

        return response.get("data", {})

    async def delete_comment(self, note_id: int, comment_id: int) -> Dict[str, Any]:
        """Delete a comment.

        Args:
            note_id: The ID of the parent note
            comment_id: The ID of the comment to delete

        Returns:
            Dictionary containing deletion confirmation

        Raises:
            PipedriveAPIError: If the API request fails
        """
        response = await self.base_client.request(
            "DELETE",
            f"/notes/{note_id}/comments/{comment_id}",
            version="v1",
        )

        return response.get("data", {})

    async def list_comments(
        self, note_id: int, start: int = 0, limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """List comments on a note.

        Args:
            note_id: The ID of the note
            start: Pagination offset (default 0)
            limit: Number of items to return (default 100)

        Returns:
            Tuple of (list of comment dictionaries, has_more boolean)

        Raises:
            PipedriveAPIError: If the API request fails
        """
        response = await self.base_client.request(
            "GET",
            f"/notes/{note_id}/comments",
            query_params={"start": start, "limit": limit},
            version="v1",
        )

        comments_list = response.get("data", [])
        additional_data = response.get("additional_data", {})
        pagination = additional_data.get("pagination", {})
        has_more = pagination.get("more_items_in_collection", False)

        return comments_list, has_more
