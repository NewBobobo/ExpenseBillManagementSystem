# 项目初始化指南

## 一、环境准备

### 1.1 开发工具安装

| 工具 | 版本要求 | 下载地址 |
|------|----------|----------|
| Python | 3.11+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| PostgreSQL | 15+ | https://www.postgresql.org/download/ |
| Git | 最新版 | https://git-scm.com/downloads |
| VS Code | 最新版 | https://code.visualstudio.com/ |

### 1.2 VS Code 推荐插件

**Python 开发**
- Python (Microsoft)
- Pylance (Microsoft)
- Ruff (Astral Software)

**前端开发**
- Vue - Official (Vue.js)
- ESLint (Microsoft)
- Prettier - Code formatter (Prettier)
- TypeScript Vue Plugin (Volar) (Vue.js)

**通用工具**
- GitLens (GitKraken)
- Docker (Microsoft)
- REST Client (Huachao Mao)

---

## 二、项目初始化

### 2.1 克隆项目 (如果已有仓库)

```bash
git clone <repository-url>
cd ExpenseBillManagementSystem
```

### 2.2 创建项目结构 (如果从零开始)

```bash
# 创建项目根目录
mkdir ExpenseBillManagementSystem
cd ExpenseBillManagementSystem

# 创建主要目录
mkdir docs backend frontend electron

# 复制设计文档到 docs/
# (假设已有设计文档)
```

---

## 三、后端初始化

### 3.1 创建目录结构

```bash
cd backend

# 创建目录
mkdir -p app/{core,models,schemas,api,services/render,db,utils}
mkdir -p alembic/versions
mkdir -p storage/{logos,seals,exports}
mkdir -p tests

# 创建 __init__.py
touch app/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/api/__init__.py
touch app/services/__init__.py
touch app/services/render/__init__.py
touch app/db/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py

# 创建 .gitkeep (保留空目录)
touch storage/logos/.gitkeep
touch storage/seals/.gitkeep
touch storage/exports/.gitkeep
```

### 3.2 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3.3 创建 requirements.txt

```bash
cat > requirements.txt << 'EOF'
# Web 框架
fastapi==0.110.0
uvicorn[standard]==0.27.0
python-multipart==0.0.9

# 数据库
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9

# 数据校验
pydantic==2.6.0
pydantic-settings==2.1.0

# 认证
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# 文件处理
Pillow==10.2.0
openpyxl==3.1.2
playwright==1.40.0

# 工具
python-dotenv==1.0.0
EOF
```

### 3.4 安装依赖

```bash
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 3.5 创建环境变量文件

```bash
cat > .env << 'EOF'
# 数据库配置
DATABASE_URL=postgresql://admin:password@localhost:5432/cctalk

# JWT 配置
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 文件存储
STORAGE_PATH=./storage

# 服务配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
EOF
```

### 3.6 初始化 Alembic

```bash
# 初始化 Alembic
alembic init alembic

# 编辑 alembic.ini,修改数据库连接
# sqlalchemy.url = postgresql://admin:password@localhost:5432/cctalk
```

### 3.7 创建 app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="费用单管理系统",
    description="费用单据填报、管理与打印系统",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "费用单管理系统 API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### 3.8 测试后端启动

```bash
# 启动开发服务器
uvicorn app.main:app --reload

# 访问 API 文档
# http://localhost:8000/docs
```

---

## 四、前端初始化

### 4.1 创建 Vue 项目

```bash
cd ../frontend

# 使用 Vite 创建 Vue 3 + TypeScript 项目
npm create vite@latest . -- --template vue-ts

# 或手动创建 package.json
```

### 4.2 安装依赖

```bash
# 安装核心依赖
npm install vue@^3.4.0
npm install vue-router@^4.2.0
npm install pinia@^2.1.0
npm install axios@^1.6.0
npm install element-plus@^2.5.0

# 安装开发依赖
npm install -D @vitejs/plugin-vue
npm install -D typescript
npm install -D @types/node
npm install -D sass
npm install -D eslint
npm install -D prettier
npm install -D @typescript-eslint/parser
npm install -D @typescript-eslint/eslint-plugin
```

### 4.3 创建目录结构

```bash
mkdir -p src/{router,stores,api,views,components,composables,utils,types,styles,assets}
mkdir -p src/views/{login,dashboard,reports,expense-items,templates,seals,orgs,users,system}
mkdir -p src/components/layout
mkdir -p src/assets/{images,icons}
```

### 4.4 配置 vite.config.ts

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 4.5 配置 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path mapping */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 4.6 创建 src/main.ts

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

### 4.7 创建 src/App.vue

```vue
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// App 根组件
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}
</style>
```

### 4.8 测试前端启动

```bash
# 启动开发服务器
npm run dev

# 访问前端
# http://localhost:5173
```

---

## 五、数据库初始化

### 5.1 启动 PostgreSQL (Docker)

```bash
cd ..  # 回到项目根目录

# 创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: cctalk-postgres
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
EOF

# 启动 PostgreSQL
docker-compose up -d

# 查看日志
docker-compose logs -f postgres
```

### 5.2 创建数据库迁移

```bash
cd backend

# 创建初始迁移
alembic revision -m "initial schema"

# 编辑 alembic/versions/xxx_initial_schema.py
# (根据 docs/03-database-design.md 创建表结构)

# 执行迁移
alembic upgrade head
```

### 5.3 初始化默认数据

```bash
# 创建初始化脚本
python -c "from app.db.init_db import init_db; init_db()"
```

---

## 六、开发工作流

### 6.1 启动开发环境

**终端 1: 后端**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**终端 2: 前端**
```bash
cd frontend
npm run dev
```

**终端 3: 数据库**
```bash
docker-compose up
```

### 6.2 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

---

## 七、Git 初始化

### 7.1 创建 .gitignore

```bash
cat > .gitignore << 'EOF'
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
EOF
```

### 7.2 初始化 Git 仓库

```bash
git init
git add .
git commit -m "feat: 项目初始化"
```

### 7.3 创建分支

```bash
# 创建开发分支
git checkout -b develop

# 创建功能分支
git checkout -b feature/auth
```

---

## 八、常见问题

### 8.1 Python 虚拟环境激活失败

**Windows PowerShell 执行策略限制**
```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 8.2 PostgreSQL 连接失败

**检查数据库是否启动**
```bash
docker-compose ps
```

**检查连接字符串**
```bash
# .env 文件中的 DATABASE_URL 是否正确
DATABASE_URL=postgresql://admin:password@localhost:5432/cctalk
```

### 8.3 前端代理失败

**检查 vite.config.ts 代理配置**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### 8.4 Playwright 安装失败

**手动安装浏览器**
```bash
playwright install chromium
```

**国内镜像加速**
```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

---

## 九、下一步

项目初始化完成后,按照以下顺序开始开发:

1. **阅读设计文档** - 熟悉架构和业务逻辑
2. **创建数据库表** - 根据 `docs/03-database-design.md` 创建迁移
3. **实现认证模块** - 登录/JWT/权限校验
4. **实现机构管理** - 机构树 CRUD + 初始化复制
5. **实现用户管理** - 用户 CRUD + 角色分配
6. **实现基础数据** - 费用项/公章/模板
7. **实现单据管理** - 填报/查询/修改/导出
8. **前端页面开发** - 按功能模块逐步实现
9. **联调测试** - 前后端接口对接
10. **部署上线** - 生产环境部署

---

**文档版本**: v1.0  
**最后更新**: 2026-05-29  
**维护者**: 架构师