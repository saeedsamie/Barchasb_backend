import uuid

import pytest
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models.task import Task


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

    # Unit Tests for Task Model

    def test_add_task(db_session):
        response = Task.add_task(db_session, type="image", data="url/to/image", point=10, tags=["urgent"])
        assert response["status"] == "success"
        task = db_session.query(Task).filter(Task.id == uuid.UUID(response["task_id"])).first()
        assert task is not None
        assert task.type == "image"
        assert task.data == "url/to/image"
        assert task.point == 10
        assert task.tags == ["urgent"]

    def test_get_task_feed(db_session):
        tasks = Task.get_task_feed(db_session)
        assert isinstance(tasks, list)
        assert len(tasks) > 0

    def test_list_done_tasks(db_session):
        tasks = Task.list_done_tasks(db_session)
        assert isinstance(tasks, list)
