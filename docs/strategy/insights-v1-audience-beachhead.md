# Insights v1 Audience Beachhead

## Decision

Insights v1 should start with **fractional operators and agency owners who manage several client workstreams, tools, and contractors at once**.

This is the first beachhead because the pain is frequent, the buyer is close to the work, the data is already scattered across accessible SaaS systems, and the willingness to pay is tied to visible time savings and client retention.

## Primary User

- Fractional COO, chief of staff, RevOps lead, growth operator, or technical agency owner.
- Manages 3-20 active client or internal initiatives.
- Coordinates humans and agents across Slack, email, project tools, docs, CRM, analytics, and publishing systems.
- Needs concise situational awareness before making prioritization, escalation, resourcing, or client communication decisions.

## Pain

- Work status lives in too many systems, so decisions rely on stale updates and manual synthesis.
- Client-facing teams lose time asking "what changed?", "what is blocked?", and "what needs attention?"
- Existing dashboards show metrics, but not the decision context around risk, momentum, accountability, and next action.
- Agents can execute tasks, but operators still need a trusted control plane to decide what should happen next.

## Wedge Use Case

**Daily decision briefing for active workstreams.**

Each morning, Insights v1 produces a ranked briefing:

- Which initiatives changed since the last briefing.
- Which tasks, conversations, metrics, or signals imply risk.
- Which blockers require a human decision.
- Which follow-ups can be delegated to an agent.
- Which client-facing updates should be sent.

The output should be actionable inside Decide: create tasks, request approvals, assign agents, record decisions, or update the execution history.

## Buying Trigger

- A client delivery miss, delayed launch, churn risk, or executive complaint.
- A founder/operator has more active projects than they can personally inspect each day.
- A team starts using agents but lacks governance, audit, and decision routing.
- A monthly retainer or client portfolio depends on proving proactive management.

## Why Not Start Broader

| Segment | Reason to defer |
| --- | --- |
| Enterprise strategy teams | Long procurement, heavy security review, bespoke integrations. |
| General knowledge workers | Weak willingness to pay and unclear repeated decision loop. |
| Consumer productivity | Too broad, low ACV, limited need for governance. |
| Data teams | Already served by BI stacks; AutonomyX differentiates on decisions, not dashboards. |

## V1 Promise

"Every morning, know what changed, what matters, and which decision or agent action should happen next."

## V1 Inputs

- Tasks and project updates.
- Slack or chat summaries.
- CRM and client account notes.
- Analytics or KPI snapshots.
- Agent execution history from Decide.
- Manual operator notes.

## V1 Outputs

- Daily briefing by workstream.
- Risk and urgency scoring.
- Decision recommendations.
- Suggested task, approval, or agent actions.
- Client update draft.
- Audit trail linking each recommendation to source signals.

## MVP Acceptance Criteria

- An operator can connect or import at least three source types for one workstream.
- The system produces a daily briefing with ranked risks and recommended next actions.
- Each insight links back to source evidence.
- The operator can convert an insight into a Decide task, approval request, decision record, or agent execution request.
- The briefing can be reviewed in less than 10 minutes.

## Positioning

AutonomyX Insights is not a BI dashboard. It is a decision briefing layer for operators who need to turn scattered work signals into governed action.

