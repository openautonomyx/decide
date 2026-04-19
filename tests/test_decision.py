"""
Decision Domain Tests

Basic API-level tests for the Decision workflow.
Uses TestClient from FastAPI for dependency-free testing.
"""
import pytest
from uuid import uuid4
from datetime import datetime

# Minimal mock for database session - tests use in-memory approach
# Note: These tests are designed to work with a running database
# or can be adapted for isolated unit testing


class TestDecisionWorkflow:
    """Test the complete decision workflow."""

    def test_decision_create(self, client, db_session):
        """Test creating a decision."""
        # Create a minimal tenant first for foreign key
        from app.models.tenant_employee import Tenant
        tenant = Tenant(id="test-tenant-1", name="Test Tenant")
        db_session.add(tenant)
        db_session.commit()

        # Create decision
        response = client.post("/api/v1/decisions", json={
            "id": "test-decision-1",
            "tenant_id": "test-tenant-1",
            "title": "Test Decision",
            "description": "A test decision",
            "category": "strategic",
            "status": "draft",
            "sponsor_type": "employee",
            "sponsor_id": "test-employee-1",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Decision"
        assert data["status"] == "draft"

    def test_add_alternative(self, client, db_session):
        """Test adding an alternative to a decision."""
        # This test assumes test_decision_create passed
        response = client.post("/api/v1/decisions/test-decision-1/alternatives", json={
            "id": "test-alt-1",
            "title": "Alternative 1",
            "description": "First option",
            "status": "active",
            "estimated_cost": "10000",
            "estimated_time_days": 30,
        })

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Alternative 1"

    def test_add_criterion(self, client, db_session):
        """Test adding a criterion."""
        response = client.post("/api/v1/decisions/test-decision-1/criteria", json={
            "id": "test-criterion-1",
            "name": "Cost",
            "description": "Implementation cost",
            "weight": 0.4,
            "scoring_method": "numeric",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["weight"] == "0.4"

    def test_add_score(self, client, db_session):
        """Test adding a score for an alternative on a criterion."""
        # First add second criterion
        client.post("/api/v1/decisions/test-decision-1/criteria", json={
            "id": "test-criterion-2",
            "name": "Time",
            "description": "Time to implement",
            "weight": 0.3,
            "scoring_method": "numeric",
        })

        # Add second alternative
        client.post("/api/v1/decisions/test-decision-1/alternatives", json={
            "id": "test-alt-2",
            "title": "Alternative 2",
            "description": "Second option",
            "status": "active",
        })

        # Add score
        response = client.post("/api/v1/decisions/test-decision-1/scores", json={
            "id": "test-score-1",
            "decision_id": "test-decision-1",
            "alternative_id": "test-alt-1",
            "criterion_id": "test-criterion-1",
            "score": 8.5,
            "rationale": "Within budget",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["score"] == "8.5"

    def test_create_recommendation(self, client, db_session):
        """Test creating a recommendation."""
        response = client.post("/api/v1/decisions/test-decision-1/recommendation", json={
            "id": "test-rec-1",
            "recommended_alternative_id": "test-alt-1",
            "summary": "Go with Alternative 1",
            "rationale": "Best overall score",
            "tradeoffs": "Higher cost but faster",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["recommended_alternative_id"] == "test-alt-1"

    def test_create_approval_step(self, client, db_session):
        """Test creating an approval step."""
        response = client.post("/api/v1/decisions/test-decision-1/approvals", json={
            "id": "test-approval-1",
            "approver_type": "employee",
            "approver_id": "test-approver-1",
            "status": "pending",
            "sequence_order": 1,
        })

        assert response.status_code == 201
        data = response.json()
        assert data["sequence_order"] == 1

    def test_get_decision_brief(self, client, db_session):
        """Test getting decision brief."""
        response = client.get("/api/v1/decisions/test-decision-1/brief")

        assert response.status_code == 200
        data = response.json()
        assert data["decision_id"] == "test-decision-1"
        assert "alternatives" in data
        assert "criteria" in data
        assert "recommendation" in data

    def test_promote_to_execution_without_approval(self, client, db_session):
        """Test promotion fails without approval."""
        response = client.post("/api/v1/decisions/test-decision-1/promote-to-execution")

        # Should fail - no approval steps approved
        assert response.status_code == 400

    def test_promote_to_execution_with_approval(self, client, db_session):
        """Test promotion succeeds with approval."""
        # Manually set approval step to approved via direct DB update
        # (In real integration test this would be done via API)
        from app.models.decision import DecisionApprovalStep
        step = db_session.query(DecisionApprovalStep).filter(
            DecisionApprovalStep.id == "test-approval-1"
        ).first()
        step.status = "approved"
        step.decided_at = datetime.utcnow()
        db_session.commit()

        # Also set decision status to approved
        from app.models.decision import Decision
        d = db_session.query(Decision).filter(
            Decision.id == "test-decision-1"
        ).first()
        d.status = "approved"
        db_session.commit()

        response = client.post("/api/v1/decisions/test-decision-1/promote-to-execution")

        assert response.status_code == 201
        data = response.json()
        assert "execution_request_id" in data
        assert data["status"] == "promoted"


# Pytest fixtures for FastAPI TestClient and in-memory DB
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

    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


# Run tests with: python -m pytest tests/test_decision.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])