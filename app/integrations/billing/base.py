# Billing Adapter Base Interface
# Abstract base class for external billing/subscription providers
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BillingCustomer:
    """Normalized customer billing info."""
    customer_id: str
    tenant_id: str
    email: str
    plan_name: str
    status: str  # active, past_due, canceled, trialing
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BillingUsage:
    """Normalized usage record."""
    metric_name: str
    quantity: float
    unit: str
    period_start: datetime
    period_end: datetime
    cost: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BillingInvoice:
    """Normalized invoice."""
    invoice_id: str
    customer_id: str
    amount_due: float
    amount_paid: float
    currency: str
    status: str  # draft, open, paid, void, uncollectible
    due_date: Optional[datetime] = None
    lines: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseBillingAdapter(ABC):
    """Abstract base class for external billing providers."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider identifier."""
        pass

    @abstractmethod
    async def get_customer(self, tenant_id: str) -> Optional[BillingCustomer]:
        """Get customer billing info for a tenant."""
        pass

    @abstractmethod
    async def get_usage(
        self,
        tenant_id: str,
        metric_name: str,
        period_start: datetime,
        period_end: datetime,
    ) -> List[BillingUsage]:
        """Get usage for a specific metric."""
        pass

    @abstractmethod
    async def get_invoices(
        self,
        tenant_id: str,
        limit: int = 10,
    ) -> List[BillingInvoice]:
        """Get recent invoices."""
        pass

    @abstractmethod
    async def check_limits(
        self,
        tenant_id: str,
        limits: Dict[str, float],
    ) -> Dict[str, bool]:
        """Check if tenant has not exceeded limits."""
        pass