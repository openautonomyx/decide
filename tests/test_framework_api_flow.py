import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.tenant_employee import Tenant

from app.models import workflow_definition as _workflow_models  # noqa: F401
from app.models import tenant_employee as _tenant_models  # noqa: F401
from app.models import execution_identity as _identity_models  # noqa: F401


@pytest.fixture()
def client_and_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c, SessionLocal
    app.dependency_overrides.clear()


def test_langgraph_import_publish_run_roundtrip(client_and_db):
    client, session_factory = client_and_db
    tenant_id = f"tenant-{uuid.uuid4()}"
    db = session_factory()
    db.add(Tenant(id=tenant_id, name="Framework Tenant"))
    db.commit()
    db.close()

    graph_definition = {
        "name": "Framework Flow",
        "description": "Imported from langgraph",
        "nodes": [
            {"id": "start", "type": "start", "data": {}},
            {"id": "llm", "type": "llm", "data": {"model": "gpt-4"}},
            {"id": "end", "type": "end", "data": {}},
        ],
        "edges": [
            {"source": "start", "target": "llm"},
            {"source": "llm", "target": "end"},
        ],
    }

    imported = client.post(
        f"/api/v1/frameworks/langgraph/import?tenant_id={tenant_id}",
        json=graph_definition,
    )
    assert imported.status_code == 200, imported.text
    workflow_id = imported.json()["workflow_id"]

    validated = client.post(f"/api/v1/workflows/{workflow_id}/validate")
    assert validated.status_code == 200, validated.text

    published = client.post(f"/api/v1/workflows/{workflow_id}/publish")
    assert published.status_code == 201, published.text

    run = client.post(f"/api/v1/workflows/{workflow_id}/run")
    assert run.status_code == 200, run.text

    roundtrip = client.get(f"/api/v1/frameworks/roundtrip/{workflow_id}")
    assert roundtrip.status_code == 200, roundtrip.text
    assert len(roundtrip.json()["nodes"]) >= 2
    assert all("legacy_id" in node for node in roundtrip.json()["nodes"])
    roundtrip_node_ids = {node["id"] for node in roundtrip.json()["nodes"]}
    assert any(node_id.startswith("start") for node_id in roundtrip_node_ids)
