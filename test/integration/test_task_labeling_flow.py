import pytest


@pytest.mark.integration
class TestTaskLabelingFlow:
    def test_complete_task_labeling_flow(self, test_client, test_db, auth_headers):
        # 1. Create a task
        task_data = {
            "type": "image",
            "data": {"url": "test/image.jpg"},
            "title": "Integration Test Task",
            "description": "Test the complete labeling flow",
            "point": 10,
            "tags": ["test", "integration"]
        }
        task_response = test_client.post("/api/v1/tasks/new", json=task_data)
        assert task_response.status_code == 201
        task_id = task_response.json()["id"]

        # 2. Get task from feed
        feed_response = test_client.get(
            "/api/v1/tasks/feed",
            params={"limit": 1},
            headers=auth_headers
        )
        assert feed_response.status_code == 200
        assert len(feed_response.json()) == 1

        # Get current user ID
        user_response = test_client.get("/api/v1/users/user/", headers=auth_headers)
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        # 3. Submit label
        label_data = {
            "task_id": task_id,
            "user_id": user_id,
            "content": {"label": "test_label"}
        }
        label_response = test_client.post(
            "/api/v1/tasks/submit",
            json=label_data,
            headers=auth_headers
        )
        assert label_response.status_code == 200

        # 4. Verify user points updated
        user_response = test_client.get("/api/v1/users/user", headers=auth_headers)
        assert user_response.status_code == 200
        assert user_response.json()["points"] == 10
        assert user_response.json()["label_count"] == 1

        # 5. Verify task no longer in feed
        new_feed_response = test_client.get(
            "/api/v1/tasks/feed",
            params={"limit": 1},
            headers=auth_headers
        )
        assert new_feed_response.status_code == 200
        feed_tasks = new_feed_response.json()
        assert not any(task["task_id"] == task_id for task in feed_tasks)
