# Identity Adapter Factory
# Resolves and manages identity provider adapters
from typing import Optional, Dict, Type
from app.integrations.identity.base import BaseIdentityAdapter


# Registry of available adapters
_ADAPTER_REGISTRY: Dict[str, Type[BaseIdentityAdapter]] = {}


def register_adapter(adapter_class: Type[BaseIdentityAdapter]) -> None:
    """Decorator to register an identity adapter."""
    # Create instance to get provider name
    instance = adapter_class()
    _ADAPTER_REGISTRY[instance.get_provider_name()] = adapter_class


def get_adapter(provider_name: str) -> Optional[BaseIdentityAdapter]:
    """Get an adapter instance by provider name."""
    adapter_class = _ADAPTER_REGISTRY.get(provider_name)
    if adapter_class:
        return adapter_class()
    return None


def list_providers() -> list[str]:
    """List all registered provider names."""
    return list(_ADAPTER_REGISTRY.keys())


# Import and register built-in adapters
from app.integrations.identity import autonomyx_agent_identity  # noqa: F401, E402