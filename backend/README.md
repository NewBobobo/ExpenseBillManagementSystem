# 费用单管理系统 - 后端

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件,配置数据库连接等
```

### 4. 初始化数据库

```bash
# 执行数据库迁移
alembic upgrade head
```

### 5. 启动开发服务器

```bash
uvicorn app.main:app --reload
```

访问:
- API: http://localhost:8000
- 文档: http://localhost:8000/docs

## 项目结构

```
backend/
├── app/                    # 应用代码
│   ├── core/              # 核心配置
│   ├── models/            # ORM 模型
│   ├── schemas/           # 数据校验
│   ├── api/               # 路由控制
│   ├── services/          # 业务逻辑
│   └── db/                # 数据库
├── alembic/               # 数据库迁移
├── storage/               # 文件存储
└── tests/                 # 测试
```

## 开发规范

- 遵循 PEP 8 规范
- 使用 Ruff 进行代码检查
- 编写单元测试
- 提交前运行测试

## 测试

```bash
# 运行所有测试
pytest

# 查看覆盖率
pytest --cov=app --cov-report=html
```
