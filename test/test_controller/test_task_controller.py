import pytest

from app.DatabaseManager import DatabaseManager, TEST_DB_URL
from app.controller.task_controller import (
    list_done_tasks,
    get_task_feed,
    add_task,
    mark_task_done,
)
from app.models.Task import Task

# Initialize the DatabaseManager with the test database URL
db_manager = DatabaseManager(TEST_DB_URL)


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
        tags=["urgent", "important"],
        is_done=False
    )
    assert task is not None
    assert task.type == "classification"
    assert task.data == {"key": "value"}
    assert task.point == 10
    assert task.is_done == False
    assert "urgent" in task.tags


def test_get_task_feed(test_session):
    """Test retrieving tasks that are not marked as done."""
    # Add tasks to the database
    task1 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task1"},
        point=5,
        tags=["tag1"],
    )
    task2 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task2"},
        point=10,
        tags=["tag2"],
    )
    mark_task_done(db=test_session, task_id=task1.id)  # Mark one task as done

    # Fetch task feedy
    task_feed = get_task_feed(db=test_session)
    assert len(task_feed) == 1
    assert task_feed[0].id == task2.id  # Only the unfinished task should be in the feed


def test_list_done_tasks(test_session):
    """Test retrieving tasks that are marked as done."""
    task1 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task1"},
        point=5,
        tags=["tag1"],
    )
    task2 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task2"},
        point=10,
        tags=["tag2"],
    )
    mark_task_done(db=test_session, task_id=task1.id)  # Mark one task as done
    # Add and mark tasks as done
    task3 = add_task(
        db=test_session,
        type="classification",
        data={"example": "task3"},
        point=15,
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
        tags=["tag4"],
    )

    # Mark the task as done
    updated_task = mark_task_done(db=test_session, task_id=task.id)
    assert updated_task.is_done is True

    # Verify in the database
    fetched_task = test_session.query(Task).filter(Task.id == task.id).first()
    assert fetched_task.is_done is True
