"""
机构相关 Pydantic schemas。/orgs/tree 字段严格对齐 CONTRACTS §4。
"""
from typing import List, Optional

from pydantic import BaseModel


class OrgTreeNode(BaseModel):
    id: int
    code: str
    name: str
    parent_id: Optional[int]
    level: int
    logo_path: Optional[str]
    children: List["OrgTreeNode"] = []


OrgTreeNode.model_rebuild()
