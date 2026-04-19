"""
Lago Billing Adapter
Real httpx adapter for Lago API - customers, subscriptions, usage, invoices
https://docs.getlago.com/api-reference/intro
"""
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

import httpx
from pydantic import BaseModel

from app.integrations.billing.base import (
    BaseBillingAdapter,
    BillingCustomer,
    BillingUsage,
    BillingInvoice,
)


class LagoSettings(BaseModel):
    """Lago API configuration."""
    base_url: str = "https://api.lago.com/api/v1"
    api_key: str = ""  # Lago API key from env LAGO_API_KEY
    timeout: float = 10.0


class LagoBillingAdapter(BaseBillingAdapter):
    """Lago billing provider implementation."""

    def __init__(self, settings: Optional[LagoSettings] = None):
        # Load settings from env if not provided
        api_key = settings.api_key if settings else os.environ.get("LAGO_API_KEY", "")
        base_url = settings.base_url if settings else os.environ.get("LAGO_BASE_URL", "https://api.lago.com/api/v1")
        
        self._settings = LagoSettings(
            api_key=api_key,
            base_url=base_url,
        )
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )

    def get_provider_name(self) -> str:
        return "lago"

    def _map_customer(self, data: Dict[str, Any]) -> BillingCustomer:
        """Map Lago customer to normalized format."""
        # Lago customer structure
        external_id = data.get("external_id", "")
        subscription = data.get("subscription", {}) or {}
        plan = subscription.get("plan", {}) or {}
        
        return BillingCustomer(
            customer_id=external_id,
            tenant_id=external_id,  # Map to tenant
            email=data.get("email", ""),
            plan_name=plan.get("name", "free"),
            status=subscription.get("status", "active"),
            current_period_start=subscription.get("created_at"),
            current_period_end=subscription.get("period_updated_at"),
            metadata=data.get("metadata", {}),
        )

    def _map_usage(self, data: Dict[str, Any], metric_name: str) -> BillingUsage:
        """Map Lago usage record."""
        return BillingUsage(
            metric_name=metric_name,
            quantity=data.get("quantity", 0),
            unit=data.get("unit", "units"),
            period_start=datetime.fromisoformat(data.get("period_from", "2024-01-01")) if data.get("period_from") else datetime.now(),
            period_end=datetime.fromisoformat(data.get("period_to", "2024-12-31")) if data.get("period_to") else datetime.now(),
            cost=data.get("amount_cents", 0) / 100 if data.get("amount_cents") else None,
            metadata=data,
        )

    def _map_invoice(self, data: Dict[str, Any]) -> BillingInvoice:
        """Map Lago invoice."""
        return BillingInvoice(
            invoice_id=data.get("number", ""),
            customer_id=data.get("customer_id", ""),
            amount_due=data.get("amount_cents", 0) / 100,
            amount_paid=data.get("amount_paid_cents", 0) / 100,
            currency=data.get("currency", "usd").upper(),
            status=data.get("status", "draft"),
            due_date=datetime.fromisoformat(data.get("due_date", "")) if data.get("due_date") else None,
            lines=data.get("lines", []),
            metadata=data,
        )

    async def get_customer(self, tenant_id: str) -> Optional[BillingCustomer]:
        """Get customer by external_id."""
        try:
            resp = self._client.get(f"/customers/{tenant_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json().get("customer", {})
            return self._map_customer(data)
        except httpx.HTTPError:
            return None

    async def get_usage(
        self,
        tenant_id: str,
        metric_name: str,
        period_start: datetime,
        period_end: datetime,
    ) -> List[BillingUsage]:
        """Get usage for a metric."""
        try:
            params = {
                "external_customer_id": tenant_id,
                "metric_code": metric_name,
                "from": period_start.isoformat(),
                "to": period_end.isoformat(),
            }
            resp = self._client.get("/billable_metrics/usage", params=params)
            resp.raise_for_status()
            usages = resp.json().get("usage", [])
            return [self._map_usage(u, metric_name) for u in usages]
        except httpx.HTTPError:
            return []

    async def get_invoices(
        self,
        tenant_id: str,
        limit: int = 10,
    ) -> List[BillingInvoice]:
        """Get recent invoices."""
        try:
            params = {"external_customer_id": tenant_id, "page": 1, "per_page": limit}
            resp = self._client.get("/invoices", params=params)
            resp.raise_for_status()
            invoices = resp.json().get("invoices", [])
            return [self._map_invoice(inv) for inv in invoices]
        except httpx.HTTPError:
            return []

    async def check_limits(
        self,
        tenant_id: str,
        limits: Dict[str, float],
    ) -> Dict[str, bool]:
        """Check if tenant has not exceeded limits."""
        results = {}
        for metric, limit in limits.items():
            # Get current usage for the metric
            now = datetime.now()
            # Default to last 30 days
            period_end = now
            period_start = now - datetime.timedelta(days=30)
            
            usages = await self.get_usage(tenant_id, metric, period_start, period_end)
            total_usage = sum(u.quantity for u in usages)
            results[metric] = total_usage < limit
        return results

    def close(self):
        """Close httpx client."""
        self._client.close()
