from typing import List

from fastapi import APIRouter, HTTPException, Depends

from app.routers.users import get_current_user
from app.schemas.task import Task, Submission
from db import MOCKING_DATABASE

router = APIRouter()

task_types = {
    0: {'title': "Automatic Speech Recognition", 'description': 'Write what you hear'},
    1: {'title': "Word Recognition", 'description': 'Word Recognition'},
    2: {'title': "Sentence Recognition", 'description': 'Word Recognition'}
}
# Mock test_database
tasks_db = MOCKING_DATABASE

submissions_db = []


# Fetch task feed
@router.get("/feed", response_model=List[Task])
def get_task_feed(limit: int = 2, current_user: dict = Depends(get_current_user)):
    tasks = [task for task in tasks_db.values() if task["status"] == "new"][:limit]
    print(tasks)
    for task in tasks:
        task.update(task_types.get(task.get('type')))
    print(tasks)
    tasks = [Task(**task) for task in tasks]
    print(tasks)

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks available")
    return tasks


# Submit a completed task
@router.post("/submit", response_model=dict)
def submit_task(submission: Submission, current_user: dict = Depends(get_current_user)):
    task = tasks_db.get(submission.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Create a new submission
    new_submission = submission.dict()
    submissions_db.append(new_submission)
    # Move task to completed state
    tasks_db[submission.task_id]["status"] = "completed"
    return {"task_id": submission.task_id, "status": "submitted"}


# Report a corrupted task
@router.post("/report", response_model=dict)
def report_task(report: dict, current_user: dict = Depends(get_current_user)):
    task_id = report.get("task_id")

    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Mark the task as corrupted
    task["status"] = "corrupted"

    return {"task_id": task_id, "status": "reported"}
