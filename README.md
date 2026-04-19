# Decide Platform with LangFlow

Deploy the Decide agent orchestration platform with custom LangFlow agent as the orchestrator.

## Quick Start

```bash
# Clone
git clone https://github.com/openautonomyx/decide.git
cd decide

# Deploy
./deploy.sh
```

## Access

| Service | URL | Credentials |
|---------|-----|------------|
| Decide API | http://localhost:18000 | - |
| LangFlow | http://localhost:17860 | admin / admin123 |

## Flow

```
SSO Employee ID → HRMS → Autonomyx Agent → Execute Task
                   ↓
              Policies + Approval
                   ↓
              Memory + Export to Decide
```

## Configuration

Edit `.env`:
- `HRMS_PROVIDER` - Your HRMS (workday, bamboohr, custom, etc.)
- `HRMS_API_URL` - Your HRMS API endpoint
- `AGENT_IDENTITY_URL` - Autonomyx agent service

## Components

| Component | Description |
|-----------|------------|
| HRMSEmployeeResolver | Query employee from HR system |
| AgentIdentityResolver | Get agent for employee from Autonomyx |
| SkillResolver | Resolve available skills |
| PolicyCheck | Validate against policies |
| ApprovalGate | Human approval for sensitive actions |
| ExportToDecide | Save execution to Decide |

## Import Flow

1. Open http://localhost:17860
2. Login as admin/admin123
3. Go to **Flows** → **Import**
4. Select `langflow_components/decide/agent_orchestrator_flow.json`
5. Configure and run