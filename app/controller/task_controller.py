import uuid

from sqlalchemy.orm import Session

from app.models import TaskLabel, TaskReport
from app.models.Task import Task


def list_done_tasks(db: Session):
    """List all tasks marked as done."""
    return db.query(Task).filter(Task.is_done == True).all()


def get_task_feed(user_id: uuid, db: Session):
    try:
        # Fetch tasks that are not completed and not labeled or reported by the user
        tasks = db.query(Task).filter(
            Task.is_done == False,
            ~Task.id.in_(db.query(TaskLabel.task_id).filter(TaskLabel.user_id == user_id)),
            ~Task.id.in_(db.query(TaskReport.task_id).filter(TaskReport.user_id == user_id))
        ).all()
        return tasks
    except Exception as e:
        print(f"Error fetching task feed: {e}")
        return []


def add_task(db: Session, type: str, data: dict, point: int, is_done: bool = False, tags: list = None):
    task = Task(type=type, data=data, point=point, is_done=is_done, tags=tags or [])
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def mark_task_done(db: Session, task_id: uuid.UUID):
    """Mark a task as done."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise ValueError(f"Task with ID {task_id} not found.")
    task.is_done = True
    db.commit()
    db.refresh(task)
    return task

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
