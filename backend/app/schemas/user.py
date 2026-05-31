"""
用户管理 Schemas (CONTRACTS §6)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1)
    real_name: str = Field(..., min_length=1, max_length=64)
    org_id: int
    role: str = Field(..., pattern="^(admin|user)$")


class UserUpdate(BaseModel):
    real_name: Optional[str] = Field(None, min_length=1, max_length=64)
    role: Optional[str] = Field(None, pattern="^(admin|user)$")
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    old_password: Optional[str] = None
    new_password: str = Field(..., min_length=1)


class UserOut(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    org_id: int
    org_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    page_size: int
