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
from app.api import skill as r_skill
from app.api import tool as r_tool
from app.api import context as r_context
from app.api import decision as r_decision
from app.api import workflow as r_workflow_definition
from app.api import execution_identity as r_execution_identity

app.include_router(r_tenants.router, prefix=settings.api_prefix)
app.include_router(r_employees.router, prefix=settings.api_prefix)
app.include_router(r_agents.router, prefix=settings.api_prefix)
app.include_router(r_collaboration.router, prefix=settings.api_prefix)
app.include_router(r_workflow.router, prefix=settings.api_prefix)
app.include_router(r_channel.router, prefix=settings.api_prefix)
app.include_router(r_runtime.router, prefix=settings.api_prefix)
app.include_router(r_skill.router, prefix=settings.api_prefix)
app.include_router(r_tool.router, prefix=settings.api_prefix)
app.include_router(r_context.router, prefix=settings.api_prefix)
app.include_router(r_decision.router, prefix=settings.api_prefix)
app.include_router(r_workflow_definition.router, prefix=settings.api_prefix)
app.include_router(r_execution_identity.router, prefix=settings.api_prefix)

# New platforms
from app.api import memory as r_memory
from app.api import skill as r_skill_new

app.include_router(r_memory.router, prefix=settings.api_prefix)
app.include_router(r_skill_new.router, prefix=settings.api_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
