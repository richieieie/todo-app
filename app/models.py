from sqlalchemy import Integer, Column, String, Boolean, ForeignKey

from .database import Base


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    role = Column(String(50))
    phone_number = Column(String(10), nullable=False)


class Todos(Base):
    __tablename__ = "Todos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    title = Column(String(255))
    description = Column(String(255))
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
