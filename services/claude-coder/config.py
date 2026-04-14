import os
from pathlib import Path
from typing import Any, Dict

import yaml

BASE_DIR = Path(os.getenv("WORKSPACE_ROOT", "/workspace"))
REGISTRY_PATH = BASE_DIR / "configs" / "backends" / "registry.yaml"
POLICIES_PATH = BASE_DIR / "configs" / "backends" / "policies.yaml"


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_env_backend_config(env_prefix: str) -> Dict[str, Any]:
    return {
        "enabled": os.getenv(f"{env_prefix}_ENABLED", "false").lower() == "true",
        "provider": os.getenv(f"{env_prefix}_PROVIDER", ""),
        "model": os.getenv(f"{env_prefix}_MODEL", ""),
        "base_url": os.getenv(f"{env_prefix}_BASE_URL", ""),
        "api_key": os.getenv(f"{env_prefix}_API_KEY", ""),
    }


def mask_backend_config(config: Dict[str, Any]) -> Dict[str, Any]:
    masked = dict(config)
    if masked.get("api_key"):
        masked["api_key"] = "***"
    return masked


def load_backend_registry() -> Dict[str, Any]:
    data = load_yaml(REGISTRY_PATH)
    backends = data.get("backends", {})
    resolved = {}

    for backend_id, meta in backends.items():
        env_prefix = meta.get("env_prefix", "")
        resolved[backend_id] = {
            **meta,
            "id": backend_id,
            "config": get_env_backend_config(env_prefix) if env_prefix else {},
        }

    return resolved


def load_public_backend_registry() -> Dict[str, Any]:
    registry = load_backend_registry()
    return {
        backend_id: {
            **backend,
            "config": mask_backend_config(backend.get("config", {})),
        }
        for backend_id, backend in registry.items()
    }


def load_routing_policies() -> Dict[str, Any]:
    return load_yaml(POLICIES_PATH)
