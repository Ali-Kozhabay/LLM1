from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.STUDENT

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str 

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetVerify(BaseModel):
    reset_id: int
    otp_code: str
    new_password: str

class PasswordResetResponse(BaseModel):
    message: str
    reset_id: int
