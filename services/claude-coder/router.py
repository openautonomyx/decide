from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RouteDecision:
    backend_id: str
    backend: Dict[str, Any]
    reason: str
    fallback_order: List[str]


class BackendRoutingError(Exception):
    pass


def _backend_enabled(backend: Dict[str, Any]) -> bool:
    return bool(backend.get("config", {}).get("enabled"))


def _supports_capability(backend: Dict[str, Any], capability: str) -> bool:
    if backend.get("capability") == capability:
        return True
    return capability in backend.get("supports", [])


def _policy_matches(policy: Dict[str, Any], request: Dict[str, Any]) -> bool:
    conditions = policy.get("when", {})
    return all(request.get(key) == value for key, value in conditions.items())


def _validate_backend(
    backend_id: str,
    registry: Dict[str, Dict[str, Any]],
    capability: str,
) -> Optional[str]:
    backend = registry.get(backend_id)
    if not backend:
        return f"backend '{backend_id}' is not registered"
    if not _backend_enabled(backend):
        return f"backend '{backend_id}' is disabled"
    if not _supports_capability(backend, capability):
        return f"backend '{backend_id}' does not support capability '{capability}'"
    return None


def _first_usable_backend(
    candidates: List[str],
    registry: Dict[str, Dict[str, Any]],
    capability: str,
) -> Optional[str]:
    for backend_id in candidates:
        if _validate_backend(backend_id, registry, capability) is None:
            return backend_id
    return None


def select_backend(
    request: Dict[str, Any],
    registry: Dict[str, Dict[str, Any]],
    policies: Dict[str, Any],
) -> RouteDecision:
    capability = request.get("capability") or "coding"
    fallback_order = request.get("fallback_order") or []
    preferred_backend = request.get("preferred_backend")

    if preferred_backend:
        validation_error = _validate_backend(preferred_backend, registry, capability)
        if validation_error is None:
            return RouteDecision(
                backend_id=preferred_backend,
                backend=registry[preferred_backend],
                reason="preferred_backend override matched an enabled capable backend",
                fallback_order=fallback_order,
            )
        if not fallback_order:
            raise BackendRoutingError(validation_error)

    for policy in policies.get("routing_policies", []):
        if not _policy_matches(policy, {**request, "capability": capability}):
            continue

        policy_candidates = []
        if policy.get("use"):
            policy_candidates.append(policy["use"])
        policy_candidates.extend(policy.get("fallback_order", []))
        policy_candidates.extend(fallback_order)

        selected = _first_usable_backend(policy_candidates, registry, capability)
        if selected:
            return RouteDecision(
                backend_id=selected,
                backend=registry[selected],
                reason="routing policy matched request conditions",
                fallback_order=policy_candidates,
            )

    fallback_candidates = list(fallback_order) + [
        backend_id
        for backend_id, backend in registry.items()
        if _supports_capability(backend, capability)
    ]
    selected = _first_usable_backend(fallback_candidates, registry, capability)
    if selected:
        return RouteDecision(
            backend_id=selected,
            backend=registry[selected],
            reason="selected first enabled capable backend from fallback order",
            fallback_order=fallback_candidates,
        )

    raise BackendRoutingError(f"no enabled backend supports capability '{capability}'")
