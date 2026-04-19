# Trace Adapter Factory
# Resolves and manages trace provider adapters
from typing import Optional, Dict, Type
from app.integrations.trace.base import BaseTraceAdapter


# Registry of available adapters
_ADAPTER_REGISTRY: Dict[str, Type[BaseTraceAdapter]] = {}


def register_trace_adapter(adapter_class: Type[BaseTraceAdapter]) -> None:
    """Register a trace adapter."""
    instance = adapter_class()
    _ADAPTER_REGISTRY[instance.get_provider_name()] = adapter_class


def get_trace_adapter(provider_name: str) -> Optional[BaseTraceAdapter]:
    """Get a trace adapter instance by provider name."""
    adapter_class = _ADAPTER_REGISTRY.get(provider_name)
    if adapter_class:
        return adapter_class()
    return None


def list_trace_providers() -> list[str]:
    """List all registered provider names."""
    return list(_ADAPTER_REGISTRY.keys())