"""Process + Policy document to AgentNxt flow blueprint component."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from langflow.base import Component
from langflow.inputs import DropdownInput, IntInput, MessageTextInput
from langflow.outputs import AnyOutput


class ProcessDocFlowBuilder(Component):
    display_name = "Process+Policy Flow Builder"
    description = "Converts process and policy docs into an end-to-end flow blueprint and policy-derived agent teams."

    inputs = [
        MessageTextInput(name="document_text", display_name="Process Document", value=""),
        MessageTextInput(name="policy_text", display_name="Policy Document", value=""),
        MessageTextInput(name="document_path", display_name="Process Path", value=""),
        MessageTextInput(name="policy_path", display_name="Policy Path", value=""),
        DropdownInput(name="format_hint", display_name="Format", options=["auto", "markdown", "plain_text", "json"], value="auto"),
        IntInput(name="max_steps", display_name="Max Steps", value=30),
    ]

    outputs = [
        AnyOutput(name="steps", display_name="Steps"),
        AnyOutput(name="policies", display_name="Policies"),
        AnyOutput(name="agent_plan", display_name="Agent Plan"),
        AnyOutput(name="flow_blueprint", display_name="Flow Blueprint"),
    ]

    def run(self) -> None:
        process_text = (self.inputs.document_text or "").strip()
        policy_text = (self.inputs.policy_text or "").strip()
        if not process_text and (self.inputs.document_path or "").strip():
            process_text = Path(self.inputs.document_path.strip()).read_text(encoding="utf-8")
        if not policy_text and (self.inputs.policy_path or "").strip():
            policy_text = Path(self.inputs.policy_path.strip()).read_text(encoding="utf-8")

        steps = self._extract_steps(process_text, (self.inputs.format_hint or "auto").strip(), int(self.inputs.max_steps or 30))
        policies = self._extract_policies(policy_text)
        agent_plan = self._build_agent_plan(policies)
        blueprint = self._to_blueprint(steps, policies, agent_plan)

        self.re_outputs.steps.send(steps)
        self.re_outputs.policies.send(policies)
        self.re_outputs.agent_plan.send(agent_plan)
        self.re_outputs.flow_blueprint.send(blueprint)

    def _extract_steps(self, text: str, fmt: str, max_steps: int) -> list[dict[str, Any]]:
        raw = (text or "").strip()
        if not raw:
            return []

        if fmt in {"json", "auto"}:
            try:
                parsed = json.loads(raw)
                items = parsed.get("steps") if isinstance(parsed, dict) else None
                if isinstance(items, list):
                    return self._normalize_steps(items[:max_steps])
            except Exception:
                pass

        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        numbered = [re.sub(r"^\d+[\.)]\s*", "", l) for l in lines if re.match(r"^\d+[\.)]\s+", l)]
        bullets = [re.sub(r"^[-*]\s+", "", l) for l in lines if re.match(r"^[-*]\s+", l)]
        headers = [re.sub(r"^#{1,6}\s+", "", l) for l in lines if l.startswith("#")]
        candidates = numbered or bullets or headers or lines
        return self._normalize_steps(candidates[:max_steps])

    def _normalize_steps(self, steps: list[Any]) -> list[dict[str, Any]]:
        out = []
        for i, step in enumerate(steps, start=1):
            if isinstance(step, dict):
                title = str(step.get("title") or step.get("name") or f"Step {i}")
                detail = str(step.get("description") or title)
            else:
                title = str(step)
                detail = str(step)
            out.append({
                "id": f"step_{i}",
                "title": title,
                "description": detail,
                "component_hint": self._hint(detail),
            })
        return out

    def _extract_policies(self, text: str) -> list[dict[str, Any]]:
        raw = (text or "").strip()
        if not raw:
            return []
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        items = []
        for i, line in enumerate(lines, start=1):
            s = re.sub(r"^[-*]\s+", "", re.sub(r"^\d+[\.)]\s*", "", line))
            level = "high" if any(x in s.lower() for x in ["must", "required", "forbidden", "deny", "block"]) else "medium"
            items.append({"id": f"policy_{i}", "rule": s, "severity": level})
        return items

    def _build_agent_plan(self, policies: list[dict[str, Any]]) -> dict[str, Any]:
        default_agents = ["default_orchestrator", "default_memory", "default_skills", "default_search"]
        if not policies:
            return {
                "default_agents_archived": False,
                "archived_default_agents": [],
                "generated_agents": [],
                "generated_teams": [],
            }

        generated_agents = []
        for index, policy in enumerate(policies, start=1):
            slug = re.sub(r"[^a-z0-9]+", "_", policy["rule"].lower()).strip("_")[:40] or f"policy_{index}"
            generated_agents.append(
                {
                    "id": f"agent_{index}_{slug}",
                    "name": f"Policy Agent {index}",
                    "source_policy_id": policy["id"],
                    "policy_rule": policy["rule"],
                    "severity": policy["severity"],
                    "team": "policy_automation_team",
                    "status": "active",
                }
            )

        return {
            "default_agents_archived": True,
            "archived_default_agents": default_agents,
            "generated_agents": generated_agents,
            "generated_teams": [
                {
                    "id": "policy_automation_team",
                    "name": "Policy Automation Team",
                    "mission": "Execute policy-derived orchestration safely.",
                    "agent_ids": [a["id"] for a in generated_agents],
                }
            ],
        }

    def _hint(self, text: str) -> str:
        t = text.lower()
        if "approve" in t or "sign-off" in t:
            return "ApprovalGate"
        if "policy" in t or "compliance" in t or "risk" in t:
            return "PolicyCheck"
        if "memory" in t or "context" in t:
            return "MemoryResolver"
        if "skill" in t or "tool" in t:
            return "SkillResolver"
        if "search" in t:
            return "SearchAction"
        if "insight" in t or "analysis" in t:
            return "InsightAction"
        if "onboard" in t:
            return "OnboardingAction"
        return "TaskNode"

    def _to_blueprint(self, steps: list[dict[str, Any]], policies: list[dict[str, Any]], agent_plan: dict[str, Any]) -> dict[str, Any]:
        nodes = [{"id": "start", "type": "StartNode", "position": {"x": 80, "y": 180}, "data": {"label": "Start"}}]
        edges = []
        prev = "start"
        for i, step in enumerate(steps, start=1):
            nid = step["id"]
            nodes.append({
                "id": nid,
                "type": step["component_hint"],
                "position": {"x": 280 + (i - 1) * 220, "y": 180},
                "data": {
                    "title": step["title"],
                    "description": step["description"],
                    "policies": policies,
                    "agent_plan": agent_plan,
                },
            })
            edges.append({"id": f"edge_{prev}_{nid}", "source": prev, "target": nid})
            prev = nid

        nodes.append({"id": "end", "type": "EndNode", "position": {"x": 280 + len(steps) * 220, "y": 180}, "data": {"label": "End"}})
        edges.append({"id": f"edge_{prev}_end", "source": prev, "target": "end"})

        return {
            "name": "Generated Process Flow",
            "description": "Auto-generated from process and policy docs",
            "status": "ok",
            "policy_count": len(policies),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "agent_plan": agent_plan,
            "nodes": nodes,
            "edges": edges,
        }
