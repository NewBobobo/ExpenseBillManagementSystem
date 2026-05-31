# 任务看板 (BOARD)

> 开工先看这里。只修改/新增**标着自己代号**的行，不要动别人的行。
> 状态: `TODO`(待办) `DOING`(进行中) `REVIEW`(待评审) `BLOCKED`(阻塞) `DONE`(完成)

📌 **当前阶段**: ✅ W2 已收口(机构CRUD+用户管理+费用项字典，含人类反馈修复) ｜ 下一步 W3 规划(模板系统+公章) ｜ W1/M1 ✅

## 进行中 / 待办

| ID | 负责 | 任务 | 状态 | 依赖 | 备注 |
|----|------|------|------|------|------|
| T-001 | ARCH | 搭建协作中枢(本目录) | DONE | - | BOARD/LOG/CONTRACTS 就绪 |
| T-002 | ARCH | 确认 W1 接口契约: 登录 + 机构树 | DONE | - | 已锁定，见 CONTRACTS §1-§4 |
| T-003 | BE | 实现 POST /auth/login + /auth/me + /auth/logout | DONE | T-004 | 见 CONTRACTS §1-§3，JWT+bcrypt；7 项 pytest 全过；ARCH 集成验证全过 |
| T-004 | BE | 建 10 张表 ORM + Alembic 迁移 + 种子数据 | DONE | ✅可开工 | 已真实落库 PG(alembic upgrade head)。ARCH 修了 env.py 的 %40→%% configparser 转义 bug |
| T-005 | BE | 实现 GET /orgs/tree (机构树, 物化路径) | DONE | T-004 | 契约 §4 ；admin 看下级/user 仅本机构；ARCH 集成验证返回真实数据 |
| T-006 | FE | 前端骨架: npm install + 路由 + Pinia + axios 封装 | DONE | ✅可开工 | 依赖装好(含修 vue-tsc→2.x)，request.ts 带 token 注入+统一拆包裹，stores/router 就绪，build 通过 |
| T-007 | FE | 登录页 + 路由守卫 + token 管理 | DONE | T-006 | 对接 §1-§3，守卫含未登录拦截/刷新恢复/角色拦截。已切真实接口联调通过 |
| T-008 | FE | 主布局(侧边栏+顶栏) + 机构树展示组件 | DONE | T-007 | 布局+按角色菜单+机构树展示，对接 §4。已切真实接口联调通过 |
| T-009 | BE | 机构 CRUD: POST/PUT/DELETE /orgs + Logo 上传 | DONE | M1 | CONTRACTS §5；新建复制默认数据+物化路径回填；删校验无子机构/无用户；5 项 pytest 通过 |
| T-010 | BE | 用户管理 CRUD + 改密码 + 软删除 | DONE | T-009 | CONTRACTS §6；列表分页/机构隔离/不返回 password_hash；require_admin 依赖；6 项 pytest 通过 |
| T-011 | BE | 费用项字典 CRUD + 软删除 | DONE | M1 | CONTRACTS §7；金额字段字符串化两位小数；按 sort_order 排序；6 项 pytest 通过 |
| T-012 | FE | 机构管理页: 树 + 新增/编辑/删除 + Logo 上传 | DONE | M1 | 对接 §5。已切真实接口，ARCH 集成验证机构CRUD全过(新建复制默认数据/40900/40901) |
| T-013 | FE | 用户管理页: 列表 + 新增/编辑/重置密码/停用 | DONE | M1 | 对接 §6。已切真实接口，ARCH 集成验证用户CRUD全过(分页/重置密码/软删) |
| T-014 | FE | 费用项字典页: 列表 + 增删改 + 启停 | DONE | M1 | 对接 §7。已切真实接口，ARCH 集成验证费用项CRUD全过(金额字符串/软删) |

> 📌 BE 与 FE 可**并行开工**：FE 在 T-006/T-007 期间用 mock 数据（按 CONTRACTS 字段）即可，
> 不必等后端。待 BE 的 T-003/T-005 完成后切真实接口联调。

## 阻塞区 (BLOCKED — 需对方/人类处理)

| ID | 提出方 | 阻塞内容 | @谁 | 状态 |
|----|--------|----------|-----|------|
| B-001 | BE | 本机未启动 PostgreSQL，`alembic upgrade head` 未真实落库 | @人类(运维) | ✅CLOSED 2026-05-31 22:22:35 — 人类已起 PG 15.18，迁移成功落库，admin/123456 可登录 |
| B-002 | ARCH | **T-009 新建机构 500 错误**：`backend/app/api/orgs.py:161` 复制默认模板时给 `Template(...)` 传了 `is_active=`，但 Template 模型无此字段（实际字段是 `is_default`，见 models/template.py:21）。system_defaults 的 template payload 也是 `is_default`。**修复**：把第161行 `is_active=tpl_data.get("is_active", True)` 改为 `is_default=tpl_data.get("is_default", False)`。改后重启 uvicorn，POST /api/orgs 应能新建并复制默认数据。BE 的 pytest 未覆盖到此路径（skip 了自增 id 用例），建议补一条新建机构的真实 PG 测试。 | @BE | ✅CLOSED 2026-05-31 23:55 — BE 已修复 orgs.py:161 字段名；ARCH 重启后端 19/19 集成验证通过 |

## 待 ARCH/人类决策

| ID | 提出方 | 内容 | 状态 |
|----|--------|------|------|
| D-001 | ARCH | **初始 HQ 机构无费用项/模板**：0002 种子只把默认数据写进 system_defaults，未给 HQ 复制。 | ✅DONE 2026-05-31 23:41 — 人类决策A。新增迁移 0003_seed_hq_defaults(从 system_defaults 复制给 HQ，幂等)，已 upgrade，HQ 现有3费用项+1模板 |

## 契约变更申请 (FE/BE 提，ARCH 裁定)

| ID | 申请方 | 申请内容 | 状态 |
|----|--------|----------|------|
| - | - | 暂无 | - |

---
**最后更新**: 2026-06-01 00:40:36 by ARCH