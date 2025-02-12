import uuid

import pytest

from app.DatabaseManager import DatabaseManager
from app.controller.taskLabel_controller import (
    list_labeled_tasks_by_user,
    submit_label,
    calculate_consensus,
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


def test_submit_label(test_session):
    """Test submitting a label using submit_label."""
    # Create a user and a task
    user = User(name="labeler", password="securepass")
    task = Task(
        type="classification", 
        data={"example": "data"}, 
        point=10, 
        title="Test Task",  # Added title
        description="Test task for labeling",  # Added description
        tags=["tag1"]
    )
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

    # Attempt to submit a label with invalid user ID
    with pytest.raises(ValueError) as exc_info:
        submit_label(
            db=test_session,
            user_id=invalid_user_id,
            task_id=invalid_task_id,
            content="Invalid label",
        )
    assert "User not found" in str(exc_info.value)


def test_list_labeled_tasks_by_user(test_session):
    """Test listing labeled tasks by a specific user."""
    # Create a user and tasks
    user = User(name="task_labeler", password="password")
    task1 = Task(
        type="classification", 
        data={"example": "task1"}, 
        point=5, 
        title="First Task",  # Added title
        description="First test task",  # Added description
        tags=["tag1"]
    )
    task2 = Task(
        type="classification", 
        data={"example": "task2"}, 
        point=10, 
        title="Second Task",  # Added title
        description="Second test task",  # Added description
        tags=["tag2"]
    )
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
    task = Task(
        type="classification", 
        data={"example": "consensus_task"}, 
        point=10, 
        title="Consensus Task",  # Added title
        description="Task for testing consensus",  # Added description
        tags=["tag1"]
    )
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


def test_submit_label_with_exception(test_session):
    """Test submitting a label when database error occurs."""
    user = User(name="error_labeler", password="password")
    task = Task(
        type="classification", 
        data={"example": "error_task"}, 
        point=5, 
        title="Error Test Task",  # Added title
        description="Task for testing errors",  # Added description
        tags=["tag1"]
    )
    test_session.add_all([user, task])
    test_session.commit()

    # Force a database error by passing invalid data
    with pytest.raises(ValueError) as exc_info:
        submit_label(
            db=test_session,
            user_id=user.id,
            task_id=task.id,
            content=None  # This will cause a database error
        )
    assert "Database error" in str(exc_info.value)


def test_calculate_consensus_no_labels(test_session):
    """Test calculating consensus when there are no labels."""
    task = Task(
        type="classification", 
        data={"example": "no_labels"}, 
        point=5, 
        title="No Labels Task",  # Added title
        description="Task for testing no labels",  # Added description
        tags=["tag1"]
    )
    test_session.add(task)
    test_session.commit()

    result = calculate_consensus(db=test_session, task_id=task.id)
    assert result is None


def test_calculate_consensus_not_enough_labels(test_session):
    """Test calculating consensus with fewer than required labels."""
    task = Task(
        type="classification", 
        data={"example": "few_labels"}, 
        point=5, 
        title="Few Labels Task",  # Added title
        description="Task for testing consensus with few labels",  # Added description
        tags=["tag1"]
    )
    test_session.add(task)
    test_session.commit()

    # Add only 3 labels (less than required 6)
    for i in range(3):
        user = User(name=f"consensus_user_{i}", password="password")
        test_session.add(user)
        test_session.commit()
        submit_label(db=test_session, user_id=user.id, task_id=task.id, content="Label")

    result = calculate_consensus(db=test_session, task_id=task.id)
    assert result is not None
    assert result.is_done is False  # Task should not be marked as done


def test_list_labeled_tasks_empty(test_session):
    """Test listing labeled tasks for a user with no labels."""
    user = User(name="empty_labeler", password="password")
    test_session.add(user)
    test_session.commit()

    labeled_tasks = list_labeled_tasks_by_user(db=test_session, user_id=user.id)
    assert len(labeled_tasks) == 0


def test_submit_label_user_not_found(test_session):
    """Test submitting a label with non-existent user."""
    task = Task(
        type="classification", 
        data={"example": "task"}, 
        point=5, 
        title="User Not Found Task",  # Added title
        description="Task for testing user not found",  # Added description
        tags=["tag1"]
    )
    test_session.add(task)
    test_session.commit()

    with pytest.raises(ValueError) as exc_info:
        submit_label(
            db=test_session,
            user_id=uuid.uuid4(),  # Non-existent user ID
            task_id=task.id,
            content="Label content"
        )
    assert "User not found" in str(exc_info.value)


def test_submit_label_task_not_found(test_session):
    """Test submitting a label with non-existent task."""
    user = User(name="task_not_found_labeler", password="password")
    test_session.add(user)
    test_session.commit()

    with pytest.raises(ValueError) as exc_info:
        submit_label(
            db=test_session,
            user_id=user.id,
            task_id=uuid.uuid4(),  # Non-existent task ID
            content="Label content"
        )
    assert "Task not found" in str(exc_info.value)
