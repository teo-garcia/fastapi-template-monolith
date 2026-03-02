import pytest
from httpx import AsyncClient

API_PREFIX = "/api"


@pytest.mark.e2e
class TestTasksCRUD:
    async def test_create_task(self, client: AsyncClient) -> None:
        response = await client.post(
            f"{API_PREFIX}/tasks/",
            json={"title": "Test task", "description": "A test task", "priority": 3},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test task"
        assert data["description"] == "A test task"
        assert data["status"] == "PENDING"
        assert data["priority"] == 3
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_list_tasks(self, client: AsyncClient) -> None:
        await client.post(f"{API_PREFIX}/tasks/", json={"title": "Task for listing"})
        response = await client.get(f"{API_PREFIX}/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_task(self, client: AsyncClient) -> None:
        create_resp = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Task to get"})
        task_id = create_resp.json()["id"]

        response = await client.get(f"{API_PREFIX}/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Task to get"

    async def test_update_task(self, client: AsyncClient) -> None:
        create_resp = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Task to update"})
        task_id = create_resp.json()["id"]

        response = await client.patch(
            f"{API_PREFIX}/tasks/{task_id}",
            json={"title": "Updated title", "status": "IN_PROGRESS"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["status"] == "IN_PROGRESS"

    async def test_delete_task(self, client: AsyncClient) -> None:
        create_resp = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Task to delete"})
        task_id = create_resp.json()["id"]

        response = await client.delete(f"{API_PREFIX}/tasks/{task_id}")
        assert response.status_code == 204

        get_resp = await client.get(f"{API_PREFIX}/tasks/{task_id}")
        assert get_resp.status_code == 404


@pytest.mark.e2e
class TestTasksValidation:
    async def test_create_task_empty_title_rejected(self, client: AsyncClient) -> None:
        response = await client.post(f"{API_PREFIX}/tasks/", json={"title": ""})
        assert response.status_code == 422

    async def test_create_task_missing_title_rejected(self, client: AsyncClient) -> None:
        response = await client.post(f"{API_PREFIX}/tasks/", json={"description": "no title"})
        assert response.status_code == 422

    async def test_create_task_invalid_priority_rejected(self, client: AsyncClient) -> None:
        response = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Bad priority", "priority": 99})
        assert response.status_code == 422

    async def test_create_task_invalid_status_rejected(self, client: AsyncClient) -> None:
        response = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Bad status", "status": "INVALID"})
        assert response.status_code == 422


@pytest.mark.e2e
class TestTasksNotFound:
    async def test_get_nonexistent_task(self, client: AsyncClient) -> None:
        response = await client.get(f"{API_PREFIX}/tasks/nonexistent-id")
        assert response.status_code == 404

    async def test_update_nonexistent_task(self, client: AsyncClient) -> None:
        response = await client.patch(f"{API_PREFIX}/tasks/nonexistent-id", json={"title": "nope"})
        assert response.status_code == 404

    async def test_delete_nonexistent_task(self, client: AsyncClient) -> None:
        response = await client.delete(f"{API_PREFIX}/tasks/nonexistent-id")
        assert response.status_code == 404
