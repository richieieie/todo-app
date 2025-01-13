import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool.impl import StaticPool

from ..main import app
from ..models import Base, Todos, Users
from ..routers.auth import bcrypt_context

SQLITE_URL = "sqlite:///./testdb.db"

engine = create_engine(SQLITE_URL, connect_args={'check_same_thread': False}, poolclass=StaticPool)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Session:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "johndoe123", "user_id": 1, "user_role": "user"}


def override_get_current_admin():
    return {"username": "admin", "user_id": 2, "user_role": "admin"}


client = TestClient(app)


@pytest.fixture
def mock_data():
    user = Users(username="johndoe123", email="johndoe123@example.com", first_name="John", last_name="Doe",
                 is_active=True, role="user",
                 phone_number="0123456789", hashed_password=bcrypt_context.hash("12345aA@"))
    admin = Users(username="admin", email="admin@example.com", first_name="David", last_name="Louis", is_active=True,
                  role="admin",
                  phone_number="0123456789")
    todo = Todos(user_id=1, title="Todo Test", description="This is a todo test", priority=5, completed=False)
    db = TestSessionLocal()
    db.add(user)
    db.add(admin)
    db.add(todo)
    db.commit()
    yield {"todo": todo, "user": user, "admin": admin}
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM Todos"))
        connection.execute(text("DELETE FROM Users"))
        connection.commit()
