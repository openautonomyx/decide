from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from uuid import uuid4

app = FastAPI()
THREADS: Dict[str, Dict[str, Any]] = {}


class ThreadCreate(BaseModel):
    namespace: str = "task"
    metadata: Dict[str, Any] = {}


class CheckpointCreate(BaseModel):
    state: Dict[str, Any]


@app.post("/threads")
def create_thread(payload: ThreadCreate):
    thread_id = str(uuid4())
    THREADS[thread_id] = {
        "namespace": payload.namespace,
        "metadata": payload.metadata,
        "checkpoints": []
    }
    return {"thread_id": thread_id}


@app.get("/threads/{thread_id}")
def get_thread(thread_id: str):
    return THREADS.get(thread_id, {"error": "not_found"})


@app.post("/threads/{thread_id}/checkpoint")
def checkpoint(thread_id: str, payload: CheckpointCreate):
    if thread_id not in THREADS:
        return {"error": "not_found"}
    THREADS[thread_id]["checkpoints"].append(payload.state)
    return {"status": "ok", "count": len(THREADS[thread_id]["checkpoints"])}
