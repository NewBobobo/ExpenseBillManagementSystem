"""
单据主表(reports) + 明细(report_items)。
单号: 机构编号-YYMMDD-流水号(由 report_seq 维护，业务层生成)。
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    recipient: Mapped[str] = mapped_column(String(128), nullable=False)
    reporter_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    template_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("templates.id", ondelete="SET NULL"), nullable=True
    )
    seal_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("seals.id", ondelete="SET NULL"), nullable=True
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[List["ReportItem"]] = relationship(
        "ReportItem",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="ReportItem.seq",
    )


class ReportItem(Base):
    __tablename__ = "report_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    qty: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("1"))
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0")
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    remark: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    report: Mapped["Report"] = relationship("Report", back_populates="items")
