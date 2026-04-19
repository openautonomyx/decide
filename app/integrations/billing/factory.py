# Billing Adapter Factory
# Resolves and manages billing provider adapters
from typing import Optional, Dict, Type
from app.integrations.billing.base import BaseBillingAdapter


# Registry of available adapters
_ADAPTER_REGISTRY: Dict[str, Type[BaseBillingAdapter]] = {}


def register_billing_adapter(adapter_class: Type[BaseBillingAdapter]) -> None:
    """Register a billing adapter."""
    instance = adapter_class()
    _ADAPTER_REGISTRY[instance.get_provider_name()] = adapter_class


def get_billing_adapter(provider_name: str) -> Optional[BaseBillingAdapter]:
    """Get a billing adapter instance by provider name."""
    adapter_class = _ADAPTER_REGISTRY.get(provider_name)
    if adapter_class:
        return adapter_class()
    return None


def list_billing_providers() -> list[str]:
    """List all registered provider names."""
    return list(_ADAPTER_REGISTRY.keys())