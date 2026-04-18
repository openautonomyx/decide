# API Reference

Base URL: `http://localhost:18000/api/v1` (local) — generated from live OpenAPI spec on 1.0.0.

## Routes by tag

### agents

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/agents` | List Agents |
| POST | `/api/v1/agents` | Create Agent |
| DELETE | `/api/v1/agents/{agent_id}` | Delete Agent |
| GET | `/api/v1/agents/{agent_id}` | Get Agent |
| PATCH | `/api/v1/agents/{agent_id}` | Update Agent |
| POST | `/api/v1/agents/{agent_id}/assign` | Assign Agent To Employee |

### channel

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/branches/{branch_id}` | Get Branch |
| POST | `/api/v1/branches/{branch_id}/close` | Close Branch |
| POST | `/api/v1/branches/{branch_id}/merge` | Merge Branch |
| GET | `/api/v1/channels` | List Channels |
| POST | `/api/v1/channels` | Create Channel |
| GET | `/api/v1/channels/{channel_id}` | Get Channel |
| PATCH | `/api/v1/channels/{channel_id}` | Update Channel |
| GET | `/api/v1/cortex/{thread_id}/summaries` | List Cortex Summaries |
| GET | `/api/v1/cortex/{thread_id}/summary` | Get Cortex Summary |
| POST | `/api/v1/threads/{thread_id}/branch` | Create Branch |
| GET | `/api/v1/threads/{thread_id}/branches` | List Branches |
| POST | `/api/v1/workers` | Create Worker |
| GET | `/api/v1/workers/{worker_id}` | Get Worker |
| POST | `/api/v1/workers/{worker_id}/complete` | Complete Worker |
| POST | `/api/v1/workers/{worker_id}/fail` | Fail Worker |
| POST | `/api/v1/workers/{worker_id}/start` | Start Worker |
| PATCH | `/api/v1/workers/{worker_id}/state` | Update Worker State |

### collaboration

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/collaboration/groups` | List Groups |
| POST | `/api/v1/collaboration/groups` | Create Group |
| GET | `/api/v1/collaboration/groups/{group_id}` | Get Group |
| GET | `/api/v1/collaboration/products` | List Products |
| POST | `/api/v1/collaboration/products` | Create Product |
| GET | `/api/v1/collaboration/products/{product_id}` | Get Product |
| PATCH | `/api/v1/collaboration/products/{product_id}` | Update Product |
| GET | `/api/v1/collaboration/projects` | List Projects |
| POST | `/api/v1/collaboration/projects` | Create Project |
| GET | `/api/v1/collaboration/projects/{project_id}` | Get Project |

### context

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/compaction/{thread_id}/summaries` | List Compaction Summaries |
| GET | `/api/v1/compaction/{thread_id}/summary` | Get Compaction Summary |
| POST | `/api/v1/compaction/{thread_id}/trigger` | Trigger Compaction |
| GET | `/api/v1/context/budgets` | List Budgets |
| POST | `/api/v1/context/budgets` | Create Budget |
| GET | `/api/v1/context/budgets/check` | Check Budget |
| PATCH | `/api/v1/context/budgets/{budget_id}` | Update Budget |
| GET | `/api/v1/context/budgets/{task_type}` | Get Budget For Task |
| POST | `/api/v1/tokens/estimate` | Estimate Tokens |
| POST | `/api/v1/tokens/usage` | Record Usage |
| GET | `/api/v1/tokens/usage/tenant/{tenant_id}` | Get Tenant Usage |
| GET | `/api/v1/tokens/usage/{thread_id}` | Get Usage |

### employees

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/employees` | List Employees |
| POST | `/api/v1/employees` | Create Employee |
| DELETE | `/api/v1/employees/{employee_id}` | Delete Employee |
| GET | `/api/v1/employees/{employee_id}` | Get Employee |
| PATCH | `/api/v1/employees/{employee_id}` | Update Employee |

### misc

| Method | Path | Summary |
|---|---|---|
| GET | `/` | Root |
| GET | `/config` | Config Check |
| GET | `/health` | Health Check |

### runtime

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/runtimes` | List Runtimes |
| POST | `/api/v1/runtimes` | Create Runtime |
| GET | `/api/v1/runtimes/health` | Get Health |
| GET | `/api/v1/runtimes/instances` | List Instances |
| GET | `/api/v1/runtimes/instances/{instance_id}` | Get Instance |
| GET | `/api/v1/runtimes/select` | Select Runtime |
| GET | `/api/v1/runtimes/{runtime_id}` | Get Runtime |
| PATCH | `/api/v1/runtimes/{runtime_id}` | Update Runtime |

### skill

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/skills` | List Skills |
| POST | `/api/v1/skills` | Create Skill |
| DELETE | `/api/v1/skills/{skill_id}` | Deprecate Skill |
| GET | `/api/v1/skills/{skill_id}` | Get Skill |
| PATCH | `/api/v1/skills/{skill_id}` | Update Skill |
| POST | `/api/v1/skills/{skill_id}/evaluate` | Record Skill Evaluation |
| GET | `/api/v1/skills/{skill_id}/evaluations` | List Skill Evaluations |
| GET | `/api/v1/skills/{skill_id}/metrics` | Get Skill Metrics |
| GET | `/api/v1/skills/{skill_id}/versions` | List Skill Versions |
| POST | `/api/v1/skills/{skill_id}/versions` | Create Skill Version |

### tasks

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/tasks` | List Tasks |
| POST | `/api/v1/tasks` | Create Task |
| GET | `/api/v1/tasks/{task_id}` | Get Task |
| PATCH | `/api/v1/tasks/{task_id}` | Update Task |

### tenants

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/tenants` | List Tenants |
| POST | `/api/v1/tenants` | Create Tenant |
| DELETE | `/api/v1/tenants/{tenant_id}` | Delete Tenant |
| GET | `/api/v1/tenants/{tenant_id}` | Get Tenant |
| PATCH | `/api/v1/tenants/{tenant_id}` | Update Tenant |

### tool

| Method | Path | Summary |
|---|---|---|
| GET | `/api/v1/tools` | List Tools |
| POST | `/api/v1/tools` | Create Tool |
| GET | `/api/v1/tools/approvals-required` | Get Tools Requiring Approval |
| GET | `/api/v1/tools/categories` | List Categories |
| GET | `/api/v1/tools/risks/{risk_level}` | Get Tools By Risk |
| GET | `/api/v1/tools/search` | Search Tools |
| DELETE | `/api/v1/tools/{tool_id}` | Deprecate Tool |
| GET | `/api/v1/tools/{tool_id}` | Get Tool |
| PATCH | `/api/v1/tools/{tool_id}` | Update Tool |
| POST | `/api/v1/tools/{tool_id}/enable` | Enable Tool |
| GET | `/api/v1/tools/{tool_id}/schema` | Get Tool Schema |
