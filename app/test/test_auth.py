from datetime import timedelta

from fastapi import status, HTTPException
from jose import jwt

from .utils import *
from ..main import app
from ..routers.auth import ACCESS_TOKEN_EXPIRE_MINUTES, generate_access_token, SECRET_KEY, ALGORITHM, get_current_user
from ..routers.auth import get_db


@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


def test_login(mock_data):
    # Arrange
    form_data = {"grant_type": "password", "username": "johndoe123", "password": "12345aA@"}

    # Act
    response = client.post("/auth/login", data=form_data)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access_token"]


def test_login_incorrect_password(mock_data):
    # Arrange
    form_data = {"grant_type": "password", "username": "johndoe123", "password": "12345aA@@"}

    # Act
    response = client.post("/auth/login", data=form_data)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_incorrect_username(mock_data):
    # Arrange
    form_data = {"grant_type": "password", "username": "johndoe123456", "password": "12345aA@"}

    # Act
    response = client.post("/auth/login", data=form_data)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_generate_access_token():
    # Arrange
    claims = {
        "sub": "johndoe123",
        "user_id": 1,
        "user_role": "user"
    }

    # Act
    access_token = generate_access_token(claims, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    decoded_access_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM],
                                      options={"verify_signature": False})

    # Assert
    assert decoded_access_token["sub"] == "johndoe123"
    assert decoded_access_token["user_id"] == 1
    assert decoded_access_token["user_role"] == "user"


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    # Arrange
    claims = {
        "sub": "johndoe123",
        "user_id": 1,
        "user_role": "user"
    }
    access_token = generate_access_token(claims, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    # Act
    payload = await get_current_user(access_token)

    # Assert
    assert payload["username"] == "johndoe123"
    assert payload["user_id"] == 1
    assert payload["user_role"] == "user"


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    # Arrange
    claims = {
        "sub": "johndoe123",
        "user_id": 1,
    }
    access_token = generate_access_token(claims, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    # Act
    with pytest.raises(HTTPException) as ex:
        await get_current_user(access_token)

    # Assert
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
