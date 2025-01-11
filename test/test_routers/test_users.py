from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app

# PostgreSQL Test Database URL
SQLALCHEMY_DATABASE_URL = "postgresql://admin:admin@barchasb.bz91.ir:5432/barchasb_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

client = TestClient(app)


# @pytest.fixture(scope="module")
# def setup_test_db():
#     db = TestingSessionLocal()
#     # Create a test user
# User.signup(db, "testuser", "SecureP@ssw0rd!")


# Unit Tests

def test_signup():
    response = client.post("/api/v1/auth/signup", json={"name": "newuser", "password": "Newpassword1!"})
    assert response.status_code == 201
    assert response.json()["name"] == "newuser"


def test_login(setup_test_db):
    response = client.post("/login", json={"name": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_user_info(setup_test_db):
    # Log in to get token
    login_response = client.post("/login", json={"name": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    # Use token to fetch user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "testuser"


def test_logout(setup_test_db):
    # Log in to get token
    login_response = client.post("/login", json={"name": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    # Use token to logout
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
