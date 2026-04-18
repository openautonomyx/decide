"""
Tool Registry Service
Phase 0 - Tool registry and governance

This service provides:
- Tool registration and discovery
- Tool governance and approval
- Tool category management

Status: IMPLEMENTED (internal + admin APIs)
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolRegistryService:
    """
    Tool registry and governance service.
    
    Manages tool registration, approval, and discovery.
    """
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, Dict[str, Any]] = {}
    
    # ========== Tool Management ==========
    
    def register_tool(
        self,
        name: str,
        category: str,
        description: str = "",
        schema: Optional[Dict[str, Any]] = None,
        handler: str = "",
        requires_approval: bool = False,
        risk_level: str = "low",
    ) -> Dict[str, Any]:
        """Register a new tool."""
        import uuid
        tool_id = f"tool-{uuid.uuid4().hex[:12]}"
        
        tool = {
            "id": tool_id,
            "name": name,
            "category": category,
            "description": description,
            "version": "1.0.0",
            "status": "active",
            "schema": schema or {},
            "handler": handler,
            "requires_approval": requires_approval,
            "risk_level": risk_level,  # low, medium, high, critical
            "enabled": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        self._tools[tool_id] = tool
        logger.info(f"Registered tool: {name} ({tool_id})")
        return tool
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool by ID."""
        return self._tools.get(tool_id)
    
    def get_tool_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool by name."""
        for tool in self._tools.values():
            if tool["name"] == name:
                return tool
        return None
    
    def list_tools(
        self,
        category: Optional[str] = None,
        enabled_only: bool = False,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List tools with optional filtering."""
        tools = list(self._tools.values())
        
        if category:
            tools = [t for t in tools if t["category"] == category]
        if enabled_only:
            tools = [t for t in tools if t.get("enabled", True)]
        if status:
            tools = [t for t in tools if t.get("status") == status]
        
        return tools
    
    def update_tool(self, tool_id: str, updates: Dict[str, Any]) -> bool:
        """Update tool configuration."""
        if tool_id not in self._tools:
            return False
        self._tools[tool_id].update(updates)
        self._tools[tool_id]["updated_at"] = datetime.utcnow()
        return True
    
    def deprecate_tool(self, tool_id: str) -> bool:
        """Mark tool as deprecated."""
        return self.update_tool(tool_id, {"status": "deprecated"})
    
    def enable_tool(self, tool_id: str, enabled: bool = True) -> bool:
        """Enable or disable tool."""
        return self.update_tool(tool_id, {"enabled": enabled})
    
    # ========== Category Management ==========
    
    def create_category(
        self,
        name: str,
        description: str = "",
        parent_category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a tool category."""
        import uuid
        category_id = f"cat-{uuid.uuid4().hex[:12]}"
        
        category = {
            "id": category_id,
            "name": name,
            "description": description,
            "parent_category": parent_category,
            "tool_count": 0,
            "created_at": datetime.utcnow(),
        }
        
        self._categories[category_id] = category
        self._update_category_counts()
        return category
    
    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get category by ID."""
        return self._categories.get(category_id)
    
    def list_categories(self) -> List[Dict[str, Any]]:
        """List all categories."""
        self._update_category_counts()
        return list(self._categories.values())
    
    def _update_category_counts(self):
        """Update tool counts per category."""
        for category in self._categories.values():
            category_name = category["name"]
            count = len([t for t in self._tools.values() if t["category"] == category_name])
            category["tool_count"] = count
    
    # ========== Search & Discovery ==========
    
    def search_tools(
        self,
        query: str,
        category: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search tools by query."""
        results = []
        query_lower = query.lower()
        
        for tool in self._tools.values():
            if not tool.get("enabled", True):
                continue
            
            # Match against name, description, category
            matches = (
                query_lower in tool["name"].lower() or
                query_lower in tool["description"].lower() or
                query_lower in tool["category"].lower()
            )
            
            if not matches:
                continue
            
            # Apply filters
            if category and tool["category"] != category:
                continue
            if risk_level and tool["risk_level"] != risk_level:
                continue
            
            results.append(tool)
        
        return results
    
    def get_tools_by_risk(self, risk_level: str) -> List[Dict[str, Any]]:
        """Get tools by risk level."""
        return [t for t in self._tools.values() if t.get("risk_level") == risk_level]
    
    def get_tools_requiring_approval(self) -> List[Dict[str, Any]]:
        """Get tools that require approval before use."""
        return [
            t for t in self._tools.values()
            if t.get("requires_approval", False) and t.get("enabled", True)
        ]


# Global instance
_tool_registry_service: Optional[ToolRegistryService] = None


def get_tool_registry_service() -> ToolRegistryService:
    """Get global tool registry service."""
    global _tool_registry_service
    if _tool_registry_service is None:
        _tool_registry_service = ToolRegistryService()
        _initialize_default_tools(_tool_registry_service)
    return _tool_registry_service


def _initialize_default_tools(service: ToolRegistryService):
    """Initialize default tools."""
    # Create categories
    service.create_category("coding", "Code execution and manipulation tools")
    service.create_category("search", "Search and retrieval tools")
    service.create_category("memory", "Memory and storage tools")
    service.create_category("communication", "Communication and notification tools")
    
    # Register sample tools
    service.register_tool(
        name="execute_code",
        category="coding",
        description="Execute code in a sandboxed environment",
        schema={
            "type": "function",
            "function": {
                "name": "execute_code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"},
                    },
                },
            },
        },
        risk_level="high",
        requires_approval=True,
    )
    
    service.register_tool(
        name="search_web",
        category="search",
        description="Search the web for information",
        schema={
            "type": "function",
            "function": {
                "name": "search_web",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "max_results": {"type": "integer"},
                    },
                },
            },
        },
        risk_level="low",
    )
    
    service.register_tool(
        name="read_file",
        category="memory",
        description="Read a file from the filesystem",
        schema={
            "type": "function",
            "function": {
                "name": "read_file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                    },
                },
            },
        },
        risk_level="medium",
    )


__all__ = [
    "ToolRegistryService",
    "get_tool_registry_service",
]