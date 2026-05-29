"""
SQLAlchemy 2.0 风格的 Declarative Base。
所有 ORM 模型继承自 Base；Alembic 通过 import app.models 收集元数据。
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
