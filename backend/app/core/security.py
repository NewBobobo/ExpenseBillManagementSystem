"""
密码哈希(bcrypt) + JWT 编解码。

直接使用 bcrypt 库（passlib 1.7.4 与 bcrypt 4.x 不兼容，会在加载时探测崩溃）。
bcrypt 单密码上限 72 字节，业务侧密码长度限制在 schemas 已约束 ≤128 字符；
为防止用户填超长密码意外报错，这里在哈希/校验前统一截断到 72 字节。
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def _to_bytes(plain: str) -> bytes:
    """编码为 bytes 并截断到 bcrypt 上限 72 字节。"""
    return plain.encode("utf-8")[:72]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_to_bytes(plain), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(plain), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    subject: str | int,
    extra: Optional[dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """生成 JWT。subject 写到 sub 字段(用户 id 字符串)。"""
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """解码 JWT；非法/过期返回 None。"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
