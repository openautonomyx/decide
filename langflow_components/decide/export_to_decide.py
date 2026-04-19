"""
ExportToDecide Component

Purpose:
    Export workflow results to the Decide platform. Posts results
    to Decide for storage and further processing.
    
Config Fields:
    - tenant_id: The tenant ID to export to
    - thread_id: Optional thread ID for continuation
    - export_format: Format to export as (json, yaml)
    
Input:
    - results: Results to export
    
Output:
    - export_ref: Reference to the exported data
    
Decide Concept Mapping:
    Uses ExecutionRequest + ExecutionHistory for tracking.
    See: app/models/execution_identity.py - ExecutionRequest, ExecutionHistory

Real API:
    POST /api/v1/execution/requests
"""

import asyncio
from langflow.base import Component
from langflow.inputs import AnyInput, StrInput
from langflow.outputs import AnyOutput

from langflow_components.decide._client import get_decide_client


class ExportToDecide(Component):
    """Export results to Decide platform."""
    
    display_name = "Export to Decide"
    description = "Exports workflow results to the Decide platform."
    documentation_urls = ["https://docs.decide.ai/export"]
    
    inputs = [
        AnyInput(
            name="results",
            display_name="Results",
            required=True,
            info="Results to export to Decide",
        ),
    ]
    
    outputs = [
        AnyOutput(
            name="export_ref",
            display_name="Export Reference",
            info="Reference to exported data in Decide",
        ),
    ]
    
    config_fields = [
        StrInput(
            name="tenant_id",
            display_name="Tenant ID",
            value="",
            info="Tenant ID to export to",
        ),
        StrInput(
            name="thread_id",
            display_name="Thread ID",
            value="",
            info="Optional thread ID for continuation",
        ),
        StrInput(
            name="export_format",
            display_name="Export Format",
            value="json",
            info="Format for export (json, yaml)",
        ),
    ]
    
    def run(self) -> None:
        """
        Export results to Decide.
        
        Calls the Decide execution API with the workflow results.
        Falls back to stub if API is unavailable.
        """
        results = self.inputs.results
        tenant_id = self.config.tenant_id
        thread_id = self.config.thread_id
        export_format = self.config.export_format
        
        if not tenant_id:
            # Fall back to stub if no tenant configured
            self.re_outputs.export_ref.send({
                "tenant_id": tenant_id or "unset",
                "export_format": export_format,
                "status": "stub",
                "execution_id": "stub-execution-id",
                "error": "tenant_id required",
            })
            return
        
        # Get client and call API
        client = get_decide_client()
        
        # Format results as request text
        request_text = str(results)
        if export_format == "json":
            import json
            request_text = json.dumps(results)
        
        try:
            # Try to call real API
            response = asyncio.get_event_loop().run_until_complete(
                client.create_execution(
                    tenant_id=tenant_id,
                    request_text=request_text,
                    thread_id=thread_id or None,
                )
            )
            self.re_outputs.export_ref.send(response)
        except Exception as e:
            # Fall back to stub on API error
            self.re_outputs.export_ref.send({
                "tenant_id": tenant_id,
                "thread_id": thread_id,
                "export_format": export_format,
                "status": "stub",
                "execution_id": f"exec-{tenant_id[:8]}",
                "fallback": True,
                "error": str(e),
            })