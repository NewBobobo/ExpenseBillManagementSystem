"""
系统默认配置(system_defaults)。新建机构时按 kind 复制为该机构的费用字典/模板。
kind: expense_item / template
payload: JSONB
"""
from typing import Any

from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SystemDefault(Base):
    __tablename__ = "system_defaults"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    payload: Mapped[Any] = mapped_column(JSONB, nullable=False)
