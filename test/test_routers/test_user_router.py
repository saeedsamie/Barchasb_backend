import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.DatabaseManager import DatabaseManager
from app.routers.users_router import router
from app.utils.JWT_helper import create_access_token

app = FastAPI()
app.include_router(router)
client = TestClient(app)

db_manager = DatabaseManager()


@pytest.fixture(scope="module")
def db_session():
    """
    Set up the database using DatabaseManager and yield a session.
    """
    db_manager.init_db()  # Initialize the database and create tables
    session = db_manager.SessionLocal()
    yield session
    session.close()
    db_manager.drop_db()  # Cleanup the database after tests


def test_create_user_success(db_session):
    response = client.post("/users/signup", json={
        "name": "signup_test_user",
        "password": "SecureP@ssw0rd!"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "signup_test_user"


def test_create_user_duplicate(db_session):
    client.post("/users/signup", json={"name": "duplicate_user", "password": "SecureP@ssw0rd!"})
    response = client.post("/users/signup", json={"name": "duplicate_user", "password": "AnotherP@ssw0rd!"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_user_success(db_session):
    client.post("/users/signup", json={"name": "login_user", "password": "SecureP@ssw0rd!"})
    response = client.post("/users/login", json={"name": "login_user", "password": "SecureP@ssw0rd!"})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_user_invalid_credentials(db_session):
    response = client.post("/users/login", json={"name": "invalid_user", "password": "wrong_password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_user_information_success(db_session):
    signup_response = client.post("/users/signup", json={
        "name": "info_test_user",
        "password": "SecureP@ssw0rd!"
    })
    login_response = client.post("/users/login", json={
        "name": "info_test_user",
        "password": "SecureP@ssw0rd!"
    })
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/user", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "info_test_user"


def test_get_user_information_unauthorized(db_session):
    response = client.get("/users/user")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_update_user_information_success(db_session):
    signup_response = client.post("/users/signup", json={
        "name": "update_info_test_user",
        "password": "SecureP@ssw0rd!"
    })
    login_response = client.post("/users/login", json={
        "name": "update_info_test_user",
        "password": "SecureP@ssw0rd!"
    })
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/users/user", json={"new_name": "updated_name"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "updated_name"


def test_update_user_password_success(db_session):
    signup_response = client.post("/users/signup", json={
        "name": "update_password_test_user",
        "password": "SecureP@ssw0rd!"
    })
    login_response = client.post("/users/login", json={
        "name": "update_password_test_user",
        "password": "SecureP@ssw0rd!"
    })
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/users/user/password", json={"new_password": "NewP@ssw0rd!"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] == "Password updated"


def test_leaderboard_access(db_session):
    db_manager.drop_db()
    db_manager.init_db()

    client.post("/users/signup", json={"name": "Alice", "password": "SecureP@ssw0rd!", "points": 100})
    client.post("/users/signup", json={"name": "Bob", "password": "SecureP@ssw0rd!", "points": 200})
    client.post("/users/signup", json={"name": "Charlie", "password": "SecureP@ssw0rd!", "points": 300})

    login_response = client.post("/users/login", json={
        "name": "Charlie",
        "password": "SecureP@ssw0rd!"
    })
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/leaderboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3  # Ensure 3 test users are returned

    # Ensure the users are sorted by points in descending order
    expected_order = ["Charlie", "Bob", "Alice"]
    actual_order = [user["name"] for user in data]
    assert actual_order == expected_order
