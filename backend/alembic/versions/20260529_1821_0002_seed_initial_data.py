"""seed initial data: HQ org + admin user + a few system_defaults

Revision ID: 0002_seed_initial_data
Revises: 0001_initial_schema
Create Date: 2026-05-29
"""
import json
from typing import Sequence, Union

import bcrypt
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_seed_initial_data"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # 初始密码 admin/123456 — 用 bcrypt 现场哈希
    admin_hash = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode("utf-8")

    # 1) 顶级机构 "总部" id=1, code=HQ, path=/1/, level=0
    bind.execute(
        sa.text(
            """
            INSERT INTO orgs (id, parent_id, code, name, path, level, logo_path)
            VALUES (1, NULL, :code, :name, :path, 0, NULL)
            """
        ),
        {"code": "HQ", "name": "总部", "path": "/1/"},
    )
    # 修正 PostgreSQL 序列(orgs.id 自增序列)，让后续 INSERT 不撞 id=1
    bind.execute(sa.text("SELECT setval('orgs_id_seq', 1, true)"))

    # 2) 初始管理员 admin/123456，挂在总部
    bind.execute(
        sa.text(
            """
            INSERT INTO users (username, password_hash, real_name, org_id, role, is_active)
            VALUES (:u, :h, :rn, 1, 'admin', TRUE)
            """
        ),
        {"u": "admin", "h": admin_hash, "rn": "管理员"},
    )

    # 3) 系统默认配置：放几个常见费用项 + 一份占位模板，供新建机构时复制
    default_expense_items = [
        {"name": "办公用品", "default_qty": 1, "unit_price": 0, "unit": "个", "sort_order": 10},
        {"name": "水电费", "default_qty": 1, "unit_price": 0, "unit": "月", "sort_order": 20},
        {"name": "差旅费", "default_qty": 1, "unit_price": 0, "unit": "次", "sort_order": 30},
    ]
    for item in default_expense_items:
        bind.execute(
            sa.text(
                "INSERT INTO system_defaults (kind, payload) VALUES ('expense_item', CAST(:p AS JSONB))"
            ),
            {"p": json.dumps(item, ensure_ascii=False)},
        )

    default_template = {
        "name": "标准版",
        "is_default": True,
        "xml_content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><template><header/><body/></template>",
    }
    bind.execute(
        sa.text(
            "INSERT INTO system_defaults (kind, payload) VALUES ('template', CAST(:p AS JSONB))"
        ),
        {"p": json.dumps(default_template, ensure_ascii=False)},
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM system_defaults"))
    bind.execute(sa.text("DELETE FROM users WHERE username = 'admin'"))
    bind.execute(sa.text("DELETE FROM orgs WHERE id = 1"))
