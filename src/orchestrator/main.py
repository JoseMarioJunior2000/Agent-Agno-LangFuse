from src.orchestrator.api.health import router as health_router
from src.orchestrator.api.routes import router as api_router
from src.orchestrator.config.settings import get_settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
import os
from orchestrator.api.auth import require_api_key
import uvicorn

security = HTTPBearer(auto_error=False)

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.PROJECT_NAME)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix=settings.API_PREFIX)
    protected_deps = [
        Depends(security),
        Depends(require_api_key()),
    ]
    app.include_router(api_router, prefix=settings.API_PREFIX, dependencies=protected_deps)
    return app

app = create_app()