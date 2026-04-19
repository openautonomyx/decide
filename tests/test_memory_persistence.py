import uuid

<<<<<<< HEAD
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.tenant_employee import Tenant

# Import models so metadata includes all required tables
from app.models import memory as _memory_models  # noqa: F401
from app.models import skill as _skill_models  # noqa: F401
from app.models import workflow_definition as _workflow_models  # noqa: F401
from app.models import execution_identity as _identity_models  # noqa: F401
from app.models import tenant_employee as _tenant_models  # noqa: F401


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

=======
from app.models.tenant_employee import Tenant

>>>>>>> origin/main

def _create_workflow(client, tenant_id: str) -> str:
    flow_data = {
        "nodes": [
            {"id": "start", "type": "ChatInput", "data": {"label": "Start"}},
            {"id": "end", "type": "ChatOutput", "data": {"label": "End"}},
        ],
        "edges": [{"source": "start", "target": "end"}],
    }
    imported = client.post(
        "/api/v1/workflows/import/langflow",
        json={"tenant_id": tenant_id, "name": f"wf-{tenant_id}", "flow_data": flow_data},
    )
<<<<<<< HEAD
    assert imported.status_code == 201, imported.text
=======
    assert imported.status_code in [200, 201], imported.text
>>>>>>> origin/main
    workflow_id = imported.json()["workflow_id"]

    validated = client.post(f"/api/v1/workflows/{workflow_id}/validate")
    assert validated.status_code == 200, validated.text

    published = client.post(f"/api/v1/workflows/{workflow_id}/publish")
<<<<<<< HEAD
    assert published.status_code == 201, published.text
    return workflow_id


def _insert_tenant(session_factory, tenant_id: str):
    db = session_factory()
    try:
        db.add(Tenant(id=tenant_id, name=f"Tenant {tenant_id}"))
        db.commit()
    finally:
        db.close()


def test_persistent_memory_create_and_query(client_and_db):
    client, session_factory = client_and_db
    tenant_id = f"tenant-{uuid.uuid4()}"
    _insert_tenant(session_factory, tenant_id)
=======
    assert published.status_code in [200, 201], published.text
    return workflow_id


def test_persistent_memory_create_and_query(client, db_session):
    tenant_id = f"tenant-{uuid.uuid4()}"
    db_session.add(Tenant(id=tenant_id, name="Memory Tenant"))
    db_session.commit()
>>>>>>> origin/main

    persisted = client.post(
        "/api/v1/memory/persist",
        json={
            "tenant_id": tenant_id,
            "scope_type": "organization",
            "scope_id": tenant_id,
            "memory_type": "fact",
            "title": "Company policy",
            "content": "Always verify customer identity before refund.",
            "tags": ["policy", "support"],
            "source_type": "human",
        },
    )
    assert persisted.status_code == 201, persisted.text

    queried = client.get(
        "/api/v1/memory/entries",
        params={"tenant_id": tenant_id, "scope_type": "organization", "scope_id": tenant_id},
    )
    assert queried.status_code == 200
    assert queried.json()["total"] >= 1


<<<<<<< HEAD
def test_scoped_recall_priority_and_inactive_filter(client_and_db):
    client, session_factory = client_and_db
    tenant_id = f"tenant-{uuid.uuid4()}"
    workflow_id = f"wf-{uuid.uuid4()}"
    run_id = f"run-{uuid.uuid4()}"
    _insert_tenant(session_factory, tenant_id)
=======
def test_scoped_recall_priority_and_inactive_filter(client, db_session):
    tenant_id = f"tenant-{uuid.uuid4()}"
    workflow_id = f"wf-{uuid.uuid4()}"
    run_id = f"run-{uuid.uuid4()}"
    db_session.add(Tenant(id=tenant_id, name="Priority Tenant"))
    db_session.commit()
>>>>>>> origin/main

    for scope, scope_id in [
        ("organization", tenant_id),
        ("workflow", workflow_id),
        ("run", run_id),
    ]:
        resp = client.post(
            "/api/v1/memory/persist",
            json={
                "tenant_id": tenant_id,
                "scope_type": scope,
                "scope_id": scope_id,
                "memory_type": "instruction",
                "title": f"{scope}-item",
                "content": f"{scope}-content",
                "tags": [scope],
            },
        )
        assert resp.status_code == 201

    resolved = client.post(
        "/api/v1/memory/resolve",
        json={
            "tenant_id": tenant_id,
            "organization_scope_id": tenant_id,
            "workflow_scope_id": workflow_id,
            "run_scope_id": run_id,
            "is_active": True,
        },
    )
    assert resolved.status_code == 200
    assert resolved.json()["resolved_scopes"] == ["organization", "workflow", "run"]

    entry_id = resolved.json()["items"][0]["id"]
    deactivated = client.patch(f"/api/v1/memory/entries/{entry_id}", json={"is_active": False})
    assert deactivated.status_code == 200

    resolved_active = client.post(
        "/api/v1/memory/resolve",
        json={"tenant_id": tenant_id, "organization_scope_id": tenant_id, "is_active": True},
    )
    assert all(item["is_active"] for item in resolved_active.json()["items"])


<<<<<<< HEAD
def test_workflow_memory_and_skills_runtime_context(client_and_db):
    client, session_factory = client_and_db
    tenant_id = f"tenant-{uuid.uuid4()}"
    _insert_tenant(session_factory, tenant_id)
=======
def test_workflow_memory_read_write_and_run_inspection(client, db_session):
    tenant_id = f"tenant-{uuid.uuid4()}"
    db_session.add(Tenant(id=tenant_id, name="Run Tenant"))
    db_session.commit()
>>>>>>> origin/main

    seed = client.post(
        "/api/v1/memory/persist",
        json={
            "tenant_id": tenant_id,
            "scope_type": "organization",
            "scope_id": tenant_id,
            "memory_type": "fact",
            "title": "Org memory",
            "content": "This org has persistent context.",
        },
    )
    assert seed.status_code == 201

<<<<<<< HEAD
    skill = client.post(
        "/api/v1/skills",
        json={
            "tenant_id": tenant_id,
            "name": "Support Style",
            "slug": f"support-style-{uuid.uuid4().hex[:8]}",
            "description": "Respond with concise, polite tone",
            "skill_type": "prompt_skill",
            "scope_type": "organization",
            "scope_id": tenant_id,
            "status": "active",
        },
    )
    assert skill.status_code == 200
    skill_id = skill.json()["id"]

    version = client.post(
        f"/api/v1/skills/{skill_id}/versions",
        json={
            "skill_id": skill_id,
            "version_number": 1,
            "content_json": '{"instruction": "Use concise polite tone"}',
            "is_current": True,
        },
    )
    assert version.status_code == 200

    workflow_id = _create_workflow(client, tenant_id)

    run = client.post(
        f"/api/v1/workflows/{workflow_id}/run",
        json={"persist_memory": True, "persist_scope": "workflow", "persist_memory_type": "summary"},
    )
    assert run.status_code == 200, run.text
    run_id = run.json()["run_id"]

    detail = client.get(f"/api/v1/workflows/{workflow_id}/runs/{run_id}")
    assert detail.status_code == 200
    payload = detail.json()

    assert len(payload["memory_read_ids"]) >= 1
    assert len(payload["memory_written_ids"]) == 1
    assert len(payload["resolved_skills"]) >= 1

    inspection = client.get(f"/api/v1/memory/runs/{run_id}")
    assert inspection.status_code == 200
    assert inspection.json()["memory_written_ids"] == payload["memory_written_ids"]
=======
    workflow_id = _create_workflow(client, tenant_id)

    run1 = client.post(f"/api/v1/workflows/{workflow_id}/run")
    assert run1.status_code == 200, run1.text
    run1_id = run1.json()["run_id"]

    detail1 = client.get(f"/api/v1/workflows/{workflow_id}/runs/{run1_id}")
    assert detail1.status_code == 200
    assert len(detail1.json()["memory_read_ids"]) >= 1

    run2 = client.post(
        f"/api/v1/workflows/{workflow_id}/run",
        json={"persist_memory": True, "persist_scope": "workflow", "persist_memory_type": "summary"},
    )
    assert run2.status_code == 200, run2.text
    run2_id = run2.json()["run_id"]

    detail2 = client.get(f"/api/v1/workflows/{workflow_id}/runs/{run2_id}")
    assert detail2.status_code == 200
    assert len(detail2.json()["memory_written_ids"]) == 1

    inspection = client.get(f"/api/v1/memory/runs/{run2_id}")
    assert inspection.status_code == 200
    assert inspection.json()["memory_written_ids"] == detail2.json()["memory_written_ids"]
>>>>>>> origin/main
