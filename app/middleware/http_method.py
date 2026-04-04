"""Restrict API routes to POST; allow GET only for docs and health."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.settings import settings

_GET_PREFIXES = tuple(
    p.strip()
    for p in settings.API_GET_ALLOWED_PREFIXES.split(",")
    if p.strip()
)


async def allow_post_only_for_api(request: Request, call_next):
    path = request.url.path
    method = request.method

    if method == "GET":
        if any(path.startswith(p) for p in _GET_PREFIXES):
            return await call_next(request)
        if path in ("/", "/favicon.ico"):
            return await call_next(request)

    if method == "POST":
        return await call_next(request)

    if method == "OPTIONS":
        return await call_next(request)

    return JSONResponse(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        content={
            "detail": (
                "Only POST is allowed for this endpoint. "
                "Use /docs for API documentation."
            ),
        },
    )
