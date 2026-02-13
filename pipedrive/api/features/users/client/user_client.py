from typing import Any, Dict

from log_config import logger
from pipedrive.api.base_client import BaseClient


class UserClient:
    """Client for Pipedrive Users API endpoints"""

    def __init__(self, base_client: BaseClient):
        """
        Initialize the User client

        Args:
            base_client: BaseClient instance for making API requests
        """
        self.base_client = base_client

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get a specific user by ID from Pipedrive

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            Dictionary containing user data

        Raises:
            PipedriveAPIError: If the API request fails
        """
        logger.info(f"UserClient: Fetching user with ID {user_id}")

        # Users API is only available on v1 endpoint
        response_data = await self.base_client.request(
            "GET",
            f"/users/{user_id}",
            version="v1",
        )

        user_data = response_data.get("data", {})
        logger.info(f"UserClient: Successfully retrieved user {user_id}")

        return user_data
