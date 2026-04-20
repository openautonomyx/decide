# Getting Started

1. Download a desktop bundle from `/downloads`.
2. Start AgentNxt (Langflow runtime):

```bash
docker compose -f langflow_components/autonomyx/docker-compose.langflow.yml up -d
```

3. Import flows from `langflow_components/autonomyx/flows/`.
4. Configure org SSO in AgentNxt settings with `OrgSSOSettings` or `org_sso_settings.template.json`.
5. Upload process doc + policy doc to `ProcessDocFlowBuilder`.
6. If policy is uploaded, default agents are archived and policy-derived agent teams are generated.
