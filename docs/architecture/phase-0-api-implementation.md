# Phase 0 API Implementation

This document describes the FastAPI endpoints implemented for Phase 0 pre-orchestrator services.

---

## Overview

Phase 0 implements the API layer for the mandatory modules required before orchestrator completion:

| Module | Service | API Endpoints |
|--------|---------|---------------|
| 1. Runtime Registry | RuntimeRegistryService | 8 endpoints |
| 2. Channel/Branch/Worker | Channel/Branch/Worker/CortexService | 15 endpoints |
| 3. Tool Registry | ToolRegistryService | 13 endpoints |
| 4. Skill Lifecycle | SkillService | 10 endpoints |
| 9. Context/Compaction | ContextBudget/TokenAccounting/CompactionService | 13 endpoints |

**Total**: 59 API endpoints

---

## Runtime API (`/api/v1/runtimes`)

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/runtimes` | List all runtimes |
| GET | `/runtimes/{runtime_id}` | Get runtime by ID |
| POST | `/runtimes` | Create runtime |
| PATCH | `/runtimes/{runtime_id}` | Update runtime |

### Runtime Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/runtimes/select` | Select runtime for task type |
| GET | `/runtimes/health` | Health check summary |
| GET | `/runtimes/instances` | List instances |
| GET | `/runtimes/instances/{id}` | Get instance |

---

## Channel API (`/api/v1`)

### Channel Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/channels` | List channels |
| POST | `/channels` | Create channel |
| GET | `/channels/{id}` | Get channel |
| PATCH | `/channels/{id}` | Update channel |

### Branch Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/threads/{id}/branches` | List branches |
| POST | `/threads/{id}/branch` | Create branch |
| GET | `/branches/{id}` | Get branch |
| POST | `/branches/{id}/merge` | Merge branch |
| POST | `/branches/{id}/close` | Close branch |

### Worker Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workers` | Create worker |
| GET | `/workers/{id}` | Get worker |
| PATCH | `/workers/{id}/state` | Update state |
| POST | `/workers/{id}/start` | Start worker |
| POST | `/workers/{id}/complete` | Complete worker |
| POST | `/workers/{id}/fail` | Fail worker |

### Cortex Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cortex/{thread_id}/summary` | Get latest summary |
| GET | `/cortex/{thread_id}/summaries` | List summaries |

---

## Tool API (`/api/v1/tools`)

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tools` | List tools |
| GET | `/tools/{id}` | Get tool |
| POST | `/tools` | Register tool |
| PATCH | `/tools/{id}` | Update tool |
| DELETE | `/tools/{id}` | Deprecate tool |
| POST | `/tools/{id}/enable` | Enable/disable tool |
| GET | `/tools/categories` | List categories |

### Runtime Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tools/search` | Search tools |
| GET | `/tools/{id}/schema` | Get schema |
| GET | `/tools/risks/{level}` | Get by risk |
| GET | `/tools/approvals-required` | Get approval-required |

---

## Skill API (`/api/v1/skills`)

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/skills` | List skills |
| GET | `/skills/{id}` | Get skill |
| POST | `/skills` | Register skill |
| PATCH | `/skills/{id}` | Update skill |
| DELETE | `/skills/{id}` | Deprecate skill |
| GET | `/skills/{id}/versions` | List versions |
| POST | `/skills/{id}/versions` | Create version |

### Internal Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/skills/{id}/evaluations` | Get evaluations |
| POST | `/skills/{id}/evaluate` | Record evaluation |
| GET | `/skills/{id}/metrics` | Get average metrics |

---

## Context API (`/api/v1`)

### Budget Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/context/budgets` | List budgets |
| GET | `/context/budgets/{task_type}` | Get budget for task |
| POST | `/context/budgets` | Create budget |
| PATCH | `/context/budgets/{id}` | Update budget |
| GET | `/context/budgets/check` | Check if should compact |

### Token Accounting Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tokens/usage` | Record usage |
| GET | `/tokens/usage/{thread_id}` | Get thread usage |
| GET | `/tokens/usage/tenant/{id}` | Get tenant total |
| POST | `/tokens/estimate` | Estimate tokens |

### Compaction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/compaction/{thread_id}/summary` | Get summary |
| GET | `/compaction/{thread_id}/summaries` | List summaries |
| POST | `/compaction/{thread_id}/trigger` | Trigger compaction |

---

## Usage Examples

### Select Runtime

```bash
curl "http://localhost:8000/api/v1/runtimes/select?task_type=coding"
```

Response:
```json
{
  "runtime_id": "langgraph",
  "runtime": {
    "id": "langgraph",
    "name": "LangGraph Orchestrator",
    "type": "langgraph",
    ...
  }
}
```

### Create Branch

```bash
curl -X POST "http://localhost:8000/api/v1/threads/thread-123/branch" \
  -H "Content-Type: application/json" \
  -d '{"channel_id": "channel-456", "branch_type": "fork"}'
```

### Search Tools

```bash
curl "http://localhost:8000/api/v1/tools/search?q=code&risk_level=high"
```

### Check Budget

```bash
curl "http://localhost:8000/api/v1/context/budgets/check?tenant_id=t1&task_type=coding&current_tokens=100000"
```

Response:
```json
{
  "should_compact": true,
  "budget": {...},
  "threshold": 120000,
  "headroom": 20000
}
```

---

## Module Status Summary

| Module | Admin APIs | Runtime APIs | Status |
|--------|-----------|--------------|--------|
| 1. Runtime Registry | 4 | 4 | ✅ IMPLEMENTED |
| 2. Channel/Branch/Worker | 4 | 11 | ✅ IMPLEMENTED |
| 3. Tool Registry | 10 | 4 | ✅ IMPLEMENTED |
| 4. Skill Lifecycle | 7 | 3 | ✅ IMPLEMENTED |
| 9. Context/Compaction | 5 | 8 | ✅ IMPLEMENTED |

---

## Next Steps

1. **Policy Governance APIs** (Phase 1) - Policy CRUD, resolution
2. **Guardrails APIs** (Phase 1) - Guardrail enforcement
3. **Access Control APIs** (Phase 2) - RBAC endpoints

---

_End of Phase 0 API Implementation_