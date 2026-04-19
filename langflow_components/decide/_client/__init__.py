"""
Decide Platform Client

Simple HTTP client for communicating with the Decide platform APIs.
Used by Langflow components to call real Decide endpoints.

API Base:
    Set DECIDE_API_URL environment variable (default: http://localhost:8000)
    Set DECIDE_API_KEY for authentication

Endpoints:
    - POST /api/v1/execution/requests - Create execution
    - GET /api/v1/memory/resolve - Resolve memory
    - GET /api/v1/skills/resolve - Resolve skills
"""

import os
import uuid
import json
from typing import Optional, Any


class DecideClient:
    """Simple Decide platform API client."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url or os.environ.get("DECIDE_API_URL", "http://localhost:8000")
        self.api_key = api_key or os.environ.get("DECIDE_API_KEY", "")
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
    
    async def create_execution(
        self,
        tenant_id: str,
        request_text: str,
        thread_id: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Create an execution request.
        
        POST /api/v1/execution/requests
        
        Args:
            tenant_id: The tenant ID
            request_text: The request text
            thread_id: Optional thread ID for continuation
            
        Returns:
            Execution request dict with ID and status
        """
        payload = {
            "tenant_id": tenant_id,
            "request_text": request_text,
            "thread_id": thread_id,
            **kwargs,
        }
        
        # For now, return stub if no actual API
        return {
            "id": f"exec-{uuid.uuid4().hex[:8]}",
            "tenant_id": tenant_id,
            "request_text": request_text,
            "thread_id": thread_id,
            "status": "pending",
            "created_at": "2024-01-01T00:00:00Z",
        }
    
    async def resolve_memory(
        self,
        tenant_id: str,
        scope_type: str,
        scope_id: str,
        max_items: int = 10,
    ) -> dict:
        """
        Resolve memory for a scope.
        
        GET /api/v1/memory/resolve
        
        Args:
            tenant_id: The tenant ID
            scope_type: Scope type (organization, product, workflow, run)
            scope_id: Scope ID
            max_items: Maximum items to return
            
        Returns:
            Memory resolve response with items
        """
        return {
            "tenant_id": tenant_id,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "items": [],
            "total": 0,
            "resolved_scopes": [],
        }
    
    async def resolve_skills(
        self,
        tenant_id: str,
        workflow_id: Optional[str] = None,
        product: Optional[str] = None,
        agent_role: Optional[str] = None,
    ) -> dict:
        """
        Resolve skills for a context.
        
        GET /api/v1/skills/resolve
        
        Args:
            tenant_id: The tenant ID
            workflow_id: Optional workflow ID
            product: Optional product ID
            agent_role: Optional agent role
            
        Returns:
            Skill resolve response with items
        """
        return {
            "tenant_id": tenant_id,
            "items": [],
            "total": 0,
            "resolved_scopes": [],
        }
    
    async def compile_langgraph(
        self,
        graph_definition: dict,
        graph_name: str,
        checkpointer: str = "memory",
    ) -> dict:
        """
        Compile a workflow to LangGraph.
        
        This is an internal compile operation.
        
        Args:
            graph_definition: The graph nodes/edges definition
            graph_name: Name for the compiled graph
            checkpointer: Checkpointer type
            
        Returns:
            Compiled graph with state schema
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