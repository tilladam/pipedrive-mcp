"""Tests for Note model."""
import pytest
from pydantic import ValidationError
from pipedrive.api.features.notes.models.note import Note


class TestNoteModel:
    """Tests for the Note model."""

    def test_create_note_with_deal(self):
        """Test creating a note attached to a deal."""
        note = Note(
            content="This is a test note",
            deal_id=123
        )
        assert note.content == "This is a test note"
        assert note.deal_id == 123
        assert note.lead_id is None
        assert note.person_id is None

    def test_create_note_with_person(self):
        """Test creating a note attached to a person."""
        note = Note(
            content="Person note",
            person_id=456
        )
        assert note.content == "Person note"
        assert note.person_id == 456
        assert note.deal_id is None

    def test_create_note_with_lead(self):
        """Test creating a note attached to a lead."""
        note = Note(
            content="Lead note",
            lead_id="abc-123-def"
        )
        assert note.content == "Lead note"
        assert note.lead_id == "abc-123-def"

    def test_create_note_with_organization(self):
        """Test creating a note attached to an organization."""
        note = Note(
            content="Org note",
            org_id=789
        )
        assert note.content == "Org note"
        assert note.org_id == 789

    def test_create_note_with_project(self):
        """Test creating a note attached to a project."""
        note = Note(
            content="Project note",
            project_id=101
        )
        assert note.content == "Project note"
        assert note.project_id == 101

    def test_empty_content_validation(self):
        """Test that empty content raises ValidationError."""
        with pytest.raises(ValidationError, match="Note content cannot be empty"):
            Note(content="", deal_id=123)

        with pytest.raises(ValidationError, match="Note content cannot be empty"):
            Note(content="   ", deal_id=123)

    def test_content_size_limit(self):
        """Test that content exceeding 100KB raises ValidationError."""
        large_content = "x" * 100001  # Just over 100KB
        with pytest.raises(ValidationError, match="exceeds maximum size"):
            Note(content=large_content, deal_id=123)

    def test_no_entity_attachment(self):
        """Test that note without entity attachment raises ValidationError."""
        with pytest.raises(ValidationError, match="must be attached to exactly one entity"):
            Note(content="Test note")

    def test_multiple_entity_attachments(self):
        """Test that note with multiple entities raises ValidationError."""
        with pytest.raises(ValidationError, match="can only be attached to one entity"):
            Note(
                content="Test note",
                deal_id=123,
                person_id=456
            )

        with pytest.raises(ValidationError, match="can only be attached to one entity"):
            Note(
                content="Test note",
                deal_id=123,
                org_id=789,
                lead_id="abc-123"
            )

    def test_html_content(self):
        """Test that HTML content is preserved."""
        html_content = "<p>This is <strong>bold</strong> text</p>"
        note = Note(content=html_content, deal_id=123)
        assert note.content == html_content

    def test_pinning_flags(self):
        """Test pinning flag validation."""
        note = Note(
            content="Pinned note",
            deal_id=123,
            pinned_to_deal_flag=1
        )
        assert note.pinned_to_deal_flag == 1

        # Test invalid flag value
        with pytest.raises(ValidationError):
            Note(
                content="Test",
                deal_id=123,
                pinned_to_deal_flag=2  # Invalid: must be 0 or 1
            )

    def test_to_api_dict(self):
        """Test conversion to API dictionary."""
        note = Note(
            content="Test note",
            deal_id=123,
            user_id=5,
            pinned_to_deal_flag=1
        )
        api_dict = note.to_api_dict()

        assert api_dict["content"] == "Test note"
        assert api_dict["deal_id"] == 123
        assert api_dict["user_id"] == 5
        assert api_dict["pinned_to_deal_flag"] == 1
        assert "id" not in api_dict  # Excluded field
        assert "add_time" not in api_dict  # Excluded field

    def test_to_api_dict_exclude_none(self):
        """Test that None values are excluded from API dict."""
        note = Note(
            content="Test note",
            deal_id=123
        )
        api_dict = note.to_api_dict(exclude_none=True)

        assert "person_id" not in api_dict
        assert "org_id" not in api_dict
        assert "lead_id" not in api_dict
        assert "deal_id" in api_dict

    def test_from_api_dict(self):
        """Test creating Note from API response."""
        api_data = {
            "id": 999,
            "content": "Test note from API",
            "deal_id": 123,
            "user_id": 5,
            "active_flag": True,
            "pinned_to_deal_flag": 1
        }
        note = Note.from_api_dict(api_data)

        assert note.id == 999
        assert note.content == "Test note from API"
        assert note.deal_id == 123
        assert note.user_id == 5
        assert note.active_flag is True
        assert note.pinned_to_deal_flag == 1

    def test_optional_fields(self):
        """Test that optional fields can be omitted."""
        note = Note(
            content="Minimal note",
            deal_id=123
        )
        assert note.user_id is None
        assert note.add_time is None
        assert note.pinned_to_deal_flag is None
