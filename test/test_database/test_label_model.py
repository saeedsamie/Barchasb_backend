import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models.TaskLabel import TaskLabel
from app.models.Task import Task
from app.models.User import User

engine = create_engine(settings.TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@pytest.fixture(scope="package")
def db_session():
    Base.metadata.create_all(bind=engine)  # Create tables for all models
    session = Session(bind=engine)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def setup_test_data(db_session):
    user = User(name="updateduser", password="password123")
    task = Task(type="image", data="Sample Data", point=10, tags=["urgent"])
    db_session.add(user)
    db_session.add(task)
    db_session.commit()
    return user, task


def test_submit_label(db_session, setup_test_data):
    user, task = setup_test_data
    # user = db_session.query(User).filter(User.name == "updateduser").first()
    # task = db_session.query(Task).first()
    response = TaskLabel.submit_label(db_session, user_id=user.id, task_id=task.id, content="Label Content")
    assert response["status"] == "success"
    label = db_session.query(TaskLabel).filter(TaskLabel.user_id == user.id, TaskLabel.task_id == task.id).first()
    assert label is not None
    assert label.content == "Label Content"


def test_calculate_consensus(db_session):
    task = db_session.query(Task).first()
    TaskLabel.submit_label(db_session, user_id=uuid.uuid4(), task_id=task.id, content="Consensus Label")
    consensus = TaskLabel.calculate_consensus(db_session, task_id=task.id)
    assert consensus["consensus"] == "Consensus Label"
    assert "votes" in consensus


def test_edit_labeled_task(db_session):
    label = db_session.query(TaskLabel).first()
    response = TaskLabel.edit_labeled_task(db_session, label_id=label.id, new_content="Updated Label Content")
    assert response["status"] == "success"
    updated_label = db_session.query(TaskLabel).filter(TaskLabel.id == label.id).first()
    assert updated_label.content == "Updated Label Content"


def test_list_labeled_tasks_by_user(db_session):
    user = db_session.query(User).filter(User.name == "updateduser").first()
    labels = TaskLabel.list_labeled_tasks_by_user(db_session, user_id=user.id)
    assert len(labels) > 0
    assert labels[0]["content"] == "Updated Label Content"


def test_list_reported_tasks_by_user(db_session):
    user = db_session.query(User).filter(User.name == "updateduser").first()
    task = db_session.query(Task).first()
    TaskLabel.submit_label(db_session, user_id=user.id, task_id=task.id, content="reported: Needs Review")
    reported_tasks = TaskLabel.list_reported_tasks_by_user(db_session, user_id=user.id)
    assert len(reported_tasks) > 0
    assert "reported" in reported_tasks[0]["content"]
