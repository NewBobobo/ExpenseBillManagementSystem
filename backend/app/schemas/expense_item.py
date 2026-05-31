"""
费用项字典 Schemas (CONTRACTS §7)
"""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ExpenseItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    default_qty: str = Field(..., pattern=r"^\d+(\.\d{1,2})?$")
    unit_price: str = Field(..., pattern=r"^\d+(\.\d{1,2})?$")
    unit: Optional[str] = Field(None, max_length=16)
    sort_order: int = Field(default=0)


class ExpenseItemCreate(ExpenseItemBase):
    org_id: int


class ExpenseItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    default_qty: Optional[str] = Field(None, pattern=r"^\d+(\.\d{1,2})?$")
    unit_price: Optional[str] = Field(None, pattern=r"^\d+(\.\d{1,2})?$")
    unit: Optional[str] = Field(None, max_length=16)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class ExpenseItemOut(BaseModel):
    id: int
    org_id: int
    name: str
    default_qty: str
    unit_price: str
    unit: Optional[str]
    is_active: bool
    sort_order: int

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, item) -> "ExpenseItemOut":
        """
        从 ORM ExpenseItem 转换，金额字段 Decimal → 两位小数字符串。
        """
        return cls(
            id=item.id,
            org_id=item.org_id,
            name=item.name,
            default_qty=f"{item.default_qty:.2f}",
            unit_price=f"{item.unit_price:.2f}",
            unit=item.unit,
            is_active=item.is_active,
            sort_order=item.sort_order,
        )
