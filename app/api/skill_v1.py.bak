"""
Skill API Endpoints
Phase 0 - Skill lifecycle and evaluation APIs

Admin APIs:
- GET /skills - List skills
- GET /skills/{id} - Get skill
- POST /skills - Register skill
- PATCH /skills/{id} - Update skill
- DELETE /skills/{id} - Deprecate skill
- GET /skills/{id}/versions - List versions

Internal APIs:
- GET /skills/{id}/evaluations - Get evaluations
- POST /skills/{id}/evaluate - Record evaluation
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.skill import get_skill_service

router = APIRouter(prefix="/skills", tags=["skill"])


@router.get("")
async def list_skills(
    category: Optional[str] = None,
    status: Optional[str] = None,
):
    """List skills with optional filtering."""
    service = get_skill_service()
    return service.list_skills(category=category, status=status)


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """Get skill by ID."""
    service = get_skill_service()
    skill = service.get_skill(skill_id)
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return skill


@router.post("")
async def create_skill(
    name: str,
    category: str,
    description: str = "",
    definition: Optional[dict] = None,
):
    """Register a new skill."""
    service = get_skill_service()
    skill = service.register_skill(
        name=name,
        category=category,
        description=description,
        definition=definition,
    )
    return skill


@router.patch("/{skill_id}")
async def update_skill(skill_id: str, updates: dict):
    """Update skill configuration."""
    service = get_skill_service()
    success = service.update_skill(skill_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return {"id": skill_id, "status": "updated"}


@router.delete("/{skill_id}")
async def deprecate_skill(skill_id: str):
    """Mark skill as deprecated."""
    service = get_skill_service()
    success = service.deprecate_skill(skill_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return {"id": skill_id, "status": "deprecated"}


@router.get("/{skill_id}/versions")
async def list_skill_versions(skill_id: str):
    """Get all versions of a skill."""
    service = get_skill_service()
    versions = service.get_versions(skill_id)
    
    if versions is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return versions


@router.post("/{skill_id}/versions")
async def create_skill_version(skill_id: str, definition: dict):
    """Create a new skill version."""
    service = get_skill_service()
    version = service.create_version(skill_id, definition)
    
    if not version:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return version


@router.get("/{skill_id}/evaluations")
async def list_skill_evaluations(
    skill_id: str,
    metric_name: Optional[str] = None,
    limit: int = Query(10),
):
    """Get evaluations for a skill."""
    service = get_skill_service()
    
    # Check skill exists
    skill = service.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return service.get_evaluations(skill_id, metric_name, limit)


@router.post("/{skill_id}/evaluate")
async def record_skill_evaluation(
    skill_id: str,
    metric_name: str,
    metric_value: float,
    benchmark_value: Optional[float] = None,
    metadata: Optional[dict] = None,
):
    """Record a skill evaluation."""
    service = get_skill_service()
    
    # Check skill exists
    skill = service.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    evaluation = service.record_evaluation(
        skill_id=skill_id,
        metric_name=metric_name,
        metric_value=metric_value,
        benchmark_value=benchmark_value,
        metadata=metadata,
    )
    return evaluation


@router.get("/{skill_id}/metrics")
async def get_skill_metrics(skill_id: str):
    """Get average metrics for a skill."""
    service = get_skill_service()
    
    # Check skill exists
    skill = service.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return service.get_average_metrics(skill_id)