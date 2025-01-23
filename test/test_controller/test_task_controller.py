import uuid

import pytest

from app.DatabaseManager import TEST_DB_URL, DatabaseManager
from app.controller import (
    add_task,
    get_task_feed,
    list_done_tasks,
    report_task,
)
from app.controller.label_controller import submit_task
from app.models import User
from app.models.Task import Task
from app.models.TaskLabel import TaskLabel
from app.models.TaskReport import TaskReport

db_manager = DatabaseManager(TEST_DB_URL)


@pytest.fixture(scope="module")
def db_session():
    db_manager.init_db()
    session = db_manager.SessionLocal()
    initialize_database_with_users(session)
    initialize_database_with_tasks(session)
    yield session
    session.rollback()
    session.close()
    db_manager.drop_db()


def test_add_task(db_session):
    task = add_task(
        db_session,
        type="image",
        data={'url': "url/to/image"},
        point=10,
        tags=["urgent"],
    )
    registered_task = db_session.query(Task).filter(Task.id == task.id).first()
    assert registered_task is not None
    assert registered_task.type == task.type
    assert registered_task.data == task.data
    assert registered_task.point == task.point
    assert registered_task.tags == task.tags


def test_get_task_feed(db_session):
    tasks = get_task_feed(db_session, limit=5)
    assert isinstance(tasks, list)
    assert len(tasks) > 0


def test_list_done_tasks(db_session):
    tasks = list_done_tasks(db_session)
    assert isinstance(tasks, list)


def test_submit_task(db_session):
    # Pre-create user and task for valid foreign key
    user = User(id=uuid.uuid4(), name="submit_test_user", password="securepassword")
    db_session.add(user)
    task = Task(type="image", data={"url": "test_image.jpg"}, point=10, tags=["urgent"])
    db_session.add(task)
    db_session.commit()

    label = TaskLabel(task_id=task.id, user_id=user.id, content="Urgent task")
    submitted_label = submit_task(db_session, label)

    assert submitted_label.content == "Urgent task"
    assert submitted_label.user_id == user.id


def test_report_task(db_session):
    # Pre-create task
    task = Task(type="image", data={"url": "test_image.jpg"}, point=10, tags=["urgent"])
    db_session.add(task)
    db_session.commit()

    report = TaskReport(task_id=task.id, details="This task has insufficient data")
    created_report = report_task(db_session, report)

    assert created_report.task_id == report.task_id
    assert created_report.details == report.details


# def test_update_task_status(db_session):
#     task = db_session.query(Task).first()
#     new_status = "completed"
#     updated_task = update_task_status(db_session, task_id=task.id, new_status=new_status)
#     assert updated_task is not None
#     assert updated_task.status == new_status


def initialize_database_with_users(db_session):
    # Add users
    users = [
        User(id=uuid.uuid4(), name="Test User", password="password"),
    ]
    db_session.bulk_save_objects(users)
    db_session.commit()


def initialize_database_with_tasks(db_session):
    sample_tasks = [
        {
            "type": "image",
            "data": {"url": "https://example.com/image1.jpg"},
            "point": 10,
            "tags": ["urgent", "image"],
        },
        {
            "type": "text",
            "data": {"content": "Translate the following text: 'Hello, world!'"},
            "point": 5,
            "tags": ["translation", "text"],
        },
        {
            "type": "audio",
            "data": {"url": "https://example.com/audio1.mp3", "duration": 30},
            "point": 15,
            "tags": ["audio", "urgent"],
        },
        {
            "type": "video",
            "data": {"url": "https://example.com/video1.mp4", "duration": 120},
            "point": 20,
            "tags": ["video"],
        },
    ]

    for task_data in sample_tasks:
        task = Task(
            id=uuid.uuid4(),
            type=task_data["type"],
            data=task_data["data"],
            point=task_data["point"],
            tags=task_data["tags"],
        )
        db_session.add(task)

    db_session.commit()
    print(f"Initialized database with {len(sample_tasks)} tasks.")
