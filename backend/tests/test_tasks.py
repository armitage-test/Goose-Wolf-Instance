import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


class TestListTasks:
    def test_empty_list(self, client: TestClient):
        response = client.get("/tasks/")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_tasks(self, client: TestClient):
        client.post("/tasks/", json={"title": "Task A"})
        client.post("/tasks/", json={"title": "Task B"})
        response = client.get("/tasks/")
        assert response.status_code == 200
        titles = [t["title"] for t in response.json()]
        assert "Task A" in titles
        assert "Task B" in titles


class TestCreateTask:
    def test_create_minimal(self, client: TestClient):
        response = client.post("/tasks/", json={"title": "Buy milk"})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy milk"
        assert data["completed"] is False
        assert data["description"] is None
        assert "id" in data

    def test_create_with_description(self, client: TestClient):
        response = client.post(
            "/tasks/", json={"title": "Buy milk", "description": "2% fat"}
        )
        assert response.status_code == 201
        assert response.json()["description"] == "2% fat"

    def test_create_empty_title_fails(self, client: TestClient):
        response = client.post("/tasks/", json={"title": ""})
        assert response.status_code == 422

    def test_create_missing_title_fails(self, client: TestClient):
        response = client.post("/tasks/", json={})
        assert response.status_code == 422


class TestGetTask:
    def test_get_existing(self, client: TestClient):
        created = client.post("/tasks/", json={"title": "Read book"}).json()
        response = client.get(f"/tasks/{created['id']}")
        assert response.status_code == 200
        assert response.json()["title"] == "Read book"

    def test_get_nonexistent(self, client: TestClient):
        response = client.get("/tasks/9999")
        assert response.status_code == 404


class TestUpdateTask:
    def test_update_title(self, client: TestClient):
        created = client.post("/tasks/", json={"title": "Old title"}).json()
        response = client.patch(f"/tasks/{created['id']}", json={"title": "New title"})
        assert response.status_code == 200
        assert response.json()["title"] == "New title"

    def test_mark_completed(self, client: TestClient):
        created = client.post("/tasks/", json={"title": "Exercise"}).json()
        response = client.patch(f"/tasks/{created['id']}", json={"completed": True})
        assert response.status_code == 200
        assert response.json()["completed"] is True

    def test_update_nonexistent(self, client: TestClient):
        response = client.patch("/tasks/9999", json={"title": "Ghost"})
        assert response.status_code == 404


class TestDeleteTask:
    def test_delete_existing(self, client: TestClient):
        created = client.post("/tasks/", json={"title": "To delete"}).json()
        response = client.delete(f"/tasks/{created['id']}")
        assert response.status_code == 204
        assert client.get(f"/tasks/{created['id']}").status_code == 404

    def test_delete_nonexistent(self, client: TestClient):
        response = client.delete("/tasks/9999")
        assert response.status_code == 404
