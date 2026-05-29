"""
端到端冒烟测试：用 SQLite 内存库覆盖 get_db，验证
  POST /api/auth/login  —— 正确密码 / 错误密码 / 停用账号
  GET  /api/auth/me     —— 带/不带 Token
  POST /api/auth/logout
  GET  /api/orgs/tree   —— admin 看到本机构+下级；user 只看本机构

注意：JSONB 字段在 SQLite 不支持，本测试不创建 system_defaults / report_logs；
仅在 PG 真实迁移上端到端跑全量。这里聚焦 W1 三个接口。
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 让 import app.* 可用
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture()
def client(tmp_path):
    # 用文件型 SQLite，避免 in-memory 多连接问题
    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    os.environ["DATABASE_URL"] = db_url

    # 重新加载 settings & session（因为 settings 是 lru_cache）
    from app.core import config as cfg

    cfg.get_settings.cache_clear()
    cfg.settings = cfg.get_settings()

    from app.db import session as db_session

    test_engine = create_engine(db_url, future=True)
    TestingSessionLocal = sessionmaker(
        bind=test_engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    db_session.engine = test_engine
    db_session.SessionLocal = TestingSessionLocal

    # 仅建 W1 用得到的表（避开 JSONB）
    from app.db.base import Base
    from app.models.org import Org  # noqa: F401
    from app.models.user import User  # noqa: F401
    from app.models.expense_item import ExpenseItem  # noqa: F401
    from app.models.seal import Seal  # noqa: F401
    from app.models.template import Template  # noqa: F401
    from app.models.report import Report, ReportItem  # noqa: F401
    from app.models.report_seq import ReportSeq  # noqa: F401

    Base.metadata.create_all(
        bind=test_engine,
        tables=[
            Base.metadata.tables[name]
            for name in ["orgs", "users", "expense_items", "seals", "templates"]
        ],
    )

    # 灌种子：HQ + admin/123456 + 上海一店 + 普通用户 zhangsan
    from app.core.security import hash_password
    from app.models.org import Org
    from app.models.user import User

    with TestingSessionLocal() as s:
        hq = Org(id=1, parent_id=None, code="HQ", name="总部", path="/1/", level=0)
        sh = Org(id=2, parent_id=1, code="SH001", name="上海一店", path="/1/2/", level=1)
        s.add_all([hq, sh])
        s.flush()
        s.add_all(
            [
                User(
                    id=1,
                    username="admin",
                    password_hash=hash_password("123456"),
                    real_name="管理员",
                    org_id=1,
                    role="admin",
                    is_active=True,
                ),
                User(
                    id=2,
                    username="zhangsan",
                    password_hash=hash_password("abcdef"),
                    real_name="张三",
                    org_id=2,
                    role="user",
                    is_active=True,
                ),
                User(
                    id=3,
                    username="disabled",
                    password_hash=hash_password("xxxxxx"),
                    real_name="已停用",
                    org_id=1,
                    role="user",
                    is_active=False,
                ),
            ]
        )
        s.commit()

    from app.main import app

    return TestClient(app)


def test_login_success_and_me(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "123456"})
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 0
    user = body["data"]["user"]
    assert user["username"] == "admin"
    assert user["role"] == "admin"
    assert user["org_id"] == 1
    assert user["org_name"] == "总部"
    assert user["real_name"] == "管理员"
    token = body["data"]["token"]
    assert token

    r2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["code"] == 0
    assert r2.json()["data"]["username"] == "admin"


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "bad"})
    assert r.status_code == 200
    assert r.json()["code"] == 40101


def test_login_disabled_account(client):
    r = client.post(
        "/api/auth/login", json={"username": "disabled", "password": "xxxxxx"}
    )
    assert r.status_code == 200
    assert r.json()["code"] == 40301


def test_me_without_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["code"] == 40100


def test_logout_ok(client):
    r = client.post(
        "/api/auth/login", json={"username": "admin", "password": "123456"}
    )
    token = r.json()["data"]["token"]
    r2 = client.post(
        "/api/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert r2.status_code == 200
    assert r2.json() == {"code": 0, "message": "success", "data": None}


def test_orgs_tree_admin_sees_descendants(client):
    r = client.post(
        "/api/auth/login", json={"username": "admin", "password": "123456"}
    )
    token = r.json()["data"]["token"]
    r2 = client.get("/api/orgs/tree", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["code"] == 0
    data = body["data"]
    assert isinstance(data, list) and len(data) == 1
    root = data[0]
    assert root["id"] == 1 and root["code"] == "HQ" and root["parent_id"] is None
    assert root["level"] == 0
    assert len(root["children"]) == 1
    child = root["children"][0]
    assert child["id"] == 2 and child["parent_id"] == 1 and child["children"] == []


def test_orgs_tree_user_sees_only_self(client):
    r = client.post(
        "/api/auth/login", json={"username": "zhangsan", "password": "abcdef"}
    )
    token = r.json()["data"]["token"]
    r2 = client.get("/api/orgs/tree", headers={"Authorization": f"Bearer {token}"})
    body = r2.json()
    assert body["code"] == 0
    data = body["data"]
    assert len(data) == 1
    assert data[0]["id"] == 2
    assert data[0]["children"] == []
