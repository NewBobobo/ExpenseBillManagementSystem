"""
认证相关 Pydantic schemas。字段严格对齐 CONTRACTS §1-§3。
"""
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class UserInfo(BaseModel):
    """登录响应里的 user 字段 / /auth/me 的 data —— 二者同构。"""

    id: int
    username: str
    real_name: str
    role: str
    org_id: int
    org_name: str


class LoginResponse(BaseModel):
    token: str
    user: UserInfo
