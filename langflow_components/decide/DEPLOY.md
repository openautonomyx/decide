# Decide + LangFlow Deployment Guide

## Overview

This package provides the **Decide Agent Orchestrator** - a custom LangFlow agent that integrates with your organization's systems to manage agent workflows.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Input    │────▶│  SSO Employee ID │────▶│ HRMS Resolver  │
│  (Chat/LLM)     │     │  (from login)    │     │ (employee data)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Export to       ◀─────│   Agent Router   ◀─────│ Policy Check   │
│ Decide Platform │     │  (LLM + Tools)   │     │ (validation)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
┌─────────────────┐     ┌──────────────────┐
│ Memory Resolver │◀────│ Agent Identity   │
│ (context)      │     │ (Autonomyx)       │
└─────────────────┘     └──────────────────┘
```

## Supported Integrations

### HRMS Systems
- **Workday** - Enterprise HR
- **BambooHR** - SMB HR
- **SAP SuccessFactors** - Enterprise HCM
- **Oracle HCM** - Enterprise HR
- **ADP** - Payroll & HR
- **UKG** - Workforce Management
- **Custom REST API** - Any HR system with REST endpoints

### Identity Providers
- **Autonomyx Agent Identity** - Agent registry and management
- Custom via BaseIdentityAdapter

## Configuration

### Environment Variables

```bash
# HRMS Configuration
HRMS_PROVIDER=custom              # workday, bamboohr, sap_successfactors, etc.
HRMS_API_URL=https://api.company.com/hr/v1
HRMS_API_KEY=your_api_key
HRMS_TENANT_ID=your_tenant_id

# Autonomyx Agent Identity
AGENT_IDENTITY_URL=http://agent-identity:8000
AGENT_IDENTITY_API_KEY=your_api_key

# Decide Platform
DECIDE_API_URL=http://decide-api:8000
DECIDE_API_KEY=your_api_key
```

## Custom Components

| Component | Purpose |
|-----------|---------|
| `HRMSEmployeeResolver` | Query employee data from HR system |
| `AgentIdentityResolver` | Resolve agent from Autonomyx by employee ID |
| `SkillResolver` | Resolve available skills |
| `PolicyCheck` | Validate actions against policies |
| `ApprovalGate` | Human approval for sensitive actions |
| `MemoryResolver` | Load conversation context |
| `ExportToDecide` | Export results to Decide platform |

## Deploying to LangFlow

### Option 1: Import Flow JSON

1. Open LangFlow
2. Go to Flows → Import
3. Select `agent_orchestrator_flow.json`
4. Configure components with your HRMS/API settings
5. Save and run

### Option 2: Programmatic Deployment

```python
from langflow import load_flow_from_json

flow = load_flow_from_json("agent_orchestrator_flow.json")
flow.deploy(port=7860)
```

### Option 3: Custom Component Loading

```bash
# Copy components to LangFlow custom components directory
cp -r langflow_components/decide ~/.langflow/custom_components/

# Restart LangFlow
langflow restart
```

## Flow Data Mapping

The orchestrator flow connects data across systems:

| Input | Maps To |
|-------|---------|
| SSO Employee ID | `employee_id` in HRMS query |
| HRMS Employee Data | `tenant_id`, `department`, `manager` |
| Employee → Agent Mapping | `EmployeeAgentAssignment` in Decide |
| Agent ID | `AgentIdentity` from Autonomyx |
| Agent Config | Skills, models, governance profile |

## API Integration

### Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/execution/requests` | Execute agent task |
| `GET /api/v1/memory/resolve` | Load context |
| `POST /api/v1/approvals` | Request human approval |
| `GET /agents/{id}` | Get Autonomyx agent config |

## Testing

```bash
# Test HRMS connection
python -c "
from app.integrations.hrms import get_hrms_adapter
adapter = get_hrms_adapter()
employees = await adapter.list_employees()
print(employees)
"

# Test agent identity
python -c "
from app.integrations.identity import get_identity_adapter
adapter = get_identity_adapter('autonomyx_agent_identity')
agent = await adapter.get_identity('emp-123')
print(agent)
"
```

## Troubleshooting

### Employee not found in HRMS
- Verify `HRMS_API_URL` is accessible
- Check `HRMS_API_KEY` is valid
- Ensure employee exists in HRMS system

### Agent identity not resolving
- Verify Autonomyx service is running
- Check employee has agent assignment
- Verify `AGENT_IDENTITY_URL` is correct

### LangFlow components not loading
- Ensure all dependencies installed
- Check component imports are correct
- Review LangFlow logs for errors