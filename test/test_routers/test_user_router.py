from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.DatabaseManager import TEST_DATABASE_URL, DatabaseManager
from app.routers.users_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

db_manager = DatabaseManager(TEST_DATABASE_URL)
db_manager.drop_db()
db_manager.init_db()


def test_create_user_success():
    response = client.post("/users/signup", json={
        "name": "signup_test_user",
        "password": "SecureP@ssw0rd!"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "signup_test_user"


def test_create_user_duplicate():
    client.post("/users/signup", json={"name": "duplicate_user", "password": "SecureP@ssw0rd!"})
    response = client.post("/users/signup", json={"name": "duplicate_user", "password": "AnotherP@ssw0rd!"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_user_success():
    client.post("/users/signup", json={"name": "login_user", "password": "SecureP@ssw0rd!"})
    response = client.post("/users/login", json={"name": "login_user", "password": "SecureP@ssw0rd!"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_user_invalid_credentials():
    response = client.post("/users/login", json={"name": "invalid_user", "password": "wrong_password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_user_information_success():
    user_response = client.post("/users/signup", json={
        "name": "info_test_user",
        "password": "SecureP@ssw0rd!"
    })
    user_id = user_response.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "info_test_user"


def test_get_user_information_not_found():
    response = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_information_success():
    user_response = client.post("/users/signup", json={
        "name": "update_info_test_user",
        "password": "SecureP@ssw0rd!"
    })
    user_id = user_response.json()["id"]
    response = client.put(f"/users/{user_id}", json={"new_name": "updated_name"})
    assert response.status_code == 200


def test_update_user_password_success():
    user_response = client.post("/users/signup", json={
        "name": "update_password_test_user",
        "password": "SecureP@ssw0rd!"
    })
    user_id = user_response.json()["id"]
    response = client.put(f"/users/{user_id}/password", json={"new_password": "NewP@ssw0rd!"})
    assert response.status_code == 200


def test_update_user_password_not_found():
    response = client.put("/users/00000000-0000-0000-0000-000000000000/password", json={
        "new_password": "NewP@ssw0rd!"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
