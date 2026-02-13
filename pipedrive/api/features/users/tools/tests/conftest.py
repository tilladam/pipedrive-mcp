import pytest
from unittest.mock import patch

from pipedrive.api.features.tool_registry import registry


@pytest.fixture(autouse=True)
def enable_users_feature():
    """
    Fixture to enable the 'users' feature for all tests in this module.

    This fixture is automatically used in all tests in this directory.
    It ensures the 'users' feature is reported as enabled during tests.
    """
    with patch('pipedrive.api.features.tool_registry.registry.is_feature_enabled') as mock_is_enabled:
        def side_effect(feature_id):
            if feature_id == "users":
                return True
            return registry.is_feature_enabled(feature_id)

        mock_is_enabled.side_effect = side_effect
        yield
