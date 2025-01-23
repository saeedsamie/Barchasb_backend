from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.DatabaseManager import TEST_DB_URL, DatabaseManager
from app.routers.tasks_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

db_manager = DatabaseManager(TEST_DB_URL)
db_manager.drop_db()
db_manager.init_db()


def test_create_task():
    payload = {
        "type": "image",
        "data": {"url": "/path/to/file1"},
        "title": "Sample Task",
        "description": "A test task for creating an image labeling task.",
        "point": 10,
        "tags": ["urgent"],
    }
    response = client.post("/tasks/new", json=payload)
    print(response.json())
    assert response.status_code == 200
    response_data = response.json()
    assert "task_id" in response_data
    assert response_data["status"] == "success"


def test_get_tasks():
    response = client.get("/tasks/feed", params={"limit": 10})
    print(response.json())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


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


def test_get_task_feed():
    response = client.get("/tasks/feed", params={"limit": 2})
    print(response.json())
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) <= 2


def test_submit_task():
    # Pre-create a task to retrieve its ID
    response = client.post("/users/signup", json={"name": "login_user", "password": "SecureP@ssw0rd!"})
    user_id = response.json()["id"]
    task_payload = {
        "type": "image",
        "data": {"url": "/path/to/file3"},
        "title": "Task to Submit",
        "description": "A test task for submission.",
        "point": 20,
        "tags": ["review"],
    }
    task_response = client.post("/tasks/new", json=task_payload)
    print(task_response.json())
    assert task_response.status_code == 200
    task_id = task_response.json()["task_id"]
    # Submit task
    submit_payload = {"user_id": user_id, "task_id": task_id, "content": "Urgent task"}
    submit_response = client.post("/tasks/submit", json=submit_payload)
    print(submit_response.json())
    assert submit_response.status_code == 200
    submission_data = submit_response.json()
    assert submission_data["status"] == "success"


def test_report_task():
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
    print(task_response.json())
    assert task_response.status_code == 200
    task_id = task_response.json()["task_id"]

    # Report task
    report_payload = {"task_id": task_id, "reason": "Incorrect labeling"}
    report_response = client.post("/tasks/report", json=report_payload)
    print(report_response.json())
    assert report_response.status_code == 200
    report_data = report_response.json()
    assert report_data["status"] == "success"
