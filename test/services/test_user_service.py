from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from app.routers import users
from app.services.JWT_helper import SECRET_KEY, ALGORITHM

app = FastAPI()
app.include_router(users.router, prefix="/api/v1/auth", tags=["auth"])
client = TestClient(app)


def test_signup_success():
    response = client.post("/api/v1/auth/signup", json={
        "username": "new_user",
        "password": "SecureP@ssw0rd!"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"


def test_signup_duplicate_user():
    client.post("/api/v1/auth/signup", json={
        "username": "duplicate_user",
        "password": "SecureP@ssw0rd!"
    })
    response = client.post("/api/v1/auth/signup", json={
        "username": "duplicate_user",
        "password": "AnotherP@ssw0rd!"
    })
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"


def test_signup_weak_password():
    response = client.post("/api/v1/auth/signup", json={
        "username": "test_user",
        "password": "12345"  # Weak password
    })
    assert response.status_code == 422


def test_login_success():
    # Pre-signup a user
    client.post("/api/v1/auth/signup", json={"username": "test_user", "password": "SecureP@ssw0rd!"})

    # Login with valid credentials
    response = client.post("/api/v1/auth/login", json={"username": "test_user", "password": "SecureP@ssw0rd!"})

    # Assert response is successful
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_username():
    response = client.post("/api/v1/auth/login", json={"username": "nonexistent_user", "password": "password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_invalid_password():
    # Signup first
    client.post("/api/v1/auth/signup", json={"username": "test_user", "password": "SecureP@ssw0rd!"})

    # Login with incorrect password
    response = client.post("/api/v1/auth/login", json={"username": "test_user", "password": "WrongPassword!"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_protected_route_with_valid_token():
    # Pre-signup a user
    client.post("/api/v1/auth/signup", json={"username": "test_user", "password": "SecureP@ssw0rd!"})

    # Login and retrieve token
    login_response = client.post("/api/v1/auth/login", json={"username": "test_user", "password": "SecureP@ssw0rd!"})
    access_token = login_response.json()["access_token"]

    # Use token to access protected route
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/auth/protected-route", headers=headers)

    # Assert success
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome, test_user!"


def test_protected_route_with_expired_token(monkeypatch):
    # Pre-signup a user
    client.post("/api/v1/auth/signup", json={"username": "test_user", "password": "SecureP@ssw0rd!"})

    # Monkeypatch token expiration to a short duration
    def mock_create_access_token(data: dict):
        expire = datetime.utcnow() + timedelta(seconds=1)  # Token expires in 1 second
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    monkeypatch.setattr("app.routers.users.create_access_token", mock_create_access_token)

    # Login and retrieve token
    login_response = client.post("/api/v1/auth/login", json={"username": "test_user", "password": "SecureP@ssw0rd!"})
    access_token = login_response.json()["access_token"]

    # Wait for the token to expire
    import time
    time.sleep(2)

    # Use expired token to access protected route
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/auth/protected-route", headers=headers)

    # Assert unauthorized due to expired token
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_get_user_info_success():
    # Pre-signup a user
    client.post("/api/v1/auth/signup", json={"username": "test_user", "password": "SecureP@ssw0rd!"})

    # Login to get the token
    login_response = client.post("/api/v1/auth/login", json={"username": "test_user", "password": "SecureP@ssw0rd!"})
    access_token = login_response.json()["access_token"]

    # Fetch user info
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"username": "test_user", "points": 0}
