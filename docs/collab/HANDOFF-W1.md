# W1 阶段交接指令包 (HANDOFF)

> **用途**：复制粘贴用。你把下面整段贴进对应会话即可让 FE/BE 开工。
> **维护人**：ARCH。每个新阶段(W2/W3...)我会更新或新增 HANDOFF-Wx.md。
> **当前阶段**：W1（登录 + 机构树）— 契约已锁定，FE/BE 可并行开工。

---

## 📦 指令包 A — 给【后端会话 BE / AwerCoder】

> 选中下面整段(从 ``` 之间)，复制，粘贴到后端会话首条消息：

```
你是本项目后端开发会话，代号 BE / AwerCoder。

【开工】先依次读这几个文件了解协作纪律和任务：
- docs/collab/README.md（协作铁律 + 你的启动咒语在第六节）
- docs/collab/BOARD.md（找标 BE 的任务）
- docs/collab/CONTRACTS.md（接口字段，已锁定）
- docs/collab/LOG.md 末尾几行（看架构师交接了什么）
- docs/03-database-design.md（10 张表结构）

【环境】后端虚拟环境已就绪：backend/venv（Python 3.11.9，依赖已装好）。
Windows 下激活：backend\venv\Scripts\activate

【本阶段你的任务】按 BOARD 上标 BE 的三条，建议顺序：
1. T-004：建 10 张表的 SQLAlchemy ORM 模型 + Alembic 迁移 + 种子数据
   （含一个初始管理员 admin，挂在顶级机构"总部"下）。
2. T-003：实现 POST /api/auth/login、GET /api/auth/me、POST /api/auth/logout
   （JWT + bcrypt，严格按 CONTRACTS §1-§3 的字段和错误码）。
3. T-005：实现 GET /api/orgs/tree（物化路径，按 CONTRACTS §4 返回树形结构）。

【纪律】只改 backend/** 和 BOARD/LOG 里属于 BE 的行；接口字段以 CONTRACTS 为唯一
准则，要改契约就去 BOARD 开"契约变更申请"@ARCH，不要自己改 CONTRACTS。
每完成一条就在 LOG 追加一行（时间格式 YYYY-MM-DD HH:MM:SS）、更新 BOARD 状态。
做完 T-003/T-005 后在 LOG 里 @FE 说明接口已就绪可联调。
```

---

## 📦 指令包 B — 给【前端会话 FE / CodeWhy】

> 选中下面整段，复制，粘贴到前端会话首条消息：

```
你是本项目前端开发会话，代号 FE / CodeWhy。

【开工】先依次读这几个文件：
- docs/collab/README.md（协作铁律 + 你的启动咒语在第六节）
- docs/collab/BOARD.md（找标 FE 的任务）
- docs/collab/CONTRACTS.md（接口字段，已锁定，照此对接/造 mock）
- docs/collab/LOG.md 末尾几行
- docs/10-folder-structure.md（前端目录结构）

【现状】frontend/ 已有骨架文件（package.json、vite.config.ts、main.ts、App.vue），
但还没 npm install。

【本阶段你的任务】按 BOARD 上标 FE 的三条，顺序：
1. T-006：npm install 装依赖，搭好路由(vue-router)、状态(pinia)、
   axios 封装(api/request.ts，带 token 注入拦截器和统一响应 {code,message,data} 处理)。
2. T-007：登录页 + 路由守卫 + token 管理，对接 CONTRACTS §1-§3。
3. T-008：主布局(侧边栏+顶栏) + 机构树展示组件，对接 CONTRACTS §4。

【可并行】后端接口可能还没好——你先按 CONTRACTS 里的字段造 mock 数据开发，
不用等后端。等 BE 在 LOG 里 @FE 说接口就绪后，再把 mock 切成真实请求联调。

【纪律】只改 frontend/** 和 BOARD/LOG 里属于 FE 的行；接口字段以 CONTRACTS 为准，
要改去 BOARD 开"契约变更申请"@ARCH。每完成一条就在 LOG 追加一行（时间格式 YYYY-MM-DD HH:MM:SS）、
更新 BOARD 状态。
```

---

## 🔁 会话上下文满了怎么办

如果某个会话上下文将满，**先让它完成"收工三件事"**(写 LOG / 更 BOARD / 留交接说明)，
再开新会话，把对应的"启动咒语"贴过去：

- ARCH 启动咒语 → 见 [README §六](README.md#六会话启动咒语上下文满了重开必用)
- FE/BE 启动咒语 → 同上

新会话 3 分钟内就能从 BOARD/LOG/CONTRACTS 恢复到"我是谁、做到哪、下一步"。

---

## ✅ W1 完成判定（M1 里程碑）

W1 完工的标志(由 ARCH 评审):
- BE: 10 张表迁移成功、初始 admin 可登录、`/auth/login` `/auth/me` `/orgs/tree` 三个接口符合 CONTRACTS。
- FE: 登录页能跳转、token 持久化、路由守卫生效、主布局加机构树正常渲染（可对接真实接口）。
- 全员: 在浏览器(Edge)用 admin 登录后能看到机构树。

达成后我会在 BOARD 标 M1 DONE，并发布 W2 的 HANDOFF-W2.md。

---
**最后更新**: 2026-05-29 18:45:00 by ARCH
