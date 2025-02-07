import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.DatabaseManager import DatabaseManager
from app.routers.users_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

db_manager = DatabaseManager()


@pytest.fixture(scope="module")
def db_session():
    """Set up the database using DatabaseManager and yield a session."""
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
    assert response.status_code == 200
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
    user_response = client.post("/users/signup", json={
        "name": "info_test_user",
        "password": "SecureP@ssw0rd!"
    })
    user_id = user_response.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "info_test_user"


def test_get_user_information_not_found(db_session):
    response = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_information_success(db_session):
    user_response = client.post("/users/signup", json={
        "name": "update_info_test_user",
        "password": "SecureP@ssw0rd!"
    })
    user_id = user_response.json()["id"]
    response = client.put(f"/users/{user_id}", json={"new_name": "updated_name"})
    assert response.status_code == 200


def test_update_user_password_success(db_session):
    user_response = client.post("/users/signup", json={
        "name": "update_password_test_user",
        "password": "SecureP@ssw0rd!"
    })
    user_id = user_response.json()["id"]
    response = client.put(f"/users/{user_id}/password", json={"new_password": "NewP@ssw0rd!"})
    assert response.status_code == 200


def test_update_user_password_not_found(db_session):
    response = client.put("/users/00000000-0000-0000-0000-000000000000/password", json={
        "new_password": "NewP@ssw0rd!"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_leaderboard(db_session):
    db_manager.drop_db()
    db_manager.init_db()
    """Test the leaderboard endpoint returns sorted user data correctly."""
    response = client.post("/users/signup", json={"name": "Alice", "password": "SecureP@ssw0rd!", "points": 100})
    response = client.post("/users/signup", json={"name": "Bob", "password": "SecureP@ssw0rd!", "points": 200})
    response = client.post("/users/signup", json={"name": "Charlie", "password": "SecureP@ssw0rd!", "points": 300})

    response = client.get(url="/users/leaderboard")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3  # Ensure 3 test users are returned

    # Ensure the users are sorted by points in descending order
    expected_order = ["Charlie", "Bob", "Alice"]
    actual_order = [user["name"] for user in data]
    assert actual_order == expected_order
