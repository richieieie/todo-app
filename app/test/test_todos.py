from fastapi import status

from .utils import *
from ..main import app
from ..models import Todos
from ..routers.auth import get_current_user
from ..routers.todos import get_db


@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()


def test_get_todos_authenticated(mock_data):
    response = client.get("/todos/")

    assert response.status_code == status.HTTP_200_OK
    assert len(list(response.json())) > 0


def test_get_todo_authenticated(mock_data):
    response = client.get(f"/todos/{mock_data["todo"].id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "user_id": 1,
        "title": "Todo Test",
        "description": "This is a todo test",
        "priority": 5,
        "completed": False
    }


def test_get_todo_authenticated_not_found():
    response = client.get("/todos/111111111")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Todo not found"
    }


def test_create_todo_authenticated(mock_data):
    # Arrange
    request_body = {
        "user_id": 1,
        "title": "Todo Test Create",
        "description": "This is a todo test create",
        "priority": 1,
        "completed": False
    }

    # Act
    response = client.post("/todos", json=request_body)
    with TestSessionLocal() as db:
        todo_model = db.query(Todos).where(Todos.id == 2).first()

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"status": "The new todo was created"}
    assert todo_model.user_id == request_body["user_id"]
    assert todo_model.title == request_body["title"]
    assert todo_model.description == request_body["description"]
    assert todo_model.priority == request_body["priority"]
    assert todo_model.completed == request_body["completed"]


def test_update_todo_authenticated(mock_data):
    # Arrange
    request_body = {
        "title": "Todo Test Updated",
        "description": "This is a todo test updated",
        "priority": 1,
        "completed": True
    }

    # Act
    response = client.put(f"/todos/{mock_data["todo"].id}", json=request_body)
    with TestSessionLocal() as db:
        todo_model = db.query(Todos).where(Todos.id == mock_data["todo"].id).first()

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert todo_model.title == request_body["title"]
    assert todo_model.description == request_body["description"]
    assert todo_model.priority == request_body["priority"]
    assert todo_model.completed == request_body["completed"]


def test_update_todo_not_found():
    # Arrange
    request_body = {
        "title": "Todo Test Updated",
        "description": "This is a todo test updated",
        "priority": 1,
        "completed": True
    }

    # Act
    response = client.put("/todos/111111111", json=request_body)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Todo not found"
    }


def test_delete_todo_authenticated(mock_data):
    response = client.delete(f"/todos/{mock_data["todo"].id}")
    with TestSessionLocal() as db:
        todo_model = db.query(Todos).where(Todos.id == mock_data["todo"].id).first()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not todo_model


def test_delete_todo_not_found():
    response = client.delete("/todos/111111111")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Todo not found"
    }
