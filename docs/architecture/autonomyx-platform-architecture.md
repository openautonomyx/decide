# AutonomyX Platform Architecture

## Purpose

AutonomyX is a decision intelligence platform for coordinating human operators, AI agents, tools, and work systems. The platform separates **decision control** from **execution**, so agents can act without bypassing approval, audit, policy, context, or accountability.

## Product Services

| Service | Responsibility |
| --- | --- |
| Decide | Operational control plane for tasks, approvals, decisions, overrides, runtime selection, and execution history. |
| Insights | Signal ingestion and decision briefing pipeline for surfacing risks, changes, recommendations, and next actions. |
| Profile | Identity, profile, relationship, preference, permission, and enrichment service for people, agents, accounts, and organizations. |
| Model Gateway | OpenAI-compatible gateway for routing model calls, quotas, virtual keys, observability, and provider abstraction. |
| MCP Fleet | Tool adapters that expose external systems as governed tools for agents and orchestrators. |

## Core Flow

1. A user, schedule, webhook, or agent creates an execution request in Decide.
2. Decide resolves tenant policy, guardrails, approvals, runtime selection, and context budget.
3. The orchestrator chooses a runtime and binds allowed tools.
4. Runtime workers execute through the model gateway and MCP tool layer.
5. Results, decisions, usage, fallbacks, approvals, and memory checkpoints are recorded.
6. Insights consumes operational traces and external signals to produce briefings and recommendations.
7. Profile resolves the people, agents, organizations, accounts, and relationships involved.

## Logical Architecture

```text
Users / Agents / Webhooks / Schedules
        |
        v
Decide API and Control Plane
        |
        +-- Policy, guardrails, approvals, overrides
        +-- Runtime registry and routing
        +-- Task, project, channel, workflow records
        +-- Execution history, usage, checkpoints
        |
        v
LangGraph Orchestrator
        |
        +-- OpenAI Agents channel runtime
        +-- Claude / generic / future worker runtimes
        |
        v
Model Gateway + MCP Fleet
        |
        +-- LLM providers
        +-- Liferay, WordPress, Ghost, Postiz, Baserow, Matomo, n8n, Logto, Hostinger, and other tools
        |
        v
External Systems and Data Sources
```

## Data Architecture

| Store | Role |
| --- | --- |
| Postgres | Source of truth for tenants, employees, agents, workflow, decisions, approvals, usage, and audit. |
| Redis | Hot working memory, cache, sessions, and short-lived orchestration state. |
| Vector / hybrid store | Semantic retrieval for memories, documents, insights, and source evidence. |
| Object storage | Files, attachments, exports, and source snapshots. |
| Event stream or job queue | Future async ingestion, enrichment, notifications, and long-running workflows. |

## Service Boundaries

### Decide

- Owns execution requests, approvals, decisions, overrides, runtime selection, usage, and operational audit.
- Does not own long-term identity enrichment beyond the current operational schema.
- Calls Profile for canonical identity and relationship resolution.
- Receives recommendations from Insights and turns them into governed action.

### Insights

- Owns ingestion, normalization, source evidence, signal scoring, briefing generation, recommendation records, and delivery state.
- Does not directly execute actions in external systems.
- Sends recommended actions to Decide for approval, routing, execution, and audit.

### Profile

- Owns canonical people, organizations, agents, accounts, identities, relationships, preferences, and enrichment provenance.
- Does not own work execution state.
- Provides context to Decide and Insights so recommendations and actions are tied to the correct actors.

### Model Gateway

- Owns provider routing, virtual keys, budgets, rate limits, model aliases, and model-call telemetry.
- Exposes OpenAI-compatible endpoints where possible.
- Keeps provider-specific credentials out of product services.

### MCP Fleet

- Owns external tool adapters.
- Each adapter maps a platform API into safe, typed tool operations.
- Tool availability is governed by Decide policy, tenant permissions, and runtime capability.

## Governance Rules

- Employee and Agent remain separate first-class entities.
- Human approval and rule decisions remain separate records.
- Overrides are recorded explicitly and never erase the default decision.
- Runtime selection, fallback, usage, and final output are all auditable.
- Insights may recommend action, but Decide governs execution.
- Tools are invoked through registered adapters, not ad hoc direct integration from agents.

## Deployment Shape

The current deployment baseline is Docker Compose on `vps.openautonomyx.com`:

- `autonomyx-decide-app-1` on port `18000`.
- `autonomyx-decide-postgres-1` on port `15432`.
- `autonomyx-decide-redis-1` on port `16379`.
- Existing LLM gateway expected at `llm.openautonomyx.com`.

The next deployment step is to add a reverse proxy route and production configuration so the app is reachable behind TLS without exposing development defaults.

## Near-Term Implementation Priorities

1. Replace manual schema bootstrap with ordered migrations or a reliable startup migration command.
2. Add production compose overrides for secrets, TLS routing, and debug-off operation.
3. Complete the first MCP service implementation before enabling the `mcp` profile.
4. Add Profile and Insights service contracts before splitting them into separate deployments.
5. Add operational health checks for DB-backed routes, not only `/health`.

