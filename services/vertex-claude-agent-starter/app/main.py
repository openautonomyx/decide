from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.middleware.request_context import RequestContextMiddleware
from app.observability.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Vertex Claude Agent Starter", version="0.1.0", lifespan=lifespan)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(health_router)
    app.include_router(chat_router)
    return app


app = create_app()
