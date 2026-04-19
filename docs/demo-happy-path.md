# Decide Demo Happy Path (End-to-End)

## 1) Start backend

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Open:
- API docs: `http://localhost:8000/docs`
- Demo UI: `http://localhost:8000/api/v1/demo`

## 2) Tenant setup

1. `POST /api/v1/tenants` to create tenant.
2. Save `tenant_id` for all downstream calls.

## 3) Persistent memory setup

1. `POST /api/v1/memory/persist` with:
   - `tenant_id`
   - `scope_type=organization`
   - `scope_id=<tenant_id>`
   - `memory_type` (`fact`, `instruction`, `summary`, etc.)
   - `title`, `content`
2. Verify with `GET /api/v1/memory/entries?tenant_id=<tenant_id>`.

## 4) Skills setup

1. `POST /api/v1/skills` with `status=active`.
2. `POST /api/v1/skills/{skill_id}/versions` with `is_current=true`.
3. Optional: bind skill to workflow via `POST /api/v1/skills/{skill_id}/bind`.

## 5) Workflow lifecycle

1. Import workflow:
   - `POST /api/v1/workflows/import/langflow` with `flow_data` (or `langflow_data`).
2. Validate:
   - `POST /api/v1/workflows/{workflow_id}/validate`
3. Publish:
   - `POST /api/v1/workflows/{workflow_id}/publish`
4. Run:
   - `POST /api/v1/workflows/{workflow_id}/run`

## 6) Run inspection

Use:
- `GET /api/v1/workflows/{workflow_id}/runs/{run_id}`
- `GET /api/v1/memory/runs/{run_id}`

Run detail now exposes:
- `memory_context`
- `memory_read_ids`
- `memory_written_ids`
- `resolved_skills`

## 7) Framework interchange flow

1. Compile only:
   - `POST /api/v1/frameworks/langgraph/compile-to-langflow`
2. Import LangGraph:
   - `POST /api/v1/frameworks/langgraph/import?tenant_id=<tenant_id>`
3. Validate/publish/run imported workflow via workflow APIs.
4. Roundtrip export:
   - `GET /api/v1/frameworks/roundtrip/{workflow_id}`

## Known practical limitations

- Workflow execution engine is intentionally lightweight and deterministic (non-LLM mocked node execution).
- No vector/semantic retrieval layer; memory retrieval is structured deterministic scope recall.
- Full integration tests expecting Postgres require a running DB; isolated tests use in-memory SQLite.
