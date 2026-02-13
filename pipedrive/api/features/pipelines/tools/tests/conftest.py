import pytest
from unittest.mock import patch

from pipedrive.api.features.tool_registry import registry


@pytest.fixture(autouse=True)
def enable_pipelines_feature():
    """
    Fixture to enable the 'pipelines' feature for all tests in this module.
    """
    with patch('pipedrive.api.features.tool_registry.registry.is_feature_enabled') as mock_is_enabled:
        def side_effect(feature_id):
            if feature_id == "pipelines":
                return True
            return registry.is_feature_enabled(feature_id)

        mock_is_enabled.side_effect = side_effect
        yield
