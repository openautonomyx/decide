# Collaboration Container Model

This document finalizes the distinctions between Product, Project, and Group as first-class entities.

---

## Overview: Three Distinct Containers

| Entity | Purpose | Lifespan | Primary Channel |
|--------|---------|----------|----------------|
| Product | Business function | Persistent | Yes (required) |
| Project | Execution | Short-term | Optional |
| Group | Community/Interest | Variable | Yes (required) |

---

## Product

### Definition
- **Persistent** business-facing entity
- **Business-function aligned** - represents a product or service
- **Long-lived** - months to years
- **One primary channel** - for ongoing communication

### Schema
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| tenant_id | VARCHAR(36) | FK to tenant |
| name | VARCHAR(255) | Product name |
| strategy | TEXT | Product strategy |
| primary_channel_id | VARCHAR(36) | FK to primary channel |

### Characteristics
- Strategic ownership
- Long-term roadmap
- Multiple projects can link to product
- Primary channel for product team communication

### Example
```
Product: "Acme Analytics Platform"
├── Primary Channel: #analytics-platform
├── Projects:
│   ├── Q2 Dashboard Redesign
│   └── API v3 Launch
└── Ownership: VP Product
```

---

## Project

### Definition
- **Short-term** execution entity
- **Strict timeline** - defined start/end
- **Deliverables** - specific outputs
- **Milestones** - progress checkpoints
- **Optional channel** - may have own channel

### Schema
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| tenant_id | VARCHAR(36) | FK to tenant |
| name | VARCHAR(255) | Project name |
| start_date | DATE | Project start |
| end_date | DATE | Project end |
| channel_id | VARCHAR(36) | Optional channel |

### Characteristics
- Timeline-driven
- Deliverable-focused
- Can link to one product
- May have optional channel

### Example
```
Project: "Q2 Dashboard Redesign"
├── Timeline: 2025-04-01 to 2025-06-30
├── Linked Product: Acme Analytics Platform
├── Channel: #dashboard-redesign (optional)
├── Milestones:
│   ├── Design Complete (2025-04-30)
│   ├── MVP Ready (2025-05-31)
│   └── Launch (2025-06-30)
└── Tasks: 15 tasks
```

---

## Group

### Definition
- **Community/interest/hobby/committee/guild/seniority** oriented
- **One primary channel** - for group communication
- **Members include employees and/or agents**
- **Chat + file sharing** enabled

### Schema
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| tenant_id | VARCHAR(36) | FK to tenant |
| name | VARCHAR(255) | Group name |
| group_type | VARCHAR(50) | community/interest/committee/guild |
| primary_channel_id | VARCHAR(36) | FK to primary channel |

### Membership
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| group_id | VARCHAR(36) | FK to group |
| member_type | VARCHAR(20) | employee/agent/group |
| member_id | VARCHAR(36) | FK to member |
| role | VARCHAR(50) | member/owner/moderator |

### Example
```
Group: "Design Guild"
├── Type: guild
├── Primary Channel: #design-guild
├── Members:
│   ├── Employees (5)
│   └── Agents (2 - design assistants)
└── Activities: Weekly design reviews, skill sharing
```

---

## Channel Behavior

### Schema
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| tenant_id | VARCHAR(36) | FK to tenant |
| context_type | VARCHAR(50) | product/project/group/task/direct |
| context_id | VARCHAR(36) | FK to context entity |
| name | VARCHAR(255) | Channel name |
| is_primary | BOOLEAN | Primary channel flag |

### Membership Roles
| Role | Permissions |
|------|-------------|
| owner | Full control, manage members, delete channel |
| moderator | Manage messages, manage members |
| member | Post messages, share files |
| viewer | Read-only access |

### Channel Capabilities
- **Chat** - Via `channel_message` table
- **File Sharing** - Via `channel_file` table
- **Membership** - Via `channel_membership` table

---

## Schema Verification

| Entity | Table | Primary Channel | Optional Channel |
|--------|-------|-----------------|------------------|
| Product | product | primary_channel_id | - |
| Project | project | - | channel_id |
| Group | group_entity | primary_channel_id | - |

---

## Key Design Rules

1. **Product ≠ Project ≠ Group** - Three distinct entity types
2. **Product/Group require primary channel** - Enforced in schema
3. **Project optional channel** - Can exist without channel
4. **Members can be employee/agent** - Via `group_membership`
5. **Channel roles enforced** - owner/moderator/member/viewer

---

## Anti-Patterns to Avoid

- ✗ Don't merge product/project/group into one generic "container"
- ✗ Don't make channel optional for product/group
- ✗ Don't restrict group members to only employees
- ✗ Don't use same table for product and project channels