"""
机构相关接口。
- GET /orgs/tree  契约 §4：管理员返回本机构及所有下级，普通用户只返回本机构。
"""
from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.response import ok
from app.db.session import get_db
from app.models.org import Org
from app.models.user import User

router = APIRouter(prefix="/orgs", tags=["orgs"])


def _node(o: Org) -> dict:
    return {
        "id": o.id,
        "code": o.code,
        "name": o.name,
        "parent_id": o.parent_id,
        "level": o.level,
        "logo_path": o.logo_path,
        "children": [],
    }


def _build_subtree(orgs: List[Org], root_id: int) -> dict | None:
    """从 orgs 列表里以 root_id 为根装配一棵树。orgs 必须包含 root 自身。"""
    by_id: Dict[int, dict] = {o.id: _node(o) for o in orgs}
    root = by_id.get(root_id)
    if root is None:
        return None
    for o in orgs:
        if o.id == root_id:
            continue
        parent = by_id.get(o.parent_id) if o.parent_id is not None else None
        if parent is not None:
            parent["children"].append(by_id[o.id])
    # 子节点稳定按 id 排序
    for node in by_id.values():
        node["children"].sort(key=lambda n: n["id"])
    return root


@router.get("/tree")
def get_org_tree(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_org = db.get(Org, current.org_id)
    if user_org is None:
        return ok([])

    if current.role == "admin":
        # 管理员可见：本机构 + 所有下级（按 path 前缀匹配）
        prefix = user_org.path  # 形如 /1/3/
        rows = db.execute(
            select(Org).where(Org.path.like(f"{prefix}%")).order_by(Org.path)
        ).scalars().all()
    else:
        # 普通用户：仅本机构
        rows = [user_org]

    tree = _build_subtree(rows, user_org.id)
    return ok([tree] if tree else [])
