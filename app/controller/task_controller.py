from sqlalchemy.orm import Session

from app.models.Task import Task
from app.models.TaskLabel import TaskLabel
from app.models.TaskReport import TaskReport


def get_task_feed(db: Session, limit):
    tasks = db.query(Task).all()[:limit]
    return tasks


def add_task(db: Session, type: str, data: dict, point: int, tags: list = None):
    task = Task(type=type, data=data, point=point, tags=tags or [])
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_done_tasks(db: Session):
    tasks = db.query(Task).filter(Task.labels.any(TaskLabel.content != None)).all()
    return tasks


def report_task(db: Session, report: TaskReport):
    """
    Report an issue with a task.

    Args:
        db (Session): Database session.
        report (TaskReport): TaskReport object containing the task ID and the report details.

    Returns:
        TaskReport: The created report object.
    """
    task_report = TaskReport(task_id=report.task_id, details=report.details)
    db.add(task_report)
    db.commit()
    db.refresh(task_report)
    return task_report

# def update_task_status(db: Session, task_id: str, new_status: str):
#     """
#     Update the status of a task.
#
#     Args:
#         db (Session): Database session.
#         task_id (str): The ID of the task to update.
#         new_status (str): The new status to set for the task.
#
#     Returns:
#         Task: The updated task object.
#     """
#     task = db.query(Task).filter(Task.id == task_id).first()
#     if not task:
#         raise ValueError(f"Task with ID {task_id} not found.")
#
#     task.status = new_status
#     db.commit()
#     db.refresh(task)
#     return task
