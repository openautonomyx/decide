"""Schema.org Action Catalog component for Langflow."""

from __future__ import annotations

import json
from pathlib import Path

from langflow.base import Component
from langflow.inputs import BoolInput, DropdownInput, IntInput, MessageTextInput
from langflow.outputs import AnyOutput


class SchemaOrgActionCatalog(Component):
    display_name = "Schema.org Action Catalog"
    description = "Loads schema.org action definitions for workflow builders."

    inputs = [
        DropdownInput(name="action_type", display_name="Action Type", options=["all","SearchAction","RegisterAction","AuthorizeAction","CreateAction","UpdateAction","DeleteAction","AssessAction"], value="all"),
        MessageTextInput(name="query", display_name="Query", value=""),
        IntInput(name="limit", display_name="Limit", value=50),
        BoolInput(name="include_examples", display_name="Include Examples", value=True),
    ]

    outputs = [
        AnyOutput(name="actions", display_name="Actions"),
        AnyOutput(name="catalog", display_name="Catalog"),
    ]

    def run(self) -> None:
        payload = json.loads((Path(__file__).resolve().parent / "schemaorg_actions.json").read_text(encoding="utf-8"))
        action_type = (self.inputs.action_type or "all").strip()
        query = (self.inputs.query or "").strip().lower()
        limit = max(1, int(self.inputs.limit or 50))
        include_examples = bool(self.inputs.include_examples)

        actions = []
        for action in payload.get("actions", []):
            if action_type != "all" and action.get("name") != action_type:
                continue
            blob = (action.get("name", "") + " " + action.get("description", "")).lower()
            if query and query not in blob:
                continue
            item = dict(action)
            if not include_examples:
                item.pop("example", None)
            actions.append(item)
            if len(actions) >= limit:
                break

        self.re_outputs.actions.send(actions)
        self.re_outputs.catalog.send({
            "source": payload.get("source", "schema.org"),
            "version": payload.get("version", "1.0"),
            "returned_actions": len(actions),
            "actions": actions,
        })
