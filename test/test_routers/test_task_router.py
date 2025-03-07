import uuid
from pprint import pprint

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.DatabaseManager import DatabaseManager
from app.routers.tasks_router import router as t_router
from app.routers.users_router import router as u_router

app = FastAPI()
app.include_router(t_router)
app.include_router(u_router)
client = TestClient(app)

db_manager = DatabaseManager(testing=True)


@pytest.fixture(scope="module")
def db_session():
    """Set up the database using DatabaseManager and yield a session."""
    db_manager.init_db()
    session = db_manager.SessionLocal()
    yield session
    session.close()
    db_manager.drop_db()


@pytest.fixture
def auth_headers(db_session):
    """Create a test user and return auth headers."""
    user_data = {
        "name": "test_user",
        "password": "SecureP@ssw0rd!"
    }
    client.post("/users/signup", json=user_data)
    response = client.post("/users/login", json=user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_task():
    """Return a sample task payload."""
    return {
        "type": "image",
        "data": {"url": "/path/to/file1"},
        "title": "Sample Task",
        "description": "A test task for creating an image labeling task.",
        "point": 10,
        "tags": ["urgent"]
    }


class TestTaskCreation:
    def test_create_task_success(self, db_session, sample_task):
        """Test successful task creation."""
        response = client.post("/tasks/new", json=sample_task)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "title" in data

    def test_create_task_invalid_points(self, db_session):
        """Test task creation with invalid points."""
        invalid_task = {
            "type": "image",
            "data": {"url": "/path/to/file"},
            "title": "Invalid Task",
            "description": "Task with invalid points",
            "point": -10,
            "tags": ["test"]
        }
        response = client.post("/tasks/new", json=invalid_task)
        assert response.status_code == 422

    def test_create_task_missing_required_fields(self, db_session):
        """Test task creation with missing required fields."""
        invalid_task = {
            "type": "image",
            "point": 10
        }
        response = client.post("/tasks/new", json=invalid_task)
        assert response.status_code == 422


class TestTaskFeed:
    def test_get_task_feed_success(self, db_session, auth_headers, sample_task):
        """Test successful retrieval of task feed."""
        # Create a task first
        client.post("/tasks/new", json=sample_task)

        response = client.get("/tasks/feed", params={"limit": 2}, headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)
        assert len(tasks) <= 2

        if tasks:
            task = tasks[0]
            assert "id" in task
            assert "type" in task
            assert "data" in task
            assert "point" in task
            assert "tags" in task

    def test_get_task_feed_unauthorized(self, db_session):
        """Test task feed access without authentication."""
        response = client.get("/tasks/feed", params={"limit": 2})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_task_feed_invalid_limit(self, db_session, auth_headers):
        """Test task feed with invalid limit parameter."""
        response = client.get("/tasks/feed", params={"limit": -1}, headers=auth_headers)
        assert response.status_code == 422  # Pydantic validation error
        assert "greater than" in response.json()["detail"][0]["msg"]


class TestTaskSubmission:
    def test_submit_task_success(self, db_session, auth_headers, sample_task):
        """Test successful task submission."""
        # Create a task first
        task_response = client.post("/tasks/new", json=sample_task)
        task_id = task_response.json()["id"]

        submit_payload = {
            "task_id": task_id,
            "content": {"label": "test_label"}
        }
        response = client.post("/tasks/submit", json=submit_payload, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_submit_task_nonexistent(self, db_session, auth_headers):
        """Test submitting a non-existent task."""
        submit_payload = {
            "task_id": str(uuid.uuid4()),
            "content": {"label": "test_label"}
        }
        response = client.post("/tasks/submit", json=submit_payload, headers=auth_headers)
        assert response.status_code == 400  # Business logic error
        assert "Task not found" in response.json()["detail"]

    def test_submit_task_invalid_content(self, db_session, auth_headers, sample_task):
        """Test submitting a task with invalid content."""
        task_response = client.post("/tasks/new", json=sample_task)
        task_id = task_response.json()["id"]

        submit_payload = {
            "task_id": task_id,
        }
        response = client.post("/tasks/submit", json=submit_payload, headers=auth_headers)
        assert response.status_code == 422


class TestTaskReporting:
    def test_report_task_success(self, db_session, auth_headers, sample_task):
        """Test successful task reporting."""
        task_response = client.post("/tasks/new", json=sample_task)
        task_id = task_response.json()["id"]

        report_payload = {
            "task_id": task_id,
            "detail": "Issue with task instructions"
        }
        response = client.post("/tasks/report", json=report_payload, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_report_nonexistent_task(self, db_session, auth_headers):
        """Test reporting a non-existent task."""
        report_payload = {
            "task_id": str(uuid.uuid4()),
            "detail": "Task does not exist"
        }
        response = client.post("/tasks/report", json=report_payload, headers=auth_headers)
        assert response.status_code == 400

    @pytest.mark.parametrize("invalid_detail", [
        "",  # Empty detail
        "a" * 1001,  # Too long detail
        None  # Missing detail
    ])
    def test_report_task_invalid_detail(self, db_session, auth_headers, sample_task, invalid_detail):
        """Test reporting a task with invalid details."""
        task_response = client.post("/tasks/new", json=sample_task)
        task_id = task_response.json()["id"]

        report_payload = {
            "detail": invalid_detail
        }
        response = client.post("/tasks/report", json=report_payload, headers=auth_headers)
        assert response.status_code == 422


class TestUserLabeledTasks:
    def test_get_user_labeled_tasks_success(self, db_session, auth_headers, sample_task):
        """Test successful retrieval of user's labeled tasks."""
        # Reset database state
        db_manager.drop_db()
        db_manager.init_db()

        # Create new user and get auth token
        user_data = {
            "name": "labeled_test_user",
            "password": "SecureP@ssw0rd!"
        }
        signup_response = client.post("/users/signup", json=user_data)
        assert signup_response.status_code == 201

        login_response = client.post("/users/login", json=user_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Create a task
        task_response = client.post("/tasks/new", json=sample_task)
        assert task_response.status_code == 201
        task_id = task_response.json()["id"]

        # Submit a label for the task
        submit_payload = {
            "task_id": task_id,
            "content": {"label": "test_label"}
        }
        submit_response = client.post("/tasks/submit", json=submit_payload, headers=auth_headers)
        assert submit_response.status_code == 200

        # Get labeled tasks
        response = client.get("/tasks/labeled", headers=auth_headers)
        pprint(response.json())
        assert response.status_code == 200

        tasks = response.json()
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert tasks[0]["id"] == task_id
        assert "type" in tasks[0]
        assert "data" in tasks[0]
        assert "point" in tasks[0]
        assert "label" in tasks[0]

    def test_get_user_labeled_tasks_unauthorized(self, db_session):
        """Test labeled tasks access without authentication."""
        response = client.get("/tasks/labeled")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_user_labeled_tasks_empty(self, db_session, auth_headers):
        """Test when user has no labeled tasks."""
        # Reset database state and create new user
        db_manager.drop_db()
        db_manager.init_db()

        # Create new user and get auth token
        user_data = {
            "name": "test_user_empty",
            "password": "SecureP@ssw0rd!"
        }
        signup_response = client.post("/users/signup", json=user_data)
        assert signup_response.status_code == 201

        login_response = client.post("/users/login", json=user_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/tasks/labeled", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
