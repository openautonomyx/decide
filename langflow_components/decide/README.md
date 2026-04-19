# Decide Custom Component Pack for Langflow

This package provides Decide-native components for visual authoring in Langflow.

## Components

| Component | Description | Decide Concept Mapping |
|-----------|-------------|----------------------|
| **ApprovalGate** | Human approval gate for agent workflows | `ApprovalRequest`, `DecisionRecord` |
| **PolicyCheck** | Policy validation and enforcement | `PolicyResolution`, `BackendSelection` |
| **ModelProfile** | Model governance and selection | `AgentGovernanceProfile` |
| **MemoryResolver** | Memory context resolution | `MemoryCheckpoint`, `MemoryService` |
| **SkillResolver** | Skill resolution and routing | `AgentSkill` |
| **ExportToDecide** | Export results to Decide platform | `ExecutionRequest`, `ExecutionHistory` |
| **PublishToLangGraph** | Compile workflow to LangGraph | LangGraph integration |

## Loading Components in Langflow

These components use Langflow's custom component style. To load them:

Option 1: Place in Langflow's custom components directory
```bash
cp -r langflow_components/decide ~/.langflow/custom_components/decide
```

Option 2: Add to Python path
```python
import sys
sys.path.insert(0, "/path/to/decide/langflow_components")
from langflow_components.decide import *
```

Langflow will automatically discover the component classes and register them in the component panel.

## Component Structure

Each component follows this pattern:

1. **Purpose**: What the component does
2. **Config Fields**: Set at flow design time (non-runtime)
3. **Inputs**: Runtime data flows into component
4. **Outputs**: Runtime data flows out of component
5. **run()**: Execution method (stubbed for this pack)

## Decide API Integration

These components map to Decide's REST APIs:

| Component | API Endpoint | Model |
|-----------|--------------|-------|
| ApprovalGate | `POST /api/v1/approvals` | `ApprovalRequest` |
| PolicyCheck | `POST /api/v1/execution/requests` | `PolicyResolution` |
| ModelProfile | `GET /api/v1/agents/{id}/governance-profile` | `AgentGovernanceProfile` |
| MemoryResolver | `GET /api/v1/memory/threads/{thread_id}` | `MemoryCheckpoint` |
| SkillResolver | `POST /api/v1/skills/resolve` | `AgentSkill` |
| ExportToDecide | `POST /api/v1/execution/requests` | `ExecutionRequest` |
| PublishToLangGraph | N/A | Internal compilation |

## Note

This is the first component pack. The `run()` methods are stubs that pass data through. Full integration with Decide APIs requires:
- Decide API server running
- Authentication configured
- API endpoints implemented

## Development

To extend this pack:
1. Add execution logic in each component's `run()` method
2. Import actual Decide API clients
3. Add error handling and validation
4. Update this README with integration details