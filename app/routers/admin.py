from typing import Annotated, Optional

from fastapi import status, HTTPException, Path, APIRouter
from fastapi.params import Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .auth import current_user_dependency, authenticate_role
from ..database import SessionLocal
from ..models import Todos

router = APIRouter(
    prefix="/todos/admin",
    tags=["todos"]
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=255)
    priority: int = Field(gt=0, lt=6)
    completed: Optional[bool] = Field(default=False)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [{
                "title": "Clean up",
                "description": "A clean up of your data in project A",
                "priority": 5,
                "completed": False
            }]
        }
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency, current_user: current_user_dependency):
    authenticate_role(current_user["user_role"], "admin")
    return db.query(Todos).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(db: db_dependency, current_user: current_user_dependency, todo_id: int = Path(gt=0)):
    authenticate_role(current_user["user_role"], "admin")
    todo = db.query(Todos).where(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, current_user: current_user_dependency, todo_id: int = Path(gt=0)):
    authenticate_role(current_user["user_role"], "admin")
    todo = db.query(Todos).where(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
