# 任务看板 (BOARD)

> 开工先看这里。只修改/新增**标着自己代号**的行，不要动别人的行。
> 状态: `TODO`(待办) `DOING`(进行中) `REVIEW`(待评审) `BLOCKED`(阻塞) `DONE`(完成)

📌 **当前阶段**: W1 — 登录 + 机构树 ｜ **指令包**: [HANDOFF-W1.md](HANDOFF-W1.md)

## 进行中 / 待办

| ID | 负责 | 任务 | 状态 | 依赖 | 备注 |
|----|------|------|------|------|------|
| T-001 | ARCH | 搭建协作中枢(本目录) | DONE | - | BOARD/LOG/CONTRACTS 就绪 |
| T-002 | ARCH | 确认 W1 接口契约: 登录 + 机构树 | DONE | - | 已锁定，见 CONTRACTS §1-§4 |
| T-003 | BE | 实现 POST /auth/login + /auth/me + /auth/logout | DONE | T-004 | 见 CONTRACTS §1-§3，JWT+bcrypt；7 项 pytest 全过 |
| T-004 | BE | 建 10 张表 ORM + Alembic 迁移 + 种子数据 | REVIEW | ✅可开工 | 模型/迁移/种子已写；本机无 PG 未做 online 落库，见阻塞 B-001 |
| T-005 | BE | 实现 GET /orgs/tree (机构树, 物化路径) | DONE | T-004 | 契约 §4 ；admin 看下级/user 仅本机构，已覆盖测试 |
| T-006 | FE | 前端骨架: npm install + 路由 + Pinia + axios 封装 | REVIEW | ✅可开工 | 完成。依赖装好(含修 vue-tsc→2.x)，request.ts 带 token 注入+统一拆包裹，stores/router 就绪，build 通过 |
| T-007 | FE | 登录页 + 路由守卫 + token 管理 | REVIEW | T-006 | 完成(mock)。对接 §1-§3，守卫含未登录拦截/刷新恢复/角色拦截。待 BE T-003 切真实联调 |
| T-008 | FE | 主布局(侧边栏+顶栏) + 机构树展示组件 | REVIEW | T-007 | 完成(mock)。布局+按角色菜单+机构树展示，对接 §4。待 BE T-005 切真实联调 |

> 📌 BE 与 FE 可**并行开工**：FE 在 T-006/T-007 期间用 mock 数据（按 CONTRACTS 字段）即可，
> 不必等后端。待 BE 的 T-003/T-005 完成后切真实接口联调。

## 阻塞区 (BLOCKED — 需对方/人类处理)

| ID | 提出方 | 阻塞内容 | @谁 | 状态 |
|----|--------|----------|-----|------|
| B-001 | BE | 本机未启动 PostgreSQL(localhost:5432 不通)且无 docker，`alembic upgrade head` 未真实落库。代码侧 0001 离线 SQL 完整、ORM 元数据 10 表全注册、SQLite 端到端 7 项 pytest 全绿。请运维起 PG（`docker compose up -d` 即可，库名/账号沿用 .env.example），然后 `cd backend && venv\Scripts\python.exe -m alembic upgrade head` 验证 admin/123456 能登录 | @人类(运维) | OPEN |

## 契约变更申请 (FE/BE 提，ARCH 裁定)

| ID | 申请方 | 申请内容 | 状态 |
|----|--------|----------|------|
| - | - | 暂无 | - |

---
**最后更新**: 2026-05-29 18:41:56 by ARCH