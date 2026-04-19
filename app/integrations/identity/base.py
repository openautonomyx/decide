# Identity Adapter Base Interface
# Abstract base class for external identity providers
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


# Normalized identity shape returned by all adapters
@dataclass
class NormalizedIdentity:
    external_identity_id: str
    provider: str
    tenant_id: str
    agent_name: Optional[str] = None
    agent_type: Optional[str] = None
    sponsor_id: Optional[str] = None
    owner_ids: List[str] = field(default_factory=list)
    manager_id: Optional[str] = None
    blueprint_id: Optional[str] = None
    allowed_models: List[str] = field(default_factory=list)
    budget_limit: Optional[float] = None
    tpm_limit: Optional[int] = None
    expires_at: Optional[datetime] = None
    status: str = "unknown"
    provider_metadata: Dict[str, Any] = field(default_factory=dict)


# Constraint evaluation result
@dataclass
class ConstraintEvaluationResult:
    is_allowed: bool
    reasons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseIdentityAdapter(ABC):
    """Abstract base class for external identity providers."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider identifier (e.g., 'autonomyx_agent_identity')."""
        pass

    @abstractmethod
    async def get_identity(self, external_identity_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch raw identity data from the external provider.
        Returns None if identity not found or unreachable.
        """
        pass

    @abstractmethod
    def normalize_identity(self, raw_data: Dict[str, Any]) -> NormalizedIdentity:
        """
        Convert external provider's raw response into the normalized shape.
        """
        pass

    async def sync_identity(self, external_identity_id: str) -> Optional[NormalizedIdentity]:
        """Fetch and normalize an identity from the external provider."""
        raw = await self.get_identity(external_identity_id)
        if raw:
            return self.normalize_identity(raw)
        return None

    def evaluate_constraints(
        self,
        normalized_identity: NormalizedIdentity,
        workflow_context: Dict[str, Any],
    ) -> ConstraintEvaluationResult:
        """
        Evaluate identity constraints against workflow context.
        
        Default implementation checks:
        - tenant match
        - active status
        - not expired
        - allowed_models compatibility (if workflow uses models)
        
        Override for provider-specific constraints.
        """
        reasons = []
        
        # Tenant match
        if normalized_identity.tenant_id != workflow_context.get("tenant_id"):
            reasons.append(f"Tenant mismatch: identity tenant={normalized_identity.tenant_id}, workflow tenant={workflow_context.get('tenant_id')}")
        
        # Status check
        if normalized_identity.status != "active":
            reasons.append(f"Identity status is '{normalized_identity.status}', expected 'active'")
        
        # Expiration check
        if normalized_identity.expires_at and normalized_identity.expires_at < datetime.now(normalized_identity.expires_at.tzinfo):
            reasons.append(f"Identity expired at {normalized_identity.expires_at.isoformat()}")
        
        # Allowed models check
        workflow_models = workflow_context.get("models_used", [])
        if workflow_models and normalized_identity.allowed_models:
            models_not_allowed = [m for m in workflow_models if m not in normalized_identity.allowed_models]
            if models_not_allowed:
                reasons.append(f"Workflow uses models not in identity allowed list: {models_not_allowed}")
        
        is_allowed = len(reasons) == 0
        return ConstraintEvaluationResult(
            is_allowed=is_allowed,
            reasons=reasons,
            metadata={"provider": self.get_provider_name(), "identity_id": normalized_identity.external_identity_id},
        )