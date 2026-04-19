"""
Autonomyx Backend - Main Application Entry Point
"""
from fastapi import FastAPI
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Autonomyx API",
    description="Decision Intelligence Platform API",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
def root():
    return {"message": "Autonomyx API", "docs": "/docs"}


@app.get("/config")
def config_check():
    return {
        "database_url_set": bool(settings.database_url),
        "debug": settings.debug,
        "api_prefix": settings.api_prefix,
    }


# Register API routers
from app.api import tenants as r_tenants
from app.api import employees as r_employees
from app.api import agents as r_agents
from app.api import collaboration as r_collaboration
from app.api import tasks as r_workflow
from app.api import channel as r_channel
from app.api import runtime as r_runtime
from app.api import tool as r_tool
from app.api import context as r_context
from app.api import decision as r_decision
from app.api import workflow as r_workflow_definition
from app.api import execution_identity as r_execution_identity
from app.api import frameworks as r_frameworks

# Memory and Skills platform (replaces old skill router)
from app.api import memory as r_memory
from app.api import skill as r_skill

app.include_router(r_tenants.router, prefix=settings.api_prefix)
app.include_router(r_employees.router, prefix=settings.api_prefix)
app.include_router(r_agents.router, prefix=settings.api_prefix)
app.include_router(r_collaboration.router, prefix=settings.api_prefix)
app.include_router(r_workflow.router, prefix=settings.api_prefix)
app.include_router(r_channel.router, prefix=settings.api_prefix)
app.include_router(r_runtime.router, prefix=settings.api_prefix)
app.include_router(r_tool.router, prefix=settings.api_prefix)
app.include_router(r_context.router, prefix=settings.api_prefix)
app.include_router(r_decision.router, prefix=settings.api_prefix)
app.include_router(r_workflow_definition.router, prefix=settings.api_prefix)
app.include_router(r_execution_identity.router, prefix=settings.api_prefix)
app.include_router(r_frameworks.router, prefix=settings.api_prefix)

# Memory and Skills platform
app.include_router(r_memory.router, prefix=settings.api_prefix)
app.include_router(r_skill.router, prefix=settings.api_prefix)

# Traceability and Billing
from app.api import trace as r_trace
from app.api import billing as r_billing

app.include_router(r_trace.router, prefix=settings.api_prefix)
app.include_router(r_billing.router, prefix=settings.api_prefix)


# Demo static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")

@app.get("/demo")
def demo_index():
    """Serve demo interface"""
    index_path = os.path.join(demo_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Demo not found. Run from demo directory or build separately."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Framework compiler (LangGraph → LangFlow)
from app.api import framework as r_framework

app.include_router(r_framework.router, prefix=settings.api_prefix)

# Demo UI
from app.api import demo as r_demo

app.include_router(r_demo.router, prefix=settings.api_prefix)
