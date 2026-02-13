from typing import Any, Dict, Optional
from pydantic import BaseModel


class User(BaseModel):
    """Model representing a Pipedrive user.

    Fields:
        id: Unique identifier of the user
        name: Full name of the user
        email: Email address of the user
        active_flag: Whether the user is active
        role_id: ID of the user's role
        icon_url: URL of the user's avatar
        is_admin: Whether the user has admin privileges
        timezone_name: User's timezone
        timezone_offset: User's timezone offset
        lang: Language preference code
    """

    id: int
    name: str
    email: str
    active_flag: bool = True
    role_id: Optional[int] = None
    icon_url: Optional[str] = None
    is_admin: Optional[bool] = None
    timezone_name: Optional[str] = None
    timezone_offset: Optional[str] = None
    lang: Optional[int] = None

    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any]) -> "User":
        """Create a User instance from Pipedrive API response data.

        Args:
            api_data: User data from Pipedrive API

        Returns:
            User instance with parsed data
        """
        return cls(**{
            k: v for k, v in api_data.items()
            if k in cls.model_fields
        })
