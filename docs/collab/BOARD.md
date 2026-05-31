# 任务看板 (BOARD)

> 开工先看这里。只修改/新增**标着自己代号**的行，不要动别人的行。
> 状态: `TODO`(待办) `DOING`(进行中) `REVIEW`(待评审) `BLOCKED`(阻塞) `DONE`(完成)

📌 **当前阶段**: W2 — 机构CRUD + 用户管理 + 费用项字典 ｜ **指令包**: [HANDOFF-W2.md](HANDOFF-W2.md) ｜ W1/M1 ✅已完成

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
| T-009 | BE | 机构 CRUD: POST/PUT/DELETE /orgs + Logo 上传 | TODO | M1 | CONTRACTS §5；新建复制默认数据+物化路径回填；删校验无子机构/无用户 |
| T-010 | BE | 用户管理 CRUD + 改密码 + 软删除 | TODO | T-009 | CONTRACTS §6；列表分页/机构隔离/不返回 password_hash；require_admin 依赖 |
| T-011 | BE | 费用项字典 CRUD + 软删除 | DOING | M1 | CONTRACTS §7；金额字段字符串化两位小数；按 sort_order 排序 |
| T-012 | FE | 机构管理页: 树 + 新增/编辑/删除 + Logo 上传 | TODO | M1 | 对接 §5；复用 W1 机构树组件加操作按钮；先 mock 后联调 |
| T-013 | FE | 用户管理页: 列表 + 新增/编辑/重置密码/停用 | TODO | M1 | 对接 §6；分页表格+机构筛选+角色下拉；先 mock 后联调 |
| T-014 | FE | 费用项字典页: 列表 + 增删改 + 启停 | TODO | M1 | 对接 §7；表格内联编辑或弹窗；先 mock 后联调 |

> 📌 BE 与 FE 可**并行开工**：FE 在 T-006/T-007 期间用 mock 数据（按 CONTRACTS 字段）即可，
> 不必等后端。待 BE 的 T-003/T-005 完成后切真实接口联调。

## 阻塞区 (BLOCKED — 需对方/人类处理)

| ID | 提出方 | 阻塞内容 | @谁 | 状态 |
|----|--------|----------|-----|------|
| B-001 | BE | 本机未启动 PostgreSQL，`alembic upgrade head` 未真实落库 | @人类(运维) | ✅CLOSED 2026-05-31 22:22:35 — 人类已起 PG 15.18，迁移成功落库，admin/123456 可登录 |

## 契约变更申请 (FE/BE 提，ARCH 裁定)

| ID | 申请方 | 申请内容 | 状态 |
|----|--------|----------|------|
| - | - | 暂无 | - |

---
**最后更新**: 2026-05-31 22:44:04 by ARCH