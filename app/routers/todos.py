from typing import Annotated, Optional

from fastapi import status, HTTPException, Path, APIRouter, Request
from fastapi.params import Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from .auth import current_user_dependency, get_current_user
from ..database import SessionLocal
from ..models import Todos

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)
templates = Jinja2Templates(directory="app/templates")


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


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response


@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        current_user = await get_current_user(request.cookies.get("access_token"))
        if not current_user:
            return redirect_to_login()
        todos = db.query(Todos).where(Todos.user_id == current_user["user_id"]).all()

        return templates.TemplateResponse("todo.html",
                                          context={"request": request, "todos": todos, "user": current_user})
    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_todo_page(request: Request, db: db_dependency, todo_id: int = Path(gt=0)):
    try:
        current_user = await get_current_user(request.cookies.get("access_token"))
        if not current_user:
            return redirect_to_login()
        todo = db.query(Todos).where(Todos.user_id == current_user["user_id"] and Todos.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html",
                                          context={"request": request, "todo": todo, "user": current_user})
    except:
        return redirect_to_login()


@router.get("/add-todo-page")
async def render_todo_page(request: Request):
    try:
        current_user = await get_current_user(request.cookies.get("access_token"))
        if not current_user:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", context={"request": request, "user": current_user})
    except:
        return redirect_to_login()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency, current_user: current_user_dependency):
    return db.query(Todos).where(Todos.user_id == current_user["user_id"]).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(db: db_dependency, current_user: current_user_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).where(Todos.id == todo_id and Todos.user_id == current_user["user_id"]).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, current_user: current_user_dependency, todo_request: TodoRequest):
    todo = Todos(**todo_request.model_dump(), user_id=current_user["user_id"])
    db.add(todo)
    db.commit()
    return {"status": "The new todo was created"}


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, current_user: current_user_dependency, todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    todo = db.query(Todos).where(Todos.id == todo_id and Todos.user_id == current_user["user_id"]).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.completed = todo_request.completed
    db.add(todo)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, current_user: current_user_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).where(Todos.id == todo_id and Todos.user_id == current_user["user_id"]).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
