import json
import time
from datetime import UTC, datetime
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config.settings import get_settings

# Paths served verbatim. Health and metrics are parsed by orchestrators and
# Prometheus, and the docs routes serve HTML/the OpenAPI document, so none of
# them may be wrapped. Mirrors the skip lists in the Nest, Adonis and Gin
# templates.
UNWRAPPED_EXACT = frozenset({"/metrics", "/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"})
UNWRAPPED_PREFIXES = ("/health",)


def _is_unwrapped(path: str) -> bool:
    return path in UNWRAPPED_EXACT or path.startswith(UNWRAPPED_PREFIXES)


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """Wraps successful responses in the shared portfolio success envelope:

    {success, statusCode, timestamp, path, method, data, meta{requestId, version, duration}}

    Failures are left alone: `app/shared/exceptions/handlers.py` already emits
    the matching error envelope.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = time.perf_counter()
        response = await call_next(request)

        if _is_unwrapped(request.url.path):
            return response

        # 204 must not carry a body, and >= 400 is already an error envelope.
        if response.status_code == 204 or response.status_code >= 400:
            return response

        if response.headers.get("content-type", "").split(";")[0] != "application/json":
            return response

        body = b""
        async for chunk in response.body_iterator:  # type: ignore[attr-defined]
            body += chunk if isinstance(chunk, bytes) else chunk.encode()

        if not body:
            return response

        try:
            data: Any = json.loads(body)
        except json.JSONDecodeError:
            return response

        # Never double-wrap (e.g. a handler that already returned an envelope).
        if isinstance(data, dict) and "success" in data:
            return response

        query = request.url.query
        path = f"{request.url.path}?{query}" if query else request.url.path
        meta: dict[str, Any] = {}
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            meta["requestId"] = request_id
        meta["version"] = get_settings().app_version
        meta["duration"] = round((time.perf_counter() - started) * 1000)

        envelope = {
            "success": True,
            "statusCode": response.status_code,
            "timestamp": datetime.now(UTC).isoformat(),
            "path": path,
            "method": request.method,
            "data": data,
            "meta": meta,
        }

        headers = {
            key: value
            for key, value in response.headers.items()
            # Content-Length is recomputed; the wrapped body is longer.
            if key.lower() not in {"content-length", "content-type"}
        }
        return JSONResponse(content=envelope, status_code=response.status_code, headers=headers)
