"""Note model for Pipedrive."""
from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class Note(BaseModel):
    """Represents a note in Pipedrive.

    Notes are HTML-formatted text entries that can be attached to deals, leads,
    persons, organizations, or projects. They're commonly used for tracking
    conversation history, meeting notes, and important updates.

    Notes can only be attached to ONE entity at a time.
    """

    id: Optional[int] = None
    content: str = Field(..., description="HTML-formatted note content")

    # Entity attachments - exactly ONE must be provided
    lead_id: Optional[str] = Field(None, description="UUID of the lead")
    deal_id: Optional[int] = Field(None, description="ID of the deal")
    person_id: Optional[int] = Field(None, description="ID of the person")
    org_id: Optional[int] = Field(None, description="ID of the organization")
    project_id: Optional[int] = Field(None, description="ID of the project")

    # Optional fields
    user_id: Optional[int] = Field(None, description="ID of the user who created/owns the note")
    add_time: Optional[datetime] = Field(None, description="When the note was created")
    update_time: Optional[datetime] = Field(None, description="When the note was last updated")

    # Pinning flags (integers 0 or 1)
    pinned_to_lead_flag: Optional[int] = Field(None, ge=0, le=1, description="Pin to lead")
    pinned_to_deal_flag: Optional[int] = Field(None, ge=0, le=1, description="Pin to deal")
    pinned_to_person_flag: Optional[int] = Field(None, ge=0, le=1, description="Pin to person")
    pinned_to_organization_flag: Optional[int] = Field(None, ge=0, le=1, description="Pin to organization")
    pinned_to_project_flag: Optional[int] = Field(None, ge=0, le=1, description="Pin to project")

    # Read-only fields from API
    active_flag: Optional[bool] = Field(None, description="Whether the note is active")
    last_update_user_id: Optional[int] = Field(None, description="ID of user who last updated")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate note content."""
        if not v or not v.strip():
            raise ValueError("Note content cannot be empty")

        # Check size limit (~100KB)
        if len(v.encode('utf-8')) > 100000:
            raise ValueError(f"Note content exceeds maximum size of 100KB (current: {len(v.encode('utf-8'))} bytes)")

        return v

    @model_validator(mode='after')
    def validate_entity_attachment(self) -> 'Note':
        """Validate that exactly one entity is attached."""
        entity_fields = [
            self.lead_id,
            self.deal_id,
            self.person_id,
            self.org_id,
            self.project_id
        ]

        attached_count = sum(1 for field in entity_fields if field is not None)

        if attached_count == 0:
            raise ValueError("Note must be attached to exactly one entity (lead_id, deal_id, person_id, org_id, or project_id)")

        if attached_count > 1:
            raise ValueError("Note can only be attached to one entity at a time")

        return self

    def to_api_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary for API requests.

        Args:
            exclude_none: Whether to exclude None values from the output

        Returns:
            Dictionary suitable for API requests
        """
        data = self.model_dump(exclude_none=exclude_none, exclude={'id', 'add_time', 'update_time', 'active_flag', 'last_update_user_id'})

        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        return data

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any]) -> 'Note':
        """Create a Note instance from API response data.

        Args:
            data: Dictionary from API response

        Returns:
            Note instance
        """
        return cls(**data)
