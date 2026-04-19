# Decide Persistent Memory Runbook

## Memory model

Decide persistent memory uses two durable tables:

- `memory_space`: tenant-scoped container for a memory scope (`organization`, `product`, `workflow`, `run`, `session`), with active state and metadata.
- `memory_entry`: durable memory facts/instructions/summaries with source metadata, tags, and active state.

Workflow runs now persist memory usage metadata in `workflow_run`:

- `memory_context_json`
- `memory_read_ids_json`
- `memory_written_ids_json`
- `memory_write_mode`

## Scope model and recall order

`POST /api/v1/memory/resolve` resolves memory by deterministic priority:

1. organization
2. product
3. workflow
4. run
5. session

Filter knobs:

- `tenant_id`
- scope IDs (`organization_scope_id`, `product_scope_id`, `workflow_scope_id`, `run_scope_id`, `session_scope_id`)
- `memory_type`
- `tags`
- `is_active`

## Write paths

### Explicit API write

`POST /api/v1/memory/persist`

Creates (or reuses) a scope space, then inserts a durable memory entry with metadata.

### Workflow write-back

`POST /api/v1/workflows/{workflow_id}/run` supports optional write-back:

```json
{
  "persist_memory": true,
  "persist_scope": "run",
  "persist_memory_type": "summary",
  "persist_title": "Run summary"
}
```

Write-back is explicit and recorded on run detail via `memory_written_ids`.

## Run inspection

- `GET /api/v1/workflows/{workflow_id}/runs/{run_id}` shows `memory_context`, `memory_read_ids`, `memory_written_ids`.
- `GET /api/v1/memory/runs/{run_id}` returns memory inspection payload only.

## Demo flow (prove persistence)

1. Create tenant.
2. `POST /memory/persist` at organization scope.
3. Run workflow once (`/workflows/{id}/run`) and inspect `memory_read_ids`.
4. Run workflow again; confirm previously persisted IDs still resolved.
5. Run with `persist_memory=true`; inspect `memory_written_ids` and query `/memory/entries` to confirm durable write.
