from collections.abc import Iterator

import pytest
from httpx import AsyncClient
from pytest import MonkeyPatch

from app.config.settings import get_settings

API_PREFIX = "/api/v1"


@pytest.fixture
def low_throttle(monkeypatch: MonkeyPatch) -> Iterator[None]:
    """Build the app with a limit small enough to exceed in one test."""
    monkeypatch.setenv("THROTTLE_LIMIT", "2/minute")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.e2e
async def test_rate_limit_rejects_requests_over_the_limit(low_throttle: None, client: AsyncClient) -> None:
    # Routes mounted through include_router are the ones a framework upgrade can
    # hide from the limiter, so exercise one of them rather than an app-level route.
    responses = [await client.get(f"{API_PREFIX}/tasks") for _ in range(4)]
    statuses = [response.status_code for response in responses]

    assert 429 in statuses, f"rate limit was not enforced: {statuses}"
    rejected = next(response for response in responses if response.status_code == 429)
    body = rejected.json()
    assert body["success"] is False
    assert body["error"] == "RateLimitError"
    assert body["meta"]["requestId"] == rejected.headers["x-request-id"]
    assert rejected.headers["retry-after"].isdigit()
    assert rejected.headers["x-content-type-options"] == "nosniff"
