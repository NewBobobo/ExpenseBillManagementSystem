"""
费用项字典 CRUD (CONTRACTS §7)
"""
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.response import BizError, ok
from app.db.session import get_db
from app.models.expense_item import ExpenseItem
from app.models.org import Org
from app.models.user import User
from app.schemas.expense_item import (
    ExpenseItemCreate,
    ExpenseItemOut,
    ExpenseItemUpdate,
)

router = APIRouter(prefix="/expense-items", tags=["expense-items"])


def _parse_decimal(s: str) -> Decimal:
    """
    解析两位小数字符串为 Decimal，失败抛 BizError(42200)。
    """
    try:
        d = Decimal(s)
        if d.as_tuple().exponent < -2:
            raise BizError(42200, f"金额字段最多两位小数: {s}")
        return d
    except (InvalidOperation, ValueError):
        raise BizError(42200, f"金额字段格式错误: {s}")


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


@router.get("")
def list_expense_items(
    org_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    §7.1 GET /api/expense-items — 列表（按 sort_order 升序）
    """
    visible_ids = _get_visible_org_ids(current_user, db)
    if not visible_ids:
        return ok([])

    stmt = select(ExpenseItem).where(ExpenseItem.org_id.in_(visible_ids))
    if org_id is not None:
        if org_id not in visible_ids:
            raise BizError(40300, "无权限访问该机构")
        stmt = stmt.where(ExpenseItem.org_id == org_id)
    if is_active is not None:
        stmt = stmt.where(ExpenseItem.is_active == is_active)
    stmt = stmt.order_by(ExpenseItem.sort_order.asc(), ExpenseItem.id.asc())

    items = db.scalars(stmt).all()
    return ok([ExpenseItemOut.from_orm_model(it) for it in items])


@router.post("")
def create_expense_item(
    payload: ExpenseItemCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §7.2 POST /api/expense-items — 新增（admin）
    """
    visible_ids = _get_visible_org_ids(current_user, db)
    if payload.org_id not in visible_ids:
        raise BizError(40300, "无权限操作该机构")

    item = ExpenseItem(
        org_id=payload.org_id,
        name=payload.name,
        default_qty=_parse_decimal(payload.default_qty),
        unit_price=_parse_decimal(payload.unit_price),
        unit=payload.unit,
        sort_order=payload.sort_order,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return ok(ExpenseItemOut.from_orm_model(item))


@router.put("/{item_id}")
def update_expense_item(
    item_id: int,
    payload: ExpenseItemUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §7.3 PUT /api/expense-items/{id} — 修改（admin）
    """
    item = db.get(ExpenseItem, item_id)
    if item is None:
        raise BizError(40400, "费用项不存在")

    visible_ids = _get_visible_org_ids(current_user, db)
    if item.org_id not in visible_ids:
        raise BizError(40300, "无权限操作该机构")

    if payload.name is not None:
        item.name = payload.name
    if payload.default_qty is not None:
        item.default_qty = _parse_decimal(payload.default_qty)
    if payload.unit_price is not None:
        item.unit_price = _parse_decimal(payload.unit_price)
    if payload.unit is not None:
        item.unit = payload.unit
    if payload.is_active is not None:
        item.is_active = payload.is_active
    if payload.sort_order is not None:
        item.sort_order = payload.sort_order

    db.commit()
    db.refresh(item)
    return ok(ExpenseItemOut.from_orm_model(item))


@router.delete("/{item_id}")
def delete_expense_item(
    item_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    §7.4 DELETE /api/expense-items/{id} — 硬删除（admin）
    物理删除字典记录。费用项字典是模板/可选项，单据明细(ReportItem)为下单时的
    值快照、不引用 expense_items，故删除字典不影响已开单据。「停用」语义由
    PUT is_active=false 承担。
    """
    item = db.get(ExpenseItem, item_id)
    if item is None:
        raise BizError(40400, "费用项不存在")

    visible_ids = _get_visible_org_ids(current_user, db)
    if item.org_id not in visible_ids:
        raise BizError(40300, "无权限操作该机构")

    db.delete(item)
    db.commit()
    return ok(None)