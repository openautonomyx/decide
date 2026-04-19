"""
LangGraph runtime adapter — Phase 4 (skeleton).

Dynamic-spawn pattern:
  planner → scheduler(Send fan-out, deps-aware) → worker(ReAct + MCP tools)
    → aggregator(reduce) → [loop to planner if incomplete] → END

Integrates with existing control plane:
  - execution_request / execution_history / usage_record (audit via app/orchestrator/audit_logger.py)
  - approval_request (HITL via app/hitl/ — wired in Task #17)
  - evaluation_record (scoring via app/eval/ — wired in Task #18)
  - cortex_memory (preference feedback via app/feedback/ — wired in Task #19)
"""
from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from app.orchestrator.types import OrchestratorRequest
from app.runtime.types import RuntimeCapability


# ─── State ────────────────────────────────────────────────────────────────────
# TODO(USER #1 of 2): merge strategy for parallel worker results.
#   operator.add      → append (list concat). Safe default; keeps all partials.
#   merge_dict        → dict merge. Use if workers return disjoint keyed outputs.
#   last_write_wins   → simple replace. Use only if workers race intentionally.
# This choice decides whether parallel workers clobber each other.
WorkerResultsReducer = operator.add  # REPLACE with chosen reducer


class LangGraphState(TypedDict, total=False):
    execution_id: str
    tenant_id: str
    goal: str
    subtasks: list[dict]                                    # planner output
    worker_results: Annotated[list[dict], WorkerResultsReducer]  # parallel-safe
    iteration: int                                          # planner loop count
    final_output: str
    approval_status: str | None                             # HITL (Task #17)
    eval_scores: list[dict]                                 # per-worker (Task #18)


# ─── Planner prompt ──────────────────────────────────────────────────────────
# TODO(USER #2 of 2): decomposition prompt.
#   Instructions must produce a JSON list: [{goal, tool_hint, deps: [subtask_id]}, ...]
#   Design considerations:
#     - What counts as "parallel-safe" in AutonomyX? (e.g. don't publish same
#       content to WP+Ghost in parallel; DO crawl+analyze in parallel)
#     - How granular should subtasks be? One-MCP-call vs multi-step goal.
#     - What tool_hint values map onto the 12 MCPs?
#         publish:  liferay | wordpress | ghost | webstudio
#         operate:  postiz | baserow | teachable | mercur | n8n | hostinger | logto
#         observe:  matomo
PLANNER_PROMPT = """
TODO: decomposition prompt goes here.
Input: a user goal. Output: JSON list of subtasks with {goal, tool_hint, deps}.
"""


# ─── Graph (stub — Task #3 implements) ───────────────────────────────────────
def build_graph():
    raise NotImplementedError("Task #3: wire planner→scheduler→worker→aggregator with LangGraph")


# ─── Adapter (stub — Task #3 registers with runtime_invoker) ─────────────────
class LangGraphRuntime:
    """BaseRuntimeAdapter impl — registered as runtime_id='langgraph'."""

    capability = RuntimeCapability(
        tags=["orchestration", "parallel", "dynamic-spawn"],
        supports_streaming=True,
        supports_tools=True,
        supports_checkpoint=True,
        supports_parallel=True,
        supports_mcp=True,
    )

    def execute(self, state, request: OrchestratorRequest):
        raise NotImplementedError("Task #3")

    def execute_fallback(self, request: OrchestratorRequest):
        raise NotImplementedError("Task #3")
