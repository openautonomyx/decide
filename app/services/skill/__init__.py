"""
Skill Service
Phase 0 - Skill lifecycle and evaluation

This service provides:
- Skill registration and versioning
- Skill evaluation and metrics
- Skill status management

Status: IMPLEMENTED (admin APIs + internal evaluation)
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillService:
    """
    Skill lifecycle and evaluation service.
    
    Manages skill registration, versioning, and performance evaluation.
    """
    
    def __init__(self):
        self._skills: Dict[str, Dict[str, Any]] = {}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}
        self._evaluations: Dict[str, List[Dict[str, Any]]] = {}
    
    # ========== Skill Management ==========
    
    def register_skill(
        self,
        name: str,
        category: str,
        description: str = "",
        definition: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Register a new skill."""
        import uuid
        skill_id = f"skill-{uuid.uuid4().hex[:12]}"
        
        skill = {
            "id": skill_id,
            "name": name,
            "category": category,
            "description": description,
            "version": "1.0.0",
            "status": "active",  # draft, active, deprecated
            "definition": definition or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        self._skills[skill_id] = skill
        self._versions[skill_id] = []
        self._evaluations[skill_id] = []
        
        # Record initial version
        self._versions[skill_id].append({
            "version": "1.0.0",
            "definition": definition or {},
            "created_at": datetime.utcnow(),
        })
        
        logger.info(f"Registered skill: {name} ({skill_id})")
        return skill
    
    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Get skill by ID."""
        return self._skills.get(skill_id)
    
    def get_skill_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get skill by name."""
        for skill in self._skills.values():
            if skill["name"] == name:
                return skill
        return None
    
    def list_skills(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List skills with optional filtering."""
        skills = list(self._skills.values())
        
        if category:
            skills = [s for s in skills if s["category"] == category]
        if status:
            skills = [s for s in skills if s.get("status") == status]
        
        return skills
    
    def update_skill(self, skill_id: str, updates: Dict[str, Any]) -> bool:
        """Update skill configuration."""
        if skill_id not in self._skills:
            return False
        self._skills[skill_id].update(updates)
        self._skills[skill_id]["updated_at"] = datetime.utcnow()
        return True
    
    def deprecate_skill(self, skill_id: str) -> bool:
        """Mark skill as deprecated."""
        return self.update_skill(skill_id, {"status": "deprecated"})
    
    def archive_skill(self, skill_id: str) -> bool:
        """Archive a skill."""
        return self.update_skill(skill_id, {"status": "archived"})
    
    # ========== Version Management ==========
    
    def create_version(
        self,
        skill_id: str,
        definition: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Create a new skill version."""
        if skill_id not in self._skills:
            return None
        
        skill = self._skills[skill_id]
        
        # Increment version
        current = skill["version"]
        parts = current.split(".")
        new_version = f"{parts[0]}.{int(parts[1]) + 1}.0"
        
        version_record = {
            "version": new_version,
            "definition": definition,
            "created_at": datetime.utcnow(),
        }
        
        self._versions[skill_id].append(version_record)
        self._skills[skill_id]["version"] = new_version
        self._skills[skill_id]["definition"] = definition
        self._skills[skill_id]["updated_at"] = datetime.utcnow()
        
        return version_record
    
    def get_versions(self, skill_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a skill."""
        return self._versions.get(skill_id, [])
    
    def get_version(self, skill_id: str, version: str) -> Optional[Dict[str, Any]]:
        """Get specific version of a skill."""
        for v in self._versions.get(skill_id, []):
            if v["version"] == version:
                return v
        return None
    
    # ========== Evaluation ==========
    
    def record_evaluation(
        self,
        skill_id: str,
        metric_name: str,
        metric_value: float,
        benchmark_value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record a skill evaluation."""
        import uuid
        eval_id = f"eval-{uuid.uuid4().hex[:12]}"
        
        evaluation = {
            "id": eval_id,
            "skill_id": skill_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "benchmark_value": benchmark_value,
            "metadata": metadata or {},
            "evaluated_at": datetime.utcnow(),
        }
        
        self._evaluations[skill_id].append(evaluation)
        
        logger.info(f"Recorded evaluation for skill {skill_id}: {metric_name}={metric_value}")
        return evaluation
    
    def get_evaluations(
        self,
        skill_id: str,
        metric_name: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get evaluations for a skill."""
        evaluations = self._evaluations.get(skill_id, [])
        
        if metric_name:
            evaluations = [e for e in evaluations if e["metric_name"] == metric_name]
        
        # Return most recent
        return sorted(
            evaluations,
            key=lambda e: e["evaluated_at"],
            reverse=True,
        )[:limit]
    
    def get_latest_evaluation(
        self,
        skill_id: str,
        metric_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get latest evaluation for a metric."""
        evaluations = self.get_evaluations(skill_id, metric_name, limit=1)
        return evaluations[0] if evaluations else None
    
    def get_average_metrics(self, skill_id: str) -> Dict[str, float]:
        """Get average metrics for a skill."""
        evaluations = self._evaluations.get(skill_id, [])
        
        if not evaluations:
            return {}
        
        # Group by metric name
        metrics: Dict[str, List[float]] = {}
        for eval_record in evaluations:
            name = eval_record["metric_name"]
            if name not in metrics:
                metrics[name] = []
            metrics[name].append(eval_record["metric_value"])
        
        # Calculate averages
        return {
            name: sum(values) / len(values)
            for name, values in metrics.items()
        }


# Global instance
_skill_service: Optional[SkillService] = None


def get_skill_service() -> SkillService:
    """Get global skill service."""
    global _skill_service
    if _skill_service is None:
        _skill_service = SkillService()
        _initialize_default_skills(_skill_service)
    return _skill_service


def _initialize_default_skills(service: SkillService):
    """Initialize default skills."""
    service.register_skill(
        name="code_execution",
        category="coding",
        description="Execute and test code in sandboxed environments",
        definition={"capabilities": ["python", "javascript", "bash"]},
    )
    
    service.register_skill(
        name="web_search",
        category="search",
        description="Search the web for current information",
        definition={"engines": ["tavily", "duckduckgo"]},
    )
    
    service.register_skill(
        name="code_review",
        category="analysis",
        description="Review code for issues and improvements",
        definition={"languages": ["python", "javascript", "typescript"]},
    )


__all__ = [
    "SkillService",
    "get_skill_service",
]