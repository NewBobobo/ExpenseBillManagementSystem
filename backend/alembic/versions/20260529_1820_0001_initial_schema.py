"""initial schema: 10 tables

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-29
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # orgs
    op.create_table(
        "orgs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("parent_id", sa.BigInteger(), sa.ForeignKey("orgs.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("level", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("logo_path", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_orgs_parent_id", "orgs", ["parent_id"])
    op.create_index("ix_orgs_path", "orgs", ["path"])

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("real_name", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.BigInteger(), sa.ForeignKey("orgs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_org_id", "users", ["org_id"])

    # expense_items
    op.create_table(
        "expense_items",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("org_id", sa.BigInteger(), sa.ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("default_qty", sa.Numeric(12, 2), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(length=16), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_expense_items_org_id", "expense_items", ["org_id"])

    # seals
    op.create_table(
        "seals",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("org_id", sa.BigInteger(), sa.ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("image_path", sa.String(length=512), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_seals_org_id", "seals", ["org_id"])

    # templates
    op.create_table(
        "templates",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("org_id", sa.BigInteger(), sa.ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("xml_content", sa.Text(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_templates_org_id", "templates", ["org_id"])

    # reports
    op.create_table(
        "reports",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("org_id", sa.BigInteger(), sa.ForeignKey("orgs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column("recipient", sa.String(length=128), nullable=False),
        sa.Column("reporter_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("template_id", sa.BigInteger(), sa.ForeignKey("templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("seal_id", sa.BigInteger(), sa.ForeignKey("seals.id", ondelete="SET NULL"), nullable=True),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_reports_org_id", "reports", ["org_id"])

    # report_items
    op.create_table(
        "report_items",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("report_id", sa.BigInteger(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("qty", sa.Numeric(12, 2), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("remark", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_report_items_report_id", "report_items", ["report_id"])

    # report_logs
    op.create_table(
        "report_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("report_id", sa.BigInteger(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column("diff", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_report_logs_report_id", "report_logs", ["report_id"])

    # report_seq (复合主键)
    op.create_table(
        "report_seq",
        sa.Column("org_id", sa.BigInteger(), sa.ForeignKey("orgs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("seq_date", sa.Date(), primary_key=True),
        sa.Column("last_seq", sa.Integer(), nullable=False, server_default="0"),
    )

    # system_defaults
    op.create_table(
        "system_defaults",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    )
    op.create_index("ix_system_defaults_kind", "system_defaults", ["kind"])


def downgrade() -> None:
    op.drop_index("ix_system_defaults_kind", table_name="system_defaults")
    op.drop_table("system_defaults")
    op.drop_table("report_seq")
    op.drop_index("ix_report_logs_report_id", table_name="report_logs")
    op.drop_table("report_logs")
    op.drop_index("ix_report_items_report_id", table_name="report_items")
    op.drop_table("report_items")
    op.drop_index("ix_reports_org_id", table_name="reports")
    op.drop_table("reports")
    op.drop_index("ix_templates_org_id", table_name="templates")
    op.drop_table("templates")
    op.drop_index("ix_seals_org_id", table_name="seals")
    op.drop_table("seals")
    op.drop_index("ix_expense_items_org_id", table_name="expense_items")
    op.drop_table("expense_items")
    op.drop_index("ix_users_org_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_orgs_path", table_name="orgs")
    op.drop_index("ix_orgs_parent_id", table_name="orgs")
    op.drop_table("orgs")
