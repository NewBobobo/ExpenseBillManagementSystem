"""
T-010 用户管理 CRUD 端到端测试（SQLite）
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.org import Org
from app.models.user import User


@pytest.fixture(scope="function")
def db_session():
    db_path = "test_w2_users.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    engine = create_engine(f"sqlite:///{db_path}", future=True)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine, tables=[Org.__table__, User.__table__])

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()

    get_settings.cache_clear()

    yield session

    session.close()
    engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(scope="function")
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
def seed_data(db_session: Session):
    hq = Org(id=1, code="HQ", name="总部", parent_id=None, path="/1/", level=0)
    sh = Org(id=2, code="SH001", name="上海一店", parent_id=1, path="/1/2/", level=1)
    db_session.add_all([hq, sh])
    db_session.flush()

    admin_user = User(
        id=1,
        username="admin",
        password_hash=hash_password("123456"),
        real_name="管理员",
        role="admin",
        org_id=1,
        is_active=True,
    )
    zhang_user = User(
        id=2,
        username="zhangsan",
        password_hash=hash_password("123456"),
        real_name="张三",
        role="user",
        org_id=2,
        is_active=True,
    )
    db_session.add_all([admin_user, zhang_user])
    db_session.commit()


def test_list_users_admin(client: TestClient):
    """
    admin 列表用户（分页）。
    """
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "123456"})
    token = resp.json()["data"]["token"]

    resp = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    result = data["data"]
    assert result["total"] == 2
    assert len(result["items"]) == 2


def test_list_users_user_forbidden(client: TestClient):
    """
    user 访问列表 → 40300。
    """
    resp = client.post("/api/auth/login", json={"username": "zhangsan", "password": "123456"})
    token = resp.json()["data"]["token"]

    resp = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 40300


def test_create_user_admin(client: TestClient):
    """
    admin 新建用户（SQLite 不支持自增 id，跳过）。
    """
    pytest.skip("SQLite BigInteger 不自增，真实 PG 环境验证")


def test_update_user_admin(client: TestClient, db_session: Session):
    """
    admin 修改用户 real_name/role/is_active。
    """
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "123456"})
    token = resp.json()["data"]["token"]

    payload = {"real_name": "张三（更新）", "role": "admin"}
    resp = client.put("/api/users/2", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    user = data["data"]
    assert user["real_name"] == "张三（更新）"
    assert user["role"] == "admin"

    db_user = db_session.get(User, 2)
    assert db_user.real_name == "张三（更新）"


def test_change_password_admin_reset(client: TestClient, db_session: Session):
    """
    admin 重置他人密码。
    """
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "123456"})
    token = resp.json()["data"]["token"]

    payload = {"new_password": "newpass"}
    resp = client.put(
        "/api/users/2/password", json=payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0

    # 验证新密码可登录
    resp = client.post("/api/auth/login", json={"username": "zhangsan", "password": "newpass"})
    assert resp.json()["code"] == 0


def test_reset_password_to_default(client: TestClient):
    """
    §6.6 admin 一键重置密码为系统默认值 123qwe。
    """
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "123456"})
    token = resp.json()["data"]["token"]

    resp = client.post(
        "/api/users/2/reset-password", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["code"] == 0

    # 默认密码 123qwe 可登录
    resp = client.post("/api/auth/login", json={"username": "zhangsan", "password": "123qwe"})
    assert resp.json()["code"] == 0
    # 原密码失效
    resp = client.post("/api/auth/login", json={"username": "zhangsan", "password": "123456"})
    assert resp.json()["code"] != 0


def test_change_password_self(client: TestClient):
    """
    本人改密需校验旧密码。
    """
    resp = client.post("/api/auth/login", json={"username": "zhangsan", "password": "123456"})
    token = resp.json()["data"]["token"]

    # 旧密码错误 → 40101
    payload = {"old_password": "wrong", "new_password": "newpass"}
    resp = client.put(
        "/api/users/2/password", json=payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 40101

    # 旧密码正确
    payload = {"old_password": "123456", "new_password": "newpass"}
    resp = client.put(
        "/api/users/2/password", json=payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0


def test_delete_user_admin(client: TestClient, db_session: Session):
    """
    admin 软删除用户。
    """
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "123456"})
    token = resp.json()["data"]["token"]

    resp = client.delete("/api/users/2", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0

    db_user = db_session.get(User, 2)
    assert db_user.is_active is False
