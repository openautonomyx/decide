import os

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture(autouse=True)
def env_setup():
    os.environ.setdefault("SERVICE_API_KEY", "test-api-key-123456")
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "proj")
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/fake.json")
    yield


@pytest.fixture
def client():
    return TestClient(create_app())
