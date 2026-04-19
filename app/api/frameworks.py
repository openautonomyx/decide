# Framework API Router
# Thin API endpoints for framework integration
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.integrations.frameworks import (
    FrameworkType,
    FrameworkCapabilityProfile,
    FrameworkImportResult,
    FrameworkCompileResult,
    list_framework_types,
    get_capabilities,
    import_workflow,
    compile_workflow,
    register_all_adapters,
)
from app.integrations.frameworks.base import BaseFrameworkAdapter


router = APIRouter(prefix="/frameworks", tags=["frameworks"])


# Response models
class FrameworkInfo(BaseModel):
    name: str
    type: str
    capabilities: Optional[FrameworkCapabilityProfile] = None


class CapabilitiesResponse(BaseModel):
    framework: str
    capabilities: FrameworkCapabilityProfile


class CompileRequest(BaseModel):
    workflow_data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


class CompileResponse(BaseModel):
    success: bool
    compiled_output: Optional[Dict[str, Any]] = None
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


@router.get("")
async def list_frameworks() -> List[FrameworkInfo]:
    """List all registered frameworks."""
    register_all_adapters()
    frameworks = []
    
    for fw_type in list_framework_types():
        caps = get_capabilities(fw_type)
        frameworks.append(FrameworkInfo(
            name=fw_type.value,
            type=fw_type.value,
            capabilities=caps,
        ))
    
    return frameworks


@router.get("/{framework}/capabilities")
async def get_framework_capabilities(
    framework: str,
) -> CapabilitiesResponse:
    """Get the capability profile for a specific framework."""
    register_all_adapters()
    
    try:
        fw_type = FrameworkType(framework.lower())
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown framework: {framework}",
        )
    
    caps = get_capabilities(fw_type)
    if not caps:
        raise HTTPException(
            status_code=404,
            detail=f"No adapter registered for framework: {framework}",
        )
    
    return CapabilitiesResponse(
        framework=fw_type.value,
        capabilities=caps,
    )