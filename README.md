# 费用单管理系统

> 面向连锁门店/多级机构的费用单据填报、管理与打印系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.4+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 项目简介

费用单管理系统是一个面向连锁门店和多级机构的费用单据管理平台,支持:

- ✅ **多机构层级隔离** - 同级机构完全隔离,管理员可向下穿透管理
- ✅ **开箱即用** - 新建机构自动复制默认配置,快速启用
- ✅ **模板驱动** - XML 模板定义单据样式,支持导入导出
- ✅ **双形态部署** - Web 部署 + Electron 单机部署
- ✅ **权限管控** - 基于角色的权限控制,支持管理员和普通用户
- ✅ **单据导出** - 支持 PDF 和 Excel 导出

---

## 🎯 核心功能

### 用户端功能
- 📝 **费用单填报** - 费用项下拉选择,数量加减,金额自动计算
- 📋 **单据管理** - 列表查询、详情查看、修改、删除
- 📄 **模板管理** - 模板列表、编辑器、导入导出
- 🖨️ **单据导出** - PDF/Excel 导出,浏览器打印
- 📚 **基础数据** - 费用项字典、公章管理

### 管理员功能
- 🏢 **机构管理** - 机构树维护、Logo 上传
- 👥 **用户管理** - 用户 CRUD、角色分配、密码重置
- ⚙️ **系统设置** - 默认配置维护(超级管理员)

---

## 🏗️ 技术架构

### 技术栈

**后端**
- Python 3.11+ / FastAPI / Uvicorn
- SQLAlchemy 2.x ORM + Alembic 迁移
- PostgreSQL 15+ (Web) / SQLite (单机)
- JWT 认证 + bcrypt 密码哈希
- Playwright (PDF 生成) + openpyxl (Excel 导出)

**前端**
- Vue 3.4+ (Composition API) + TypeScript 5.x
- Element Plus 2.x (UI 组件库)
- Pinia 2.x (状态管理) + Vue Router 4.x
- Vite 5.x (构建工具) + Axios 1.x

**部署**
- Docker Compose (开发环境)
- Nginx (生产环境)
- Electron 28+ (单机部署,二期)

### 架构图

```
┌─────────────────────────────────────────────────────┐
│  客户端层                                            │
│  Vue 3 + Element Plus + Pinia                       │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST (JSON)
┌────────────────────▼────────────────────────────────┐
│  服务端层                                            │
│  Python 3.11+ / FastAPI / Uvicorn                   │
│  SQLAlchemy 2.x ORM + Alembic 迁移                 │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  数据层                                              │
│  PostgreSQL 15+ (Web) / SQLite (单机)               │
│  本地磁盘文件存储 (logo/公章/PDF)                   │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (或 Docker)
- Git

### 1. 克隆项目

```bash
git clone <repository-url>
cd ExpenseBillManagementSystem
```

### 2. 启动数据库 (Docker)

```bash
docker-compose up -d
```

### 3. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件,配置数据库连接等

# 执行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload
```

### 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 5. 访问应用

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 📚 文档

完整的设计文档和开发指南请查看 [docs/](docs/) 目录:

| 文档 | 说明 |
|------|------|
| [文档索引](docs/README.md) | 所有文档的导航和速查 |
| [设计理念](docs/01-design-overview.md) | 核心设计理念与产品定位 |
| [技术栈](docs/02-tech-stack.md) | 技术选型与版本说明 |
| [数据库设计](docs/03-database-design.md) | 数据库表结构设计 |
| [API 文档](docs/05-api-spec.md) | RESTful API 接口文档 |
| [功能规格](docs/08-feature-spec.md) | 功能模块详细说明 |
| [架构总览](docs/09-architecture-overview.md) | 系统架构与分层设计 |
| [初始化指南](docs/11-initialization-guide.md) | 项目初始化步骤 |
| [架构决策](docs/12-architecture-decisions.md) | 重要架构决策记录 |

---

## 📁 项目结构

```
ExpenseBillManagementSystem/
├── docs/                              # 📚 设计文档
├── backend/                           # 🐍 Python FastAPI 后端
│   ├── app/                           # 应用代码
│   │   ├── core/                      # 核心配置 (JWT/权限)
│   │   ├── models/                    # SQLAlchemy ORM 模型
│   │   ├── schemas/                   # Pydantic 数据校验
│   │   ├── api/                       # 路由控制层
│   │   ├── services/                  # 业务逻辑层
│   │   └── db/                        # 数据库会话
│   ├── alembic/                       # 数据库迁移
│   ├── storage/                       # 文件存储
│   └── tests/                         # 测试
├── frontend/                          # 🎨 Vue 3 前端
│   ├── src/
│   │   ├── router/                    # 路由配置
│   │   ├── stores/                    # Pinia 状态管理
│   │   ├── api/                       # API 接口封装
│   │   ├── views/                     # 页面视图
│   │   ├── components/                # 公共组件
│   │   └── utils/                     # 工具函数
│   └── public/                        # 静态资源
├── electron/                          # 🖥️ Electron 打包 (二期)
└── docker-compose.yml                 # 🐳 开发环境编排
```

---

## 🔑 核心设计

### 1. 机构隔离与层级穿透

使用**物化路径 (Materialized Path)** 实现机构层级:

```sql
-- 机构表
CREATE TABLE orgs (
  id BIGSERIAL PRIMARY KEY,
  parent_id BIGINT,
  path VARCHAR(512),  -- 物化路径: /1/3/7/
  level SMALLINT,     -- 层级深度
  ...
);

-- 查询某机构及所有下级
SELECT * FROM orgs WHERE path LIKE '/1/2/%';
```

**权限规则**:
- 同级机构完全隔离,互不可见
- 管理员可向下穿透管理所有子机构
- 普通用户严格限制在本机构

### 2. 开箱即用的初始化

新建机构时自动执行:
1. 从 `system_defaults` 表查询默认费用项和模板
2. 复制到新机构的 `expense_items` 和 `templates` 表
3. 各机构独立维护,修改不影响其他机构

### 3. 模板驱动的单据生成

**XML 模板定义**:
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
        <column key="amount" title="金额" width="24%"/>
      </columns>
    </table>
  </body>
  <footer>
    <seal x="420" y="-30" width="100" height="100"/>
  </footer>
</template>
```

**渲染流程**:
- 前端: XML → 对象树 → HTML 预览
- 后端: XML → HTML → Playwright → PDF

---

## 🛠️ 开发指南

### 后端开发

**创建新的 API 路由**:
```python
# app/api/example.py
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/example")
def get_example(user = Depends(get_current_user)):
    return {"message": "Hello World"}
```

**数据库迁移**:
```bash
# 创建迁移
alembic revision -m "add new table"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 前端开发

**创建新页面**:
```vue
<!-- src/views/example/ExampleView.vue -->
<template>
  <div>
    <h1>示例页面</h1>
  </div>
</template>

<script setup lang="ts">
// 页面逻辑
</script>
```

**添加路由**:
```typescript
// src/router/index.ts
{
  path: '/example',
  component: () => import('@/views/example/ExampleView.vue'),
  meta: { requiresAuth: true }
}
```

---

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行指定测试
pytest tests/test_auth.py

# 查看覆盖率
pytest --cov=app --cov-report=html
```

### 前端测试

```bash
cd frontend

# 运行单元测试
npm run test

# 运行 E2E 测试
npm run test:e2e
```

---

## 📦 部署

### Web 部署

**使用 Docker Compose**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**手动部署**:
1. 配置 PostgreSQL 数据库
2. 部署后端 (Uvicorn + Supervisor)
3. 构建前端 (`npm run build`)
4. 配置 Nginx 反向代理

详见: [部署文档](docs/deployment.md) (待补充)

### 单机部署 (Electron,二期)

```bash
# 构建 Electron 应用
cd electron
npm run build

# 生成安装包
npm run dist
```

---

## 📅 开发排期

| 阶段 | 时间 | 产出 |
|------|------|------|
| 第一阶段 | W1 D1-D3 | 基础框架 (认证/前后端骨架) |
| 第二阶段 | W1 D4 - W2 D2 | 机构与用户管理 |
| 第三阶段 | W2 D3 - W3 D1 | 业务基础数据 |
| 第四阶段 | W3 D2 - W3 D5 | 模板系统 |
| 第五阶段 | W4 D1 - W4 D5 | 单据填报与导出 |
| 第六阶段 | W5 | 联调与完善 |

**里程碑**:
- ✅ M1 (W1): 能登录,看到机构树
- ⏳ M2 (W3): 能维护字典/模板/公章,模板能预览
- ⏳ M3 (W4): 能填报单据并导出 PDF/Excel
- ⏳ M4 (W5): 一期交付,全流程跑通

---

## 🤝 贡献指南

### 分支策略

- `main`: 生产分支
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支

### 提交规范

```
feat: 新增费用单填报功能
fix: 修复单号生成重复问题
docs: 更新 API 文档
refactor: 重构模板渲染逻辑
test: 添加机构隔离测试用例
```

### 代码规范

- Python: 遵循 PEP 8,使用 Ruff 检查
- TypeScript: 使用 ESLint + Prettier
- 提交前运行测试和代码检查

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

## 📞 联系方式

- **项目负责人**: [待填写]
- **技术支持**: [待填写]
- **问题反馈**: [GitHub Issues](https://github.com/your-repo/issues)

---

## 🙏 致谢

感谢以下开源项目:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Playwright](https://playwright.dev/)

---

**项目版本**: v1.0.0  
**最后更新**: 2026-05-29