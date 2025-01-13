from fastapi import status

from .utils import *
from ..routers.auth import get_current_user
from ..routers.users import get_db


@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()


def test_get_user_info(mock_data):
    # Arrange
    user_model = mock_data['user']
    expected_user = {
        "username": user_model.username,
        "email": user_model.email,
        "first_name": user_model.first_name,
        "last_name": user_model.last_name,
        "is_active": user_model.is_active,
        "role": user_model.role,
        "phone_number": user_model.phone_number
    }

    # Act
    response = client.get("/users/")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"] == expected_user


def test_password_change(mock_data):
    # Arrange
    request_body = {"old_password": "12345aA@", "new_password": "123456aA@", "confirm_new_password": "123456aA@"}

    # Act
    response = client.put("/users/password-change/", json=request_body)

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_password_change_invalid_current_password(mock_data):
    # Arrange
    request_body = {"old_password": "12345678aA@", "new_password": "123456aA@", "confirm_new_password": "123456aA@"}

    # Act
    response = client.put("/users/password-change/", json=request_body)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_phone_number(mock_data):
    # Arrange
    phone_number = "0000000000"

    # Act
    response = client.put(f"/users/phone-number/{phone_number}")

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
