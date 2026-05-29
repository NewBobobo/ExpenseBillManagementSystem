"""
认证接口：POST /auth/login, POST /auth/logout, GET /auth/me
契约：CONTRACTS §1-§3，错误码 40101/40301/40100。
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.response import BizError, ok
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.org import Org
from app.models.user import User
from app.schemas.auth import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_payload(user: User, org: Org) -> dict:
    """构造 CONTRACTS §1 中的 user 对象（与 §3 同构）。"""
    return {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "role": user.role,
        "org_id": user.org_id,
        "org_name": org.name,
    }


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.username == body.username)
    ).scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise BizError(40101, "用户名或密码错误")
    if not user.is_active:
        raise BizError(40301, "账号已停用")

    org = db.get(Org, user.org_id)
    if org is None:
        # 数据异常：用户挂在不存在的机构上
        raise BizError(40101, "用户名或密码错误")

    token = create_access_token(subject=user.id)
    return ok({"token": token, "user": _user_payload(user, org)})


@router.post("/logout")
def logout(_: User = Depends(get_current_user)):
    """前端清 Token 即可；后端可选黑名单，本实现仅返回 200。"""
    return ok(None)


@router.get("/me")
def me(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = db.get(Org, current.org_id)
    if org is None:
        raise BizError(40100, "未登录或 Token 失效")
    return ok(_user_payload(current, org))
