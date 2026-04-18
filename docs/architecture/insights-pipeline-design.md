# Insights Pipeline Design

## Purpose

The Insights pipeline turns scattered operational signals into ranked, evidence-backed recommendations that can be reviewed and acted on through Decide.

Insights does not execute actions directly. It produces decision-ready records and sends action candidates to Decide for policy, approval, runtime routing, and audit.

## Pipeline Stages

```text
Sources
  -> Ingestion
  -> Normalization
  -> Identity and entity resolution
  -> Signal extraction
  -> Scoring and clustering
  -> Insight generation
  -> Recommendation mapping
  -> Delivery and feedback
```

## Sources

Initial source types:

- Decide execution history, tasks, approvals, decisions, overrides, and usage.
- Project and task tools.
- Slack or chat transcripts.
- CRM notes and account updates.
- Analytics snapshots from Matomo or similar systems.
- Manual operator notes.
- External docs, files, and client updates.

Each source should preserve provenance so every insight can explain why it exists.

## Data Objects

| Object | Purpose |
| --- | --- |
| source_connector | Configured source integration. |
| source_event | Raw or lightly parsed source record. |
| normalized_event | Common event representation. |
| resolved_entity | Link from event content to Profile/Decide entities. |
| signal | Atomic observation extracted from events. |
| insight | Clustered interpretation of one or more signals. |
| recommendation | Suggested decision, task, approval, message, or agent action. |
| briefing | Ordered package of insights for a user, project, tenant, or time window. |
| feedback | User response used to tune scoring and future recommendations. |

## Normalized Event Shape

```json
{
  "id": "event_uuid",
  "tenant_id": "tenant_uuid",
  "source": "slack",
  "source_ref": "channel/message/timestamp",
  "event_type": "message",
  "occurred_at": "2026-04-18T10:00:00Z",
  "actor_ref": "external_actor_id",
  "subject_refs": ["project_id", "account_id"],
  "content": "message or summary",
  "metadata": {}
}
```

## Signal Types

| Signal | Description |
| --- | --- |
| status_change | A work item, metric, or relationship changed state. |
| blocker | Progress depends on a missing decision, input, access, or resource. |
| deadline_risk | A milestone or deadline is likely to slip. |
| client_risk | Account health, sentiment, or delivery risk changed. |
| duplicate_work | Multiple people or agents are working the same issue. |
| missing_owner | A task or decision lacks an accountable actor. |
| agent_opportunity | A follow-up can be delegated safely to an agent. |
| approval_needed | A recommended action requires human approval. |

## Scoring

Each signal receives:

- `impact_score`: consequence if ignored.
- `urgency_score`: time sensitivity.
- `confidence_score`: evidence quality and consistency.
- `novelty_score`: whether this is new or repeated.
- `actionability_score`: whether a clear next action exists.

Recommended priority:

```text
priority_score = impact * 0.30 + urgency * 0.25 + confidence * 0.20 + actionability * 0.20 + novelty * 0.05
```

The formula should remain configurable per tenant once policy controls exist.

## Insight Generation

An insight should include:

- Title.
- Summary.
- Evidence list.
- Affected entities.
- Risk or opportunity type.
- Priority score and component scores.
- Recommended next action.
- Confidence and caveats.
- Links to source events.

Insights must not contain unsupported claims. If evidence is weak, the insight should say so explicitly.

## Recommendation Mapping

Recommendations map into Decide actions:

| Recommendation Type | Decide Action |
| --- | --- |
| create_task | Create task with source evidence. |
| request_approval | Create approval_request linked to insight. |
| record_decision | Create decision_record after user confirmation. |
| assign_agent | Create execution_request for selected runtime. |
| escalate | Create escalation or reminder. |
| draft_update | Create message draft for human review. |

## Delivery

Initial delivery channels:

- Daily briefing endpoint.
- Project or client briefing endpoint.
- Decide UI feed.
- Email or chat summary after review controls exist.

Briefings should be short by default. The target for the beachhead user is a 10-minute morning review.

## Feedback Loop

Capture:

- Accepted recommendations.
- Rejected recommendations and reason.
- Edited recommendation text.
- Converted tasks or approvals.
- Hidden or muted signal types.
- User corrections to entity resolution.

Feedback tunes scoring and improves source-specific extraction.

## MVP Acceptance Criteria

- Ingest events from Decide plus two external or imported sources.
- Resolve events to tenant, project/workstream, actor, and account where possible.
- Produce ranked insights with source evidence.
- Generate at least three Decide-compatible recommendation types: create task, request approval, draft update.
- Expose a daily briefing API.
- Store feedback for accepted, rejected, and edited recommendations.

## Failure Modes

| Failure | Mitigation |
| --- | --- |
| Wrong entity resolution | Keep confidence scores, show evidence, allow correction. |
| Unsupported insight | Require evidence links and confidence caveats. |
| Too many alerts | Default to briefing batches, not real-time noise. |
| Unsafe action | Route all execution through Decide approvals and policy. |
| Source outage | Mark stale sources and reduce confidence. |

