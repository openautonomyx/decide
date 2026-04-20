"""Org SSO settings generator component for AgentNxt."""

from __future__ import annotations

import json

from langflow.base import Component
from langflow.inputs import DropdownInput, MessageTextInput
from langflow.outputs import AnyOutput


class OrgSSOSettings(Component):
    display_name = "Org SSO Settings"
    description = "Builds org SSO/auth settings payload for AgentNxt."

    inputs = [
        MessageTextInput(name="org_id", display_name="Org ID", value="org-001"),
        MessageTextInput(name="org_name", display_name="Org Name", value="Organization"),
        DropdownInput(
            name="provider",
            display_name="Provider",
            options=["google", "github", "openai", "claude", "oidc"],
            value="oidc",
        ),
        MessageTextInput(name="client_id", display_name="Client ID", value=""),
        MessageTextInput(name="client_secret", display_name="Client Secret", value=""),
        MessageTextInput(name="issuer", display_name="Issuer URL", value=""),
        MessageTextInput(name="scopes", display_name="Scopes", value="openid profile email"),
        MessageTextInput(name="default_model", display_name="Default Model", value="gemma3:27b"),
    ]

    outputs = [
        AnyOutput(name="settings", display_name="Settings JSON"),
    ]

    def run(self) -> None:
        scopes = [s for s in (self.inputs.scopes or "").split() if s]
        payload = {
            "org_id": (self.inputs.org_id or "").strip(),
            "org_name": (self.inputs.org_name or "").strip(),
            "enabled": True,
            "default_model": (self.inputs.default_model or "gemma3:27b").strip(),
            "auth": {
                "provider": (self.inputs.provider or "oidc").strip(),
                "client_id": (self.inputs.client_id or "").strip(),
                "client_secret": (self.inputs.client_secret or "").strip(),
                "issuer": (self.inputs.issuer or "").strip(),
                "scopes": scopes,
            },
            "integrations": {
                "project_management": ["jira", "asana"],
                "hrms": ["workday", "bamboohr", "custom"],
                "notifications": ["email", "slack", "teams", "webhook"],
            },
        }
        self.re_outputs.settings.send(json.loads(json.dumps(payload)))
