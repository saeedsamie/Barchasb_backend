import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Task, User
from app.models.TaskLabel import TaskLabel


def get_label_by_task(db: Session, task_id: uuid.UUID):
    """
    Get the label object for a specific task.

    Args:
        db (Session): SQLAlchemy database session
        task_id (uuid.UUID): ID of the task to get the label object for

    Returns:
        TaskLabel: The label object for the given task
        
    Raises:
        ValueError: If no label found for the task
    """
    label = db.query(TaskLabel).filter(TaskLabel.task_id == task_id).first()
    if not label:
        raise ValueError(f"No label found for task {task_id}")
    return label


def submit_label(db: Session, user_id: uuid.UUID, task_id: uuid.UUID, content: str):
    """
    Submit a new label for a task and update user points.

    Args:
        db (Session): SQLAlchemy database session
        user_id (uuid.UUID): ID of the user submitting the label
        task_id (uuid.UUID): ID of the task being labeled
        content (str): The label content

    Returns:
        TaskLabel: The created label object

    Raises:
        ValueError: If user or task not found, or on database error
    """
    try:
        label = TaskLabel(user_id=user_id, task_id=task_id, content=content)
        db.add(label)

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            db.rollback()
            raise ValueError("User not found")

        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            db.rollback()
            raise ValueError("Task not found")

        user.points += task.point
        user.labeled_count += 1
        db.commit()
        return label
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Database error: {str(e)}")


def calculate_consensus(db: Session, task_id: uuid.UUID):
    """
    Calculate the consensus label for a task based on submitted labels.
    Marks task as done if consensus is reached with more than 5 labels.

    Args:
        db (Session): SQLAlchemy database session
        task_id (uuid.UUID): ID of the task to calculate consensus for

    Returns:
        Task: The updated task object if consensus reached, None otherwise
    """
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
