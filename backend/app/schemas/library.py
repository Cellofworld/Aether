"""Pydantic schemas for library operations."""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LibraryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(...)  # movies, series, anime, music, etc.
    description: Optional[str] = None


class LibraryCreate(LibraryBase):
    paths: Optional[List[str]] = []


class LibraryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class LibraryPathResponse(BaseModel):
    id: int
    path: str
    
    class Config:
        from_attributes = True


class LibraryResponse(LibraryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    paths: List[LibraryPathResponse] = []
    
    class Config:
        from_attributes = True
