import pytest
from httpx import ASGITransport, AsyncClient

from app.config.settings import get_settings


@pytest.mark.e2e
async def test_service_info_available(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "ok"
    assert data["name"] == "FastAPI Monolith Template"


@pytest.mark.e2e
async def test_openapi_docs_available(client: AsyncClient) -> None:
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.e2e
async def test_openapi_schema_available(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "FastAPI Monolith Template"
    schemas = data["components"]["schemas"]
    assert "ErrorEnvelope" in schemas
    assert "SuccessEnvelope" in schemas
    assert "TaskListResponse" in schemas

    # Successful payloads travel inside the envelope, so the documented schema
    # must describe the wrapper with the payload under `data`.
    list_schema = data["paths"]["/api/v1/tasks/"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert list_schema["allOf"][0]["$ref"] == "#/components/schemas/SuccessEnvelope"
    assert list_schema["allOf"][1]["properties"]["data"]["$ref"] == "#/components/schemas/TaskListResponse"

    # 204 has no body, so it must not advertise an envelope.
    delete_responses = data["paths"]["/api/v1/tasks/{task_id}"]["delete"]["responses"]
    assert "content" not in delete_responses["204"]

    # Health is parsed by orchestrators and must stay unwrapped.
    health_schema = data["paths"]["/health"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert "allOf" not in health_schema


@pytest.mark.e2e
async def test_docs_available_when_rate_limit_storage_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REDIS_HOST", "127.0.0.1")
    monkeypatch.setenv("REDIS_PORT", "1")
    get_settings.cache_clear()

    from app.main import create_app

    app = create_app()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as rate_limited_client:
            docs_response = await rate_limited_client.get("/docs")
            root_response = await rate_limited_client.get("/")
    finally:
        get_settings.cache_clear()

    assert docs_response.status_code == 200
    assert root_response.status_code == 200
