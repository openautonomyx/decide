from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os

from claude_agent_sdk import query
from config import load_backend_registry, load_routing_policies

app = FastAPI()

CODING_SPECIALIST_MODEL = os.getenv("CODING_SPECIALIST_MODEL", "")
WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", "/workspace")


class CodingTask(BaseModel):
    task_type: str
    repo_path: str
    goal: str
    constraints: List[str] = []
    acceptance_criteria: List[str] = []


@app.get("/.well-known/agent-card")
def agent_card():
    return {
        "name": "claude-coder",
        "description": "Autonomyx coding specialist",
        "url": "http://claude-coder:8080/invoke",
        "version": "0.1.0",
        "skills": [
            {
                "id": "coding",
                "name": "coding",
                "description": "Implements features, fixes bugs, writes tests, refactors code"
            }
        ]
    }


@app.get("/debug/backends")
def debug_backends():
    return {
        "registry": load_backend_registry(),
        "policies": load_routing_policies(),
    }


async def run_agent(task: CodingTask) -> str:
    prompt = f"""
You are the Autonomyx coding specialist.

Task type: {task.task_type}
Repository path: {task.repo_path}
Goal: {task.goal}

Constraints:
{chr(10).join(f"- {c}" for c in task.constraints) if task.constraints else "- None"}

Acceptance criteria:
{chr(10).join(f"- {a}" for a in task.acceptance_criteria) if task.acceptance_criteria else "- None"}

For now, analyze the task and return a concise execution plan.
Do not assume missing details.
"""
    chunks = []
    async for message in query(prompt):
        chunks.append(str(message))
    return "\n".join(chunks).strip()


@app.post("/invoke")
async def invoke(task: CodingTask):
    if not CODING_SPECIALIST_MODEL:
        raise HTTPException(status_code=500, detail="CODING_SPECIALIST_MODEL is not set")

    try:
        result = await run_agent(task)
        return {
            "status": "success",
            "summary": result or f"Processed coding task for goal: {task.goal}",
            "model": CODING_SPECIALIST_MODEL,
            "workspace_root": WORKSPACE_ROOT,
            "files_changed": [],
            "artifacts": {},
            "next_actions": ["Add backend selection and structured tool use"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
