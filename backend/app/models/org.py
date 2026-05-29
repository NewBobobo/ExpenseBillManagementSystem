"""
机构(orgs)。物化路径：path 形如 `/1/3/7/`，level=路径深度(根=0)。
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Org(Base):
    __tablename__ = "orgs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    logo_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    parent: Mapped[Optional["Org"]] = relationship(
        "Org", remote_side="Org.id", back_populates="children"
    )
    children: Mapped[List["Org"]] = relationship("Org", back_populates="parent")
