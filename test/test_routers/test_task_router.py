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

db_manager = DatabaseManager()


@pytest.fixture(scope="module")
def db_session():
    """Set up the database using DatabaseManager and yield a session."""
    db_manager.init_db()  # Initialize the database and create tables
    session = db_manager.SessionLocal()
    yield session
    session.close()

    db_manager.drop_db()  # Cleanup the database after tests


def test_create_task(db_session):
    payload = {
        "type": "image",
        "data": {"url": "/path/to/file1"},
        "title": "Sample Task",
        "description": "A test task for creating an image labeling task.",
        "point": 10,
        "tags": ["urgent"]
    }
    response = client.post("/tasks/new", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert "task_id" in response_data
    assert response_data["status"] == "success"


def test_get_task_feed(db_session):
    signup_response = client.post("/users/signup", json={
        "name": "feed_test_user",
        "password": "SecureP@ssw0rd!"
    })
    login_response = client.post("/users/login", json={
        "name": "feed_test_user",
        "password": "SecureP@ssw0rd!"
    })
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/tasks/feed", params={"limit": 2}, headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) <= 2


def test_submit_task(db_session):
    # Pre-create a task to retrieve its ID
    response = client.post("/users/signup", json={
        "name": "submit_task_user",
        "password": "SecureP@ssw0rd!"
    })
    user_id = response.json()["id"]
    login_response = client.post("/users/login", json={
        "name": "submit_task_user",
        "password": "SecureP@ssw0rd!"
    })
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    task_payload = {
        "type": "image",
        "data": {"url": "/path/to/file3"},
        "title": "Task to Submit",
        "description": "A test task for submission.",
        "point": 20,
        "tags": ["review"],
    }
    task_response = client.post("/tasks/new", json=task_payload)
    assert task_response.status_code == 200
    task_id = task_response.json()["task_id"]
    submit_payload = {"user_id": user_id, "task_id": task_id, "content": {"string": "Urgent task"}}
    submit_response = client.post("/tasks/submit", json=submit_payload, headers=headers)
    assert submit_response.status_code == 200
    submission_data = submit_response.json()
    assert submission_data["status"] == "success"


def test_report_task(db_session):
    response = client.post("/users/signup", json={"name": "report_user", "password": "SecureP@ssw0rd!"})
    user_id = response.json()["id"]

    login_response = client.post("/users/login", json={
        "name": "report_user",
        "password": "SecureP@ssw0rd!"
    })
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    # Pre-create a task to retrieve its ID
    task_payload = {
        "type": "image",
        "data": {"url": "/path/to/file4"},
        "title": "Task to Report",
        "description": "A test task to report.",
        "point": 5,
        "tags": ["low_priority"],
    }
    task_response = client.post("/tasks/new", json=task_payload)
    assert task_response.status_code == 200
    task_id = task_response.json()["task_id"]

    # Report task
    report_payload = {"task_id": task_id, "user_id": user_id, "detail": "Incorrect labeling"}
    report_response = client.post("/tasks/report", json=report_payload, headers=headers)
    assert report_response.status_code == 200
    report_data = report_response.json()
    assert report_data["status"] == "success"

# def test_update_task_status():
#     # Pre-create a task to retrieve its ID
#     task_payload = {
#         "type": "image",
#         "data": {"url": "/path/to/file2"},
#         "title": "Task to Update Status",
#         "description": "A test task to update the status.",
#         "point": 15,
#         "tags": ["important"],
#     }
#     task_response = client.post("/tasks/new", json=task_payload)
#     print(task_response.json())
#     assert task_response.status_code == 200
#     task_id = task_response.json()["task_id"]
#
#     # Update task status
#     update_payload = {"new_status": "completed"}
#     update_response = client.put(f"/tasks/update/{task_id}/status", json=update_payload)
#     print(update_response.json())
#     assert update_response.status_code == 200
#     updated_data = update_response.json()
#     assert updated_data["status"] == "success"
