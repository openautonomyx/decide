# Identity Integration Module
# Pluggable identity providers for Decide

from app.integrations.identity.base import (
    BaseIdentityAdapter,
    NormalizedIdentity,
    ConstraintEvaluationResult,
)
from app.integrations.identity.factory import get_adapter, list_providers, register_adapter

__all__ = [
    "BaseIdentityAdapter",
    "NormalizedIdentity", 
    "ConstraintEvaluationResult",
    "get_adapter",
    "list_providers",
    "register_adapter",
]