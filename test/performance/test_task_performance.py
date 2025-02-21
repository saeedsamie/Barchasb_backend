import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest


@pytest.mark.performance
class TestTaskPerformance:
    def test_task_feed_performance(self, test_client, auth_headers):
        start_time = time.time()
        response = test_client.get("/api/v1/tasks/feed", params={"limit": 100}, headers=auth_headers)
        end_time = time.time()

        assert response.status_code == 200
        assert end_time - start_time < 1.0  # Should respond within 1 second

    def test_concurrent_task_submissions(self, test_client, auth_headers, sample_task):
        # Get user ID first
        user_response = test_client.get("/api/v1/users/user/", headers=auth_headers)
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        # Create multiple tasks
        tasks = []
        for _ in range(10):
            response = test_client.post("/api/v1/tasks/new", json=sample_task)
            assert response.status_code == 201
            tasks.append(response.json()["id"])

        def submit_label(task_id):
            return test_client.post(
                "/api/v1/tasks/submit",
                json={
                    "task_id": task_id,
                    "user_id": user_id,
                    "content": {"label": "test"}
                },
                headers=auth_headers
            )

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(submit_label, task_id) for task_id in tasks]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.time()

        assert all(r.status_code == 200 for r in results)
        assert end_time - start_time < 10.0
