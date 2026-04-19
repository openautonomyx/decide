# Gateway Adapter Base Interface
# Abstract base class for external gateway providers
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class GatewayContext:
    """Normalized gateway context for a request."""
    request_id: str
    tenant_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatewayDecision:
    """Gateway decision result."""
    allowed: bool
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseGatewayAdapter(ABC):
    """Abstract base class for external gateway providers."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider identifier."""
        pass

    @abstractmethod
    async def evaluate_request(
        self,
        context: GatewayContext,
        policy_name: str,
    ) -> GatewayDecision:
        """
        Evaluate a request against a gateway policy.
        Returns allow/deny decision with reasons.
        """
        pass

    @abstractmethod
    async def get_policy(self, policy_name: str) -> Optional[Dict[str, Any]]:
        """Get policy configuration from gateway."""
        pass