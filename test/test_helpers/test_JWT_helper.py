import pytest
from fastapi import HTTPException

from app.utils.JWT_helper import create_access_token, decode_access_token


def test_create_access_token():
    data = {"sub": "user123"}
    token = create_access_token(data)
    assert len(token) > 0


def test_decode_access_token():
    data = {"sub": "user123"}
    token = create_access_token(data)
    decoded_data = decode_access_token(token)
    assert decoded_data["sub"] == data["sub"]


def test_decode_access_token_invalid():
    with pytest.raises(HTTPException) as excinfo:
        decode_access_token("invalidtoken")
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid token"
