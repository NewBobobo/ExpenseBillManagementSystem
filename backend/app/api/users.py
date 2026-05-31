"""
用户管理 CRUD (CONTRACTS §6)
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.config import settings
from app.core.response import BizError, ok
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.org import Org
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    UserCreate,
    UserListResponse,
    UserOut,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


def _get_visible_org_ids(user: User, db: Session) -> list[int]:
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


@router.get("")
def list_users(
    org_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §6.1 GET /api/users — 列表（admin，分页）
    """
    visible_ids = _get_visible_org_ids(current_user, db)
    if not visible_ids:
        return ok(UserListResponse(items=[], total=0, page=page, page_size=page_size))

    stmt = select(User).where(User.org_id.in_(visible_ids))
    if org_id is not None:
        if org_id not in visible_ids:
            raise BizError(40300, "无权限访问该机构")
        stmt = stmt.where(User.org_id == org_id)
    if keyword:
        stmt = stmt.where(
            (User.username.like(f"%{keyword}%")) | (User.real_name.like(f"%{keyword}%"))
        )

    # 总数
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(total_stmt) or 0

    # 分页
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    users = db.scalars(stmt).all()

    # 构造响应（带 org_name）
    items = []
    for u in users:
        org = db.get(Org, u.org_id)
        items.append(
            UserOut(
                id=u.id,
                username=u.username,
                real_name=u.real_name,
                role=u.role,
                org_id=u.org_id,
                org_name=org.name if org else "",
                is_active=u.is_active,
                created_at=u.created_at,
            )
        )

    return ok(UserListResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("")
def create_user(
    payload: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §6.2 POST /api/users — 新建（admin）
    """
    visible_ids = _get_visible_org_ids(current_user, db)
    if payload.org_id not in visible_ids:
        raise BizError(40300, "无权限操作该机构")

    # 检查 username 唯一
    existing = db.execute(
        select(User).where(User.username == payload.username)
    ).scalar_one_or_none()
    if existing:
        raise BizError(40900, f"用户名 {payload.username} 已存在")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        real_name=payload.real_name,
        org_id=payload.org_id,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    org = db.get(Org, user.org_id)
    return ok(
        UserOut(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            role=user.role,
            org_id=user.org_id,
            org_name=org.name if org else "",
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )


@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §6.3 PUT /api/users/{id} — 改 real_name/role/is_active（admin）
    """
    user = db.get(User, user_id)
    if user is None:
        raise BizError(40400, "用户不存在")

    visible_ids = _get_visible_org_ids(current_user, db)
    if user.org_id not in visible_ids:
        raise BizError(40300, "无权限操作该用户")

    if payload.real_name is not None:
        user.real_name = payload.real_name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)

    org = db.get(Org, user.org_id)
    return ok(
        UserOut(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            role=user.role,
            org_id=user.org_id,
            org_name=org.name if org else "",
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )


@router.put("/{user_id}/password")
def change_password(
    user_id: int,
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    §6.4 PUT /api/users/{id}/password — 改密码
    admin 重置他人：只需 new_password
    本人改密：需校验 old_password
    """
    user = db.get(User, user_id)
    if user is None:
        raise BizError(40400, "用户不存在")

    # 权限校验
    if current_user.role == "admin":
        # admin 可重置任何可见机构的用户
        visible_ids = _get_visible_org_ids(current_user, db)
        if user.org_id not in visible_ids:
            raise BizError(40300, "无权限操作该用户")
    else:
        # 普通用户只能改自己的密码
        if user.id != current_user.id:
            raise BizError(40300, "无权限操作该用户")
        # 本人改密需校验旧密码
        if not payload.old_password:
            raise BizError(42200, "本人改密需提供旧密码")
        if not verify_password(payload.old_password, user.password_hash):
            raise BizError(40101, "旧密码错误")

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return ok(None)


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §6.6 POST /api/users/{id}/reset-password — 一键重置密码（admin）
    无请求体，把目标用户密码重置为系统默认值 DEFAULT_RESET_PASSWORD(123qwe)。
    """
    user = db.get(User, user_id)
    if user is None:
        raise BizError(40400, "用户不存在")

    visible_ids = _get_visible_org_ids(current_user, db)
    if user.org_id not in visible_ids:
        raise BizError(40300, "无权限操作该用户")

    user.password_hash = hash_password(settings.DEFAULT_RESET_PASSWORD)
    db.commit()
    return ok(None)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §6.5 DELETE /api/users/{id} — 软删除（admin）
    """
    user = db.get(User, user_id)
    if user is None:
        raise BizError(40400, "用户不存在")

    visible_ids = _get_visible_org_ids(current_user, db)
    if user.org_id not in visible_ids:
        raise BizError(40300, "无权限操作该用户")

    user.is_active = False
    db.commit()
    return ok(None)
