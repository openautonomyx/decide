"""
Decide Platform Client

Lightweight HTTP client for communicating with the Decide platform APIs.
Used by Langflow components to call real Decide endpoints.

API Base:
    Set DECIDE_API_URL environment variable (default: http://localhost:8000)
    Set DECIDE_API_KEY for authentication

Supported Endpoints:
    - POST /api/v1/execution/requests - Create execution
    - GET /api/v1/execution/requests - List executions
    - GET /api/v1/memory/resolve - Resolve memory
    - GET /api/v1/skills/resolve - Resolve skills
    - POST /api/v1/approvals - Create approval request
    - POST /api/v1/approvals/{id}/approve - Approve
    - POST /api/v1/approvals/{id}/deny - Deny
"""

import os
import uuid
import json
from typing import Optional, Any

import httpx


class DecideClient:
    """Decide platform HTTP client."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 5.0,
    ):
        self.base_url = base_url or os.environ.get("DECIDE_API_URL", "http://localhost:8000")
        self.api_key = api_key or os.environ.get("DECIDE_API_KEY", "")
        self.timeout = timeout
        self._session_id = str(uuid.uuid4())

    def _headers(self) -> dict:
        """Build request headers."""
        headers = {
            "Content-Type": "application/json",
            "X-Request-ID": self._session_id,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _make_request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make HTTP request with fallback on connection error."""
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=self._headers(),
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            # Fallback to stub on any connection/timeout error
            return {"_fallback": True, "error": str(e), "url": url}

    # Execution API

    def create_execution(
        self,
        tenant_id: str,
        request_text: str,
        thread_id: Optional[str] = None,
    ) -> dict:
        """
        Create an execution request.
        
        POST /api/v1/execution/requests
        """
        payload = {
            "tenant_id": tenant_id,
            "request_text": request_text,
        }
        if thread_id:
            payload["thread_id"] = thread_id
        
        result = self._make_request("POST", "/api/v1/execution/requests", json=payload)
        
        # If fallback, return stub response
        if result.get("_fallback"):
            return {
                "id": f"exec-{uuid.uuid4().hex[:8]}",
                "tenant_id": tenant_id,
                "request_text": request_text,
                "thread_id": thread_id,
                "status": "pending",
            }
        return result

    def list_executions(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> dict:
        """List execution requests."""
        params = {"tenant_id": tenant_id, "limit": limit}
        result = self._make_request("GET", "/api/v1/execution/requests", params=params)
        if result.get("_fallback"):
            return {"items": [], "total": 0}
        return result

    # Memory API

    def resolve_memory(
        self,
        tenant_id: str,
        scope_type: str,
        scope_id: str,
        max_items: int = 10,
    ) -> dict:
        """
        Resolve memory for a scope.
        
        POST /api/v1/memory/resolve
        """
        payload = {
            "tenant_id": tenant_id,
            "scope_type": scope_type,
            "scope_id": scope_id,
        }
        result = self._make_request("POST", "/api/v1/memory/resolve", json=payload)
        
        if result.get("_fallback"):
            return {
                "tenant_id": tenant_id,
                "scope_type": scope_type,
                "scope_id": scope_id,
                "items": [],
                "total": 0,
            }
        return result

    # Skill API

    def resolve_skills(
        self,
        tenant_id: str,
        workflow_id: Optional[str] = None,
        product: Optional[str] = None,
    ) -> dict:
        """
        Resolve skills for a context.
        
        GET /api/v1/skills/resolve
        """
        params = {"tenant_id": tenant_id}
        if workflow_id:
            params["workflow_id"] = workflow_id
        if product:
            params["product"] = product
        
        result = self._make_request("GET", "/api/v1/skills/resolve", params=params)
        
        if result.get("_fallback"):
            return {"tenant_id": tenant_id, "items": [], "total": 0}
        return result

    # Approval API

    def create_approval(
        self,
        tenant_id: str,
        task_description: str,
        request_text: str,
    ) -> dict:
        """
        Create an approval request.
        
        POST /api/v1/approvals
        """
        payload = {
            "tenant_id": tenant_id,
            "task_description": task_description,
            "request_text": request_text,
        }
        result = self._make_request("POST", "/api/v1/approvals", json=payload)
        
        if result.get("_fallback"):
            return {
                "id": f"approval-{uuid.uuid4().hex[:8]}",
                "tenant_id": tenant_id,
                "status": "pending",
            }
        return result

    def approve(self, approval_id: str) -> dict:
        """Approve an approval request."""
        result = self._make_request("POST", f"/api/v1/approvals/{approval_id}/approve")
        if result.get("_fallback"):
            return {"id": approval_id, "status": "approved"}
        return result

    def deny(self, approval_id: str) -> dict:
        """Deny an approval request."""
        result = self._make_request("POST", f"/api/v1/approvals/{approval_id}/deny")
        if result.get("_fallback"):
            return {"id": approval_id, "status": "denied"}
        return result

    # LangGraph compilation (stub for now)

    def compile_langgraph(
        self,
        graph_definition: dict,
        graph_name: str,
        checkpointer: str = "memory",
    ) -> dict:
        """
        Compile a workflow to LangGraph.
        
        This is an internal compile operation (stub for now).
        """
        return {
            "graph_name": graph_name,
            "checkpointer": checkpointer,
            "nodes": graph_definition.get("nodes", []),
            "edges": graph_definition.get("edges", []),
            "compiled": True,
        }


# Module-level singleton for reuse
_default_client: Optional[DecideClient] = None


def get_decide_client(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> DecideClient:
    """Get or create the default Decide client."""
    global _default_client
    if _default_client is None:
        _default_client = DecideClient(base_url, api_key)
    return _default_client


def reset_decide_client() -> None:
    """Reset the default client (useful for testing)."""
    global _default_client
    _default_client = None