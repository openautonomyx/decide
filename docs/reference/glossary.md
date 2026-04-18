# Glossary

Source: Decision Intelligence Platform — canonical vocabulary from the Autonomyx product.

## Orchestration primitives

**Node** — A discrete step in the orchestrator graph. A node can perform policy evaluation, approval lookup, runtime selection, worker invocation, memory update, checkpoint write, or audit logging.

**Edge** — A directed connection between nodes. Edges define how requests move from intake to policy checks, human review, worker execution, or fallback paths.

**Loop** — A repeated execution pattern used for retries, iterative task progress, evaluation passes, or controlled re-entry after tool failure or human correction.

**Branch** — A temporary execution path created by the orchestrator to explore alternatives, route to a specialist worker, run evaluation logic, or split work in parallel.

## Human–agent interaction

**Human-in-the-Loop** — A workflow pattern where a person must review, approve, deny, correct, or guide a decision or action before the system continues.

**Approval** — A structured human decision point in the control plane. Approvals can be mandatory, optional, delegated, time-bound, escalated, or policy-triggered.

**Decision** — A control-plane outcome that records what the platform concluded and why. A decision may come from a human, a policy rule, or a runtime selection process.

**Override** — An explicit exception to a default route, policy, or decision. Overrides are recorded with actor, reason, time, and audit context so deviations remain explainable.

**Delegation** — The controlled transfer of decision authority or responsibility from one human or agent to another for a defined purpose or time window.

## Capabilities

**Skill** — A reusable capability package that can combine instructions, prompts, tools, code, memory rules, and evaluation logic for a specific type of work.

**Tool** — A callable mechanism used by an agent or runtime to perform actions such as search, file handling, web access, code execution, data lookup, or external integration.

## Runtime

**Runtime Registry** — The catalog of supported runtimes, their capabilities, policy constraints, fallback rules, and selection metadata used by the orchestrator.

**Execution Request** — A durable request record that captures what was asked, by whom, under what policy and runtime conditions, and how execution progressed over time.

## Memory

**Cortex** — A cross-thread memory and briefing layer that synthesizes summaries, open loops, constraints, and relevant context across work instead of relying only on raw transcript history.

**Compaction** — The process of reducing growing context into structured summaries, state snapshots, and memory objects before the active runtime context becomes too large.

## Data

**Master Data** — Reusable, governed reference data such as departments, job titles, seniority, skills, policies, tools, runtimes, and compliance mappings that keeps workflows and agents aligned to business definitions.
