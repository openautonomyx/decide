# Framework Adapter Base Interface
# Abstract base class for framework translation layers
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class FrameworkType(str, Enum):
    """Supported framework types for import/export."""
    LANGFLOW = "langflow"
    LANGGRAPH = "langgraph"
    LANGCHAIN = "langchain"
    AUTOGEN = "autogen"
    CAMELAI = "camelai"


# Framework capability profile
@dataclass
class FrameworkCapabilityProfile:
    """Describes what a framework can do."""
    framework_type: FrameworkType
    supports_stateful_execution: bool = False
    supports_parallel_execution: bool = False
    supports_conditional_branches: bool = False
    supports_loops: bool = False
    supports_tool_binding: bool = False
    supports_human_in_loop: bool = False
    supports_memory_persistence: bool = False
    supports_streaming: bool = False
    supports_async: bool = False
    supports_multi_agent: bool = False
    supported_input_modes: List[str] = field(default_factory=list)
    supported_output_modes: List[str] = field(default_factory=list)
    version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# Framework import result
@dataclass
class FrameworkImportResult:
    """Result of importing a workflow from an external framework."""
    success: bool
    workflow_data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    source_framework: Optional[FrameworkType] = None
    import_metadata: Dict[str, Any] = field(default_factory=dict)


# Framework compile result
@dataclass
class FrameworkCompileResult:
    """Result of compiling a Decide workflow to an external framework."""
    success: bool
    compiled_output: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    target_framework: Optional[FrameworkType] = None
    compile_metadata: Dict[str, Any] = field(default_factory=dict)


class BaseFrameworkAdapter(ABC):
    """Abstract base class for framework translation adapters."""

    @abstractmethod
    def get_framework_type(self) -> FrameworkType:
        """Return the framework type this adapter handles."""
        pass

    @abstractmethod
    def get_capabilities(self) -> FrameworkCapabilityProfile:
        """Return the capability profile for this framework."""
        pass

    @abstractmethod
    async def import_workflow(self, raw_data: Dict[str, Any]) -> FrameworkImportResult:
        """
        Import a workflow from the external framework format.
        Returns a FrameworkImportResult with the imported workflow data.
        """
        pass

    @abstractmethod
    async def compile_workflow(
        self,
        workflow_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ) -> FrameworkCompileResult:
        """
        Compile a Decide workflow to the external framework format.
        Returns a FrameworkCompileResult with the compiled output.
        """
        pass

    def validate_import(self, raw_data: Dict[str, Any]) -> List[str]:
        """
        Validate raw import data before processing.
        Returns list of validation errors (empty if valid).
        """
        return []

    def validate_compile_input(
        self,
        workflow_data: Dict[str, Any],
    ) -> List[str]:
        """
        Validate workflow data before compiling.
        Returns list of validation errors (empty if valid).
        """
        return []