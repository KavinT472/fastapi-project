from pydantic import BaseModel,EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password:str

class UserOut(BaseModel):
    name: str
    email: str
class Login(BaseModel):
    email:EmailStr
    password:str
class Token(BaseModel):
    access_token: str
    token_type: str
class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None

class Config:
        from_attributes = True
