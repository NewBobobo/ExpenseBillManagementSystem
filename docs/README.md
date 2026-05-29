# 📚 费用单管理系统 - 文档索引

## 项目概述

**项目名称**: 费用单管理系统  
**项目定位**: 面向连锁门店/多级机构的费用单据填报、管理与打印系统  
**技术栈**: Python FastAPI + Vue 3 + PostgreSQL  
**部署形态**: Web 部署 + Electron 单机部署(二期)

---

## 📖 文档导航

### 一、设计文档 (Design Documents)

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [01-design-overview.md](01-design-overview.md) | 设计理念与核心概念 | 所有人 |
| [02-tech-stack.md](02-tech-stack.md) | 技术栈选型与版本 | 开发者 |
| [03-database-design.md](03-database-design.md) | 数据库表结构设计 | 后端开发者 |
| [04-template-xml-spec.md](04-template-xml-spec.md) | 模板 XML 规范 | 前后端开发者 |
| [05-api-spec.md](05-api-spec.md) | API 接口文档 | 前后端开发者 |
| [06-project-structure.md](06-project-structure.md) | 项目目录结构 | 开发者 |
| [07-development-plan.md](07-development-plan.md) | 开发排期与里程碑 | 项目经理/开发者 |
| [08-feature-spec.md](08-feature-spec.md) | 功能规格说明 | 产品经理/开发者 |

### 二、架构文档 (Architecture Documents)

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [09-architecture-overview.md](09-architecture-overview.md) | 架构总览与分层设计 | 架构师/开发者 |
| [10-folder-structure.md](10-folder-structure.md) | 文件夹结构详解 | 开发者 |
| [11-initialization-guide.md](11-initialization-guide.md) | 项目初始化指南 | 新成员/开发者 |
| [12-architecture-decisions.md](12-architecture-decisions.md) | 架构决策记录 (ADR) | 架构师/技术负责人 |

### 三、快速开始 (Quick Start)

**新成员入门路径**:
1. 阅读 [01-design-overview.md](01-design-overview.md) - 了解项目定位和核心理念
2. 阅读 [08-feature-spec.md](08-feature-spec.md) - 熟悉功能模块
3. 阅读 [11-initialization-guide.md](11-initialization-guide.md) - 搭建开发环境
4. 阅读 [10-folder-structure.md](10-folder-structure.md) - 熟悉代码结构
5. 开始开发!

**前端开发者路径**:
1. [02-tech-stack.md](02-tech-stack.md) - 前端技术栈
2. [05-api-spec.md](05-api-spec.md) - API 接口文档
3. [04-template-xml-spec.md](04-template-xml-spec.md) - 模板 XML 规范
4. [10-folder-structure.md](10-folder-structure.md) - 前端目录结构

**后端开发者路径**:
1. [02-tech-stack.md](02-tech-stack.md) - 后端技术栈
2. [03-database-design.md](03-database-design.md) - 数据库设计
3. [05-api-spec.md](05-api-spec.md) - API 接口文档
4. [10-folder-structure.md](10-folder-structure.md) - 后端目录结构

---

## 🎯 核心概念速查

### 机构隔离

- **同级隔离**: 同级机构完全隔离,互不可见
- **层级穿透**: 管理员可向下穿透管理所有子机构
- **实现方式**: 物化路径 (Materialized Path)
- **查询示例**: `WHERE path LIKE '/1/2/%'`

详见: [01-design-overview.md](01-design-overview.md#1-机构隔离层级穿透)

### 开箱即用

- **自动初始化**: 新建机构时自动复制系统默认配置
- **独立维护**: 各机构独立维护字典和模板
- **降低成本**: 减少初始化配置工作量

详见: [01-design-overview.md](01-design-overview.md#2-开箱即用独立运营)

### 模板驱动

- **XML 定义**: 单据样式由 XML 模板定义
- **前端预览**: 前端解析 XML 渲染 HTML 预览
- **后端生成**: 后端解析 XML 生成 PDF/Excel
- **导入导出**: 支持 XML 文件导入导出

详见: [04-template-xml-spec.md](04-template-xml-spec.md)

### 双形态部署

- **Web 部署**: 后端服务 + 前端静态资源,多终端浏览器访问
- **单机部署**: Electron 打包,内嵌后端服务,双击即用
- **同一代码**: 通过构建配置切换部署形态

详见: [01-design-overview.md](01-design-overview.md#4-双形态部署)

---

## 🗂️ 数据库表速查

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `orgs` | 机构树 | `path` (物化路径), `parent_id` |
| `users` | 用户 | `org_id`, `role` (admin/user) |
| `expense_items` | 费用项字典 | `org_id`, `is_active` |
| `seals` | 公章 | `org_id`, `is_default` |
| `templates` | 打印模板 | `org_id`, `xml_content` |
| `reports` | 单据主表 | `org_id`, `code` (单号) |
| `report_items` | 单据明细 | `report_id`, `seq` |
| `report_logs` | 修改日志 | `report_id`, `diff` (JSONB) |
| `report_seq` | 单号流水 | `org_id`, `seq_date` |
| `system_defaults` | 系统默认配置 | `kind`, `payload` (JSONB) |

详见: [03-database-design.md](03-database-design.md)

---

## 🔌 API 接口速查

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 认证 | `/api/auth` | 登录/登出/获取当前用户 |
| 机构 | `/api/orgs` | 机构树 CRUD |
| 用户 | `/api/users` | 用户管理 |
| 费用项 | `/api/expense-items` | 费用项字典 |
| 公章 | `/api/seals` | 公章管理 |
| 模板 | `/api/templates` | 模板管理 + 导入导出 |
| 单据 | `/api/reports` | 单据 CRUD + 导出 |
| 系统设置 | `/api/system/defaults` | 系统默认配置 |

详见: [05-api-spec.md](05-api-spec.md)

---

## 🏗️ 架构决策速查

| ADR | 决策 | 理由 |
|-----|------|------|
| ADR-001 | 技术栈: FastAPI + Vue 3 | 开发效率高,生态成熟 |
| ADR-002 | 机构隔离: 物化路径 | 查询性能好,实现简单 |
| ADR-003 | 文件存储: 一期本地,二期数据库 | 快速上线,平滑迁移 |
| ADR-004 | 模板系统: XML + 解析器 | 结构清晰,安全性高 |
| ADR-005 | PDF 生成: Playwright | 样式还原度高,中文支持好 |
| ADR-006 | 认证授权: JWT | 无状态,支持集群 |
| ADR-007 | 状态管理: Pinia | 类型安全,官方推荐 |

详见: [12-architecture-decisions.md](12-architecture-decisions.md)

---

## 📅 开发排期速查

| 阶段 | 时间 | 产出 |
|------|------|------|
| 第一阶段 | W1 D1-D3 | 基础框架 (认证/前后端骨架) |
| 第二阶段 | W1 D4 - W2 D2 | 机构与用户管理 |
| 第三阶段 | W2 D3 - W3 D1 | 业务基础数据 (字典/公章/默认配置) |
| 第四阶段 | W3 D2 - W3 D5 | 模板系统 (XML 解析/编辑器) |
| 第五阶段 | W4 D1 - W4 D5 | 单据填报与导出 |
| 第六阶段 | W5 | 联调与完善 |

**里程碑**:
- M1 (W1 结束): 能登录,看到机构树
- M2 (W3 结束): 能维护字典/模板/公章,模板能预览
- M3 (W4 结束): 能填报单据并导出 PDF/Excel
- M4 (W5 结束): 一期交付,全流程跑通

详见: [07-development-plan.md](07-development-plan.md)

---

## 🎨 功能模块速查

### 用户端功能

| 模块 | 路径 | 权限 |
|------|------|------|
| 工作台 | `/dashboard` | 所有用户 |
| 填报费用单 | `/reports/create` | 所有用户 |
| 单据列表 | `/reports` | 所有用户 |
| 费用项字典 | `/expense-items` | 所有用户 |
| 公章管理 | `/seals` | 所有用户 |
| 模板列表 | `/templates` | 所有用户 |
| 模板编辑器 | `/templates/:id/edit` | 所有用户 |

### 管理员功能

| 模块 | 路径 | 权限 |
|------|------|------|
| 机构树 | `/orgs` | 管理员 |
| 用户管理 | `/users` | 管理员 |
| 系统默认配置 | `/system/defaults` | 超级管理员 |

详见: [08-feature-spec.md](08-feature-spec.md)

---

## 🛠️ 开发环境速查

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Git

### 启动命令

**后端**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**前端**
```bash
cd frontend
npm run dev
```

**数据库**
```bash
docker-compose up
```

### 访问地址

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

详见: [11-initialization-guide.md](11-initialization-guide.md)

---

## 📝 文档维护规范

### 文档更新原则

1. **架构变更**: 必须更新相关文档
2. **API 变更**: 必须更新 [05-api-spec.md](05-api-spec.md)
3. **数据库变更**: 必须更新 [03-database-design.md](03-database-design.md)
4. **功能变更**: 必须更新 [08-feature-spec.md](08-feature-spec.md)
5. **重大决策**: 必须在 [12-architecture-decisions.md](12-architecture-decisions.md) 中记录

### 文档版本管理

- 每次更新文档时,更新文档底部的"最后更新"日期
- 重大变更时,更新文档版本号 (v1.0 → v1.1)
- 文档变更随代码一起提交到 Git

### 文档命名规范

- 设计文档: `{序号}-{名称}.md` (如 `01-design-overview.md`)
- 序号从 01 开始,两位数字
- 名称使用 kebab-case (小写字母 + 连字符)

---

## 🔗 外部资源

### 官方文档

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Pinia 文档](https://pinia.vuejs.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [Playwright 文档](https://playwright.dev/python/)

### 学习资源

- [FastAPI 教程](https://fastapi.tiangolo.com/tutorial/)
- [Vue 3 教程](https://vuejs.org/tutorial/)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [PostgreSQL 教程](https://www.postgresql.org/docs/)

---

## 📞 联系方式

**架构师**: [待填写]  
**项目经理**: [待填写]  
**技术负责人**: [待填写]

---

**文档索引版本**: v1.0  
**最后更新**: 2026-05-29  
**维护者**: 架构师