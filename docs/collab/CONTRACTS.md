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

## 变更历史

| 日期 | 接口 | 变更 | 申请方 | 裁定 |
|------|------|------|--------|------|
| 2026-05-29 15:44:00 | - | 初始化契约区 | ARCH | - |
| 2026-05-29 17:28:00 | W1 全部 | 字段逐条锁定，置 🔒LOCKED，放行 T-003~T-006 | ARCH | 通过 |

---
**最后更新**: 2026-05-29 18:41:56 by ARCH
