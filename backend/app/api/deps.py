"""
FastAPI 依赖：从 Authorization: Bearer <token> 解析当前用户。

未登录/Token 失效 → 抛 BizError(40100)
账号已停用 → 抛 BizError(40301)
"""
from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.response import BizError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User


def _extract_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_bearer(authorization)
    if not token:
        raise BizError(40100, "未登录或 Token 失效")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise BizError(40100, "未登录或 Token 失效")

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise BizError(40100, "未登录或 Token 失效")

    user = db.get(User, user_id)
    if user is None:
        raise BizError(40100, "未登录或 Token 失效")
    if not user.is_active:
        raise BizError(40301, "账号已停用")
    return user
