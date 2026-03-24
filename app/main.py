"""
Main FastAPI app: handles all requests. Only POST allowed on API routes.
GET allowed for /docs, /redoc, /openapi.json, /health.
DB provider is initialized once at startup so /health and all endpoints use the same pool (fast).
"""
import logging
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config._config import PRIMARY_CONFIG, REPLICA_CONFIG, REPLICA_FALLBACK
from app.config.database_session_provider import get_provider
from app.db_health_checker.health_check import router as health_router
from app.settings import settings

logger = logging.getLogger(__name__)

# Paths that allow GET (docs and health)
GET_ALLOWED_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/health")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB pool once at startup; dispose at shutdown."""
    try:
        get_provider(
            primary_config=PRIMARY_CONFIG,
            replica_config=REPLICA_CONFIG,
            replica_fallback=REPLICA_FALLBACK,
        )
        logger.info("DB provider initialized (connection pool ready)")
    except Exception as exc:
        logger.exception("DB provider startup failed: %s", exc)
        raise
    yield
    try:
        get_provider().dispose_all()
        logger.info("DB provider disposed")
    except Exception as exc:
        logger.exception("DB provider shutdown error: %s", exc)


app = FastAPI(
    title="Spirix API",
    description="Spirix backend API. Use POST for API endpoints.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(health_router)


@app.middleware("http")
async def allow_only_post_for_api(request: Request, call_next):
    """Allow GET only for docs and health; require POST for other API routes."""
    path = request.url.path
    method = request.method

    if method == "GET":
        if any(path.startswith(p) for p in GET_ALLOWED_PREFIXES):
            return await call_next(request)
        if path == "/" or path == "/favicon.ico":
            return await call_next(request)

    if method == "POST":
        return await call_next(request)

    return JSONResponse(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        content={"detail": "Only POST is allowed for this endpoint. Use /docs for API documentation."},
    )


if __name__ == "__main__":
    uvicorn.run(app, host=settings.SPIRIX_HOST, port=settings.SPIRIX_POST)