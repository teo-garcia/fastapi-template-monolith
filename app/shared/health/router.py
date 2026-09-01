from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Response
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.shared.database.engine import get_db
from app.shared.redis.client import get_redis

router = APIRouter(tags=["health"])
logger = structlog.get_logger("health")

# Shared portfolio health contract, identical to the frontend templates'
# `lib/health.ts` and the Nest, Adonis and Gin backends:
#   {status, timestamp, version, checks{name: "up"|"down"}}
CHECK_UP = "up"
CHECK_DOWN = "down"


def _resolve_status(checks: dict[str, str]) -> str:
    """Every check up -> ok, some up -> degraded, none up -> down."""
    states = list(checks.values())

    if not states or all(state == CHECK_UP for state in states):
        return "ok"
    if all(state == CHECK_DOWN for state in states):
        return "down"
    return "degraded"


def _now() -> str:
    return datetime.now(UTC).isoformat()


async def _run_checks(db: AsyncSession, redis: Redis) -> dict[str, str]:
    checks: dict[str, str] = {}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = CHECK_UP
    except Exception:
        await logger.awarning("health_check_failed", service="database")
        checks["database"] = CHECK_DOWN

    try:
        await redis.ping()  # type: ignore[misc]
        checks["redis"] = CHECK_UP
    except Exception:
        await logger.awarning("health_check_failed", service="redis")
        checks["redis"] = CHECK_DOWN

    return checks


async def _report(response: Response, db: AsyncSession, redis: Redis) -> dict[str, Any]:
    """Shared by /health and /health/ready so the two can never disagree."""
    checks = await _run_checks(db, redis)
    status = _resolve_status(checks)

    # Degraded and down both drain the instance.
    response.status_code = 200 if status == "ok" else 503

    return {
        "status": status,
        "timestamp": _now(),
        "version": get_settings().app_version,
        "checks": checks,
    }


@router.get("/health/live")
async def liveness() -> dict[str, Any]:
    """Liveness reports no checks: a dependency outage must not restart a
    healthy process."""
    return {
        "status": "ok",
        "timestamp": _now(),
        "version": get_settings().app_version,
    }


@router.get("/health/ready")
async def readiness(
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict[str, Any]:
    return await _report(response, db, redis)


@router.get("/health")
async def health(
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict[str, Any]:
    return await _report(response, db, redis)
