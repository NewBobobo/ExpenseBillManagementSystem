# 项目架构总览

## 一、系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  浏览器 (Chrome/Edge/Safari)                              │  │
│  │  ├─ Vue 3 SPA (Vite 构建)                                │  │
│  │  ├─ Element Plus UI 组件                                 │  │
│  │  ├─ Pinia 状态管理 (认证/机构上下文)                     │  │
│  │  └─ Vue Router (路由守卫/权限拦截)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Electron Shell (二期,可选)                              │  │
│  │  └─ 内嵌后端进程 + 前端资源                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────┬───────────────────────────────────────┘
                        │ HTTP/REST (JSON)
                        │ JWT Bearer Token 认证
┌───────────────────────▼───────────────────────────────────────┐
│                         服务端层                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI (Python 3.11+)                                  │  │
│  │  ├─ Uvicorn ASGI Server                                  │  │
│  │  ├─ JWT 认证中间件                                       │  │
│  │  ├─ 权限校验中间件 (机构隔离/角色检查)                   │  │
│  │  └─ OpenAPI 自动文档                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  业务逻辑层                                               │  │
│  │  ├─ 机构服务 (树形结构维护/初始化复制)                   │  │
│  │  ├─ 单据服务 (单号生成/修改日志)                         │  │
│  │  └─ 渲染引擎                                             │  │
│  │      ├─ XML 解析器                                       │  │
│  │      ├─ HTML 渲染器                                      │  │
│  │      ├─ PDF 导出 (Playwright)                            │  │
│  │      └─ Excel 导出 (openpyxl)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  数据访问层                                               │  │
│  │  ├─ SQLAlchemy 2.x ORM                                   │  │
│  │  ├─ Alembic 数据库迁移                                   │  │
│  │  └─ Pydantic 数据校验                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────┬───────────────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────────────┐
│                         数据层                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL 15+ (Web 部署)                               │  │
│  │  └─ JSONB 支持 / 物化路径索引                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite 3.40+ (Electron 单机部署)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  本地文件存储 (一期)                                      │  │
│  │  ├─ storage/logos/    (机构 Logo)                        │  │
│  │  ├─ storage/seals/    (公章图片)                         │  │
│  │  └─ storage/exports/  (临时 PDF/Excel)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 二、分层架构设计

### 2.1 前端架构 (Vue 3)

**技术栈**
- Vue 3.4+ (Composition API)
- TypeScript 5.x
- Element Plus 2.x (UI 组件库)
- Pinia 2.x (状态管理)
- Vue Router 4.x (路由)
- Vite 5.x (构建工具)
- Axios 1.x (HTTP 客户端)

**分层结构**

```
frontend/src/
├── main.ts                    # 应用入口
├── App.vue                    # 根组件
│
├── router/                    # 路由层
│   └── index.ts              # 路由配置 + 权限守卫
│
├── stores/                    # 状态管理层 (Pinia)
│   ├── auth.ts               # 认证状态 (token/用户信息)
│   └── org.ts                # 机构上下文 (当前机构)
│
├── api/                       # API 接口层
│   ├── request.ts            # Axios 封装 (拦截器/token 注入)
│   ├── auth.ts               # 认证接口
│   ├── orgs.ts               # 机构接口
│   ├── users.ts              # 用户接口
│   ├── expense-items.ts      # 费用项接口
│   ├── templates.ts          # 模板接口
│   ├── seals.ts              # 公章接口
│   └── reports.ts            # 单据接口
│
├── views/                     # 页面视图层
│   ├── login/                # 登录模块
│   ├── dashboard/            # 工作台
│   ├── reports/              # 费用单管理
│   ├── expense-items/        # 费用项字典
│   ├── templates/            # 模板管理
│   ├── seals/                # 公章管理
│   ├── orgs/                 # 机构管理
│   └── users/                # 用户管理
│
├── components/                # 组件层
│   ├── layout/               # 布局组件 (侧边栏/顶栏)
│   ├── ReportForm.vue        # 费用单填报表单
│   ├── TemplateRenderer.vue  # XML 模板实时预览
│   └── NumberInput.vue       # 数量输入组件 (+/- 按钮)
│
└── utils/                     # 工具层
    ├── xml-parser.ts         # XML 解析器
    ├── xml-renderer.ts       # XML → HTML 渲染器
    └── number-to-cn.ts       # 金额转中文大写
```

**核心流程**

1. **认证流程**
   - 用户登录 → 后端验证 → 返回 JWT Token
   - Token 存入 Pinia Store + LocalStorage
   - Axios 拦截器自动注入 Token 到请求头
   - 路由守卫检查 Token 有效性

2. **权限控制**
   - 路由守卫根据用户角色显示/隐藏菜单
   - 页面内根据权限显示/隐藏操作按钮
   - API 层统一处理 403 错误

3. **模板渲染**
   - 从后端获取 XML 模板字符串
   - 前端 XML 解析器解析为对象树
   - 渲染器将对象树转换为 HTML + CSS
   - 替换占位符为实际数据或 Mock 数据
   - 实时预览在 iframe 或 Shadow DOM 中渲染

### 2.2 后端架构 (FastAPI)

**技术栈**
- Python 3.11+
- FastAPI 0.110+ (Web 框架)
- Uvicorn 0.27+ (ASGI 服务器)
- SQLAlchemy 2.x (ORM)
- Alembic 1.13+ (数据库迁移)
- Pydantic 2.x (数据校验)
- python-jose 3.x (JWT)
- passlib[bcrypt] 1.7+ (密码哈希)
- Playwright 1.40+ (PDF 生成)
- openpyxl 3.1+ (Excel 导出)

**分层结构**

```
backend/app/
├── main.py                    # FastAPI 应用入口
│
├── core/                      # 核心配置层
│   ├── config.py             # 环境变量/数据库连接
│   ├── security.py           # JWT 签发验证/密码哈希
│   └── deps.py               # 依赖注入 (当前用户/权限校验)
│
├── models/                    # 数据模型层 (SQLAlchemy ORM)
│   ├── org.py                # 机构模型
│   ├── user.py               # 用户模型
│   ├── expense_item.py       # 费用项模型
│   ├── template.py           # 模板模型
│   ├── seal.py               # 公章模型
│   ├── report.py             # 单据主表 + 明细模型
│   ├── report_log.py         # 修改日志模型
│   └── system_default.py     # 系统默认配置模型
│
├── schemas/                   # 数据传输对象层 (Pydantic)
│   ├── auth.py               # 认证请求/响应
│   ├── org.py                # 机构请求/响应
│   ├── user.py               # 用户请求/响应
│   ├── expense_item.py       # 费用项请求/响应
│   ├── template.py           # 模板请求/响应
│   ├── seal.py               # 公章请求/响应
│   └── report.py             # 单据请求/响应
│
├── api/                       # 路由控制层 (Controller)
│   ├── auth.py               # 认证路由
│   ├── orgs.py               # 机构管理路由
│   ├── users.py              # 用户管理路由
│   ├── expense_items.py      # 费用项路由
│   ├── templates.py          # 模板路由
│   ├── seals.py              # 公章路由
│   ├── reports.py            # 单据路由
│   └── system_defaults.py    # 系统默认配置路由
│
├── services/                  # 业务逻辑层
│   ├── org_service.py        # 机构 CRUD + 初始化复制
│   ├── user_service.py       # 用户 CRUD + 密码管理
│   ├── report_service.py     # 单号生成 + 修改日志
│   └── render/               # 渲染引擎
│       ├── xml_parser.py     # XML 模板解析
│       ├── html_renderer.py  # XML → HTML
│       ├── pdf_exporter.py   # Playwright → PDF
│       └── excel_exporter.py # openpyxl → Excel
│
└── db/                        # 数据库层
    ├── session.py            # 数据库会话工厂
    └── init_db.py            # 初始化默认数据
```

**核心流程**

1. **请求处理流程**
   ```
   HTTP 请求
     ↓
   FastAPI 路由层 (api/)
     ↓
   依赖注入 (core/deps.py)
     ├─ 解析 JWT Token
     ├─ 获取当前用户
     └─ 权限校验 (机构隔离/角色检查)
     ↓
   业务逻辑层 (services/)
     ↓
   数据访问层 (models/ + SQLAlchemy)
     ↓
   数据库 (PostgreSQL/SQLite)
     ↓
   响应 (Pydantic schemas/)
   ```

2. **机构隔离机制**
   - 每个请求通过依赖注入获取当前用户的 `org_id`
   - 查询时自动添加 `WHERE org_id = current_user.org_id` 或 `WHERE path LIKE '/1/2/%'`
   - 管理员可穿透查询下级机构 (通过物化路径)
   - 普通用户严格限制在本机构

3. **单号生成策略**
   - 格式: `{机构编号}-{YYMMDD}-{流水号}`
   - 使用 `report_seq` 表维护每日流水号
   - 事务内原子递增,避免并发冲突

4. **PDF 导出流程**
   ```
   单据数据 + 模板 XML
     ↓
   XML 解析器 (xml_parser.py)
     ↓
   HTML 渲染器 (html_renderer.py)
     ├─ 替换占位符
     ├─ 嵌入 Logo/公章 (Base64)
     └─ 生成完整 HTML + CSS
     ↓
   Playwright 无头浏览器
     ├─ 加载 HTML
     ├─ 设置纸张参数
     └─ 输出 PDF
     ↓
   返回文件流
   ```

### 2.3 数据库架构

**数据库选型**
- **Web 部署**: PostgreSQL 15+ (支持 JSONB、物化路径索引)
- **单机部署**: SQLite 3.40+ (零配置、文件数据库)

**核心表结构**

```
orgs (机构树)
  ├─ id, parent_id, code, name
  ├─ path (物化路径: /1/3/7/)
  ├─ level (层级深度)
  └─ logo_path

users (用户)
  ├─ id, username, password_hash
  ├─ real_name, org_id, role
  └─ is_active

expense_items (费用项字典)
  ├─ id, org_id, name
  ├─ default_qty, unit_price, unit
  ├─ is_active, sort_order

seals (公章)
  ├─ id, org_id, name
  ├─ image_path, is_default

templates (打印模板)
  ├─ id, org_id, name
  ├─ xml_content, is_default

reports (单据主表)
  ├─ id, org_id, code
  ├─ report_date, recipient
  ├─ reporter_id, template_id, seal_id
  ├─ total_amount, remark

report_items (单据明细)
  ├─ id, report_id, seq
  ├─ name, qty, unit_price, amount

report_logs (修改日志)
  ├─ id, report_id, user_id
  ├─ action, diff (JSONB)

report_seq (单号流水)
  ├─ org_id, seq_date
  └─ last_seq

system_defaults (系统默认配置)
  ├─ id, kind (expense_item/template)
  └─ payload (JSONB)
```

**物化路径索引**
```sql
CREATE INDEX idx_orgs_path ON orgs USING btree (path);
-- 查询某机构及所有下级: WHERE path LIKE '/1/2/%'
```

**机构隔离索引**
```sql
CREATE INDEX idx_reports_org_id ON reports (org_id);
CREATE INDEX idx_expense_items_org_id ON expense_items (org_id);
CREATE INDEX idx_templates_org_id ON templates (org_id);
```

## 三、核心设计模式

### 3.1 机构隔离与层级穿透

**设计理念**
- 同级机构完全隔离,互不可见
- 管理员可向下穿透管理所有子机构
- 普通用户严格限制在本机构

**实现方式**
- 物化路径 (Materialized Path): `path` 字段存储 `/1/3/7/`
- 查询本机构: `WHERE org_id = current_user.org_id`
- 查询下级: `WHERE path LIKE '/1/2/%'`

**权限矩阵**

| 操作 | 管理员 | 用户 |
|------|--------|------|
| 查看数据 | 本机构 + 下级 | 仅本机构 |
| 创建数据 | 本机构 + 下级 | 仅本机构 |
| 修改数据 | 本机构 + 下级 | 仅本机构 |
| 删除数据 | 本机构 + 下级 | 不可 |
| 管理机构 | 本机构 + 下级 | 不可 |
| 管理用户 | 本机构 + 下级 | 不可 |

### 3.2 开箱即用的初始化复制

**设计理念**
- 新建机构时自动复制系统默认配置
- 各机构独立维护,修改不影响其他机构

**实现流程**
```
创建新机构
  ↓
查询 system_defaults 表
  ├─ kind='expense_item' → 复制到 expense_items
  └─ kind='template' → 复制到 templates
  ↓
设置新机构的 org_id
  ↓
完成初始化
```

### 3.3 模板驱动的单据生成

**设计理念**
- 单据样式由 XML 模板定义
- 前端解析渲染预览,后端解析生成 PDF
- 模板可导入导出,便于跨机构复用

**XML 模板结构**
```xml
<template name="标准版" version="1.0">
  <page size="A4" orientation="portrait"/>
  <header>
    <logo x="15" y="10" width="60" height="60"/>
    <title>{{org.name}} 费用单</title>
  </header>
  <body>
    <table>
      <columns>
        <column key="name" title="费用名称" width="34%"/>
        <column key="qty" title="数量" width="14%"/>
        <column key="amount" title="金额" width="24%"/>
      </columns>
    </table>
  </body>
  <footer>
    <seal x="420" y="-30" width="100" height="100"/>
  </footer>
</template>
```

**占位符系统**
- `{{org.name}}` - 机构名称
- `{{report.code}}` - 单号
- `{{report.total_amount}}` - 合计金额
- `{{report.total_cn}}` - 大写金额

### 3.4 双形态部署

**Web 部署**
- 后端: FastAPI + Uvicorn + PostgreSQL
- 前端: Nginx 托管静态资源
- 部署方式: Docker Compose 或手动部署

**单机部署 (二期)**
- Electron 打包桌面应用
- 内嵌 Python 后端进程 + SQLite
- 双击启动,零配置

## 四、文件存储策略

### 4.1 一期:本地磁盘存储

```
backend/storage/
├── logos/                     # 机构 Logo
│   └── {org_id}_{timestamp}.png
├── seals/                     # 公章图片
│   └── {seal_id}_{timestamp}.png
└── exports/                   # 临时导出文件
    └── {report_code}_{timestamp}.pdf
```

**特点**
- 简单直接,开发快速
- 适合单机部署
- 不适合多服务器集群

### 4.2 二期:数据库存储 (规划)

**方案**
- 文件以 Base64 或二进制存入数据库
- 前端通过 API 获取文件流
- 支持服务器集中部署

**表结构调整**
```sql
ALTER TABLE orgs ADD COLUMN logo_data BYTEA;
ALTER TABLE seals ADD COLUMN image_data BYTEA;
```

## 五、安全设计

### 5.1 认证与授权

**认证方式**
- JWT (JSON Web Token)
- Token 有效期: 24 小时
- 刷新机制: 前端定时刷新或过期后重新登录

**密码安全**
- bcrypt 哈希算法
- 盐值自动生成
- 不可逆加密

### 5.2 权限控制

**后端权限校验**
```python
# 依赖注入
def get_current_user(token: str) -> User:
    # 解析 JWT,获取用户信息
    pass

def require_admin(user: User) -> User:
    if user.role != "admin":
        raise HTTPException(403, "权限不足")
    return user

# 路由使用
@router.get("/orgs")
def list_orgs(user: User = Depends(get_current_user)):
    # 自动注入当前用户
    pass
```

**前端权限控制**
- 路由守卫: 未登录跳转登录页
- 菜单显示: 根据角色动态显示
- 按钮权限: v-if 控制操作按钮

### 5.3 数据隔离

**机构隔离**
- 所有业务表包含 `org_id` 字段
- 查询时自动过滤 `WHERE org_id IN (可见机构列表)`
- 防止跨机构数据泄露

**SQL 注入防护**
- 使用 SQLAlchemy ORM,参数化查询
- 禁止拼接 SQL 字符串

**XSS 防护**
- 前端 Vue 自动转义
- 后端 Pydantic 数据校验

## 六、性能优化

### 6.1 数据库优化

**索引策略**
```sql
-- 机构路径索引
CREATE INDEX idx_orgs_path ON orgs (path);

-- 机构隔离索引
CREATE INDEX idx_reports_org_id ON reports (org_id);
CREATE INDEX idx_expense_items_org_id ON expense_items (org_id);

-- 单据查询索引
CREATE INDEX idx_reports_date ON reports (report_date);
CREATE INDEX idx_reports_code ON reports (code);

-- 用户查询索引
CREATE INDEX idx_users_org_id ON users (org_id);
CREATE INDEX idx_users_username ON users (username);
```

**查询优化**
- 使用物化路径避免递归查询
- 分页查询避免全表扫描
- 使用 `select_related` 减少 N+1 查询

### 6.2 前端优化

**代码分割**
- 路由懒加载
- 组件按需加载

**缓存策略**
- 字典数据缓存 (费用项/模板/公章)
- LocalStorage 缓存用户信息

**打包优化**
- Vite 自动代码分割
- Tree Shaking 移除未使用代码
- Gzip 压缩

### 6.3 文件处理优化

**图片优化**
- Logo/公章上传时自动压缩
- 限制文件大小 (< 2MB)
- 转换为 WebP 格式 (二期)

**PDF 生成优化**
- 异步生成,避免阻塞
- 生成后缓存,相同单据复用
- 定时清理临时文件

## 七、开发规范

### 7.1 代码规范

**Python (后端)**
- 使用 Ruff 进行代码检查
- 遵循 PEP 8 规范
- 类型注解 (Type Hints)

**TypeScript (前端)**
- 使用 ESLint + Prettier
- 严格模式 (strict: true)
- 组件命名: PascalCase
- 文件命名: kebab-case

### 7.2 Git 工作流

**分支策略**
- `main`: 生产分支
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支

**提交规范**
```
feat: 新增费用单填报功能
fix: 修复单号生成重复问题
docs: 更新 API 文档
refactor: 重构模板渲染逻辑
test: 添加机构隔离测试用例
```

### 7.3 测试策略

**后端测试**
- 单元测试: pytest
- 覆盖率目标: > 80%
- 测试重点: 权限校验、机构隔离、单号生成

**前端测试**
- 单元测试: Vitest
- 组件测试: Vue Test Utils
- E2E 测试: Playwright (可选)

## 八、部署架构

### 8.1 开发环境

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: cctalk
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
```

**启动流程**
```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

### 8.2 生产环境 (Web 部署)

**架构图**
```
Internet
  ↓
Nginx (反向代理)
  ├─ /api → FastAPI (Uvicorn)
  └─ /    → 前端静态资源
  ↓
PostgreSQL
```

**部署清单**
- 服务器: Linux (Ubuntu 22.04+)
- Web 服务器: Nginx
- 应用服务器: Uvicorn (Systemd 管理)
- 数据库: PostgreSQL 15+
- 进程管理: Supervisor 或 Systemd

### 8.3 单机部署 (Electron,二期)

**打包流程**
```
前端构建 (npm run build)
  ↓
后端打包 (PyInstaller)
  ↓
Electron 打包 (electron-builder)
  ↓
生成安装包 (.exe / .dmg)
```

**启动流程**
1. Electron 主进程启动
2. 启动内嵌 Python 后端进程
3. 等待后端就绪 (健康检查)
4. 加载前端页面 (http://localhost:8000)

## 九、技术债务与二期规划

### 9.1 一期已知限制

- 文件存储在本地磁盘,不支持多服务器集群
- 模板编辑器为表单式,不支持拖拽定位
- 无数据统计和图表功能
- 无审批流程

### 9.2 二期规划

| 模块 | 内容 | 预估工时 |
|------|------|----------|
| Electron 打包 | 单机桌面版 | 1 周 |
| 模板拖拽编辑器 | 可视化定位 logo/章/字段 | 2 周 |
| 文件入库 | 文件 JSON 存数据库,前端 Web 渲染 | 1 周 |
| 数据统计 | 费用汇总、趋势图表 | 1 周 |
| 审批流程 | 单据提交审批、多级审批 | 2 周 |

---

**文档版本**: v1.0  
**最后更新**: 2026-05-29  
**维护者**: 架构师
