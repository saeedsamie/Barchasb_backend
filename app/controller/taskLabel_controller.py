import uuid

from sqlalchemy.orm import Session

from app.models import Task, User
from app.models.TaskLabel import TaskLabel


def list_labeled_tasks_by_user(db: Session, user_id: uuid.UUID):
    return db.query(TaskLabel).filter(TaskLabel.user_id == user_id).all()


def submit_label(db: Session, user_id: uuid.UUID, task_id: uuid.UUID, content: str):
    label = TaskLabel(user_id=user_id, task_id=task_id, content=content)
    db.add(label)

    user = db.query(User).filter(User.id == user_id).first()
    task = db.query(Task).filter(Task.id == task_id).first()

    if user and task:
        user.points += task.point
        user.labeled_count += 1
        db.commit()
        return label
    db.rollback()
    return None


def calculate_consensus(db: Session, task_id: uuid.UUID):
    labels = db.query(TaskLabel).filter(TaskLabel.task_id == task_id).all()
    if labels:
        content_votes = {}
        for label in labels:
            content_votes[label.content] = content_votes.get(label.content, 0) + 1
        consensus = max(content_votes, key=content_votes.get)
        # Mark task as done if consensus is reached
        task = db.query(Task).filter(Task.id == task_id).first()
        if task and len(labels) > 5:
            task.is_done = True
            db.commit()
        return task
    return None

# def submit_task(db: Session, label: TaskLabel):
#     """
#     Submit a label for a specific task.
#
#     Args:
#         db (Session): Database session.
#         label (TaskLabel): TaskLabel object containing the task ID and the label content.
#
#     Returns:
#         TaskLabel: The created label object.
#     """
#     """
#         Submit a label for a task.
#         """
#     # Ensure all required fields are set
#     if not label.user_id or not label.task_id or not label.content:
#         raise ValueError("Missing required fields: user_id, task_id, or content")
#     db.add(label)
#     db.commit()
#     db.refresh(label)
#     return label

# def edit_labeled_task(db: Session, label_id: uuid.UUID, new_content: str):
#     label = db.query(TaskLabel).filter(TaskLabel.id == label_id).first()
#     if label:
#         label.content = new_content
#         db.commit()
#         return {"status": "success"}
#     return {"status": "failure"}
