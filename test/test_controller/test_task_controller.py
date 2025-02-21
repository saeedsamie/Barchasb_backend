import pytest

from app.DatabaseManager import DatabaseManager
from app.controller.task_controller import (
    list_done_tasks,
    get_task_feed,
    add_task,
    mark_task_done,
    get_user_labeled_tasks,
)
from app.controller.user_controller import create_user
from app.models.Task import Task

# Initialize the DatabaseManager with the test database URL
db_manager = DatabaseManager()


@pytest.fixture(scope="function")
def test_session():
    """Set up the database using DatabaseManager and yield a session."""
    db_manager.init_db()  # Initialize the database and create tables
    session = db_manager.SessionLocal()
    yield session
    session.close()
    # db_manager.drop_db()  # Cleanup the database after tests


def test_add_task(test_session):
    """Test adding a task using add_task."""
    task = add_task(
        db=test_session,
        type="classification",
        data={"key": "value"},
        point=10,
        title="Test Task",
        description="This is a test task",
        tags=["urgent", "important"],
        is_done=False
    )
    assert task is not None
    assert task.type == "classification"
    assert task.data == {"key": "value"}
    assert task.point == 10
    assert task.title == "Test Task"
    assert task.description == "This is a test task"
    assert task.is_done == False
    assert "urgent" in task.tags


def test_get_task_feed(test_session):
    db_manager.drop_db()
    db_manager.init_db()
    user = create_user(test_session, name="task_feed_user", password="SecureP@ssw0rd!")
    """Test retrieving tasks that are not marked as done."""
    # Add tasks to the database
    task1 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task1"},
        point=5,
        title="Task 1",
        description="First test task",
        tags=["tag1"],
    )
    task2 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task2"},
        point=10,
        title="Task 2",
        description="Second test task",
        tags=["tag2"],
    )
    mark_task_done(db=test_session, task_id=task1.id)  # Mark one task as done

    # Fetch task feed
    task_feed = get_task_feed(user_id=user.id, db=test_session)
    assert len(task_feed) == 1
    assert task_feed[0].id == task2.id  # Only the unfinished task should be in the feed


def test_list_done_tasks(test_session):
    db_manager.drop_db()
    db_manager.init_db()
    """Test retrieving tasks that are marked as done."""
    task1 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task1"},
        point=5,
        title="Done Task 1",
        description="First task to be marked as done",
        tags=["tag1"],
    )
    task2 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task2"},
        point=10,
        title="Done Task 2",
        description="Second task to remain undone",
        tags=["tag2"],
    )
    mark_task_done(db=test_session, task_id=task1.id)  # Mark one task as done
    # Add and mark tasks as done
    task3 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task3"},
        point=15,
        title="Done Task 3",
        description="Third task to be marked as done",
        tags=["tag3"],
    )
    mark_task_done(db=test_session, task_id=task3.id)

    done_tasks = list_done_tasks(db=test_session)
    assert len(done_tasks) == 2  # Task1 and Task3 should be marked as done
    assert any(task.id == task3.id for task in done_tasks)


def test_mark_task_done(test_session):
    """Test marking a task as done."""
    # Add a new task
    task = add_task(
        db=test_session,
        type="classification",
        data={"example": "task4"},
        point=20,
        title="Task to Mark Done",
        description="Task that will be marked as done",
        tags=["tag4"],
    )

    # Mark the task as done
    updated_task = mark_task_done(db=test_session, task_id=task.id)
    assert updated_task.is_done is True

    # Verify in the database
    fetched_task = test_session.query(Task).filter(Task.id == task.id).first()
    assert fetched_task.is_done is True


def test_get_user_labeled_tasks(test_session):
    """Test retrieving tasks labeled by a specific user."""
    db_manager.drop_db()
    db_manager.init_db()

    # Create a test user
    user = create_user(test_session, name="label_test_user", password="SecureP@ssw0rd!")

    # Create some tasks
    task1 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task1"},
        point=5,
        title="Task 1",
        description="First test task",
        tags=["tag1"],
    )
    task2 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task2"},
        point=10,
        title="Task 2",
        description="Second test task",
        tags=["tag2"],
    )

    # Add labels for the tasks
    from app.controller.taskLabel_controller import submit_label
    submit_label(test_session, user_id=user.id, task_id=task1.id, content="label1")
    submit_label(test_session, user_id=user.id, task_id=task2.id, content="label2")

    # Get labeled tasks
    labeled_tasks = get_user_labeled_tasks(test_session, user.id)

    # Verify results
    assert len(labeled_tasks) == 2
    assert any(task.id == task1.id for task in labeled_tasks)
    assert any(task.id == task2.id for task in labeled_tasks)
