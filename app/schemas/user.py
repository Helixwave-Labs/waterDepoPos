from typing import Optional
from pydantic import BaseModel
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str
    phone: Optional[str] = None
    role: UserRole = UserRole.STAFF
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True