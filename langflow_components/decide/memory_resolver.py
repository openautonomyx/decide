"""
MemoryResolver Component

Purpose:
    Memory context resolution. Resolves memory context from Decide's
    memory service for a given thread and user.
    
Config Fields:
    - tenant_id: Tenant ID for the memory space
    - scope_type: Scope type (organization, product, workflow, run)
    - max_history: Maximum history items to retrieve
    - include_shared: Whether to include shared memory
    
Input:
    - scope_id: The scope ID to resolve memory for
    
Output:
    - context: Resolved memory context
    - checkpoint_id: ID of the checkpoint to resume from
    
Decide Concept Mapping:
    Maps to MemoryCheckpoint + MemoryService in Decide.
    See: app/models/memory.py - MemoryCheckpoint, MemoryService

Real API:
    POST /api/v1/memory/resolve
"""

import asyncio
from langflow.base import Component
from langflow.inputs import StrInput, IntInput, BoolInput, DropdownInput
from langflow.outputs import AnyOutput

from langflow_components.decide._client import get_decide_client


class MemoryResolver(Component):
    """Memory context resolution component."""
    
    display_name = "Memory Resolver"
    description = "Resolves memory context for agent execution."
    documentation_urls = ["https://docs.decide.ai/memory-resolver"]
    
    inputs = [
        StrInput(
            name="scope_id",
            display_name="Scope ID",
            required=True,
            info="Scope ID to resolve memory for",
        ),
    ]
    
    outputs = [
        AnyOutput(
            name="context",
            display_name="Context",
            info="Resolved memory context",
        ),
        AnyOutput(
            name="checkpoint_id",
            display_name="Checkpoint ID",
            info="ID of checkpoint to resume from",
        ),
    ]
    
    config_fields = [
        StrInput(
            name="tenant_id",
            display_name="Tenant ID",
            value="",
            info="Tenant ID for memory resolution",
        ),
        DropdownInput(
            name="scope_type",
            display_name="Scope Type",
            options=["organization", "product", "workflow", "run"],
            value="workflow",
            info="Scope type for resolution",
        ),
        IntInput(
            name="max_history",
            display_name="Max History Items",
            value=10,
            info="Maximum history items to retrieve",
        ),
        BoolInput(
            name="include_shared",
            display_name="Include Shared Memory",
            value=False,
            info="Whether to include shared memory",
        ),
    ]
    
    def run(self) -> None:
        """
        Resolve memory context.
        
        Calls Decide's memory resolve API.
        Falls back to stub if API is unavailable.
        """
        scope_id = self.inputs.scope_id
        tenant_id = self.config.tenant_id
        scope_type = self.config.scope_type
        max_history = self.config.max_history
        include_shared = self.config.include_shared
        
        if not tenant_id:
            self.re_outputs.context.send({
                "scope_type": scope_type,
                "scope_id": scope_id,
                "items": [],
                "status": "stub",
            })
            self.re_outputs.checkpoint_id.send("")
            return
        
        client = get_decide_client()
        
        try:
            response = asyncio.get_event_loop().run_until_complete(
                client.resolve_memory(
                    tenant_id=tenant_id,
                    scope_type=scope_type,
                    scope_id=scope_id,
                    max_items=max_history,
                )
            )
            checkpoint_id = f"cp-{scope_id[:8]}" if scope_id else ""
            self.re_outputs.context.send(response)
            self.re_outputs.checkpoint_id.send(checkpoint_id)
        except Exception as e:
            self.re_outputs.context.send({
                "scope_type": scope_type,
                "scope_id": scope_id,
                "items": [],
                "status": "stub",
                "fallback": True,
                "error": str(e),
            })
            self.re_outputs.checkpoint_id.send("")