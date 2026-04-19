"""
Workflow Smoke Tests - Basic workflow lifecycle tests
"""
import pytest


class TestWorkflowSmoke:
    """Smoke tests for workflow lifecycle."""

    def test_import_langflow(self, client, db_session):
        """Test importing a Langflow workflow."""
        from app.models.tenant_employee import Tenant
        tenant = Tenant(id="test-tenant-wf", name="Test Tenant WF")
        db_session.add(tenant)
        db_session.commit()

        flow_data = {"nodes": [], "edges": []}

        response = client.post("/api/v1/workflows/import/langflow", json={
            "tenant_id": "test-tenant-wf",
            "name": "Test Workflow",
            "description": "A test workflow",
            "flow_data": flow_data,
        })

        assert response.status_code == 201
        data = response.json()
        assert "workflow_id" in data

    def test_validate_workflow(self, client, db_session):
        """Test validating a workflow."""
        from app.models.tenant_employee import Tenant
        tenant = Tenant(id="test-tenant-wf-2", name="Test Tenant WF2")
        db_session.add(tenant)
        db_session.commit()

        flow_data = {"nodes": [], "edges": []}

        import_resp = client.post("/api/v1/workflows/import/langflow", json={
            "tenant_id": "test-tenant-wf-2",
            "name": "Test Workflow Validate",
            "flow_data": flow_data,
        })
        wf = import_resp.json()
        workflow_id = wf["workflow_id"]

        response = client.post(f"/api/v1/workflows/{workflow_id}/validate")

        assert response.status_code == 200

    def test_publish_workflow(self, client, db_session):
        """Test publishing a workflow."""
        from app.models.tenant_employee import Tenant
        tenant = Tenant(id="test-tenant-wf-3", name="Test Tenant WF3")
        db_session.add(tenant)
        db_session.commit()

        flow_data = {"nodes": [], "edges": []}

        import_resp = client.post("/api/v1/workflows/import/langflow", json={
            "tenant_id": "test-tenant-wf-3",
            "name": "Test Publish",
            "flow_data": flow_data,
        })
        wf = import_resp.json()
        workflow_id = wf["workflow_id"]

        client.post(f"/api/v1/workflows/{workflow_id}/validate")
        response = client.post(f"/api/v1/workflows/{workflow_id}/publish")

        assert response.status_code == 201

    def test_run_workflow(self, client, db_session):
        """Test running a workflow."""
        from app.models.tenant_employee import Tenant
        tenant = Tenant(id="test-tenant-wf-4", name="Test Tenant WF4")
        db_session.add(tenant)
        db_session.commit()

        flow_data = {"nodes": [], "edges": []}

        import_resp = client.post("/api/v1/workflows/import/langflow", json={
            "tenant_id": "test-tenant-wf-4",
            "name": "Test Run",
            "flow_data": flow_data,
        })
        wf = import_resp.json()
        workflow_id = wf["workflow_id"]

        client.post(f"/api/v1/workflows/{workflow_id}/validate")
        client.post(f"/api/v1/workflows/{workflow_id}/publish")
        response = client.post(f"/api/v1/workflows/{workflow_id}/run")

        assert response.status_code == 200

    def test_get_run_detail(self, client, db_session):
        """Test fetching run detail."""
        from app.models.tenant_employee import Tenant
        tenant = Tenant(id="test-tenant-wf-5", name="Test Tenant WF5")
        db_session.add(tenant)
        db_session.commit()

        flow_data = {"nodes": [], "edges": []}

        import_resp = client.post("/api/v1/workflows/import/langflow", json={
            "tenant_id": "test-tenant-wf-5",
            "name": "Test Replay",
            "flow_data": flow_data,
        })
        wf = import_resp.json()
        workflow_id = wf["workflow_id"]

        client.post(f"/api/v1/workflows/{workflow_id}/validate")
        client.post(f"/api/v1/workflows/{workflow_id}/publish")
        run_resp = client.post(f"/api/v1/workflows/{workflow_id}/run")
        run_id = run_resp.json()["run_id"]

        response = client.get(f"/api/v1/workflows/{workflow_id}/runs/{run_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == run_id


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def db_session():
    """Create test database session."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.base import Base

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])