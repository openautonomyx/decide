# Framework Adapter Factory
# Factory for creating and accessing framework adapters
from typing import Dict, Optional, List
from app.integrations.frameworks.base import (
    BaseFrameworkAdapter,
    FrameworkType,
    FrameworkCapabilityProfile,
    FrameworkImportResult,
    FrameworkCompileResult,
)


# Global registry of framework adapters
_adapters: Dict[FrameworkType, BaseFrameworkAdapter] = {}


def register_adapter(adapter: BaseFrameworkAdapter) -> None:
    """Register a framework adapter."""
    _adapters[adapter.get_framework_type()] = adapter


def get_adapter(framework_type: FrameworkType) -> Optional[BaseFrameworkAdapter]:
    """Get an adapter by framework type."""
    return _adapters.get(framework_type)


def list_framework_types() -> List[FrameworkType]:
    """List all registered framework types."""
    return list(_adapters.keys())


def get_capabilities(framework_type: FrameworkType) -> Optional[FrameworkCapabilityProfile]:
    """Get the capability profile for a framework."""
    adapter = get_adapter(framework_type)
    if adapter:
        return adapter.get_capabilities()
    return None


async def import_workflow(
    framework_type: FrameworkType,
    raw_data: dict,
) -> FrameworkImportResult:
    """Import a workflow from an external framework."""
    adapter = get_adapter(framework_type)
    if not adapter:
        return FrameworkImportResult(
            success=False,
            errors=[f"No adapter registered for framework: {framework_type}"],
        )
    return await adapter.import_workflow(raw_data)


async def compile_workflow(
    framework_type: FrameworkType,
    workflow_data: dict,
    options: Optional[dict] = None,
) -> FrameworkCompileResult:
    """Compile a Decide workflow to an external framework."""
    adapter = get_adapter(framework_type)
    if not adapter:
        return FrameworkCompileResult(
            success=False,
            errors=[f"No adapter registered for framework: {framework_type}"],
        )
    return await adapter.compile_workflow(workflow_data, options)


def register_all_adapters() -> None:
    """Register all available framework adapters.
    
    Import individual adapters to register them.
    """
    from app.integrations.frameworks.langflow_adapter import LangflowAdapter
    from app.integrations.frameworks.langgraph_compiler import LangGraphCompiler
    
    register_adapter(LangflowAdapter())
    register_adapter(LangGraphCompiler())