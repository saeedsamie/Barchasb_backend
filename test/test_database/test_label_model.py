import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models.label import Label
from app.models.task import Task
from app.models.user import User

engine = create_engine(settings.TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(engine)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

    # Unit Tests for Label Model

    def test_submit_label(db_session):
        user = db_session.query(User).filter(User.name == "updateduser").first()
        task = db_session.query(Task).first()
        response = Label.submit_label(db_session, user_id=user.id, task_id=task.id, content="Label Content")
        assert response["status"] == "success"
        label = db_session.query(Label).filter(Label.user_id == user.id, Label.task_id == task.id).first()
        assert label is not None
        assert label.content == "Label Content"

    def test_calculate_consensus(db_session):
        task = db_session.query(Task).first()
        Label.submit_label(db_session, user_id=uuid.uuid4(), task_id=task.id, content="Consensus Label")
        consensus = Label.calculate_consensus(db_session, task_id=task.id)
        assert consensus["consensus"] == "Consensus Label"
        assert "votes" in consensus

    def test_edit_labeled_task(db_session):
        label = db_session.query(Label).first()
        response = Label.edit_labeled_task(db_session, label_id=label.id, new_content="Updated Label Content")
        assert response["status"] == "success"
        updated_label = db_session.query(Label).filter(Label.id == label.id).first()
        assert updated_label.content == "Updated Label Content"

    def test_list_labeled_tasks_by_user(db_session):
        user = db_session.query(User).filter(User.name == "updateduser").first()
        labels = Label.list_labeled_tasks_by_user(db_session, user_id=user.id)
        assert len(labels) > 0
        assert labels[0]["content"] == "Updated Label Content"

    def test_list_reported_tasks_by_user(db_session):
        user = db_session.query(User).filter(User.name == "updateduser").first()
        task = db_session.query(Task).first()
        Label.submit_label(db_session, user_id=user.id, task_id=task.id, content="reported: Needs Review")
        reported_tasks = Label.list_reported_tasks_by_user(db_session, user_id=user.id)
        assert len(reported_tasks) > 0
        assert "reported" in reported_tasks[0]["content"]
