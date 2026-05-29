# 项目目录结构

```
cctalk/
├── docs/                              # 设计文档(当前目录)
│   ├── 01-design-overview.md
│   ├── 02-tech-stack.md
│   ├── 03-database-design.md
│   ├── 04-template-xml-spec.md
│   ├── 05-api-spec.md
│   ├── 06-project-structure.md
│   ├── 07-development-plan.md
│   └── 08-feature-spec.md
│
├── backend/                           # Python FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI 应用入口
│   │   │
│   │   ├── core/                      # 核心配置
│   │   │   ├── config.py              # 环境变量、数据库连接串
│   │   │   ├── security.py            # JWT 签发/验证、密码哈希
│   │   │   └── deps.py               # 依赖注入(当前用户、权限校验)
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM 模型
│   │   │   ├── __init__.py
│   │   │   ├── org.py                 # 机构
│   │   │   ├── user.py                # 用户
│   │   │   ├── expense_item.py        # 费用项字典
│   │   │   ├── template.py            # 打印模板
│   │   │   ├── seal.py                # 公章
│   │   │   ├── report.py              # 单据主表 + 明细
│   │   │   ├── report_log.py          # 修改日志
│   │   │   └── system_default.py      # 系统默认配置
│   │   │
│   │   ├── schemas/                   # Pydantic 请求/响应模型
│   │   │   ├── auth.py
│   │   │   ├── org.py
│   │   │   ├── user.py
│   │   │   ├── expense_item.py
│   │   │   ├── template.py
│   │   │   ├── seal.py
│   │   │   └── report.py
│   │   │
│   │   ├── api/                       # 路由层(Controller)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── orgs.py
│   │   │   ├── users.py
│   │   │   ├── expense_items.py
│   │   │   ├── templates.py
│   │   │   ├── seals.py
│   │   │   ├── reports.py
│   │   │   └── system_defaults.py
│   │   │
│   │   ├── services/                  # 业务逻辑层
│   │   │   ├── org_service.py         # 机构 CRUD + 初始化复制
│   │   │   ├── user_service.py
│   │   │   ├── report_service.py      # 单号生成、修改日志
│   │   │   └── render/                # 渲染引擎
│   │   │       ├── xml_parser.py      # XML 模板解析
│   │   │       ├── html_renderer.py   # XML → HTML
│   │   │       ├── pdf_exporter.py    # Playwright → PDF
│   │   │       └── excel_exporter.py  # openpyxl → Excel
│   │   │
│   │   └── db/                        # 数据库相关
│   │       ├── session.py             # 数据库会话工厂
│   │       └── init_db.py             # 初始化默认数据
│   │
│   ├── alembic/                       # 数据库迁移
│   │   ├── alembic.ini
│   │   └── versions/
│   │
│   ├── storage/                       # 本地文件存储
│   │   ├── logos/                     # 机构 Logo
│   │   ├── seals/                     # 公章图片
│   │   └── exports/                   # 临时导出文件(PDF/Excel)
│   │
│   ├── tests/                         # 后端测试
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/                          # Vue 3 前端
│   ├── public/
│   ├── src/
│   │   ├── main.ts                    # 应用入口
│   │   ├── App.vue
│   │   │
│   │   ├── router/                    # 路由配置
│   │   │   └── index.ts              # 含路由守卫(权限拦截)
│   │   │
│   │   ├── stores/                    # Pinia 状态管理
│   │   │   ├── auth.ts               # 认证状态(token、用户信息)
│   │   │   └── org.ts                # 当前机构上下文
│   │   │
│   │   ├── api/                       # 接口封装
│   │   │   ├── request.ts            # Axios 实例(拦截器、token注入)
│   │   │   ├── auth.ts
│   │   │   ├── orgs.ts
│   │   │   ├── users.ts
│   │   │   ├── expense-items.ts
│   │   │   ├── templates.ts
│   │   │   ├── seals.ts
│   │   │   └── reports.ts
│   │   │
│   │   ├── views/                     # 页面视图
│   │   │   ├── login/                 # 登录页
│   │   │   │   └── LoginView.vue
│   │   │   ├── dashboard/             # 首页仪表盘
│   │   │   │   └── DashboardView.vue
│   │   │   ├── reports/               # 费用单管理
│   │   │   │   ├── ReportList.vue    # 单据列表
│   │   │   │   ├── ReportCreate.vue  # 填报页面
│   │   │   │   └── ReportDetail.vue  # 详情/修改
│   │   │   ├── expense-items/         # 费用项字典
│   │   │   │   └── ExpenseItemList.vue
│   │   │   ├── templates/             # 模板管理
│   │   │   │   ├── TemplateList.vue
│   │   │   │   └── TemplateEditor.vue # 表单式XML编辑器
│   │   │   ├── seals/                 # 公章管理
│   │   │   │   └── SealList.vue
│   │   │   ├── orgs/                  # 机构管理
│   │   │   │   └── OrgTree.vue
│   │   │   └── users/                 # 用户管理
│   │   │       └── UserList.vue
│   │   │
│   │   ├── components/                # 公共组件
│   │   │   ├── layout/               # 布局(侧边栏、顶栏)
│   │   │   ├── ReportForm.vue        # 费用单填报表单
│   │   │   ├── TemplateRenderer.vue  # XML→HTML 实时预览
│   │   │   └── NumberInput.vue       # 数量输入(+/- 按钮)
│   │   │
│   │   └── utils/                     # 工具函数
│   │       ├── xml-parser.ts         # XML 解析为对象树
│   │       ├── xml-renderer.ts       # 对象树 → HTML
│   │       └── number-to-cn.ts       # 金额转中文大写
│   │
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── electron/                          # Electron 桌面打包(二期)
│   ├── main.ts                        # 主进程:启动后端+加载前端
│   ├── preload.ts
│   └── package.json
│
├── docker-compose.yml                 # 开发环境(PostgreSQL)
├── .env.example                       # 环境变量模板
└── README.md
```
