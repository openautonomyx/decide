import os

import pytest

from app.core.config import Settings


def test_config_requires_fields():
    os.environ.pop("SERVICE_API_KEY", None)
    with pytest.raises(Exception):
        Settings()


def test_tool_allowlist_parses():
    cfg = Settings(
        service_api_key="1234567890abcdef",
        google_cloud_project="x",
        google_application_credentials="/tmp/fake.json",
        enabled_tools="calculator,current_datetime",
    )
    assert cfg.tool_allowlist == {"calculator", "current_datetime"}
