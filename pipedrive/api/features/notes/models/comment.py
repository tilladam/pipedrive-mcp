"""Comment model for Pipedrive note comments."""
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator


class Comment(BaseModel):
    """Represents a comment on a note in Pipedrive.

    Comments are threaded text entries attached to notes, used for
    collaborative discussions on note content.
    """

    id: Optional[int] = None
    content: str = Field(..., description="Comment text content")
    note_id: Optional[int] = Field(None, description="ID of the parent note")
    user_id: Optional[int] = Field(None, description="ID of the user who created the comment")
    add_time: Optional[str] = Field(None, description="When the comment was created")
    update_time: Optional[str] = Field(None, description="When the comment was last updated")
    active_flag: Optional[bool] = Field(None, description="Whether the comment is active")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate comment content is not empty."""
        if not v or not v.strip():
            raise ValueError("Comment content cannot be empty")
        return v

    def to_api_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary for API requests.

        Args:
            exclude_none: Whether to exclude None values from the output

        Returns:
            Dictionary suitable for API requests
        """
        return self.model_dump(
            exclude_none=exclude_none,
            exclude={"id", "note_id", "user_id", "add_time", "update_time", "active_flag"},
        )

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any]) -> "Comment":
        """Create a Comment instance from API response data.

        Args:
            data: Dictionary from API response

        Returns:
            Comment instance
        """
        return cls(**data)
