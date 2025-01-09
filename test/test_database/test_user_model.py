import pytest
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models.user import User
from app.services.hash_helper import check_password_hash


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


# Unit Tests for User Model

def test_user_signup(db_session):
    response = User.signup(db_session, name="testuser", password="SecureP@ssw0rd!")
    user = db_session.query(User).filter(User.name == "testuser").first()
    assert response["status"] == "success"
    assert user is not None
    assert check_password_hash(user.password, "SecureP@ssw0rd!")


def test_user_login(db_session):
    response = User.login(db_session, name="testuser", password="SecureP@ssw0rd!")
    assert response["status"] == "success"
    assert "token" in response


def test_user_get_information(db_session):
    user = db_session.query(User).filter(User.name == "testuser").first()
    response = User.get_information(db_session, user_id=user.id)
    assert response["user_id"] == str(user.id)
    assert response["name"] == "testuser"


def test_user_change_information(db_session):
    user = db_session.query(User).filter(User.name == "testuser").first()
    response = User.change_information(db_session, user_id=user.id, new_name="updateduser")
    assert response["status"] == "success"
    updated_user = db_session.query(User).filter(User.name == "updateduser").first()
    assert updated_user is not None


def test_user_change_password(db_session):
    user = db_session.query(User).filter(User.name == "updateduser").first()
    response = User.change_password(db_session, user_id=user.id, new_password="newSecureP@ssw0rd!")
    assert response["status"] == "success"
    updated_user = db_session.query(User).filter(User.id == user.id).first()
    assert check_password_hash(updated_user.password, "newSecureP@ssw0rd!")
