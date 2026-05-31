"""
机构相关接口。
- GET /orgs/tree  契约 §4：管理员返回本机构及所有下级，普通用户只返回本机构。
- POST /orgs      契约 §5.1：新建子机构（回填 path，复制默认数据）
- PUT /orgs/{id}  契约 §5.2：改 name/code
- DELETE /orgs/{id} 契约 §5.3：删机构（校验无子机构/无用户）
- PUT /orgs/{id}/logo 契约 §5.4：上传 Logo
"""
import os
from decimal import Decimal
from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.config import settings
from app.core.response import BizError, ok
from app.db.session import get_db
from app.models.expense_item import ExpenseItem
from app.models.org import Org
from app.models.system_default import SystemDefault
from app.models.template import Template
from app.models.user import User
from app.schemas.org import OrgCreate, OrgOut, OrgUpdate

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


def _get_visible_org_ids(user: User, db: Session) -> List[int]:
    """
    返回当前用户可见的机构 id 列表。
    admin → 本机构 + 所有下级（path LIKE 前缀）
    user → 仅本机构
    """
    org = db.get(Org, user.org_id)
    if org is None:
        return []
    if user.role == "admin":
        stmt = select(Org.id).where(Org.path.like(f"{org.path}%"))
        return list(db.scalars(stmt).all())
    else:
        return [user.org_id]


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


@router.post("")
def create_org(
    payload: OrgCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §5.1 POST /api/orgs — 新建子机构（admin）
    """
    visible_ids = _get_visible_org_ids(current_user, db)
    if payload.parent_id not in visible_ids:
        raise BizError(40300, "无权限操作该机构")

    parent = db.get(Org, payload.parent_id)
    if parent is None:
        raise BizError(40400, "父机构不存在")

    # 检查 code 唯一
    existing = db.execute(select(Org).where(Org.code == payload.code)).scalar_one_or_none()
    if existing:
        raise BizError(40900, f"机构代码 {payload.code} 已存在")

    # 新建机构，flush 取 id 后回填 path
    new_org = Org(
        parent_id=payload.parent_id,
        code=payload.code,
        name=payload.name,
        path="",  # 临时占位
        level=parent.level + 1,
    )
    db.add(new_org)
    db.flush()
    new_org.path = f"{parent.path}{new_org.id}/"

    # 复制默认数据：system_defaults 中 kind='expense_item'/'template'
    defaults = db.execute(
        select(SystemDefault).where(SystemDefault.kind.in_(["expense_item", "template"]))
    ).scalars().all()

    for default in defaults:
        if default.kind == "expense_item":
            item_data = default.payload
            db.add(
                ExpenseItem(
                    org_id=new_org.id,
                    name=item_data.get("name", ""),
                    default_qty=Decimal(str(item_data.get("default_qty", "1.00"))),
                    unit_price=Decimal(str(item_data.get("unit_price", "0.00"))),
                    unit=item_data.get("unit"),
                    is_active=item_data.get("is_active", True),
                    sort_order=item_data.get("sort_order", 0),
                )
            )
        elif default.kind == "template":
            tpl_data = default.payload
            db.add(
                Template(
                    org_id=new_org.id,
                    name=tpl_data.get("name", ""),
                    xml_content=tpl_data.get("xml_content", ""),
                    is_default=tpl_data.get("is_default", False),
                )
            )

    db.commit()
    db.refresh(new_org)
    return ok(OrgOut.model_validate(new_org))


@router.put("/{org_id}")
def update_org(
    org_id: int,
    payload: OrgUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §5.2 PUT /api/orgs/{id} — 改 name/code（admin）
    """
    org = db.get(Org, org_id)
    if org is None:
        raise BizError(40400, "机构不存在")

    visible_ids = _get_visible_org_ids(current_user, db)
    if org_id not in visible_ids:
        raise BizError(40300, "无权限操作该机构")

    if payload.name is not None:
        org.name = payload.name
    if payload.code is not None:
        # 检查 code 唯一
        existing = db.execute(
            select(Org).where(Org.code == payload.code, Org.id != org_id)
        ).scalar_one_or_none()
        if existing:
            raise BizError(40900, f"机构代码 {payload.code} 已存在")
        org.code = payload.code

    db.commit()
    db.refresh(org)
    return ok(OrgOut.model_validate(org))


@router.delete("/{org_id}")
def delete_org(
    org_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §5.3 DELETE /api/orgs/{id} — 删机构（admin）
    前置校验：无子机构、无用户
    """
    org = db.get(Org, org_id)
    if org is None:
        raise BizError(40400, "机构不存在")

    visible_ids = _get_visible_org_ids(current_user, db)
    if org_id not in visible_ids:
        raise BizError(40300, "无权限操作该机构")

    # 校验无子机构
    child_count = db.execute(
        select(Org).where(Org.parent_id == org_id)
    ).scalars().first()
    if child_count:
        raise BizError(40901, "该机构下存在子机构，无法删除")

    # 校验无用户
    user_count = db.execute(
        select(User).where(User.org_id == org_id)
    ).scalars().first()
    if user_count:
        raise BizError(40901, "该机构下存在用户，无法删除")

    db.delete(org)
    db.commit()
    return ok(None)


@router.put("/{org_id}/logo")
async def upload_logo(
    org_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §5.4 PUT /api/orgs/{id}/logo — 上传/更换 Logo（admin）
    """
    org = db.get(Org, org_id)
    if org is None:
        raise BizError(40400, "机构不存在")

    visible_ids = _get_visible_org_ids(current_user, db)
    if org_id not in visible_ids:
        raise BizError(40300, "无权限操作该机构")

    # 校验文件类型
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise BizError(42200, "仅支持 PNG/JPG 格式")

    # 校验文件大小 ≤2MB
    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise BizError(42200, "文件大小不能超过 2MB")

    # 存储到 STORAGE_PATH/logos/
    logos_dir = Path(settings.STORAGE_PATH) / "logos"
    logos_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix if file.filename else ".png"
    filename = f"{org_id}_{os.urandom(4).hex()}{ext}"
    file_path = logos_dir / filename

    with open(file_path, "wb") as f:
        f.write(content)

    # 回写 logo_path
    org.logo_path = f"/storage/logos/{filename}"
    db.commit()
    db.refresh(org)

    return ok({"logo_path": org.logo_path})
