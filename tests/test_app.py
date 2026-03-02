import pytest
from httpx import AsyncClient


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
