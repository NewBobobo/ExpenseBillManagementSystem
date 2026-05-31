# 接口契约对齐区 (CONTRACTS)

> **唯一事实来源**。FE 和 BE 都以本文件锁定的契约为准。
> 细节字段定义见 [05-api-spec.md](../05-api-spec.md)，本文件记录**对齐状态**与精确字段。
> 只有 **ARCH** 能修改本文件。FE/BE 要改契约 → 去 BOARD 开「契约变更申请」。

## 约定

- 基础路径 `/api`，JWT Bearer Token（Header: `Authorization: Bearer <token>`）。
- 统一响应包裹：`{ "code": 0, "message": "success", "data": <payload> }`，`code=0` 成功，非 0 为业务错误码。
- 分页响应 data：`{ "items": [...], "total": <int>, "page": <int>, "page_size": <int> }`。
- 状态: `🔒LOCKED`(已锁定可开发) `🟡DRAFT`(草拟中) `🔴CHANGING`(变更中勿用)

## W1 契约（登录 + 机构树）— 🔒 全部 LOCKED (2026-05-29)

### §1 POST /api/auth/login 🔒LOCKED

请求体：
```json
{ "username": "admin", "password": "123456" }
```
成功响应 data：
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "admin",
    "real_name": "管理员",
    "role": "admin",
    "org_id": 1,
    "org_name": "总部"
  }
}
```
错误码：`40101` 用户名或密码错误；`40301` 账号已停用。

### §2 POST /api/auth/logout 🔒LOCKED

请求头带 Token，无请求体。成功响应 `data: null`。
（后端可只做 200 返回，黑名单可选；前端清除本地 Token 即可。）

### §3 GET /api/auth/me 🔒LOCKED

请求头带 Token。成功响应 data 与登录的 `user` 对象同构。
未登录/Token 失效返回 `code=40100`。

### §4 GET /api/orgs/tree 🔒LOCKED

请求头带 Token。返回当前用户可见的机构树（管理员=本机构及下级，用户=本机构）。
成功响应 data（树形数组，children 递归）：
```json
[
  {
    "id": 1, "code": "HQ", "name": "总部",
    "parent_id": null, "level": 0,
    "logo_path": "/storage/logos/1_xxx.png",
    "children": [
      { "id": 3, "code": "SH001", "name": "上海一店",
        "parent_id": 1, "level": 1, "logo_path": null, "children": [] }
    ]
  }
]
```

> 字段类型锁定：id/parent_id/level 为整数，parent_id 顶级为 null；code/name 字符串；
> logo_path 可为 null；children 为数组（无子节点时空数组）。

## W2 契约（机构 CRUD + 用户管理 + 费用项字典）— 🔒 全部 LOCKED (2026-05-31)

### 通用约定（W2）

- **角色**：`role` 仅两值 `admin` / `user`。**`super_admin` 不是枚举值**，是派生判断：`role=="admin"` 且所在机构为顶级（`level==0`）。W2 不新增角色。
- **机构隔离（物化路径）**：沿用 W1 写法。取当前用户机构的 `path`（形如 `/1/3/`）：
  - `admin` → 可见 `WHERE orgs.path LIKE '<我的path>%'`（本机构 + 全部下级）。
  - `user` → 仅本机构自身。
  - 带 `org_id` 的表（users / expense_items）先算可见 org_id 集合再过滤；写操作须校验目标 org 落在可见 path 前缀内，否则 `40300`。
- **写操作权限**：机构/用户的增删改仅 `admin`；费用项增删改 `admin`。`user` 对三者均只读（费用项只读本机构，机构只读树，用户列表 user 不可访问→`40300`）。
- **错误码（W2 新增，沿用 W1 的 40100/40101/40301）**：

| code | 含义 |
|------|------|
| 40300 | 无权限 / 越权操作（角色不足，或操作非可见机构的数据）|
| 40400 | 资源不存在 |
| 40900 | 唯一冲突（机构 code 重复 / 用户名重复）|
| 40901 | 删除受阻（机构下存在子机构或用户，详见 §7）|
| 42200 | 参数校验失败（缺字段 / 非法值）|

> **路径说明**：W1 已锁 `GET /api/orgs/tree` 为树形读取；W2 的机构 CRUD 走 `/api/orgs`（扁平），二者并存。

### §5 机构 CRUD 🔒LOCKED

**§5.1 POST /api/orgs** — 新建子机构（admin）
请求体：
```json
{ "parent_id": 1, "code": "SH001", "name": "上海一店" }
```
- `parent_id` 必填且须在调用者可见范围内；`code` 全局唯一；`name` 必填。
- 后端职责：① flush 取 id 后回填 `path = parent.path + id + "/"`、`level = parent.level + 1`；② **同事务复制默认数据**：把 `system_defaults` 中 `kind='expense_item'` / `kind='template'` 的记录按 payload 写入新机构。
- 成功 data：新机构对象 `{id, code, name, parent_id, path, level, logo_path, created_at}`。
- 错误：`40900` code 重复；`40300` 越权；`42200` 缺字段。

**§5.2 PUT /api/orgs/{id}** — 改 name / code（admin）
请求体（字段均可选，至少一项）：`{ "name": "上海旗舰店", "code": "SH001" }`
- 不允许改 parent_id（W2 不做移动机构）。成功 data：更新后的机构对象。

**§5.3 DELETE /api/orgs/{id}** — 删机构（admin）
- 前置校验：**无子机构、无用户**才可删（费用项 CASCADE 自动删，不阻断）。
- 受阻返回 `40901`，message 说明原因。成功 data：null。

**§5.4 PUT /api/orgs/{id}/logo** — 上传/更换 Logo（admin）
- `multipart/form-data`，字段名 `file`（png/jpg，≤2MB）。
- 后端存到 STORAGE_PATH/logos/，回写 `logo_path`。成功 data：`{ "logo_path": "/storage/logos/xxx.png" }`。

### §6 用户管理 🔒LOCKED

**§6.1 GET /api/users** — 列表（admin）
- query：`org_id`(可选,默认全部可见)、`keyword`(可选,匹配 username/real_name)、`page`(默认1)、`page_size`(默认20)。
- `user` 角色访问 → `40300`。
- 成功 data（分页）：`{ items: [{id, username, real_name, role, org_id, org_name, is_active, created_at}], total, page, page_size }`。**不返回 password_hash**。

**§6.2 POST /api/users** — 新建（admin）
```json
{ "username": "zhangsan", "password": "123456", "real_name": "张三", "org_id": 3, "role": "user" }
```
- `username` 全局唯一；`org_id` 须可见；`role` ∈ {admin,user}。成功 data：用户对象（同 §6.1 单条，无 password_hash）。
- 错误：`40900` 用户名重复；`40300` 越权；`42200` 校验失败。

**§6.3 PUT /api/users/{id}** — 改 real_name / role / is_active（admin）
请求体（均可选）：`{ "real_name": "张三丰", "role": "admin", "is_active": true }`
- 不允许改 username / org_id。成功 data：更新后用户对象。

**§6.4 PUT /api/users/{id}/password** — 修改密码 🔄变更(2026-06-01)
- admin 改他人：`{ "new_password": "xxx" }`；本人改密：`{ "old_password": "xxx", "new_password": "yyy" }`（须校验旧密码）。
- 成功 data：null。错误：`40101` 旧密码错；`40300` 越权。
- 前端按钮文案为「修改密码」（管理员手动输入新密码）。

**§6.5 DELETE /api/users/{id}** — 软删除（admin）
- 实为设 `is_active=false`（不物理删，保留单据外键）。成功 data：null。

**§6.6 POST /api/users/{id}/reset-password** — 一键重置密码（admin）🆕新增(2026-06-01)
- 无请求体。把目标用户密码重置为系统默认值 `123qwe`（常量，后端 settings.DEFAULT_RESET_PASSWORD 可配）。
- 权限：仅 admin，且目标用户须在可见机构范围内（否则 `40300`）。
- 成功 data：null。错误：`40400` 用户不存在；`40300` 越权。
- 前端按钮文案为「重置密码」，点击后二次确认，无需输入。

### §7 费用项字典 🔒LOCKED

**§7.1 GET /api/expense-items** — 列表
- query：`org_id`(可选)、`is_active`(可选 true/false,不传则全部)。`user` 仅能查本机构。
- 成功 data（数组,按 sort_order 升序）：`[{id, org_id, name, default_qty, unit_price, unit, is_active, sort_order}]`。
- 金额字段 `default_qty/unit_price` 为字符串化的两位小数（NUMERIC，避免 JS 浮点失真），如 `"100.00"`。

**§7.2 POST /api/expense-items** — 新增（admin）
```json
{ "org_id": 3, "name": "差旅费", "default_qty": "1.00", "unit_price": "500.00", "unit": "次", "sort_order": 0 }
```
- `unit` 可为 null；`org_id` 须可见。成功 data：费用项对象。

**§7.3 PUT /api/expense-items/{id}** — 修改（admin）
- 可改 name/default_qty/unit_price/unit/is_active/sort_order（均可选）。成功 data：更新后对象。

**§7.4 DELETE /api/expense-items/{id}** — 硬删除（admin）🔄变更(2026-06-01)
- **物理删除**该费用项字典记录（原为软删 is_active=false，应用户要求改为真删除）。
- 费用项字典是「模板/可选项」，单据明细(ReportItem)为下单时的值快照、不引用 expense_items，故删除字典不影响已开单据。
- 「停用」语义由 §7.3 PUT 改 `is_active=false` 承担；前端列表默认仅显示启用项。
- 成功 data：null。错误：`40400` 不存在；`40300` 越权。

## 变更历史

| 日期 | 接口 | 变更 | 申请方 | 裁定 |
|------|------|------|--------|------|
| 2026-05-29 15:44:00 | - | 初始化契约区 | ARCH | - |
| 2026-05-29 17:28:00 | W1 全部 | 字段逐条锁定，置 🔒LOCKED，放行 T-003~T-006 | ARCH | 通过 |
| 2026-05-31 22:35:53 | W2 全部 | 锁定机构CRUD(§5)/用户管理(§6)/费用项(§7)契约，置 🔒LOCKED，放行 W2 任务 | ARCH | 通过 |
| 2026-06-01 00:10:00 | §7.4 | 费用项删除由软删改**硬删除**(用户要求) | 人类 | ARCH 采纳 |
| 2026-06-01 00:10:00 | §6.4/§6.6 | §6.4 改密码按钮文案改「修改密码」；新增 §6.6 一键重置密码(默认123qwe) | 人类 | ARCH 采纳 |

---
**最后更新**: 2026-06-01 00:10:00 by ARCH
