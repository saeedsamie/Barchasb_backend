import pytest

from app.DatabaseManager import DatabaseManager, TEST_DATABASE_URL
from app.models import Task
from app.services.hash_helper import check_password_hash
from app.services.user_service import login_user, get_information, change_information, change_password

db_manager = DatabaseManager(TEST_DATABASE_URL)


@pytest.fixture(scope="module")
def db_session():
    # Initialize database
    db_manager.init_db()
    session = db_manager.SessionLocal()
    yield session
    session.close()
    # Cleanup database
    db_manager.drop_db()


@pytest.fixture(scope="function")
def setup_test_data(db_session):
    user = User(name="testuser", password="SecureP@ssw0rd!")
    task = Task(type="image", data="Sample Data", point=10, tags=["urgent"])
    db_session.add(user)
    db_session.add(task)
    db_session.commit()
    return user, task


# Unit Tests for User Model

def test_user_create(db_session):
    user = create_user(db_session, name="testuser", password="SecureP@ssw0rd!")  # Returns User object
    assert user is not None
    assert user.name == "testuser"
    assert check_password_hash(user.password, "SecureP@ssw0rd!")  # Validate hashed password


def test_user_login(db_session):
    # Create a user first
    user = create_user(db_session, name="logintestuser", password="SecureP@ssw0rd!")

    # Test login
    authenticated_user, token = login_user(db_session, name="logintestuser", password="SecureP@ssw0rd!")
    db_session.refresh(user)  # Refresh user to ensure session consistency
    assert authenticated_user.id == user.id
    assert token is not None


def test_user_get_information(db_session):
    user = create_user(db_session, name="getinfotestuser", password="SecureP@ssw0rd!")
    retrieved_user = get_information(db_session, user_id=user.id)
    assert retrieved_user == user
    assert retrieved_user.name == "getinfotestuser"


def test_user_change_information(db_session):
    user = create_user(db_session, name="changeinfotestuser", password="SecureP@ssw0rd!")
    updated_user = change_information(db_session, user_id=user.id, new_name="updateduser")
    assert updated_user is not None
    assert updated_user.name == "updateduser"


def test_user_change_password(db_session):
    user = create_user(db_session, name="changepasswordtestuser", password="SecureP@ssw0rd!")
    updated_user = change_password(db_session, user_id=user.id, new_password="newSecureP@ssw0rd!")
    assert updated_user is not None
    assert check_password_hash(updated_user.password, "newSecureP@ssw0rd!")


import pytest
from app.services.user_service import create_user, UserAlreadyExistsError
from app.models.User import User


def test_create_user_already_exists(db_session):
    """
    Test that creating a user with an existing username raises an exception.
    """
    # Step 1: Create a user
    create_user(db_session, name="duplicatedtestuser", password="SecureP@ssw0rd!")

    # Step 2: Attempt to create another user with the same username
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        create_user(db_session, name="duplicatedtestuser", password="AnotherP@ssw0rd!")

    # Step 3: Assert the exception message
    assert str(exc_info.value) == "User with name 'duplicatedtestuser' already exists."

    # Step 4: Ensure only one user exists in the database
    users = db_session.query(User).filter_by(name="duplicatedtestuser").all()
    assert len(users) == 1
