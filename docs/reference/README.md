# Decide Reference Docs

Curated entry point to the Autonomyx Decide platform docs. All content is already in the repo under `docs/`; this page is the map.

## Start here

- **[Glossary](glossary.md)** — Canonical vocabulary. Read this first.
- **[API Reference](api-reference.md)** — 91 endpoints across 11 tags, generated from the live OpenAPI spec.

## Architecture

- **[Design Summary v1](../architecture/design-summary-v1.md)** — One-page overview of the design decisions.
- **[Entity Catalog v1](../architecture/entity-catalog.md)** — All entities by domain (organization, agent, collaboration, workflow, control plane, master data).
- **[ERD v1 (Mermaid)](../architecture/erd-v1.mmd)** — Visual entity relationships.
- **[Runtime Architecture v2](../architecture/runtime-architecture-v2.md)** — LangGraph = orchestrator; OpenAI Agents SDK = channel; 5 worker runtimes (Claude Agent SDK, Deep Agents, CrewAI, LangChain, OpenAI Agents).
- **[Memory & Storage Decision](../architecture/memory-storage-decision.md)** — Redis (working/episodic hot cache), SingleStore (vector/semantic), Postgres (transactional).
- **[Control Plane Model](../architecture/control-plane-model.md)** — Execution requests, approvals, overrides, audit.
- **[Workflow Model](../architecture/workflow-model.md)** — Tasks, milestones, deadlines, reminders, escalations.
- **[Collaboration Model](../architecture/collaboration-model.md)** — Products, projects, groups, channels.
- **[Cortex Implementation](../architecture/cortex-implementation.md)** — Cross-thread summarization.

## Orchestrator (Phase 0 → 3)

- **[Pre-Orchestrator API Plan](../architecture/pre-orchestrator-api-plan.md)** — Phase 0 service and API boundaries.
- **[Phase 0 API Implementation](../architecture/phase-0-api-implementation.md)** — Runtime/channel/tool/skill/context services.
- **[Orchestrator Core (Phase 1)](../architecture/orchestrator-core-implementation.md)** — Engine, router, state, types.
- **[Phase 2: Policy & Guardrails](../architecture/orchestrator-phase-2-policy-guardrails.md)** — Policy gate, guardrail checks, approval gate.
- **[Phase 3: Runtime Invocation](../architecture/orchestrator-phase-3-runtime-invocation.md)** — Runtime invoker, adapters for each worker runtime.
- **[Runtime Selection Implementation](../architecture/runtime-selection-implementation.md)** — How a task type gets routed to a runtime.
- **[Runtime Memory Implementation](../architecture/runtime-memory-implementation.md)** — How memory layers wire in.
- **[OpenAI Channel Runtime](../architecture/openai-channel-runtime.md)** — Default human-facing runtime spec.
- **[Module Roadmap v2](../architecture/module-roadmap-v2.md)** — What's implemented vs planned per module.
- **[Schema Expansion Before Orchestrator](../architecture/schema-expansion-before-orchestrator.md)** — Which modules had to land before orchestrator completion.

## Data model

- **[Schema v1 (consolidated SQL)](../data-model/schema-v1.sql)** — 76 tables in one file, canonical.
- **[Schema Audit v1](../data-model/schema-audit-v1.md)** — Completeness check against design decisions.
- **[Master Data Dictionary](../data-model/master-data-dictionary.md)** — Every master table with its fields.
- **[Naming Conventions](../data-model/naming-conventions.md)** — Stable string IDs, timestamp patterns.
- **[Schema Expansion Roadmap](../data-model/schema-expansion-roadmap.md)** — Planned additions.
- **[Migrations](../../db/migrations/README.md)** — 8 ordered migration files that build the schema.

## State machines

- **[State Machines Overview](../architecture/state-machines/README.md)**
- **[Approval](../architecture/state-machines/approval.md)** | **[Decision](../architecture/state-machines/decision.md)** | **[Escalation](../architecture/state-machines/escalation.md)**
- **[Execution Request](../architecture/state-machines/execution-request.md)** | **[Override](../architecture/state-machines/override.md)** | **[Reminder](../architecture/state-machines/reminder.md)**
- **[Responsibility Assignment](../architecture/state-machines/responsibility-assignment.md)** | **[Task](../architecture/state-machines/task.md)**

## Profiles

- **[Agent Profile Schema](../architecture/agent-profile-schema.md)** — Agent identity, governance, memory, skills, goals.
- **[Employee Schema](../architecture/employee-schema.md)** — Employee identity, employment, education, certifications.

## Operations

- **[DATABASE_SETUP.md](../../DATABASE_SETUP.md)** — How to stand up the DB locally.
- **[IMPLEMENTATION_SUMMARY.md](../../IMPLEMENTATION_SUMMARY.md)** — Mid-session snapshot from OpenHands (partially stale).

## What's in code, not in docs yet

- The 10 FastAPI routers in `app/api/` — behavior documented via the generated [API Reference](api-reference.md).
- The 6 memory layer classes in `app/memory/` (WorkingMemoryStore, EpisodicMemoryStore, SemanticMemoryStore, CortexService-adjacent, CheckpointStore, CompactionService).
- The 10 Phase-0 services (RuntimeRegistryService, ChannelService, BranchService, WorkerService, CortexService, ToolRegistryService, SkillService, ContextBudgetService, TokenAccountingService, CompactionService) — all in `app/services/*/__init__.py`.
- The orchestrator (10-stage engine in `app/orchestrator/engine.py`) — design doc covers it; the live code implements phases 1-3.
