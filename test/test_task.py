# from fastapi.testclient import TestClient
#
# from app.main import app
#
# client = TestClient(app)
#
# # Simulate user login and token retrieval
# client.post("/api/v1/auth/signup", json={"username": "test_user", "password": "SecureP@ssw0rd!"})
# login_response = client.post("/api/v1/auth/login", json={"username": "test_user", "password": "SecureP@ssw0rd!"})
# access_token = login_response.json().get("access_token")
#
#
# def test_get_task_feed():
#     response = client.get("/api/v1/tasks/feed", headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) > 0
#
#
# def test_submit_task():
#     submission = {
#         "id": 1,
#         "user_id": 1,
#         "task_id": 30418,
#         "content": {"transcription": "This is a test"}
#     }
#     response = client.post("/api/v1/tasks/submit", json=submission, headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["task_id"] == 30418
#     assert data["status"] == "submitted"
#     assert tasks_db[30418]["status"] == "completed"
#
#
# def test_report_task():
#     report = {"task_id": 30418}
#     response = client.post("/api/v1/tasks/report", json=report, headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["task_id"] == 30418
#     assert data["status"] == "reported"
#     assert tasks_db[30418]["status"] == "corrupted"
#
#
# def test_get_empty_task_feed():
#     # Simulate all tasks being completed
#     for task in tasks_db.values():
#         task["status"] = "completed"
#     response = client.get("/api/v1/tasks/feed", headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 404
#     data = response.json()
#     assert data["detail"] == "No tasks available"
