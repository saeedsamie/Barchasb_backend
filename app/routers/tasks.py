from fastapi import APIRouter, HTTPException

from app.schemas.task import Submission

router = APIRouter()

tasks_db = {}
submissions_db = {}


@router.get("/")
def get_tasks():
    return list(tasks_db.values())


@router.get("/{task_id}")
def get_task(task_id: int):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/submit")
def submit_task(task_id: int, submission: Submission):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    submissions_db.setdefault(task_id, []).append(submission)
    tasks_db[task_id].total_labels += 1
    return {"message": "Submission recorded"}


@router.post("/report")
def report_task(task_id: int, reason: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task reported", "reason": reason}
