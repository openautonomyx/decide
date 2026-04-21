"""
Autonomyx Backend - Main Application Entry Point
"""

from contextlib import asynccontextmanager
import os
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import get_settings
from app.services.seed import seed_all

settings = get_settings()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(duration_ms)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Optionally seed default data on startup."""
    if settings.seed_on_startup:
        from app.db.session import SessionLocal

        db = SessionLocal()
        try:
            seed_all(db)
        finally:
            db.close()
    yield


app = FastAPI(
    title=settings.project_name,
    description="Decision Intelligence Platform API",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Response-Time-Ms"],
    )

if settings.allowed_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

app.add_middleware(RequestContextMiddleware)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "api_prefix": settings.api_prefix,
    }


@app.get("/")
def root():
    return {
        "message": settings.project_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/config")
def config_check():
    return {
        "database_url_set": bool(settings.database_url),
        "redis_url_set": bool(settings.redis_url),
        "debug": settings.debug,
        "api_prefix": settings.api_prefix,
        "environment": settings.environment,
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

# Memory and skills platform
from app.api import memory as r_memory
from app.api import skill as r_skill_new
from app.api import template as r_template
from app.api import component as r_component

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
app.include_router(r_memory.router, prefix=settings.api_prefix)
app.include_router(r_skill_new.router, prefix=settings.api_prefix)
app.include_router(r_template.router, prefix=settings.api_prefix)
app.include_router(r_component.router, prefix=settings.api_prefix)

# Traceability and billing
from app.api import trace as r_trace
from app.api import billing as r_billing

app.include_router(r_trace.router, prefix=settings.api_prefix)
app.include_router(r_billing.router, prefix=settings.api_prefix)

# Framework compiler (LangGraph → LangFlow)
from app.api import framework as r_framework

app.include_router(r_framework.router, prefix=settings.api_prefix)

# Demo UI
from app.api import demo as r_demo

app.include_router(r_demo.router, prefix=settings.api_prefix)

# Demo static files

demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")


@app.get("/demo")
def demo_index():
    """Serve demo interface."""
    index_path = os.path.join(demo_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Demo not found. Run from demo directory or build separately."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
