# Trace Adapter Base Interface
# Abstract base class for external trace/observability providers
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TraceSpan:
    """Normalized trace span."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service_name: str
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status_code: Optional[str] = None
    status_message: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TraceMetric:
    """Normalized metric point."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class TraceSummary:
    """Trace summary for a request."""
    trace_id: str
    service_name: str
    operation_name: str
    duration_ms: float
    spans_count: int
    error_count: int
    timestamp: datetime


class BaseTraceAdapter(ABC):
    """Abstract base class for external trace/observability providers."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider identifier."""
        pass

    @abstractmethod
    async def send_span(self, span: TraceSpan) -> bool:
        """Send a span to the trace backend."""
        pass

    @abstractmethod
    async def send_batch(self, spans: List[TraceSpan]) -> bool:
        """Send multiple spans."""
        pass

    @abstractmethod
    async def get_trace(self, trace_id: str) -> Optional[TraceSummary]:
        """Get trace summary by ID."""
        pass

    @abstractmethod
    async def query_traces(
        self,
        service_name: Optional[str] = None,
        operation_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[TraceSummary]:
        """Query traces with filters."""
        pass

    @abstractmethod
    async def record_metric(
        self,
        metric: TraceMetric,
    ) -> bool:
        """Record a metric point."""
        pass