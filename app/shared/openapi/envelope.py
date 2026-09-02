"""Documents the success envelope in the generated OpenAPI schema.

FastAPI derives each operation's schema from its `response_model`, which
describes the handler's return value. `ResponseEnvelopeMiddleware` then wraps
that value under `data`, so without this pass the spec would describe a payload
clients never actually receive.
"""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

SUCCESS_ENVELOPE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["success", "statusCode", "timestamp", "path", "method", "data"],
    "properties": {
        "success": {"type": "boolean", "enum": [True]},
        "statusCode": {"type": "integer", "minimum": 200, "maximum": 399},
        "timestamp": {"type": "string", "format": "date-time"},
        "path": {"type": "string"},
        "method": {"type": "string"},
        "data": {},
        "meta": {
            "type": "object",
            "properties": {
                "requestId": {"type": "string"},
                "version": {"type": "string"},
                "duration": {"type": "integer", "minimum": 0},
            },
        },
    },
}

# Paths whose payloads are served verbatim; must match the middleware skip list.
UNWRAPPED_EXACT = frozenset({"/metrics"})
UNWRAPPED_PREFIXES = ("/health",)


def _is_unwrapped(path: str) -> bool:
    return path in UNWRAPPED_EXACT or path.startswith(UNWRAPPED_PREFIXES)


def _envelope_of(data_schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "allOf": [
            {"$ref": "#/components/schemas/SuccessEnvelope"},
            {"type": "object", "required": ["data"], "properties": {"data": data_schema}},
        ]
    }


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description=app.description or None,
    )

    schema.setdefault("components", {}).setdefault("schemas", {})
    schema["components"]["schemas"]["SuccessEnvelope"] = SUCCESS_ENVELOPE_SCHEMA

    for path, path_item in schema.get("paths", {}).items():
        if _is_unwrapped(path):
            continue

        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue

            for status_code, response in operation.get("responses", {}).items():
                # 204 carries no body, and 4xx/5xx are already error envelopes.
                if not status_code.startswith("2") or status_code == "204":
                    continue

                content = response.get("content", {}).get("application/json")
                if content and "schema" in content:
                    content["schema"] = _envelope_of(content["schema"])

    app.openapi_schema = schema
    return schema
