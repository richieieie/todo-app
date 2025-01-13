from typing import Annotated

from fastapi import status, APIRouter, HTTPException
from fastapi.params import Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .auth import current_user_dependency, bcrypt_context
from ..database import SessionLocal
from ..models import Users

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class UserInfoResponse(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
    phone_number: str
    model_config = {
        "from_attributes": True
    }


class UserChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_info(current_user: current_user_dependency, db: db_dependency):
    user_model = db.query(Users).where(Users.username == current_user["username"]).first()
    if user_model is None or not user_model.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot find your account details")

    return {"user": UserInfoResponse.model_validate(user_model).model_dump(exclude={"hashed_password"})}


@router.put("/password-change", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(current_user: current_user_dependency, db: db_dependency,
                               user_info: UserChangePasswordRequest):
    user_model = db.query(Users).where(Users.username == current_user["username"]).first()
    if not user_model or not user_model.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot find your account details")

    if not bcrypt_context.verify(user_info.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect old password")

    if user_info.new_password != user_info.confirm_new_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Confirm new password must match new password")

    user_model.hashed_password = bcrypt_context.hash(user_info.new_password)
    db.add(user_model)
    db.commit()


@router.put("/phone-number/{new_phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(current_user: current_user_dependency, db: db_dependency,
                              new_phone_number: str = Path(min_length=10, max_length=10)):
    user_model = db.query(Users).where(Users.id == current_user["user_id"]).first()
    if user_model.phone_number == new_phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your new phone number is already taken")
    user_model.phone_number = new_phone_number
    db.add(user_model)
    db.commit()
