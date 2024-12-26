from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import users

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
