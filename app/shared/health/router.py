from typing import Any

import structlog
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.engine import get_db
from app.shared.redis.client import get_redis

router = APIRouter(tags=["health"])
logger = structlog.get_logger("health")


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict[str, Any]:
    await db.execute(text("SELECT 1"))
    await redis.ping()  # type: ignore[misc]
    return {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}


@router.get("/health")
async def health(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict[str, Any]:
    checks: dict[str, str] = {}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        await logger.awarning("health_check_failed", service="database")
        checks["database"] = "error"

    try:
        await redis.ping()  # type: ignore[misc]
        checks["redis"] = "ok"
    except Exception:
        await logger.awarning("health_check_failed", service="redis")
        checks["redis"] = "error"

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}
