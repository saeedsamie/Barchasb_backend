import uuid

from sqlalchemy.orm import Session

from app.models import User, Task
from app.models.TaskReport import TaskReport


def list_reported_tasks_by_user(db: Session, user_id: uuid.UUID):
    """
    Get all tasks that have been reported by a specific user.

    Args:
        db (Session): SQLAlchemy database session
        user_id (uuid.UUID): ID of the user whose reports to retrieve

    Returns:
        Query[TaskReport]: Query object containing user's task reports
    """
    return db.query(TaskReport).filter(TaskReport.user_id == user_id)


def report_task(db: Session, user_id: uuid.UUID, task_id: uuid.UUID, details: str):
    """
    Create a new task report.

    Args:
        db (Session): SQLAlchemy database session
        user_id (uuid.UUID): ID of the user submitting the report
        task_id (uuid.UUID): ID of the task being reported
        details (str): Details of the report

    Returns:
        TaskReport: The created report object if successful, None otherwise
    """
    task_report = TaskReport(user_id=user_id, task_id=task_id, details=details)
    db.add(task_report)

    user = db.query(User).filter(User.id == user_id).first()
    task = db.query(Task).filter(Task.id == task_id).first()

    if user and task:
        db.commit()
        db.refresh(task_report)
        return task_report
    db.rollback()
    return None
