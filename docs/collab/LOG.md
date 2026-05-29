# 工作流水日志 (LOG)

> **只追加，不修改历史**。每次有进展追加一行。格式：
> `YYYY-MM-DD HH:MM:SS | 代号 | 动作 | 关联ID | 改动/备注`
>
> 动作建议用：开始 / 完成 / 阻塞 / 解除阻塞 / 交接 / 评审 / 提问

---

2026-05-29 15:44:00 | ARCH | 完成 | T-001 | 搭建协作中枢 docs/collab/(README + BOARD + LOG + CONTRACTS)。下一步 T-002 写登录与机构树契约，写好后会在 BOARD 通知 FE/BE。
2026-05-29 17:28:00 | ARCH | 完成 | T-002 | 锁定 W1 契约：登录/me/logout/orgs.tree 字段逐条确认为 🔒LOCKED(CONTRACTS §1-§4)。已在 BOARD 放行 T-003~T-008，BE 与 FE 可并行开工(FE 先用 mock)。环境侧: Python3.11.9 已装, backend/venv 依赖就绪, 后端骨架 /health 验证通过。Playwright 浏览器内核推迟到 W4。
2026-05-29 18:35:00 | ARCH | 完成 | - | 产出 HANDOFF-W1.md（W1 阶段 FE/BE 指令包，可复制粘贴到对应会话）；BOARD 顶部加当前阶段指针；README 补全会话启动咒语(§六)与防"重头开始"纪律(§七)。FE/BE 现可独立并行开工。
2026-05-29 18:41:56 | ARCH | 规范 | - | 统一时间格式为 YYYY-MM-DD HH:MM:SS（精确到秒），已回溯修正 LOG 历史记录，并在 README 中固化此规范。
2026-05-29 18:45:00 | ARCH | 提醒 | - | @FE @BE: LOG 中时间格式已统一为 YYYY-MM-DD HH:MM:SS（精确到秒），你们后续追加日志时请遵守此格式。历史记录中只到天的条目（2026-05-29 无时分秒）由你们各自会话在下次开工时自行补全时分秒（估算即可，保持时序合理）。
2026-05-29 | FE | 开始 | T-006/T-007/T-008 | 接班 W1 前端三连：先 T-006 装依赖+搭路由/Pinia/axios 封装，再 T-007 登录页+守卫，再 T-008 主布局+机构树。后端未就绪，按 CONTRACTS §1-§4 字段先造 mock 开发，待 BE @FE 接口就绪后切真实请求联调。
2026-05-29 | BE | 开始 | T-004 | 接班开工。计划顺序 T-004→T-003→T-005。本条建 10 张表 ORM(SQLAlchemy 2.0 风格) + Alembic 首迁移 + 种子(总部 HQ + admin/123456，挂 HQ 下)。
2026-05-29 | BE | 完成 | T-004 | 10 张表 ORM 全部落地于 backend/app/models/*；Alembic 配 backend/alembic.ini + env.py(从 settings 读 DATABASE_URL)；迁移 0001(建表)/0002(种子: HQ org id=1 + admin/123456 + 默认费用项 3 条 + 默认模板 1 条)。0001 离线 SQL 已完整 emit 校验；ORM 元数据 10 表全注册成功。**未真实执行 alembic upgrade**：本机 5432 不通且无 docker，已开 B-001 求人类启 PG。
2026-05-29 | BE | 完成 | T-003 | 实现 /api/auth/login /me /logout，严格按 CONTRACTS §1-§3 字段；统一响应 {code,message,data} 由 main.py 全局 BizError handler 输出；错误码 40101(用户名/密码错)、40301(账号停用)、40100(未登录/Token失效) 全覆盖。JWT 用 jose, 密码哈希直接用 bcrypt 库(原 passlib 与 bcrypt 4.x 不兼容，已切换并更新 requirements)。
2026-05-29 | BE | 完成 | T-005 | 实现 GET /api/orgs/tree，admin 走 path LIKE 前缀拿本机构+所有下级，user 仅返回本机构；返回结构严格对齐 CONTRACTS §4(id/code/name/parent_id/level/logo_path/children)。tests/test_w1_smoke.py 7 项 pytest 全绿(用 SQLite 文件库做端到端冒烟，仅覆盖 W1 表，避开 JSONB)。
2026-05-29 | BE | 交接 | T-003/T-005 | @FE: 接口 POST /api/auth/login、POST /api/auth/logout、GET /api/auth/me、GET /api/orgs/tree 已就绪，字段与 CONTRACTS §1-§4 一致。**联调前提**：等 B-001 解除(人类起 PG 并跑 alembic upgrade head)；起 PG 后默认账号 admin / 123456。本机调试也可临时把 backend/.env 的 DATABASE_URL 改成 sqlite:///./dev.db 跑测试库。CORS 已读 settings.CORS_ORIGINS(默认 http://localhost:5173)。
2026-05-29 | FE | 完成 | T-006 | 前端骨架就位。npm install(246 pkg)；axios 封装 `frontend/src/api/request.ts`(token 注入拦截器 + 统一拆 {code,message,data} 包裹 + 40100/401 自动跳登录)；Pinia `stores/auth.ts`(token 持久化/login/logout/fetchMe，含 isAdmin/isSuperAdmin) 与 `stores/org.ts`(机构树+扁平化)；`router/index.ts` 全局守卫；TS 类型 `types/{api,user,org}.ts` 全部对齐 CONTRACTS。工具链修复：vue-tsc 1.8→2.x(原版与 TS5.9/Node23 不兼容导致 build 崩)。`npm run build` 通过、`vue-tsc --noEmit` 0 错、dev server 冒烟 OK。
2026-05-29 | FE | 完成 | T-007 | 登录页 `views/login/LoginView.vue`(表单校验+回车提交+redirect 跳转) + 路由守卫(未登录拦截带 redirect / 刷新用 token 调 fetchMe 恢复 / 角色 meta.roles 拦截) + token 管理。对接 §1-§3，当前走 mock(VITE_USE_MOCK=true)。演示账号 admin/123456、zhangsan/123456(user)、disabled(测停用 40301)。
2026-05-29 | FE | 完成 | T-008 | 主布局 `components/layout/`(AppLayout 侧边栏+顶栏+内容区；Sidebar 按角色过滤菜单，对应 08-feature 菜单结构，未开发页以"待开发"禁用占位；Header 含机构名+用户名+角色标签+注销) + 机构树展示 `views/orgs/OrgTree.vue`(el-tree 渲染+选中查看详情)，对接 §4 走 mock。另:工作台/404 占位页。@BE：FE 三条已完成待联调，你做完 T-003/T-005 在 LOG @FE，我把 VITE_USE_MOCK 改 false 切真实请求即可联调(vite 已代理 /api→:8000)。三条置 REVIEW 待 ARCH 评审。
