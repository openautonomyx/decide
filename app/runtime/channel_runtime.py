"""
Channel Runtime Abstraction
Runtime Architecture v2 - Base class for human-facing channel runtimes

This module provides:
- Abstract channel runtime interface
- Session/context handling
- Tool handoff support
- Response normalization
"""
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in a channel conversation"""
    role: str = "user"  # user, assistant, system
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class SessionContext(BaseModel):
    """Session context for a channel conversation"""
    session_id: str
    thread_id: str
    tenant_id: str
    user_id: Optional[str] = None
    
    # Conversation history
    messages: List[Message] = Field(default_factory=list)
    
    # Metadata
    channel_type: str = "openai_agents"
    capabilities: List[str] = Field(default_factory=lambda: ["conversation", "general"])
    
    # Agent-specific context
    agent_id: Optional[str] = None
    agent_config: Dict[str, Any] = Field(default_factory=dict)


class ChannelResponse(BaseModel):
    """Normalized response from channel runtime"""
    # Content
    message: str
    role: str = "assistant"
    
    # State
    session_id: str
    thread_id: str
    
    # Tool execution (if any)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    requires_handoff: bool = False
    handoff_reason: Optional[str] = None
    
    # Diagnostics
    latency_ms: int = 0
    tokens_used: int = 0
    model: Optional[str] = None
    
    # Error handling
    error: Optional[str] = None
    error_code: Optional[str] = None


class ChannelRuntime(ABC):
    """
    Abstract base class for channel runtimes.
    
    Channel runtimes handle human-facing conversation through
    various channels (web, Slack, Discord, etc.).
    """
    
    def __init__(self, runtime_id: str, config: Dict[str, Any]):
        self.runtime_id = runtime_id
        self.config = config
    
    @abstractmethod
    async def chat(
        self,
        session: SessionContext,
        message: str,
    ) -> ChannelResponse:
        """
        Process a chat message and return response.
        
        Args:
            session: Current session context
            message: User message content
            
        Returns:
            ChannelResponse with assistant reply
        """
        raise NotImplementedError
    
    @abstractmethod
    async def handle_tool_result(
        self,
        session: SessionContext,
        tool_call_id: str,
        tool_result: Any,
    ) -> ChannelResponse:
        """
        Handle tool execution result and continue conversation.
        
        Args:
            session: Current session context
            tool_call_id: ID of the tool call
            tool_result: Result from tool execution
            
        Returns:
            ChannelResponse with continued assistant reply
        """
        raise NotImplementedError
    
    @abstractmethod
    async def create_session(
        self,
        tenant_id: str,
        user_id: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> SessionContext:
        """
        Create a new session.
        
        Args:
            tenant_id: Tenant ID
            user_id: Optional user ID
            initial_context: Optional initial context
            
        Returns:
            New SessionContext
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Get existing session.
        
        Args:
            session_id: Session ID
            
        Returns:
            SessionContext or None if not found
        """
        raise NotImplementedError
    
    def _normalize_response(
        self,
        message: str,
        session: SessionContext,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        latency_ms: int = 0,
        tokens_used: int = 0,
        model: Optional[str] = None,
    ) -> ChannelResponse:
        """Create normalized channel response."""
        return ChannelResponse(
            message=message,
            role="assistant",
            session_id=session.session_id,
            thread_id=session.thread_id,
            tool_calls=tool_calls or [],
            requires_handoff=bool(tool_calls),
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            model=model,
        )
    
    def _error_response(
        self,
        error_message: str,
        error_code: str,
        session: SessionContext,
    ) -> ChannelResponse:
        """Create error channel response."""
        return ChannelResponse(
            message=f"Error: {error_message}",
            role="assistant",
            session_id=session.session_id,
            thread_id=session.thread_id,
            error=error_message,
            error_code=error_code,
        )


__all__ = [
    "Message",
    "SessionContext",
    "ChannelResponse",
    "ChannelRuntime",
]