# AutonomyX Profile Service Data Model

## Purpose

The Profile service is the canonical identity and relationship layer for AutonomyX. It resolves who or what an actor is, which accounts and organizations they belong to, what preferences and permissions apply, and which source records support that profile.

Profile serves Decide and Insights, but it does not replace Decide's operational tables. Decide can keep execution-specific snapshots; Profile owns durable identity context.

## Core Entities

| Entity | Purpose |
| --- | --- |
| profile_subject | Canonical root for a person, agent, organization, or service account. |
| person_profile | Human-specific profile data. |
| agent_profile | AI agent-specific profile data and operational identity. |
| organization_profile | Company, client, tenant, vendor, or partner profile. |
| account_profile | External account or workspace identity, such as Slack user, GitHub user, Liferay user, CRM contact, or domain account. |
| identity_claim | Email, phone, domain, username, wallet, SCIM ID, OAuth subject, or other identifying claim. |
| profile_relationship | Relationship between two subjects. |
| profile_preference | Communication, routing, privacy, notification, and interaction preferences. |
| profile_permission | Effective permission or entitlement exported for policy evaluation. |
| enrichment_source | Source system, provider, document, API, or manual assertion that contributed profile data. |
| profile_evidence | Evidence record supporting a claim, relationship, or enrichment. |
| profile_merge_event | Audit record for profile deduplication and merge decisions. |

## Subject Types

| Type | Examples |
| --- | --- |
| person | Employee, client stakeholder, vendor contact, community member. |
| agent | AutonomyX agent, customer-owned agent, integration bot. |
| organization | Tenant, client, vendor, partner, project company. |
| service_account | API key owner, webhook actor, automation identity. |

## Suggested Tables

### profile_subject

| Field | Type | Notes |
| --- | --- | --- |
| id | varchar(36) | UUID string. |
| tenant_id | varchar(36) | Owning tenant when scoped; nullable for global records. |
| subject_type | varchar(32) | person, agent, organization, service_account. |
| display_name | varchar(255) | Human-readable label. |
| canonical_slug | varchar(255) | Stable internal slug. |
| status | varchar(32) | active, inactive, archived, disputed. |
| confidence_score | numeric(5,2) | Identity confidence from 0 to 1. |
| created_at | timestamp | Creation time. |
| updated_at | timestamp | Last update. |

### identity_claim

| Field | Type | Notes |
| --- | --- | --- |
| id | varchar(36) | UUID string. |
| subject_id | varchar(36) | FK to profile_subject. |
| claim_type | varchar(50) | email, phone, domain, username, oauth_sub, scim_id, external_id. |
| claim_value | text | Normalized value. |
| provider | varchar(100) | Source provider. |
| verified | boolean | Whether the claim is verified. |
| confidence_score | numeric(5,2) | Claim confidence. |
| first_seen_at | timestamp | First observed. |
| last_seen_at | timestamp | Most recent observation. |

### account_profile

| Field | Type | Notes |
| --- | --- | --- |
| id | varchar(36) | UUID string. |
| subject_id | varchar(36) | FK to profile_subject. |
| provider | varchar(100) | Slack, GitHub, Liferay, HubSpot, Google, etc. |
| workspace_id | varchar(255) | External workspace or tenant ID. |
| account_id | varchar(255) | External account ID. |
| account_handle | varchar(255) | Username or display handle. |
| account_status | varchar(32) | active, disabled, removed. |
| linked_at | timestamp | Link creation time. |

### profile_relationship

| Field | Type | Notes |
| --- | --- | --- |
| id | varchar(36) | UUID string. |
| from_subject_id | varchar(36) | Source profile. |
| to_subject_id | varchar(36) | Target profile. |
| relationship_type | varchar(64) | owns, manages, reports_to, member_of, client_of, vendor_of, delegated_to, supervises_agent. |
| scope | varchar(100) | Optional product, project, tenant, workspace, or account scope. |
| confidence_score | numeric(5,2) | Relationship confidence. |
| effective_from | timestamp | Start. |
| effective_to | timestamp | End. |
| status | varchar(32) | active, inactive, disputed. |

### profile_preference

| Field | Type | Notes |
| --- | --- | --- |
| id | varchar(36) | UUID string. |
| subject_id | varchar(36) | FK to profile_subject. |
| preference_type | varchar(64) | communication, notification, channel, language, timezone, escalation. |
| key | varchar(100) | Preference key. |
| value | text | JSON string or scalar. |
| source | varchar(100) | manual, inferred, imported. |
| updated_at | timestamp | Last update. |

### profile_permission

| Field | Type | Notes |
| --- | --- | --- |
| id | varchar(36) | UUID string. |
| subject_id | varchar(36) | FK to profile_subject. |
| resource_type | varchar(64) | tenant, project, product, tool, account, deployment, insight. |
| resource_id | varchar(255) | Scoped resource ID. |
| permission | varchar(100) | read, write, approve, execute, delegate, administer. |
| grant_source | varchar(100) | direct, group, policy, external_idp. |
| effective_from | timestamp | Start. |
| effective_to | timestamp | End. |

### enrichment_source

| Field | Type | Notes |
| --- | --- | --- |
| id | varchar(36) | UUID string. |
| source_type | varchar(64) | api, file, webhook, manual, scrape, idp, crm. |
| provider | varchar(100) | Source provider name. |
| external_ref | text | Source-specific URI or ID. |
| trust_level | varchar(32) | high, medium, low. |
| collected_at | timestamp | Source collection time. |

### profile_evidence

| Field | Type | Notes |
| --- | --- | --- |
| id | varchar(36) | UUID string. |
| subject_id | varchar(36) | Related subject. |
| source_id | varchar(36) | FK to enrichment_source. |
| evidence_type | varchar(64) | claim, relationship, preference, permission, enrichment. |
| evidence_payload | text | JSON payload or extracted snippet. |
| hash | varchar(128) | Optional integrity hash. |
| created_at | timestamp | Creation time. |

## Identity Resolution Rules

- Email and verified OAuth subject are high-confidence person claims.
- Domain plus organization name is medium-confidence organization resolution.
- Agent profiles must not be merged with person profiles.
- Service accounts are separate from agents unless explicitly linked.
- Merge decisions must create a `profile_merge_event` with source and target IDs.
- Low-confidence enrichments can inform Insights but should not grant permissions.

## Integration With Decide

- Decide keeps `employee`, `agent`, and execution tables as operational records.
- Profile can map a Decide employee or agent to a profile subject through `account_profile` or `identity_claim`.
- Decide asks Profile for context when resolving approvers, owners, escalation paths, and actor relationships.
- Decide records the effective decision snapshot so future profile changes do not rewrite audit history.

## Integration With Insights

- Insights uses Profile to resolve signals to canonical subjects.
- Insights attaches profile evidence to generated recommendations.
- Insights should avoid creating new canonical profiles without a confidence threshold or human review.

## MVP Scope

- `profile_subject`
- `identity_claim`
- `account_profile`
- `profile_relationship`
- `enrichment_source`
- `profile_evidence`

Preferences, permissions, and merge events can follow once resolution is stable.

