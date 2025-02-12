import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.DatabaseManager import DatabaseManager, Base
from app.routers import users_router, tasks_router


@pytest.fixture(scope="session")
def test_app():
    app = FastAPI()
    app.include_router(users_router.router, prefix="/api/v1", tags=["users"])
    app.include_router(tasks_router.router, prefix="/api/v1", tags=["tasks"])
    return app


@pytest.fixture(scope="session")
def test_client(test_app):
    return TestClient(test_app)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    db_manager = DatabaseManager(testing=True)  # Use test database
    print(db_manager.database_url)

    engine = db_manager.engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    try:
        db = db_manager.SessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers(test_client, test_db):  # Add test_db dependency
    """Create a test user and return auth headers."""
    user_data = {
        "name": "test_user",
        "password": "SecureP@ssw0rd!",
        "points": 0
    }
    # Create a new user
    signup_response = test_client.post("/api/v1/users/signup", json=user_data)
    assert signup_response.status_code == 201, f"Signup failed: {signup_response.json()}"

    # Login to get the token
    login_response = test_client.post("/api/v1/users/login", json={
        "name": user_data["name"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_task():
    """Return a sample task payload."""
    return {
        "type": "image",
        "data": {"url": "/path/to/file1"},
        "title": "Sample Task",
        "description": "A test task for creating an image labeling task.",
        "point": 10,
        "tags": ["urgent"]
    }


@pytest.fixture
async def async_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def async_db():
    """Create a fresh test database for each async test."""
    db_manager = DatabaseManager(testing=True)
    db_manager.init_db()
    
    try:
        db = db_manager.SessionLocal()
        yield db
    finally:
        db.close()
        db_manager.drop_db()
