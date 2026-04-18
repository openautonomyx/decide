"""
Orchestrator Router
Phase 1 - Task type detection and runtime selection
"""
import logging
import re
from typing import Optional, Dict, Any, List, Tuple

from app.orchestrator.types import TaskType, ExecutionStage, StageResult
from app.services.runtime import get_runtime_registry_service
from app.services.tool import get_tool_registry_service
from app.services.skill import get_skill_service

logger = logging.getLogger(__name__)

# Task type keywords for detection
TASK_TYPE_KEYWORDS = {
    TaskType.CODING: [
        "write code", "implement", "fix bug", "refactor", "create function",
        "create class", "debug", "test", "deploy", "build", "compile",
        "python", "javascript", "typescript", "code", "api endpoint",
    ],
    TaskType.CONVERSATION: [
        "chat", "talk", "discuss", "explain", "help me understand",
        "what is", "how does", "tell me about", "conversation",
    ],
    TaskType.AUTONOMOUS: [
        "analyze", "research", "investigate", "explore", "find patterns",
        "optimize", "improve", "automate", "discover", "gather info",
    ],
    TaskType.COLLABORATION: [
        "team", "collaborate", "share", "review together", "brainstorm",
        "meeting", "coordinate", "sync", "group",
    ],
    TaskType.RESEARCH: [
        "search", "find information", "look up", "investigate", "explore",
        "document", "compare", "benchmark", "analyze options",
    ],
    TaskType.SIMPLE: [
        "hello", "hi", "thanks", "thank you", "ok", "okay", "sure",
    ],
}


class OrchestratorRouter:
    """
    Router handles task type detection and runtime selection.
    
    Uses keyword matching for task type detection.
    Delegates to RuntimeRegistryService for runtime selection.
    """
    
    def __init__(self):
        self._runtime_service = get_runtime_registry_service()
        self._tool_service = get_tool_registry_service()
        self._skill_service = get_skill_service()
    
    def detect_task_type(
        self,
        request_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[TaskType, float]:
        """
        Detect task type from request text.
        
        Returns:
            (task_type, confidence_score)
        """
        text_lower = request_text.lower()
        scores = {}
        
        for task_type, keywords in TASK_TYPE_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            if score > 0:
                scores[task_type] = score
        
        if not scores:
            return TaskType.SIMPLE, 0.0
        
        # Return highest scoring type
        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]
        
        # Normalize confidence (0-1)
        confidence = min(max_score / 5.0, 1.0)
        
        # Override from metadata if provided
        if metadata and "task_type" in metadata:
            try:
                best_type = TaskType(metadata["task_type"])
                confidence = 1.0
            except ValueError:
                pass
        
        logger.info(f"Detected task type: {best_type.value} (confidence: {confidence})")
        return best_type, confidence
    
    def select_runtime(
        self,
        task_type: TaskType,
        tenant_id: str,
        preferred_runtime: Optional[str] = None,
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Select runtime for task type.
        
        Returns:
            (runtime_id, runtime_info)
        """
        # Use preferred runtime if specified
        if preferred_runtime:
            runtime = self._runtime_service.get_runtime(preferred_runtime)
            if runtime and runtime.get("enabled", True):
                return preferred_runtime, runtime
            logger.warning(f"Preferred runtime {preferred_runtime} not available")
        
        # Use runtime registry service for selection
        runtime_id = self._runtime_service.select_runtime(
            task_type=task_type.value,
            tenant_id=tenant_id,
        )
        
        if not runtime_id:
            return None, {}
        
        runtime = self._runtime_service.get_runtime(runtime_id)
        return runtime_id, runtime or {}
    
    def resolve_tools(
        self,
        tool_names: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Resolve tool names to tool definitions.
        
        Returns list of resolved tool definitions.
        """
        resolved = []
        
        for name in tool_names:
            tool = self._tool_service.get_tool_by_name(name)
            if tool:
                resolved.append(tool)
            else:
                logger.warning(f"Tool not found: {name}")
        
        return resolved
    
    def resolve_skills(
        self,
        skill_names: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Resolve skill names to skill definitions.
        
        Returns list of resolved skill definitions.
        """
        resolved = []
        
        for name in skill_names:
            skill = self._skill_service.get_skill_by_name(name)
            if skill:
                resolved.append(skill)
            else:
                logger.warning(f"Skill not found: {name}")
        
        return resolved
    
    def route(
        self,
        request_text: str,
        tenant_id: str,
        preferred_runtime: Optional[str] = None,
        required_tools: Optional[List[str]] = None,
        required_skills: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Full routing logic.
        
        Returns dict with:
            - task_type
            - task_confidence
            - runtime_id
            - runtime_info
            - tools
            - skills
        """
        # Detect task type
        task_type, confidence = self.detect_task_type(request_text, metadata)
        
        # Select runtime
        runtime_id, runtime_info = self.select_runtime(
            task_type=task_type,
            tenant_id=tenant_id,
            preferred_runtime=preferred_runtime,
        )
        
        # Resolve tools
        tools = self.resolve_tools(required_tools or [])
        
        # Resolve skills
        skills = self.resolve_skills(required_skills or [])
        
        return {
            "task_type": task_type,
            "task_confidence": confidence,
            "runtime_id": runtime_id,
            "runtime_info": runtime_info,
            "tools": tools,
            "skills": skills,
        }


# Global instance
_router: Optional[OrchestratorRouter] = None


def get_router() -> OrchestratorRouter:
    """Get global router."""
    global _router
    if _router is None:
        _router = OrchestratorRouter()
    return _router


__all__ = [
    "OrchestratorRouter",
    "get_router",
]