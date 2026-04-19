# Gateway Adapter Factory
# Resolves and manages gateway provider adapters
from typing import Optional, Dict, Type
from app.integrations.gateway.base import BaseGatewayAdapter


# Registry of available adapters
_ADAPTER_REGISTRY: Dict[str, Type[BaseGatewayAdapter]] = {}


def register_gateway_adapter(adapter_class: Type[BaseGatewayAdapter]) -> None:
    """Register a gateway adapter."""
    instance = adapter_class()
    _ADAPTER_REGISTRY[instance.get_provider_name()] = adapter_class


def get_gateway_adapter(provider_name: str) -> Optional[BaseGatewayAdapter]:
    """Get a gateway adapter instance by provider name."""
    adapter_class = _ADAPTER_REGISTRY.get(provider_name)
    if adapter_class:
        return adapter_class()
    return None


def list_gateway_providers() -> list[str]:
    """List all registered provider names."""
    return list(_ADAPTER_REGISTRY.keys())