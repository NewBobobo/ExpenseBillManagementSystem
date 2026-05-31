"""seed HQ (org_id=1) with default expense_items and template (D-001)

为初始总部 HQ 复制一份默认费用项/模板。0002 只把默认数据放进 system_defaults
作为新建子机构的复制源，未给 HQ 自身复制，导致总部费用项列表为空。本迁移补齐。
从 system_defaults 读取（单一数据源），幂等：HQ 已有数据则跳过。

Revision ID: 0003_seed_hq_defaults
Revises: 0002_seed_initial_data
Create Date: 2026-05-31
"""
import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_seed_hq_defaults"
down_revision: Union[str, None] = "0002_seed_initial_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HQ_ORG_ID = 1


def upgrade() -> None:
    bind = op.get_bind()

    # 幂等：HQ 已有费用项则认为已初始化，跳过
    existing = bind.execute(
        sa.text("SELECT COUNT(*) FROM expense_items WHERE org_id = :oid"),
        {"oid": HQ_ORG_ID},
    ).scalar()
    if existing and existing > 0:
        return

    # 从 system_defaults 读默认费用项，复制给 HQ
    rows = bind.execute(
        sa.text("SELECT payload FROM system_defaults WHERE kind = 'expense_item'")
    ).fetchall()
    for (payload,) in rows:
        p = payload if isinstance(payload, dict) else json.loads(payload)
        bind.execute(
            sa.text(
                """
                INSERT INTO expense_items
                  (org_id, name, default_qty, unit_price, unit, is_active, sort_order)
                VALUES
                  (:oid, :name, :qty, :price, :unit, TRUE, :sort)
                """
            ),
            {
                "oid": HQ_ORG_ID,
                "name": p.get("name", ""),
                "qty": p.get("default_qty", 1),
                "price": p.get("unit_price", 0),
                "unit": p.get("unit"),
                "sort": p.get("sort_order", 0),
            },
        )

    # 从 system_defaults 读默认模板，复制给 HQ
    tpl_rows = bind.execute(
        sa.text("SELECT payload FROM system_defaults WHERE kind = 'template'")
    ).fetchall()
    for (payload,) in tpl_rows:
        p = payload if isinstance(payload, dict) else json.loads(payload)
        bind.execute(
            sa.text(
                """
                INSERT INTO templates (org_id, name, xml_content, is_default)
                VALUES (:oid, :name, :xml, :is_default)
                """
            ),
            {
                "oid": HQ_ORG_ID,
                "name": p.get("name", ""),
                "xml": p.get("xml_content", ""),
                "is_default": p.get("is_default", False),
            },
        )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text("DELETE FROM templates WHERE org_id = :oid"), {"oid": HQ_ORG_ID}
    )
    bind.execute(
        sa.text("DELETE FROM expense_items WHERE org_id = :oid"), {"oid": HQ_ORG_ID}
    )

