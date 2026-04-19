# Example: Langflow → Decide Integration Flow

This document shows an example of how to use the Decide component pack
to create an end-to-end flow from Langflow to the Decide platform.

## Example Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Input     │────▶│  ApprovalGate   │────▶│  SkillResolver  │
│   (request)      │     │  (tenant_id)      │     │  (tenant_id)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  PublishToLang  │◀────│ ExportToDecide   │◀────│ MemoryResolver  │
│  Graph          │     │  (tenant_id)    │     │  (tenant_id)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Verified Endpoints

These are the actual routes verified in the repo:

| Component | Endpoint | Method |
|-----------|-----------|--------|
| ExportToDecide | `/api/v1/execution/requests` | POST |
| MemoryResolver | `/api/v1/memory/resolve` | POST |
| SkillResolver | `/api/v1/skills/resolve` | GET |
| ApprovalGate | `/api/v1/approvals` | POST |
| ApprovalGate | `/api/v1/approvals/{id}` | GET |
| ApprovalGate | `/api/v1/approvals/{id}/approve` | POST |
| ApprovalGate | `/api/v1/approvals/{id}/deny` | POST |

See: `app/api/tasks.py` (exec_router, approval_router), `app/api/memory.py`, `app/api/skill.py`

## Configuration

Set the following environment variables:

```bash
# Point to your Decide API
export DECIDE_API_URL=http://localhost:8000

# Optional: API key for authentication
export DECIDE_API_KEY=your-api-key
```

## Approval Flow

The ApprovalGate component demonstrates one practical path:

1. **Create approval request** → `POST /api/v1/approvals`
2. **Check status** → `GET /api/v1/approvals/{id}`
3. **Approve** → `POST /api/v1/approvals/{id}/approve`
4. **Deny** → `POST /api/v1/approvals/{id}/deny`

Note: Real implementation would need async polling for status checks.

## API Fallback Behavior

If the Decide API is unavailable, components will:
- Return stub responses with `_fallback: true`
- Include error message in the response
- Flow continues without failure

This allows for:
- Offline development/testing
- Graceful degradation
- Easy debugging