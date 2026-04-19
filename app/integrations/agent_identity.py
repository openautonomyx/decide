# Agent Identity Integration Client
# API-reference integration to autonomyx-agent-identity
import os
import json
import httpx
from typing import Optional, Dict, Any
from datetime import datetime


class AgentIdentityClient:
    """Client for external Agent Identity service API calls."""

    def __init__(self):
        self.base_url = os.getenv("AGENT_IDENTITY_URL", "http://agent-identity:8000")
        self.api_key = os.getenv("AGENT_IDENTITY_API_KEY", "")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def get_execution_identity(
        self, identity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch external execution identity details by ID."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/api/v1/execution-identities/{identity_id}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 404:
                    return None
                else:
                    resp.raise_for_status()
        except httpx.RequestError:
            return None

    async def get_identity_status(
        self, identity_id: str
    ) -> Optional[str]:
        """Get identity status (active, expired, etc.)."""
        data = await self.get_execution_identity(identity_id)
        if data:
            return data.get("status", "unknown")
        return None

    async def get_allowed_models(
        self, identity_id: str
    ) -> Optional[list]:
        """Get allowed model list for identity."""
        data = await self.get_execution_identity(identity_id)
        if data:
            return data.get("allowed_models", [])
        return None

    async def check_identity_valid(
        self, identity_id: str, tenant_id: str
    ) -> tuple[bool, str]:
        """
        Check if identity is valid for the given tenant.
        Returns (is_valid, reason).
        """
        data = await self.get_execution_identity(identity_id)
        if not data:
            return False, "Identity not found"

        if data.get("tenant_id") != tenant_id:
            return False, "Tenant mismatch"

        status = data.get("status")
        if status != "active":
            return False, f"Identity status is {status}"

        expires_at = data.get("expires_at")
        if expires_at:
            try:
                exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if exp < datetime.now(exp.tzinfo):
                    return False, "Identity expired"
            except (ValueError, TypeError):
                pass

        return True, ""


def normalize_identity_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize external identity response into Decide-friendly shape."""
    if not data:
        return {}

    return {
        "agent_name": data.get("name") or data.get("agent_name"),
        "agent_type": data.get("agent_type"),
        "sponsor_id": data.get("sponsor_id"),
        "owner_ids_json": json.dumps(data.get("owner_ids", [])),
        "manager_id": data.get("manager_id"),
        "blueprint_id": data.get("blueprint_id"),
        "allowed_models_json": json.dumps(data.get("allowed_models", [])),
        "budget_limit": data.get("budget_limit"),
        "tpm_limit": data.get("tpm_limit"),
        "expires_at": data.get("expires_at"),
        "status": data.get("status", "active"),
        "metadata_json": json.dumps(data.get("metadata", {})),
    }


# Singleton client instance
_client: Optional[AgentIdentityClient] = None


def get_agent_identity_client() -> AgentIdentityClient:
    global _client
    if _client is None:
        _client = AgentIdentityClient()
    return _client