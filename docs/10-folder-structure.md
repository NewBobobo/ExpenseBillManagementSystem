# 项目文件夹结构详解

## 一、项目根目录

```
ExpenseBillManagementSystem/
├── docs/                              # 📚 设计文档目录
├── backend/                           # 🐍 Python FastAPI 后端
├── frontend/                          # 🎨 Vue 3 前端
├── electron/                          # 🖥️ Electron 桌面打包 (二期)
├── docker-compose.yml                 # 🐳 开发环境编排
├── .env.example                       # 🔧 环境变量模板
├── .gitignore                         # 📝 Git 忽略规则
└── README.md                          # 📖 项目说明
```

---

## 二、docs/ - 设计文档目录

```
docs/
├── 01-design-overview.md              # 设计理念与核心概念
├── 02-tech-stack.md                   # 技术栈选型
├── 03-database-design.md              # 数据库表结构设计
├── 04-template-xml-spec.md            # 模板 XML 规范
├── 05-api-spec.md                     # API 接口文档
├── 06-project-structure.md            # 项目目录结构
├── 07-development-plan.md             # 开发排期与里程碑
├── 08-feature-spec.md                 # 功能规格说明
├── 09-architecture-overview.md        # 架构总览 (本文档)
├── 10-folder-structure.md             # 文件夹结构详解 (当前文档)
└── 文件功能描述.jpg                   # 原始需求图片
```

**用途**
- 架构师维护的设计文档
- 开发团队的技术参考
- 新成员的入门指南

---

## 三、backend/ - 后端目录

### 3.1 目录树

```
backend/
├── app/                               # 应用主目录
│   ├── __init__.py
│   ├── main.py                        # FastAPI 应用入口
│   │
│   ├── core/                          # 核心配置模块
│   │   ├── __init__.py
│   │   ├── config.py                  # 配置管理 (环境变量/数据库连接)
│   │   ├── security.py                # 安全模块 (JWT/密码哈希)
│   │   └── deps.py                    # 依赖注入 (当前用户/权限校验)
│   │
│   ├── models/                        # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── base.py                    # 基础模型类
│   │   ├── org.py                     # 机构模型
│   │   ├── user.py                    # 用户模型
│   │   ├── expense_item.py            # 费用项字典模型
│   │   ├── template.py                # 打印模板模型
│   │   ├── seal.py                    # 公章模型
│   │   ├── report.py                  # 单据主表模型
│   │   ├── report_item.py             # 单据明细模型
│   │   ├── report_log.py              # 修改日志模型
│   │   ├── report_seq.py              # 单号流水模型
│   │   └── system_default.py          # 系统默认配置模型
│   │
│   ├── schemas/                       # Pydantic 数据传输对象
│   │   ├── __init__.py
│   │   ├── common.py                  # 通用响应模型
│   │   ├── auth.py                    # 认证请求/响应
│   │   ├── org.py                     # 机构请求/响应
│   │   ├── user.py                    # 用户请求/响应
│   │   ├── expense_item.py            # 费用项请求/响应
│   │   ├── template.py                # 模板请求/响应
│   │   ├── seal.py                    # 公章请求/响应
│   │   └── report.py                  # 单据请求/响应
│   │
│   ├── api/                           # 路由控制层
│   │   ├── __init__.py
│   │   ├── deps.py                    # API 依赖注入
│   │   ├── auth.py                    # 认证路由 (/api/auth)
│   │   ├── orgs.py                    # 机构管理路由 (/api/orgs)
│   │   ├── users.py                   # 用户管理路由 (/api/users)
│   │   ├── expense_items.py           # 费用项路由 (/api/expense-items)
│   │   ├── templates.py               # 模板路由 (/api/templates)
│   │   ├── seals.py                   # 公章路由 (/api/seals)
│   │   ├── reports.py                 # 单据路由 (/api/reports)
│   │   └── system_defaults.py         # 系统默认配置路由 (/api/system/defaults)
│   │
│   ├── services/                      # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── org_service.py             # 机构服务 (CRUD + 初始化复制)
│   │   ├── user_service.py            # 用户服务 (CRUD + 密码管理)
│   │   ├── report_service.py          # 单据服务 (单号生成 + 修改日志)
│   │   ├── template_service.py        # 模板服务 (导入导出)
│   │   └── render/                    # 渲染引擎
│   │       ├── __init__.py
│   │       ├── xml_parser.py          # XML 模板解析器
│   │       ├── html_renderer.py       # XML → HTML 渲染器
│   │       ├── pdf_exporter.py        # Playwright → PDF 导出
│   │       └── excel_exporter.py      # openpyxl → Excel 导出
│   │
│   ├── db/                            # 数据库相关
│   │   ├── __init__.py
│   │   ├── session.py                 # 数据库会话工厂
│   │   └── init_db.py                 # 初始化默认数据
│   │
│   └── utils/                         # 工具函数
│       ├── __init__.py
│       ├── file_utils.py              # 文件上传/存储工具
│       └── number_utils.py            # 数字转中文大写
│
├── alembic/                           # 数据库迁移
│   ├── alembic.ini                    # Alembic 配置
│   ├── env.py                         # 迁移环境配置
│   ├── script.py.mako                 # 迁移脚本模板
│   └── versions/                      # 迁移版本文件
│       └── 001_initial_schema.py      # 初始表结构
│
├── storage/                           # 本地文件存储 (一期)
│   ├── logos/                         # 机构 Logo
│   │   └── .gitkeep
│   ├── seals/                         # 公章图片
│   │   └── .gitkeep
│   └── exports/                       # 临时导出文件 (PDF/Excel)
│       └── .gitkeep
│
├── tests/                             # 测试目录
│   ├── __init__.py
│   ├── conftest.py                    # pytest 配置
│   ├── test_auth.py                   # 认证测试
│   ├── test_orgs.py                   # 机构测试
│   ├── test_reports.py                # 单据测试
│   └── test_permissions.py            # 权限测试
│
├── requirements.txt                   # Python 依赖
├── pyproject.toml                     # 项目配置 (Ruff/pytest)
├── .env                               # 环境变量 (不提交)
└── README.md                          # 后端说明
```

### 3.2 核心文件说明

#### app/main.py
```python
"""
FastAPI 应用入口
- 创建 FastAPI 实例
- 注册路由
- 配置 CORS
- 配置中间件
- 启动事件处理
"""
```

#### app/core/config.py
```python
"""
配置管理
- 从环境变量读取配置
- 数据库连接串
- JWT 密钥
- 文件存储路径
"""
```

#### app/core/security.py
```python
"""
安全模块
- JWT Token 签发与验证
- 密码哈希 (bcrypt)
- 密码验证
"""
```

#### app/core/deps.py
```python
"""
依赖注入
- get_db(): 获取数据库会话
- get_current_user(): 获取当前用户
- require_admin(): 要求管理员权限
- check_org_access(): 检查机构访问权限
"""
```

#### app/services/org_service.py
```python
"""
机构服务
- create_org(): 创建机构 + 自动复制默认数据
- update_org_path(): 更新物化路径
- get_visible_orgs(): 获取用户可见机构列表
"""
```

#### app/services/report_service.py
```python
"""
单据服务
- generate_report_code(): 生成单号
- create_report(): 创建单据 + 记录日志
- update_report(): 修改单据 + 记录日志
- get_report_logs(): 获取修改历史
"""
```

#### app/services/render/pdf_exporter.py
```python
"""
PDF 导出
- parse_template(): 解析 XML 模板
- render_html(): 生成 HTML
- generate_pdf(): Playwright 渲染 PDF
"""
```

---

## 四、frontend/ - 前端目录

### 4.1 目录树

```
frontend/
├── public/                            # 静态资源
│   ├── favicon.ico
│   └── logo.png
│
├── src/                               # 源代码目录
│   ├── main.ts                        # 应用入口
│   ├── App.vue                        # 根组件
│   │
│   ├── router/                        # 路由配置
│   │   └── index.ts                   # 路由定义 + 权限守卫
│   │
│   ├── stores/                        # Pinia 状态管理
│   │   ├── auth.ts                    # 认证状态 (token/用户信息)
│   │   └── org.ts                     # 机构上下文 (当前机构)
│   │
│   ├── api/                           # API 接口封装
│   │   ├── request.ts                 # Axios 实例 (拦截器/token 注入)
│   │   ├── auth.ts                    # 认证接口
│   │   ├── orgs.ts                    # 机构接口
│   │   ├── users.ts                   # 用户接口
│   │   ├── expense-items.ts           # 费用项接口
│   │   ├── templates.ts               # 模板接口
│   │   ├── seals.ts                   # 公章接口
│   │   └── reports.ts                 # 单据接口
│   │
│   ├── views/                         # 页面视图
│   │   ├── login/                     # 登录模块
│   │   │   └── LoginView.vue          # 登录页面
│   │   │
│   │   ├── dashboard/                 # 工作台
│   │   │   └── DashboardView.vue      # 首页仪表盘
│   │   │
│   │   ├── reports/                   # 费用单管理
│   │   │   ├── ReportList.vue         # 单据列表
│   │   │   ├── ReportCreate.vue       # 填报页面
│   │   │   └── ReportDetail.vue       # 详情/修改页面
│   │   │
│   │   ├── expense-items/             # 费用项字典
│   │   │   └── ExpenseItemList.vue    # 费用项列表
│   │   │
│   │   ├── templates/                 # 模板管理
│   │   │   ├── TemplateList.vue       # 模板列表
│   │   │   └── TemplateEditor.vue     # 模板编辑器
│   │   │
│   │   ├── seals/                     # 公章管理
│   │   │   └── SealList.vue           # 公章列表
│   │   │
│   │   ├── orgs/                      # 机构管理
│   │   │   └── OrgTree.vue            # 机构树管理
│   │   │
│   │   ├── users/                     # 用户管理
│   │   │   └── UserList.vue           # 用户列表
│   │   │
│   │   └── system/                    # 系统设置
│   │       └── DefaultConfig.vue      # 默认配置管理
│   │
│   ├── components/                    # 公共组件
│   │   ├── layout/                    # 布局组件
│   │   │   ├── AppLayout.vue          # 主布局 (侧边栏+顶栏+内容区)
│   │   │   ├── Sidebar.vue            # 侧边栏菜单
│   │   │   ├── Header.vue             # 顶部导航栏
│   │   │   └── Breadcrumb.vue         # 面包屑导航
│   │   │
│   │   ├── ReportForm.vue             # 费用单填报表单
│   │   ├── TemplateRenderer.vue       # XML 模板实时预览
│   │   ├── NumberInput.vue            # 数量输入组件 (+/- 按钮)
│   │   ├── FileUpload.vue             # 文件上传组件
│   │   └── ConfirmDialog.vue          # 确认对话框
│   │
│   ├── composables/                   # 组合式函数 (Composition API)
│   │   ├── useAuth.ts                 # 认证逻辑
│   │   ├── usePermission.ts           # 权限判断
│   │   └── useTable.ts                # 表格分页逻辑
│   │
│   ├── utils/                         # 工具函数
│   │   ├── xml-parser.ts              # XML 解析器
│   │   ├── xml-renderer.ts            # XML → HTML 渲染器
│   │   ├── number-to-cn.ts            # 金额转中文大写
│   │   ├── date-format.ts             # 日期格式化
│   │   └── file-utils.ts              # 文件处理工具
│   │
│   ├── types/                         # TypeScript 类型定义
│   │   ├── api.ts                     # API 响应类型
│   │   ├── user.ts                    # 用户类型
│   │   ├── org.ts                     # 机构类型
│   │   ├── report.ts                  # 单据类型
│   │   └── template.ts                # 模板类型
│   │
│   ├── styles/                        # 全局样式
│   │   ├── index.scss                 # 主样式文件
│   │   ├── variables.scss             # SCSS 变量
│   │   └── print.scss                 # 打印样式
│   │
│   └── assets/                        # 静态资源
│       ├── images/                    # 图片
│       └── icons/                     # 图标
│
├── index.html                         # HTML 入口
├── package.json                       # npm 依赖
├── tsconfig.json                      # TypeScript 配置
├── vite.config.ts                     # Vite 构建配置
├── .eslintrc.js                       # ESLint 配置
├── .prettierrc                        # Prettier 配置
└── README.md                          # 前端说明
```

### 4.2 核心文件说明

#### src/main.ts
```typescript
/**
 * 应用入口
 * - 创建 Vue 应用
 * - 注册 Pinia
 * - 注册 Router
 * - 注册 Element Plus
 * - 挂载应用
 */
```

#### src/router/index.ts
```typescript
/**
 * 路由配置
 * - 路由定义
 * - 路由守卫 (beforeEach)
 * - 权限拦截
 * - 动态菜单生成
 */
```

#### src/stores/auth.ts
```typescript
/**
 * 认证状态管理
 * - token 存储
 * - 用户信息
 * - 登录/登出
 * - token 刷新
 */
```

#### src/api/request.ts
```typescript
/**
 * Axios 封装
 * - 请求拦截器 (注入 token)
 * - 响应拦截器 (统一错误处理)
 * - 超时配置
 * - 基础 URL 配置
 */
```

#### src/utils/xml-renderer.ts
```typescript
/**
 * XML 模板渲染器
 * - 解析 XML 为对象树
 * - 替换占位符
 * - 生成 HTML + CSS
 * - 实时预览
 */
```

#### src/components/ReportForm.vue
```vue
<!--
费用单填报表单
- 费用项下拉选择
- 数量加减按钮
- 单价输入
- 金额自动计算
- 合计金额实时更新
- 大写金额转换
-->
```

---

## 五、electron/ - Electron 打包目录 (二期)

```
electron/
├── main.ts                            # Electron 主进程
│   ├─ 启动后端进程 (Python)
│   ├─ 创建窗口
│   └─ 加载前端页面
│
├── preload.ts                         # 预加载脚本
│   └─ 暴露安全的 API 给渲染进程
│
├── package.json                       # Electron 依赖
├── electron-builder.yml               # 打包配置
└── README.md                          # Electron 说明
```

---

## 六、开发环境配置文件

### 6.1 docker-compose.yml
```yaml
# 开发环境 PostgreSQL
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: cctalk
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 6.2 .env.example
```bash
# 数据库配置
DATABASE_URL=postgresql://admin:password@localhost:5432/cctalk

# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 文件存储
STORAGE_PATH=./storage

# 服务配置
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 七、文件命名规范

### 7.1 Python (后端)

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 模块文件 | snake_case | `org_service.py` |
| 类名 | PascalCase | `class OrgService` |
| 函数名 | snake_case | `def create_org()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_FILE_SIZE` |

### 7.2 TypeScript (前端)

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 组件文件 | PascalCase | `ReportForm.vue` |
| 工具文件 | kebab-case | `xml-parser.ts` |
| 类名 | PascalCase | `class XmlParser` |
| 函数名 | camelCase | `function parseXml()` |
| 常量 | UPPER_SNAKE_CASE | `const MAX_FILE_SIZE` |

### 7.3 目录命名

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 后端目录 | snake_case | `services/`, `models/` |
| 前端目录 | kebab-case | `expense-items/`, `report-logs/` |

---

## 八、Git 忽略规则

### 8.1 .gitignore (根目录)
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# Node.js
node_modules/
dist/
.DS_Store

# 环境变量
.env
.env.local

# 数据库
*.db
*.sqlite

# 文件存储
backend/storage/logos/*
backend/storage/seals/*
backend/storage/exports/*
!backend/storage/*/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# 日志
*.log
logs/

# 测试覆盖率
.coverage
htmlcov/
.pytest_cache/
```

---

## 九、目录创建脚本

### 9.1 后端目录初始化
```bash
#!/bin/bash
# 创建后端目录结构

mkdir -p backend/app/{core,models,schemas,api,services/render,db,utils}
mkdir -p backend/alembic/versions
mkdir -p backend/storage/{logos,seals,exports}
mkdir -p backend/tests

touch backend/app/__init__.py
touch backend/app/main.py
touch backend/app/core/{__init__.py,config.py,security.py,deps.py}
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/api/__init__.py
touch backend/app/services/__init__.py
touch backend/app/services/render/__init__.py
touch backend/app/db/{__init__.py,session.py,init_db.py}
touch backend/app/utils/__init__.py
touch backend/tests/__init__.py
touch backend/storage/{logos,seals,exports}/.gitkeep
```

### 9.2 前端目录初始化
```bash
#!/bin/bash
# 创建前端目录结构

mkdir -p frontend/src/{router,stores,api,views,components,composables,utils,types,styles,assets}
mkdir -p frontend/src/views/{login,dashboard,reports,expense-items,templates,seals,orgs,users,system}
mkdir -p frontend/src/components/layout
mkdir -p frontend/src/assets/{images,icons}

touch frontend/src/main.ts
touch frontend/src/App.vue
touch frontend/src/router/index.ts
touch frontend/src/stores/{auth.ts,org.ts}
touch frontend/src/api/request.ts
```

---

**文档版本**: v1.0  
**最后更新**: 2026-05-29  
**维护者**: 架构师