from app.services.hash_helper import generate_password_hash, check_password_hash


def test_generate_password_hash():
    password = "securepassword"
    hashed_password = generate_password_hash(password)
    assert hashed_password != password
    assert len(hashed_password) > 0


def test_check_password_hash():
    password = "securepassword"
    hashed_password = generate_password_hash(password)
    assert check_password_hash(hashed_password, password) is True
    assert check_password_hash(hashed_password, "wrongpassword") is False
