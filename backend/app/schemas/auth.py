"""Auth schemas."""
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    username: str | None = None


class UserCreate(BaseModel):
    """User registration data."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """User response data."""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True
