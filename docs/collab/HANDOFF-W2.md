# W2 阶段交接指令包 (HANDOFF)

> **用途**：复制粘贴用。把下面整段贴进对应会话即可让 FE/BE 开工。
> **维护人**：ARCH。
> **当前阶段**：W2（机构 CRUD + 用户管理 + 费用项字典）— 契约 §5-§7 已锁定，FE/BE 可并行开工。
> **前置**：W1/M1 已完成（登录 + 机构树前后端联调通过）。

---

## 🧭 W2 背景（FE/BE 都先看）

W1 搭好了登录认证和机构树只读展示。W2 把三块后台基础数据做成可增删改：
1. **机构管理**：在 W1 只读树的基础上，加新建子机构/改名/删除/传 Logo。
2. **用户管理**：列表 + 新建/编辑/重置密码/停用，带机构隔离和分页。
3. **费用项字典**：每个机构维护自己的费用项（后续填报单据时下拉用）。

三块共用同一套模式：**物化路径机构隔离** + **admin 可写 / user 只读** + **列表+表单**。
契约见 CONTRACTS §5（机构）、§6（用户）、§7（费用项），错误码见"通用约定（W2）"。

---

## 📦 指令包 A — 给【后端会话 BE / AwerCoder】

> 选中下面整段，复制，粘贴到后端会话：

```
你是本项目后端开发会话，代号 BE / AwerCoder。

【接班】先依次读：
- docs/collab/README.md（协作铁律 + 启动咒语第六节）
- docs/collab/BOARD.md（找标 BE 的 T-009/T-010/T-011）
- docs/collab/CONTRACTS.md（§5 机构 / §6 用户 / §7 费用项 + "通用约定（W2）"错误码，已锁定）
- docs/collab/LOG.md 末尾 10 行（看 ARCH 交接与 W1 已落地的范式）

【环境】backend/venv（Python 3.11.9）依赖已装好。本机 PostgreSQL 已就绪
（127.0.0.1:5432，库 expense_system，用户 admin），backend/.env 已配好可直接用。
迁移已到 head（10 表 + 种子）。激活：backend\venv\Scripts\activate

【复用 W1 已有范式】（别重造轮子，照着写）
- 鉴权依赖：app/api/deps.py 的 get_current_user。建议在此新增 require_admin 依赖
  （current.role=="admin" 否则抛 BizError(40300)）。
- 机构隔离：参考 app/api/orgs.py 里 path LIKE 前缀过滤的写法（admin 看本机构+下级，user 仅本机构）。
- 统一响应/错误：app/core/response.py 的 ok() 与 BizError(code,message)，HTTP 恒 200。

【本阶段任务】按 BOARD 标 BE 的三条，建议顺序 T-011→T-009→T-010（费用项最简单先练手）：
1. T-011 费用项字典 CRUD（CONTRACTS §7）：GET/POST/PUT/DELETE /api/expense-items。
   - 金额 default_qty/unit_price 用 NUMERIC，序列化成两位小数字符串（如 "100.00"）避免 JS 浮点失真。
   - 列表按 sort_order 升序；DELETE 是软删除（is_active=false）。
2. T-009 机构 CRUD（CONTRACTS §5）：POST/PUT/DELETE /api/orgs + PUT /api/orgs/{id}/logo。
   - 新建：flush 取 id 后回填 path=parent.path+id+"/"、level=parent.level+1；
     同事务复制默认数据（system_defaults 里 kind='expense_item'/'template' 按 payload 写入新机构）。
   - 删除：前置校验无子机构、无用户才允许（费用项是 CASCADE 自动删，不算阻碍），受阻返回 40901。
   - Logo：multipart/form-data 字段名 file，存 STORAGE_PATH/logos/，回写 logo_path。
3. T-010 用户管理（CONTRACTS §6）：GET（分页）/POST/PUT/DELETE /api/users + PUT /api/users/{id}/password。
   - 列表分页 {items,total,page,page_size}，绝不返回 password_hash；user 角色访问列表→40300。
   - 改密码：admin 重置只需 new_password；本人改密需校验 old_password（错→40101）。
   - DELETE 是软删除（is_active=false），保留单据外键。

【纪律】只改 backend/** 和 BOARD/LOG 里属于 BE 的行。接口字段以 CONTRACTS 为唯一准则，
要改契约 → 去 BOARD 开"契约变更申请"@ARCH，不要自己动 CONTRACTS。
每完成一条在 LOG 追加一行（时间格式 YYYY-MM-DD HH:MM:SS）、更新 BOARD 状态。
每组接口写 pytest（沿用 W1 的 SQLite 冒烟方式即可）。
做完后在 LOG @FE 说明哪些接口已就绪可联调。
```

---

## 📦 指令包 B — 给【前端会话 FE / CodeWhy】

> 选中下面整段，复制，粘贴到前端会话：

```
你是本项目前端开发会话，代号 FE / CodeWhy。

【接班】先依次读：
- docs/collab/README.md（协作铁律 + 启动咒语第六节）
- docs/collab/BOARD.md（找标 FE 的 T-012/T-013/T-014）
- docs/collab/CONTRACTS.md（§5 机构 / §6 用户 / §7 费用项 + "通用约定（W2）"错误码，已锁定）
- docs/collab/LOG.md 末尾 10 行（看 BE 接口进度）

【环境】frontend/ 依赖已装好（W1 已 npm install）。dev server：npm run dev（端口 5173）。
.env.development 的 VITE_USE_MOCK 现在是 false（真实联调）。BE 接口若还没好，
你可临时把它改回 true 用 mock 开发，联调时再改回 false。vite 已代理 /api→:8000。

【复用 W1 已有范式】（别重造轮子）
- 请求封装 src/api/request.ts（token 注入 + 拆 {code,message,data} + 40100 跳登录）。
  注意：W2 新增错误码 40300/40400/40900/40901/42200，统一在拦截器里 ElMessage 提示即可。
- 状态 stores/auth.ts（含 isAdmin/role）、stores/org.ts（机构树）。
- 主布局 components/layout/（Sidebar 按角色过滤菜单）。W2 三个页面挂到侧边栏对应菜单项，
  user 角色看不到管理类入口（沿用 Sidebar 角色过滤）。

【本阶段任务】按 BOARD 标 FE 的三条，建议顺序 T-014→T-013→T-012：
1. T-014 费用项字典页（CONTRACTS §7）：表格列出本机构费用项，新增/编辑（弹窗或行内）、启停、软删。
   金额按字符串展示与提交（"100.00"）。
2. T-013 用户管理页（CONTRACTS §6）：分页表格（username/real_name/role/机构/状态），
   机构筛选 + 关键字搜索，新增/编辑用户、重置密码弹窗、停用。绝不显示密码。
3. T-012 机构管理页（CONTRACTS §5）：在 W1 机构树基础上加操作——新增子机构、改名、删除、上传 Logo。
   删除受阻（40901）要给清晰提示。新建成功后刷新树。

【纪律】只改 frontend/** 和 BOARD/LOG 里属于 FE 的行。接口字段以 CONTRACTS 为唯一准则，
要改契约 → 去 BOARD 开"契约变更申请"@ARCH。
每完成一条在 LOG 追加一行（时间格式 YYYY-MM-DD HH:MM:SS）、更新 BOARD 状态。
每条做完跑 npm run build 确认 0 错。BE 接口就绪后切真实联调，联调通过在 LOG 记一笔。
```

---

## ✅ W2 完成标准（M2 前半程）

- 后端 T-009/T-010/T-011 三组 CRUD 接口实现，字段/错误码对齐 CONTRACTS §5-§7，pytest 覆盖。
- 前端 T-012/T-013/T-014 三个管理页可用，切真实接口联调通过。
- 浏览器实测：admin 能新建机构（并自动带出默认费用项）、建用户、维护费用项；user 登录看不到管理入口或只读。
- M2 完整收口还需 W3 的模板/公章，W2 只交付"基础数据可维护"。
