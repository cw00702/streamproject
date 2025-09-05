
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .deps import get_settings
from .routers import categories, timeseries, top_streams

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="StreamSpot API", version="0.2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins if settings.cors_allow_origins != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = settings.api_prefix
    app.include_router(categories.router, prefix=prefix)
    app.include_router(timeseries.router, prefix=prefix)
    app.include_router(top_streams.router, prefix=prefix)

    @app.get("/health", tags=["health"])
    def health():
        return {"ok": True}

    return app

app = create_app()
