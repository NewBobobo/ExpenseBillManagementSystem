# 数据库核心表设计

## 物化路径说明

机构层级关系使用物化路径(materialized path)实现,`path` 字段存储从根到当前节点的 ID 链。
查询"某机构及其所有下级"只需 `WHERE path LIKE '/1/2/%'`,索引友好,性能优于递归查询。

## 表结构

### orgs — 机构树

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PK | 主键 |
| parent_id | BIGINT FK(orgs.id) | 上级机构,顶级为 NULL |
| code | VARCHAR(32) UNIQUE | 机构编号,管理员可改,用于单号前缀 |
| name | VARCHAR(128) | 机构名称 |
| path | VARCHAR(512) | 物化路径,如 `/1/3/7/` |
| level | SMALLINT | 层级深度,根=0 |
| logo_path | VARCHAR(512) | Logo 文件路径 |
| created_at | TIMESTAMP | 创建时间 |

### users — 用户

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PK | 主键 |
| username | VARCHAR(64) UNIQUE | 登录账号 |
| password_hash | VARCHAR(256) | bcrypt 哈希 |
| real_name | VARCHAR(64) | 真实姓名 |
| org_id | BIGINT FK(orgs.id) | 归属机构(唯一) |
| role | VARCHAR(16) | admin / user |
| is_active | BOOLEAN | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |

### expense_items — 费用项字典

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PK | 主键 |
| org_id | BIGINT FK(orgs.id) | 所属机构 |
| name | VARCHAR(128) | 费用名称 |
| default_qty | NUMERIC(12,2) | 默认数量,默认 1 |
| unit_price | NUMERIC(12,2) | 默认单价 |
| unit | VARCHAR(16) | 单位(个/次/月等) |
| is_active | BOOLEAN | 是否启用 |
| sort_order | INT | 排序权重 |

### seals — 公章

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PK | 主键 |
| org_id | BIGINT FK(orgs.id) | 所属机构 |
| name | VARCHAR(64) | 公章名称 |
| image_path | VARCHAR(512) | 图片文件路径 |
| is_default | BOOLEAN | 是否默认章 |

### templates — 打印模板

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PK | 主键 |
| org_id | BIGINT FK(orgs.id) | 所属机构 |
| name | VARCHAR(64) | 模板名称 |
| xml_content | TEXT | XML 模板内容 |
| is_default | BOOLEAN | 是否默认模板 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### reports — 单据主表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PK | 主键 |
| org_id | BIGINT FK(orgs.id) | 所属机构 |
| code | VARCHAR(32) UNIQUE | 单号:机构编号-YYMMDD-流水号 |
| report_date | DATE | 单据日期 |
| recipient | VARCHAR(128) | 收单据方 |
| reporter_id | BIGINT FK(users.id) | 填报人 |
| template_id | BIGINT FK(templates.id) | 使用的模板 |
| seal_id | BIGINT FK(seals.id) | 使用的公章 |
| total_amount | NUMERIC(14,2) | 合计金额 |
| remark | TEXT | 备注 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### report_items — 单据明细

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PK | 主键 |
| report_id | BIGINT FK(reports.id) | 所属单据 |
| seq | INT | 序号 |
| name | VARCHAR(128) | 费用名称 |
| qty | NUMERIC(12,2) | 数量 |
| unit_price | NUMERIC(12,2) | 单价 |
| amount | NUMERIC(14,2) | 金额(qty × unit_price) |
| remark | VARCHAR(255) | 备注 |

### report_logs — 修改日志

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PK | 主键 |
| report_id | BIGINT FK(reports.id) | 所属单据 |
| user_id | BIGINT FK(users.id) | 操作人 |
| action | VARCHAR(16) | 操作类型:create/update/delete |
| diff | JSONB | 变更前后对比 |
| created_at | TIMESTAMP | 操作时间 |

### report_seq — 单号流水

| 字段 | 类型 | 说明 |
|------|------|------|
| org_id | BIGINT PK | 机构 ID |
| seq_date | DATE PK | 日期 |
| last_seq | INT | 当日最后流水号 |

### system_defaults — 系统默认配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PK | 主键 |
| kind | VARCHAR(16) | 类型:expense_item / template |
| payload | JSONB | 默认数据内容 |

## 新建机构自动初始化

新建机构时,系统自动执行:
1. 从 `system_defaults` 中查出 kind='expense_item' 的所有记录
2. 逐条插入到 `expense_items` 表(org_id 设为新机构)
3. 从 `system_defaults` 中查出 kind='template' 的所有记录
4. 逐条插入到 `templates` 表(org_id 设为新机构)
