from lib2to3.pgen2.token import OP
from typing import Optional
from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    userid: Optional[str] = None
    useraddress: Optional[str] = None
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: bool = False
    account: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    hashed_password: str


class UserUpdate(UserBase):
    hashed_password: Optional[str] = None


class User(UserCreate):
    id: Optional[int] = None