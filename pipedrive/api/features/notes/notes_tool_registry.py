"""Tool registry for Notes feature."""
from pipedrive.api.features.tool_registry import registry, FeatureMetadata

# Register the feature
registry.register_feature(
    "notes",
    FeatureMetadata(
        name="Notes",
        description="Tools for managing notes in Pipedrive (API v1 only)",
        version="1.0.0",
    )
)

# Import and register tools
from .tools.note_create_tool import create_note_in_pipedrive
from .tools.note_get_tool import get_note_from_pipedrive
from .tools.note_update_tool import update_note_in_pipedrive
from .tools.note_delete_tool import delete_note_from_pipedrive
from .tools.note_list_tool import list_notes_in_pipedrive

registry.register_tool("notes", create_note_in_pipedrive)
registry.register_tool("notes", get_note_from_pipedrive)
registry.register_tool("notes", update_note_in_pipedrive)
registry.register_tool("notes", delete_note_from_pipedrive)
registry.register_tool("notes", list_notes_in_pipedrive)
