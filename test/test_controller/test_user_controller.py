import pytest
from app.DatabaseManager import DatabaseManager, TEST_DB_URL
from app.controller.user_controller import (
    create_user,
    login_user,
    get_information,
    change_information,
    change_password,
    UserAlreadyExistsError
)
from app.models.User import User
from app.utils.hash_helper import check_password_hash

# Initialize the DatabaseManager with the test database URL
db_manager = DatabaseManager(TEST_DB_URL)


@pytest.fixture(scope="module")
def db_session():
    """Set up the database using DatabaseManager and yield a session."""
    db_manager.init_db()  # Initialize the database and create tables
    session = db_manager.SessionLocal()
    yield session
    session.close()
    db_manager.drop_db()  # Cleanup the database after tests


def test_user_create(db_session):
    """Test user creation with the `create_user` function."""
    user = create_user(db_session, name="testuser", password="SecureP@ssw0rd!")
    assert user is not None
    assert user.name == "testuser"
    assert check_password_hash(user.password, "SecureP@ssw0rd!")  # Validate hashed password


def test_user_login(db_session):
    """Test user login functionality."""
    # Create a user first
    user = create_user(db_session, name="logintestuser", password="SecureP@ssw0rd!")

    # Test login
    authenticated_user, token = login_user(db_session, name="logintestuser", password="SecureP@ssw0rd!")
    assert authenticated_user.id == user.id
    assert token is not None


def test_user_get_information(db_session):
    """Test retrieving user information by ID."""
    user = create_user(db_session, name="getinfotestuser", password="SecureP@ssw0rd!")
    retrieved_user = get_information(db_session, user_id=user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.name == "getinfotestuser"


def test_user_change_information(db_session):
    """Test updating user information (name)."""
    user = create_user(db_session, name="changeinfotestuser", password="SecureP@ssw0rd!")
    updated_user = change_information(db_session, user_id=user.id, new_name="updateduser")
    assert updated_user is not None
    assert updated_user.name == "updateduser"


def test_user_change_password(db_session):
    """Test updating user password."""
    user = create_user(db_session, name="changepasswordtestuser", password="SecureP@ssw0rd!")
    updated_user = change_password(db_session, user_id=user.id, new_password="newSecureP@ssw0rd!")
    assert updated_user is not None
    assert check_password_hash(updated_user.password, "newSecureP@ssw0rd!")


def test_create_user_already_exists(db_session):
    """Test handling of duplicate user creation."""
    create_user(db_session, name="duplicatedtestuser", password="SecureP@ssw0rd!")
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        create_user(db_session, name="duplicatedtestuser", password="AnotherP@ssw0rd!")

    assert str(exc_info.value) == "User with name 'duplicatedtestuser' already exists."

    users = db_session.query(User).filter_by(name="duplicatedtestuser").all()
    assert len(users) == 1
