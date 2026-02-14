"""Tests for Comment model."""
import pytest
from pydantic import ValidationError
from pipedrive.api.features.notes.models.comment import Comment


class TestCommentModel:
    """Tests for the Comment model."""

    def test_create_comment(self):
        """Test creating a basic comment."""
        comment = Comment(content="This is a test comment")
        assert comment.content == "This is a test comment"
        assert comment.id is None
        assert comment.note_id is None
        assert comment.user_id is None

    def test_create_comment_with_all_fields(self):
        """Test creating a comment with all fields."""
        comment = Comment(
            id=1,
            content="Full comment",
            note_id=123,
            user_id=5,
            add_time="2024-01-01 12:00:00",
            update_time="2024-01-02 12:00:00",
            active_flag=True,
        )
        assert comment.id == 1
        assert comment.content == "Full comment"
        assert comment.note_id == 123
        assert comment.user_id == 5
        assert comment.active_flag is True

    def test_empty_content_validation(self):
        """Test that empty content raises ValidationError."""
        with pytest.raises(ValidationError, match="Comment content cannot be empty"):
            Comment(content="")

        with pytest.raises(ValidationError, match="Comment content cannot be empty"):
            Comment(content="   ")

    def test_to_api_dict(self):
        """Test conversion to API dictionary."""
        comment = Comment(content="Test comment")
        api_dict = comment.to_api_dict()

        assert api_dict["content"] == "Test comment"
        assert "id" not in api_dict
        assert "note_id" not in api_dict
        assert "user_id" not in api_dict
        assert "add_time" not in api_dict

    def test_to_api_dict_excludes_read_only_fields(self):
        """Test that read-only fields are excluded from API dict."""
        comment = Comment(
            id=1,
            content="Test",
            note_id=123,
            user_id=5,
            add_time="2024-01-01",
            update_time="2024-01-02",
            active_flag=True,
        )
        api_dict = comment.to_api_dict()

        assert "id" not in api_dict
        assert "note_id" not in api_dict
        assert "user_id" not in api_dict
        assert "add_time" not in api_dict
        assert "update_time" not in api_dict
        assert "active_flag" not in api_dict
        assert api_dict["content"] == "Test"

    def test_from_api_dict(self):
        """Test creating Comment from API response."""
        api_data = {
            "id": 999,
            "content": "API comment",
            "note_id": 123,
            "user_id": 5,
            "active_flag": True,
        }
        comment = Comment.from_api_dict(api_data)

        assert comment.id == 999
        assert comment.content == "API comment"
        assert comment.note_id == 123
        assert comment.user_id == 5
        assert comment.active_flag is True
