import uuid

import pytest

from app.DatabaseManager import DatabaseManager
from app.controller.taskReport_controller import (
    list_reported_tasks_by_user,
    report_task,
)
from app.models.Task import Task
from app.models.User import User

# Initialize the DatabaseManager with the test database URL
db_manager = DatabaseManager()


@pytest.fixture(scope="module")
def test_session():
    """Set up the database using DatabaseManager and yield a session."""
    db_manager.init_db()  # Initialize the database and create tables
    session = db_manager.SessionLocal()
    yield session
    session.close()
    db_manager.drop_db()  # Cleanup the database after tests


def test_report_task(test_session):
    """Test reporting a task using report_task."""
    # Create a user and a task
    user = User(name="reporter", password="securepassword")
    task = Task(
        type="classification", 
        data={"example": "data"}, 
        point=10, 
        title="Report Test Task",  # Added title
        description="Task for testing reports",  # Added description
        tags=["tag1"]
    )
    test_session.add_all([user, task])
    test_session.commit()

    # Report the task
    task_report = report_task(
        db=test_session,
        user_id=user.id,
        task_id=task.id,
        details="This task has an issue.",
    )
    assert task_report is not None
    assert task_report.user_id == user.id
    assert task_report.task_id == task.id
    assert task_report.details == "This task has an issue."


def test_report_task_invalid_user_or_task(test_session):
    """Test reporting a task with invalid user or task."""
    invalid_user_id = uuid.uuid4()
    invalid_task_id = uuid.uuid4()

    # Attempt to report a task with invalid IDs
    task_report = report_task(
        db=test_session,
        user_id=invalid_user_id,
        task_id=invalid_task_id,
        details="This task cannot be found.",
    )
    assert task_report is None  # Task report should not be created


def test_list_reported_tasks_by_user(test_session):
    """Test listing reported tasks by a specific user."""
    # Create a user and tasks
    user = User(name="task_reporter", password="anotherpassword")
    task1 = Task(
        type="classification", 
        data={"example": "task1"}, 
        point=5, 
        title="First Report Task",  # Added title
        description="First task for reporting",  # Added description
        tags=["tag1"]
    )
    task2 = Task(
        type="classification", 
        data={"example": "task2"}, 
        point=10, 
        title="Second Report Task",  # Added title
        description="Second task for reporting",  # Added description
        tags=["tag2"]
    )
    test_session.add_all([user, task1, task2])
    test_session.commit()

    # Report the tasks
    report_task(db=test_session, user_id=user.id, task_id=task1.id, details="Issue with task1.")
    report_task(db=test_session, user_id=user.id, task_id=task2.id, details="Issue with task2.")

    # List reported tasks
    reported_tasks = list_reported_tasks_by_user(db=test_session, user_id=user.id).all()
    assert len(reported_tasks) == 2
    assert any(report.details == "Issue with task1." for report in reported_tasks)
    assert any(report.details == "Issue with task2." for report in reported_tasks)
