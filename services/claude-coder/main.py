from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from adapters import get_coding_backend
from config import (
    load_backend_registry,
    load_public_backend_registry,
    load_routing_policies,
    mask_backend_config,
)
from router import BackendRoutingError, RouteDecision, select_backend

app = FastAPI(title="Autonomyx Coding Backend Service")


class CodingTask(BaseModel):
    task_type: str = "coding"
    repo_path: str = "/workspace"
    goal: str
    capability: str = "coding"
    quality: Optional[str] = None
    locality: Optional[str] = None
    preferred_backend: Optional[str] = None
    fallback_order: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _routing_request(task: CodingTask) -> Dict[str, Any]:
    return task.model_dump(exclude_none=True)


def _public_backend(backend: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **backend,
        "config": mask_backend_config(backend.get("config", {})),
    }


def _public_decision(decision: RouteDecision) -> Dict[str, Any]:
    return {
        "backend_id": decision.backend_id,
        "reason": decision.reason,
        "fallback_order": decision.fallback_order,
        "backend": _public_backend(decision.backend),
    }


def _select_for_request(request: Dict[str, Any]) -> RouteDecision:
    return select_backend(
        request=request,
        registry=load_backend_registry(),
        policies=load_routing_policies(),
    )


@app.get("/.well-known/agent-card")
def agent_card():
    return {
        "name": "coding-service",
        "description": "Autonomyx generic coding backend service",
        "url": "http://claude-coder:8080/invoke",
        "version": "0.2.0",
        "skills": [
            {
                "id": "coding",
                "name": "coding",
                "description": "Routes coding tasks to configured coding backends",
            }
        ],
    }


@app.get("/debug/backends")
def debug_backends():
    return {
        "registry": load_public_backend_registry(),
        "policies": load_routing_policies(),
    }


@app.get("/debug/route")
def debug_route(
    capability: str = "coding",
    quality: Optional[str] = None,
    locality: Optional[str] = None,
    preferred_backend: Optional[str] = None,
    fallback_order: Optional[List[str]] = Query(default=None),
):
    request = {
        "capability": capability,
        "quality": quality,
        "locality": locality,
        "preferred_backend": preferred_backend,
        "fallback_order": fallback_order or [],
    }
    request = {key: value for key, value in request.items() if value not in (None, [], "")}

    try:
        decision = _select_for_request(request)
    except BackendRoutingError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "sample_request": request,
        "selection": _public_decision(decision),
    }


@app.post("/invoke")
async def invoke(task: CodingTask):
    try:
        decision = _select_for_request(_routing_request(task))
    except BackendRoutingError as e:
        raise HTTPException(status_code=400, detail=str(e))

    backend = get_coding_backend(decision.backend_id, decision.backend)
    result = await backend.run(task)

    return {
        **result,
        "selected_backend": decision.backend_id,
        "route_reason": decision.reason,
        "backend_config": mask_backend_config(decision.backend.get("config", {})),
        "capability": task.capability,
    }
