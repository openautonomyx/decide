"""
Context API Endpoints
Phase 0 - Context budget, token accounting, compaction APIs

Admin APIs:
- GET /context/budgets - List budgets
- POST /context/budgets - Create budget
- PATCH /context/budgets/{id} - Update budget

Runtime APIs:
- GET /context/budgets/{task_type} - Get budget for task type
- GET /context/budgets/check - Check if should compact
- POST /tokens/usage - Record usage
- GET /tokens/usage/{thread_id} - Get usage
- GET /tokens/usage/tenant/{tenant_id} - Get tenant total
- GET /compaction/{thread_id}/summary - Get summary
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.context import (
    get_context_budget_service,
    get_token_accounting_service,
    get_compaction_service,
)

router = APIRouter(prefix="", tags=["context"])


# ========== Budget Endpoints ==========

@router.get("/context/budgets")
async def list_budgets(tenant_id: Optional[str] = None):
    """List context budgets."""
    service = get_context_budget_service()
    return service.list_budgets(tenant_id)


@router.get("/context/budgets/{task_type}")
async def get_budget_for_task(
    tenant_id: str,
    task_type: str,
):
    """Get or create budget for task type."""
    service = get_context_budget_service()
    return service.get_budget_for_task(tenant_id, task_type)


@router.post("/context/budgets")
async def create_budget(
    tenant_id: str,
    task_type: str,
    input_budget: Optional[int] = None,
    output_budget: Optional[int] = None,
    threshold: float = 0.8,
):
    """Create a context budget."""
    service = get_context_budget_service()
    budget = service.create_budget(
        tenant_id=tenant_id,
        task_type=task_type,
        input_budget=input_budget,
        output_budget=output_budget,
        threshold=threshold,
    )
    return budget


@router.patch("/context/budgets/{budget_id}")
async def update_budget(budget_id: str, updates: dict):
    """Update budget configuration."""
    service = get_context_budget_service()
    success = service.update_budget(budget_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return {"id": budget_id, "status": "updated"}


@router.get("/context/budgets/check")
async def check_budget(
    tenant_id: str,
    task_type: str,
    current_tokens: int,
):
    """Check if current tokens exceed budget threshold."""
    service = get_context_budget_service()
    return service.check_budget(tenant_id, task_type, current_tokens)


# ========== Token Accounting Endpoints ==========

@router.post("/tokens/usage")
async def record_usage(
    thread_id: str,
    tenant_id: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    runtime_id: Optional[str] = None,
):
    """Record token usage for a request."""
    service = get_token_accounting_service()
    return service.record_usage(
        thread_id=thread_id,
        tenant_id=tenant_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        runtime_id=runtime_id,
    )


@router.get("/tokens/usage/{thread_id}")
async def get_usage(thread_id: str):
    """Get usage record for a thread."""
    service = get_token_accounting_service()
    usage = service.get_usage(thread_id)
    
    if not usage:
        raise HTTPException(status_code=404, detail="No usage record found")
    
    return usage


@router.get("/tokens/usage/tenant/{tenant_id}")
async def get_tenant_usage(tenant_id: str):
    """Get total usage for a tenant."""
    service = get_token_accounting_service()
    return service.get_total_usage(tenant_id)


@router.post("/tokens/estimate")
async def estimate_tokens(text: str):
    """Estimate tokens for text."""
    service = get_token_accounting_service()
    return {"text_length": len(text), "estimated_tokens": service.estimate_tokens(text)}


# ========== Compaction Endpoints ==========

@router.get("/compaction/{thread_id}/summary")
async def get_compaction_summary(thread_id: str):
    """Get latest compaction summary for a thread."""
    service = get_compaction_service()
    summary = service.get_latest_summary(thread_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="No summary found")
    
    return summary


@router.get("/compaction/{thread_id}/summaries")
async def list_compaction_summaries(
    thread_id: str,
    limit: int = Query(10),
):
    """List compaction summaries for a thread."""
    service = get_compaction_service()
    return service.list_summaries(thread_id, limit)


@router.post("/compaction/{thread_id}/trigger")
async def trigger_compaction(
    thread_id: str,
    tenant_id: str,
    running_summary: str,
    open_loops: list,
    tokens_before: int,
    tokens_after: int,
    step: int,
):
    """Trigger a compaction."""
    service = get_compaction_service()
    summary = service.create_summary(
        thread_id=thread_id,
        tenant_id=tenant_id,
        running_summary=running_summary,
        open_loops=open_loops,
        tokens_before=tokens_before,
        tokens_after=tokens_after,
        step=step,
    )
    return summary