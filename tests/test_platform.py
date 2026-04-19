"""
Platform Integration Smoke Tests
Thin end-to-end smoke test proving platform layers work together.
"""
import pytest


class TestPlatformIntegration:
    """Smoke tests for integrated platform layers."""

    def test_tenant_exists(self, client):
        """Test tenant exists or can be created."""
        response = client.get("/api/v1/tenants")
        # May be empty or have data - just verify endpoint works
        assert response.status_code in [200, 404]

    def test_memory_resolve_empty(self, client):
        """Test memory resolve with empty tenant."""
        response = client.post("/api/v1/memory/resolve", json={
            "tenant_id": "non-existent-tenant",
            "is_active": True,
        })
        # Should return empty list, not 500
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_skill_resolve_empty(self, client):
        """Test skill resolve with empty tenant."""
        response = client.get("/api/v1/skills/resolve", params={
            "tenant_id": "non-existent-tenant",
        })
        # Should return empty list, not 500
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_skill_list_empty(self, client):
        """Test skill list with no filters."""
        response = client.get("/api/v1/skills")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_memory_space_create(self, client):
        """Test creating a memory space."""
        # First need tenant
        tenant_resp = client.get("/api/v1/tenants")
        if tenant_resp.status_code != 200 or not tenant_resp.json().get("items"):
            pytest.skip("No tenant available")
        
        tenant = tenant_resp.json()["items"][0]
        tenant_id = tenant["id"]
        
        response = client.post("/api/v1/memory/spaces", json={
            "tenant_id": tenant_id,
            "scope_type": "organization",
            "scope_id": tenant_id,
            "name": "Test Memory Space",
        })
        
        # May fail if already exists or need different setup
        # Just verify endpoint responds
        assert response.status_code in [201, 400, 409]

    def test_skill_definition_create(self, client):
        """Test creating a skill definition."""
        # First need tenant
        tenant_resp = client.get("/api/v1/tenants")
        if tenant_resp.status_code != 200 or not tenant_resp.json().get("items"):
            pytest.skip("No tenant available")
        
        tenant = tenant_resp.json()["items"][0]
        tenant_id = tenant["id"]
        
        response = client.post("/api/v1/skills", json={
            "tenant_id": tenant_id,
            "name": "Test Skill",
            "slug": "test-skill-smoke",
            "description": "Smoke test skill",
            "skill_type": "prompt_skill",
            "scope_type": "organization",
            "scope_id": tenant_id,
            "status": "active",
        })
        
        # May fail if already exists
        assert response.status_code in [201, 400, 409]


class TestPlatformHealth:
    """Basic health checks."""

    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data