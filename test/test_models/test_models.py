import pytest

from app.DatabaseManager import DatabaseManager
from app.models.Task import Task
from app.models.TaskLabel import TaskLabel
from app.models.TaskReport import TaskReport
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


def test_task_model(test_session):
    """Test creation and relationship of Task model."""
    task = Task(type="classification", data={"key": "value"}, point=10, tags=["urgent", "important"], is_done=False)
    test_session.add(task)
    test_session.commit()

    saved_task = test_session.query(Task).filter_by(type="classification").first()
    assert saved_task is not None
    assert saved_task.type == "classification"
    assert saved_task.point == 10
    assert "urgent" in saved_task.tags
    assert saved_task.is_done is False  # Verify the default value of is_done


def test_user_model(test_session):
    """Test creation and relationship of User model."""
    user = User(name="testuser", password="SecureP@ssw0rd!", points=50, labeled_count=10)
    test_session.add(user)
    test_session.commit()

    saved_user = test_session.query(User).filter_by(name="testuser").first()
    assert saved_user is not None
    assert saved_user.name == "testuser"
    assert saved_user.points == 50
    assert saved_user.labeled_count == 10


def test_task_label_model(test_session):
    """Test creation and relationship of TaskLabel model."""
    user = User(name="labeler", password="labelpass")
    task = Task(type="annotation", data={"example": "data"}, point=5, is_done=False)
    test_session.add_all([user, task])
    test_session.commit()

    task_label = TaskLabel(user_id=user.id, task_id=task.id, content="Label content")
    test_session.add(task_label)
    test_session.commit()

    saved_label = test_session.query(TaskLabel).filter_by(content="Label content").first()
    assert saved_label is not None
    assert saved_label.user_id == user.id
    assert saved_label.task_id == task.id


def test_task_report_model(test_session):
    """Test creation and relationship of TaskReport model."""
    user = User(name="reporter", password="reportpass")
    task = Task(type="report", data={"report": "data"}, point=2, is_done=False)
    test_session.add_all([user, task])
    test_session.commit()

    task_report = TaskReport(task_id=task.id, user_id=user.id, details="This is a test report.")
    test_session.add(task_report)
    test_session.commit()

    saved_report = test_session.query(TaskReport).filter_by(details="This is a test report.").first()
    assert saved_report is not None
    assert saved_report.task_id == task.id
    assert saved_report.user_id == user.id
    assert "test report" in saved_report.details


def test_task_with_labels_and_reports_relationship(test_session):
    """Test relationships between Task, TaskLabel, and TaskReport."""
    # Create a task
    task = Task(type="complex", data={"task": "data"}, point=15, tags=["tag1", "tag2"], is_done=True)
    test_session.add(task)
    test_session.commit()

    # Add labels and reports to the task
    user = User(name="user1", password="password")
    test_session.add(user)
    test_session.commit()

    label1 = TaskLabel(user_id=user.id, task_id=task.id, content="Label 1")
    label2 = TaskLabel(user_id=user.id, task_id=task.id, content="Label 2")
    report1 = TaskReport(task_id=task.id, user_id=user.id, details="Report 1")
    test_session.add_all([label1, label2, report1])
    test_session.commit()

    # Fetch task with relationships
    saved_task = test_session.query(Task).filter_by(id=task.id).first()
    assert len(saved_task.labels) == 2
    assert len(saved_task.reports) == 1
    assert saved_task.labels[0].content == "Label 1"
    assert saved_task.reports[0].details == "Report 1"
    assert saved_task.is_done is True  # Verify is_done status


def test_user_with_labels_and_reports_relationship(test_session):
    """Test relationships between User, TaskLabel, and TaskReport."""
    # Create a user and task
    user = User(name="user2", password="securepass")
    task = Task(type="basic", data={"task": "info"}, point=5, is_done=False)
    test_session.add_all([user, task])
    test_session.commit()

    # Create labels and reports for the user and task
    label1 = TaskLabel(user_id=user.id, task_id=task.id, content="User2 Label 1")
    report1 = TaskReport(user_id=user.id, task_id=task.id, details="User2 Report 1")
    test_session.add_all([label1, report1])
    test_session.commit()

    # Fetch user with labels and reports
    saved_user = test_session.query(User).filter_by(id=user.id).first()
    assert len(saved_user.labels) == 1
    assert len(saved_user.reports) == 1
    assert saved_user.labels[0].content == "User2 Label 1"
    assert saved_user.reports[0].details == "User2 Report 1"
