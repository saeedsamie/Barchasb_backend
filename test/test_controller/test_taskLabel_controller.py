import pytest
import uuid
from app.DatabaseManager import DatabaseManager, TEST_DB_URL
from app.models.Task import Task
from app.models.User import User
from app.models.TaskLabel import TaskLabel
from app.controller.taskLabel_controller import (
    list_labeled_tasks_by_user,
    submit_label,
    calculate_consensus,
)

# Initialize the DatabaseManager with the test database URL
db_manager = DatabaseManager(TEST_DB_URL)


@pytest.fixture(scope="module")
def test_session():
    """Set up the database using DatabaseManager and yield a session."""
    db_manager.init_db()  # Initialize the database and create tables
    session = db_manager.SessionLocal()
    yield session
    session.close()
    db_manager.drop_db()  # Cleanup the database after tests


def test_submit_label(test_session):
    """Test submitting a label using submit_label."""
    # Create a user and a task
    user = User(name="labeler", password="securepass")
    task = Task(type="classification", data={"example": "data"}, point=10, tags=["tag1"])
    test_session.add_all([user, task])
    test_session.commit()

    # Submit a label
    label = submit_label(
        db=test_session,
        user_id=user.id,
        task_id=task.id,
        content="Label content",
    )
    assert label is not None
    assert label.user_id == user.id
    assert label.task_id == task.id
    assert label.content == "Label content"

    # Check user points and labeled count
    updated_user = test_session.query(User).filter(User.id == user.id).first()
    assert updated_user.points == 10
    assert updated_user.labeled_count == 1


def test_submit_label_invalid_user_or_task(test_session):
    """Test submitting a label with invalid user or task IDs."""
    invalid_user_id = uuid.uuid4()
    invalid_task_id = uuid.uuid4()

    # Attempt to submit a label with invalid IDs
    label = submit_label(
        db=test_session,
        user_id=invalid_user_id,
        task_id=invalid_task_id,
        content="Invalid label",
    )
    assert label is None  # Label should not be created


def test_list_labeled_tasks_by_user(test_session):
    """Test listing labeled tasks by a specific user."""
    # Create a user and tasks
    user = User(name="task_labeler", password="password")
    task1 = Task(type="classification", data={"example": "task1"}, point=5, tags=["tag1"])
    task2 = Task(type="classification", data={"example": "task2"}, point=10, tags=["tag2"])
    test_session.add_all([user, task1, task2])
    test_session.commit()

    # Submit labels for the tasks
    submit_label(db=test_session, user_id=user.id, task_id=task1.id, content="Label for task1")
    submit_label(db=test_session, user_id=user.id, task_id=task2.id, content="Label for task2")

    # List labeled tasks
    labeled_tasks = list_labeled_tasks_by_user(db=test_session, user_id=user.id)
    assert len(labeled_tasks) == 2
    assert any(label.content == "Label for task1" for label in labeled_tasks)
    assert any(label.content == "Label for task2" for label in labeled_tasks)


def test_calculate_consensus(test_session):
    """Test calculating consensus for a task."""
    # Create a task and labels
    task = Task(type="classification", data={"example": "consensus_task"}, point=10, tags=["tag1"])
    test_session.add(task)
    test_session.commit()

    # Add labels for the task
    for i in range(6):  # Add multiple labels to trigger consensus
        user = User(name=f"user{i}", password="password")
        test_session.add(user)
        test_session.commit()
        submit_label(db=test_session, user_id=user.id, task_id=task.id, content="ConsensusLabel")

    # Calculate consensus
    consensus_task = calculate_consensus(db=test_session, task_id=task.id)
    assert consensus_task is not None
    assert consensus_task.is_done is True  # Task should be marked as done
