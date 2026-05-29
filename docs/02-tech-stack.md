# 技术栈

## 总体架构

```
┌─────────────────────────────────────────────────────┐
│  客户端层                                            │
│  Vue 3 + Element Plus + Pinia (Vite 构建)           │
│  Electron Shell (可选,单机部署)                      │
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
│  PostgreSQL 15+(Web部署) / SQLite(单机部署)         │
│  本地磁盘文件存储(logo/公章/PDF)                   │
└─────────────────────────────────────────────────────┘
```

## 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.4+ | 响应式框架,Composition API |
| Element Plus | 2.x | UI 组件库(表单、表格、树、弹窗) |
| Pinia | 2.x | 状态管理(认证、机构上下文) |
| Vue Router | 4.x | 路由,含权限守卫 |
| Vite | 5.x | 构建工具,开发热更新 |
| Axios | 1.x | HTTP 请求封装 |
| TypeScript | 5.x | 类型安全 |

## 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 运行时 |
| FastAPI | 0.110+ | Web 框架,自动 OpenAPI 文档 |
| Uvicorn | 0.27+ | ASGI 服务器 |
| SQLAlchemy | 2.x | ORM,支持 PostgreSQL 和 SQLite |
| Alembic | 1.13+ | 数据库版本迁移 |
| Pydantic | 2.x | 请求/响应数据校验 |
| python-jose | 3.x | JWT 令牌签发与验证 |
| passlib[bcrypt] | 1.7+ | 密码哈希 |
| Playwright | 1.40+ | HTML → PDF 渲染 |
| openpyxl | 3.1+ | Excel 导出 |
| Pillow | 10.x | 图片处理(logo/公章裁剪) |

## 数据库

| 技术 | 用途 |
|------|------|
| PostgreSQL 15+ | Web 部署,支持 JSONB、物化路径索引 |
| SQLite 3.40+ | Electron 单机部署,零配置 |
| Alembic | 数据库版本迁移,支持双数据库方言 |

## PDF / Excel 生成

| 技术 | 用途 |
|------|------|
| Playwright (Python) | 解析模板 XML → 渲染 HTML → 生成 PDF |
| openpyxl | 解析模板 XML → 生成 Excel 文件 |

## 单机部署(Electron)

| 技术 | 用途 |
|------|------|
| Electron 28+ | 桌面壳,启动时拉起后端进程 |
| electron-builder | 打包分发(Windows/macOS) |

## 开发工具

| 工具 | 用途 |
|------|------|
| Docker Compose | 本地开发环境(PostgreSQL) |
| pytest | 后端单元/集成测试 |
| Vitest | 前端单元测试 |
| ESLint + Prettier | 前端代码规范 |
| Ruff | Python 代码规范 |
