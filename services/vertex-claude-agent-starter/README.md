# Vertex Claude Agent Starter (FastAPI)

Production-minded Python starter for building an enterprise agent service that runs **Anthropic Claude on Google Vertex AI**.

## What this project does

- FastAPI service with `/health`, `/chat`, and `/chat/stream` (SSE).
- Anthropic Claude through Vertex AI provider wrapper.
- First-class tool calling with an extensible registry.
- Structured logging, request correlation IDs, and latency headers.
- Baseline governance controls: API key auth, tool allowlist, input/turn limits, timeout config.

## Architecture overview

```text
app/
  api/routes        # HTTP endpoints
  agents            # Base agent + Claude enterprise agent loop + memory/policies
  services          # Claude Vertex provider + DI container
  tools             # Tool interfaces, implementations, registry/dispatch
  middleware        # Request ID + latency middleware
  observability     # Structured logging
  core              # Config + security
  schemas           # Request/response models
```

### Request flow

1. Request enters FastAPI with API key authentication.
2. Middleware sets `x-request-id` and captures latency.
3. Agent loop sends messages to Claude on Vertex.
4. If Claude requests tools, tools are executed and results are returned to Claude.
5. Final answer and audit metadata are returned.

## Google Cloud / Vertex AI prerequisites

- A GCP project with Vertex AI enabled.
- IAM principal allowed to call Vertex AI model endpoints.
- A service account JSON key (or equivalent workload identity mechanism).
- Anthropic Claude model access in Vertex AI for your project/region.

## Environment variables

Copy `.env.example` to `.env` and set values:

- `SERVICE_API_KEY` – API key clients must send in `x-api-key`.
- `GOOGLE_CLOUD_PROJECT` – your GCP project id.
- `VERTEX_REGION` or `CLOUD_ML_REGION` – Vertex region.
- `GOOGLE_APPLICATION_CREDENTIALS` – path to service account credentials JSON.
- `CLAUDE_MODEL` – Claude model identifier on Vertex AI.
- `ENABLED_TOOLS` – comma-separated allowlist of tools.
- `MAX_TURNS`, `MAX_TOOL_CALLS`, `MAX_INPUT_CHARS` – runtime guardrails.

## Setup

### Option A: pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### Option B: uv

```bash
uv sync --extra dev
```

## Run locally

```bash
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run tests

```bash
pytest -q
```

## Example API calls

### Health

```bash
curl -s http://localhost:8000/health
```

### Chat

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "content-type: application/json" \
  -H "x-api-key: replace-with-long-random-key" \
  -d '{
    "message": "What is 21*2?",
    "history": []
  }'
```

### Streaming chat (SSE)

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "content-type: application/json" \
  -H "x-api-key: replace-with-long-random-key" \
  -d '{"message":"What time is it in UTC?","history":[]}'
```

You will receive events like:

- `thinking_started`
- `tool_requested`
- `tool_completed`
- `answer_chunk`
- `completed`

## Tooling model

The default tools included are:

- `calculator` (read-only)
- `current_datetime` (read-only)
- `web_search_stub` (read-only stub for enterprise search integration)

The tool registry enforces the configured allowlist and makes it easy to add new tools.

## Security and governance baseline

- API key required per request.
- Input size guardrail (`MAX_INPUT_CHARS`).
- Maximum turns and tool calls.
- Configurable timeout for model calls.
- Audit object returned in chat responses.
- Explicit tool metadata supports read-only vs side-effecting classification.

## Extensibility notes

- `BaseAgent` enables future specializations/multi-agent orchestration.
- `ConversationMemory` abstraction can be swapped for persistent storage.
- Policies are pluggable via agent `policies` list.
- Provider layer is isolated (`ClaudeVertexProvider`) for easier model/provider substitution.
