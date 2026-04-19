# Autonomyx Agent Identity Adapter
# Concrete adapter for openautonomyx/autonomyx-agent-identity
import os
import json
import httpx
from datetime import datetime
from typing import Optional, Dict, Any

from app.integrations.identity.base import (
    BaseIdentityAdapter,
    NormalizedIdentity,
    ConstraintEvaluationResult,
)
from app.integrations.identity.factory import register_adapter


class AutonomyxAgentIdentityAdapter(BaseIdentityAdapter):
    """Adapter for Autonomyx Agent Identity service."""

    def __init__(self):
        self.base_url = os.getenv("AGENT_IDENTITY_URL", "http://agent-identity:8000")
        self.api_key = os.getenv("AGENT_IDENTITY_API_KEY", "")

    def get_provider_name(self) -> str:
        return "autonomyx_agent_identity"

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def get_identity(self, external_identity_id: str) -> Optional[Dict[str, Any]]:
        """Fetch external identity from Autonomyx Agent Identity API."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/api/v1/execution-identities/{external_identity_id}",
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

    def normalize_identity(self, raw_data: Dict[str, Any]) -> NormalizedIdentity:
        """Normalize Autonomyx response to standard shape."""
        return NormalizedIdentity(
            external_identity_id=raw_data.get("id") or raw_data.get("execution_identity_id"),
            provider=self.get_provider_name(),
            tenant_id=raw_data.get("tenant_id", ""),
            agent_name=raw_data.get("name") or raw_data.get("agent_name"),
            agent_type=raw_data.get("agent_type"),
            sponsor_id=raw_data.get("sponsor_id"),
            owner_ids=raw_data.get("owner_ids", []),
            manager_id=raw_data.get("manager_id"),
            blueprint_id=raw_data.get("blueprint_id"),
            allowed_models=raw_data.get("allowed_models", []),
            budget_limit=raw_data.get("budget_limit"),
            tpm_limit=raw_data.get("tpm_limit"),
            expires_at=raw_data.get("expires_at"),
            status=raw_data.get("status", "unknown"),
            provider_metadata=raw_data.get("metadata", {}),
        )


# Register this adapter
register_adapter(AutonomyxAgentIdentityAdapter)