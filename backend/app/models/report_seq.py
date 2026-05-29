"""
单号流水(report_seq)。复合主键 (org_id, seq_date)，记录该机构当日的最后流水号。
"""
from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportSeq(Base):
    __tablename__ = "report_seq"

    org_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orgs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    seq_date: Mapped[date] = mapped_column(Date, primary_key=True)
    last_seq: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
