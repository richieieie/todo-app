from datetime import timedelta, datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Users

SECRET_KEY = "sieunhandosieunhandensieunhanvangsieunhanhhongsieunhancam"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def authenticate_user_credentials(db: Session, form_data: OAuth2PasswordRequestForm):
    user_model = db.query(Users).where(Users.username == form_data.username).first()
    if not user_model or not bcrypt_context.verify(form_data.password, user_model.hashed_password):
        return None
    return user_model


def generate_access_token(claims: dict, expires_delta: timedelta) -> str:
    to_encode = claims.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    if not expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username, user_id, user_role = payload.get("sub"), payload.get("user_id"), payload.get("user_role")
        if not username or not user_id or not user_role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        return {"username": username, "user_id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")


def authenticate_role(user_role: str, role: str):
    if user_role != role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot perform this action")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
current_user_dependency = Annotated[dict, Depends(get_current_user)]


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    password: str
    password_confirm: str
    is_active: Optional[bool] = Field(default=True)
    role: str
    phone_number: str = Field(min_length=10, max_length=10)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "john.doe@example.com",
                    "username": "johndoe123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "password": "12345aA@",
                    "password_confirm": "12345aA@",
                    "is_active": True,
                    "role": "user",
                    "phone_number": "0123456789"
                },
                {
                    "email": "david.louis@example.com",
                    "username": "davidlouis123",
                    "first_name": "David",
                    "last_name": "Louis",
                    "password": "12345aA@",
                    "password_confirm": "12345aA@",
                    "is_active": True,
                    "role": "admin",
                    "phone_number": "0123456789"
                }
            ]
        }
    }


@router.get("/login-page")
async def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register-page")
async def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(db: db_dependency, user_request: CreateUserRequest):
    # if user_request.password != user_request.password_confirm:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords don't match")

    user_model = Users(**user_request.model_dump(exclude={"password", "password_confirm"}),
                       hashed_password=bcrypt_context.hash(user_request.password))
    db.add(user_model)
    db.commit()
    return {"status": "New account was created"}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user_model = authenticate_user_credentials(db, form_data)
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    claims = {"sub": user_model.username, "user_id": user_model.id, "user_role": user_model.role}
    access_token = generate_access_token(claims, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token}
