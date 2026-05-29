# API 接口文档

## 基础信息

- 基础路径:`/api`
- 认证方式:JWT Bearer Token(Header: `Authorization: Bearer <token>`)
- 响应格式:JSON
- 分页参数:`page`(页码,从1开始)、`page_size`(每页条数,默认20)

## 通用响应结构

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

错误响应:
```json
{
  "code": 40001,
  "message": "权限不足",
  "data": null
}
```

---

## 1. 认证模块

### POST /api/auth/login

登录获取令牌。

请求:
```json
{
  "username": "admin",
  "password": "123456"
}
```

响应:
```json
{
  "token": "eyJ...",
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

### POST /api/auth/logout

注销(前端清除 token 即可,后端可选黑名单)。

### GET /api/auth/me

获取当前用户信息。

---

## 2. 机构管理

### GET /api/orgs

获取当前用户可见的机构树。管理员返回本机构及所有下级,用户只返回本机构。

### POST /api/orgs

新建子机构(仅管理员)。自动复制系统默认费用字典和模板。

请求:
```json
{
  "parent_id": 1,
  "code": "SH001",
  "name": "上海一店"
}
```

### PUT /api/orgs/{id}

修改机构信息(名称、编号、logo)。

### DELETE /api/orgs/{id}

删除机构(需无子机构、无用户、无单据)。

### PATCH /api/orgs/{id}/logo

上传/更换机构 Logo。Content-Type: multipart/form-data。

---

## 3. 用户管理

### GET /api/users

查询用户列表。管理员可查本机构及下级,用户只能查本机构。

参数:`org_id`(可选)、`page`、`page_size`

### POST /api/users

新建用户(仅管理员)。

请求:
```json
{
  "username": "zhangsan",
  "password": "初始密码",
  "real_name": "张三",
  "org_id": 3,
  "role": "user"
}
```

### PUT /api/users/{id}

修改用户信息(姓名、角色、是否启用)。

### DELETE /api/users/{id}

删除用户(软删除,设 is_active=false)。

### PUT /api/users/{id}/password

重置密码(管理员)或修改密码(本人)。

---

## 4. 费用项字典

### GET /api/expense-items

查询本机构的费用项列表。

参数:`is_active`(可选,筛选启用/停用)

### POST /api/expense-items

新增费用项。

请求:
```json
{
  "name": "办公用品",
  "default_qty": 1,
  "unit_price": 50.00,
  "unit": "个"
}
```

### PUT /api/expense-items/{id}

修改费用项。

### DELETE /api/expense-items/{id}

删除费用项(软删除,设 is_active=false)。

---

## 5. 公章管理

### GET /api/seals

查询本机构的公章列表。

### POST /api/seals

上传公章图片。Content-Type: multipart/form-data。

请求字段:`name`(公章名称)、`image`(图片文件)、`is_default`(是否默认)

### PUT /api/seals/{id}

修改公章信息(名称、是否默认)。

### DELETE /api/seals/{id}

删除公章。

---

## 6. 模板管理

### GET /api/templates

查询本机构的模板列表。

### POST /api/templates

创建模板或导入 XML 文件。

请求(JSON 方式):
```json
{
  "name": "标准版",
  "xml_content": "<?xml ...>...</template>",
  "is_default": true
}
```

请求(文件导入):Content-Type: multipart/form-data,字段 `file`(XML 文件)

### PUT /api/templates/{id}

修改模板(名称、XML 内容、是否默认)。

### DELETE /api/templates/{id}

删除模板(非默认模板才可删)。

### GET /api/templates/{id}/xml

导出模板 XML 文件(返回文件下载)。

---

## 7. 单据管理

### GET /api/reports

查询本机构的单据列表。

参数:`date_from`、`date_to`、`keyword`、`page`、`page_size`

### POST /api/reports

新建单据。自动生成单号,自动计算合计金额。

请求:
```json
{
  "report_date": "2026-05-29",
  "recipient": "XX供应商",
  "template_id": 1,
  "seal_id": 1,
  "remark": "",
  "items": [
    { "name": "办公用品", "qty": 2, "unit_price": 50.00 },
    { "name": "水电费", "qty": 1, "unit_price": 300.00 }
  ]
}
```

### GET /api/reports/{id}

获取单据详情(含明细)。

### PUT /api/reports/{id}

修改单据(需有修改权限,自动写入修改日志)。

### DELETE /api/reports/{id}

删除单据(仅管理员)。

### GET /api/reports/{id}/logs

查询单据修改日志。

---

## 8. 导出

### GET /api/reports/{id}/export

导出单据文件。

参数:
- `format`:pdf(默认) | excel
- `template_id`:可选,指定使用的模板(默认用单据关联的模板)

返回:文件流(Content-Type: application/pdf 或 application/vnd.openxmlformats...)

---

## 9. 系统默认配置(超级管理员)

### GET /api/system/defaults

查询系统默认费用项和模板。

### PUT /api/system/defaults

修改系统默认配置(新建机构时复制的初始数据)。
