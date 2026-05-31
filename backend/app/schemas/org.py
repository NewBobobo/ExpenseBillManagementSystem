"""
机构相关 Pydantic schemas。/orgs/tree 字段严格对齐 CONTRACTS §4。
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OrgTreeNode(BaseModel):
    id: int
    code: str
    name: str
    parent_id: Optional[int]
    level: int
    logo_path: Optional[str]
    children: List["OrgTreeNode"] = []


OrgTreeNode.model_rebuild()


class OrgCreate(BaseModel):
    parent_id: int
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)


class OrgUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    code: Optional[str] = Field(None, min_length=1, max_length=32)


class OrgOut(BaseModel):
    id: int
    code: str
    name: str
    parent_id: Optional[int]
    path: str
    level: int
    logo_path: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
