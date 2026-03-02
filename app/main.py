import signal
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config.settings import get_settings
from app.modules.tasks.router import router as tasks_router
from app.shared.database.engine import dispose_engine
from app.shared.exceptions.handlers import register_exception_handlers
from app.shared.health.router import router as health_router
from app.shared.logging.config import configure_logging
from app.shared.metrics.middleware import MetricsMiddleware
from app.shared.metrics.router import router as metrics_router
from app.shared.middleware.logging_mw import LoggingMiddleware
from app.shared.middleware.request_id import RequestIdMiddleware
from app.shared.middleware.security_headers import SecurityHeadersMiddleware
from app.shared.redis.client import redis_client

logger = structlog.get_logger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    configure_logging(log_level=settings.log_level, json_output=settings.log_json)
    await logger.ainfo("starting", app=settings.app_name, version=settings.app_version)
    yield
    await logger.ainfo("shutting_down")
    await redis_client.aclose()
    await dispose_engine()


def _setup_shutdown_hooks(timeout: int) -> None:
    def _force_exit(signum: int, _frame: object) -> None:
        name = signal.Signals(signum).name
        print(f"{name} received, forcing exit after {timeout}s timeout", file=sys.stderr)  # noqa: T201
        sys.exit(1)

    signal.signal(signal.SIGTERM, _force_exit)
    signal.signal(signal.SIGINT, _force_exit)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Middleware stack (last added = first executed)
    if settings.metrics_enabled:
        app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(SlowAPIMiddleware)

    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[settings.cors_origin],
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_credentials=True,
            allow_headers=["*"],
        )

    # Rate limiting
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address, default_limits=[settings.throttle_limit])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # Exception handlers
    register_exception_handlers(app)

    # Routers (health and metrics are outside the API prefix)
    app.include_router(health_router)
    if settings.metrics_enabled:
        app.include_router(metrics_router)
    app.include_router(tasks_router, prefix=settings.api_prefix)

    _setup_shutdown_hooks(settings.shutdown_timeout)

    return app


app = create_app()
