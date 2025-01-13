from fastapi import status

from .utils import *
from ..main import app
from ..routers.admin import get_db
from ..routers.auth import get_current_user


@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_admin
    yield
    app.dependency_overrides.clear()


def test_get_todos_authenticated(mock_data):
    response = client.get("/todos/admin/")
    assert response.status_code == status.HTTP_200_OK


def test_get_todo_by_id(mock_data):
    # Arrange
    todo = mock_data["todo"]
    expected_todo = {
        "id": todo.id,
        "user_id": todo.user_id,
        "title": todo.title,
        "description": todo.description,
        "priority": todo.priority,
        "completed": todo.completed
    }

    # Act
    response = client.get(f"/todos/admin/{todo.id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_todo
    assert response.json()["user_id"] != mock_data["admin"].id


def test_delete_todo_by_id(mock_data):
    # Arrange
    todo = mock_data["todo"]
    db = TestSessionLocal()

    # Act
    delete_response = client.delete(f"/todos/admin/{todo.id}")
    todo_model = db.query(Todos).where(Todos.id == todo.id).first()

    # Assert
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert todo_model is None
