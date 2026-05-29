# 架构决策记录 (ADR - Architecture Decision Record)

## 文档说明

本文档记录项目中的重要架构决策,包括决策背景、考虑的方案、最终选择及理由。

---

## ADR-001: 技术栈选型

**日期**: 2026-05-29  
**状态**: ✅ 已采纳  
**决策者**: 架构师

### 背景

需要为费用单管理系统选择合适的技术栈,要求:
- 开发效率高
- 易于维护
- 支持 Web 和单机双形态部署
- 团队学习成本可控

### 考虑的方案

#### 方案 1: Python FastAPI + Vue 3
- **优点**: FastAPI 开发快速,自动生成 API 文档;Vue 3 生态成熟,组件丰富
- **缺点**: Python 性能相对较低(但本项目不是性能瓶颈)

#### 方案 2: Node.js Express + React
- **优点**: 全栈 JavaScript,前后端统一语言
- **缺点**: Express 需要手动配置较多;React 学习曲线较陡

#### 方案 3: Java Spring Boot + Angular
- **优点**: 企业级成熟方案,性能好
- **缺点**: 开发效率低,配置复杂,打包体积大

### 决策

**选择方案 1: Python FastAPI + Vue 3**

### 理由

1. **开发效率**: FastAPI 自动数据校验、自动文档生成,开发速度快
2. **生态成熟**: Vue 3 + Element Plus 提供丰富的 UI 组件,减少开发量
3. **类型安全**: Pydantic + TypeScript 提供完整的类型检查
4. **PDF 生成**: Python 生态有成熟的 Playwright/ReportLab 方案
5. **单机部署**: Python 可通过 PyInstaller 打包,配合 Electron 实现桌面应用

### 后果

- ✅ 开发速度快,预计 5 周完成一期
- ✅ API 文档自动生成,前后端协作顺畅
- ⚠️ Python 性能相对较低,但本项目不是性能瓶颈
- ⚠️ 需要团队熟悉 Python 和 Vue 3

---

## ADR-002: 机构隔离方案

**日期**: 2026-05-29  
**状态**: ✅ 已采纳  
**决策者**: 架构师

### 背景

系统需要支持多机构层级隔离,要求:
- 同级机构完全隔离
- 管理员可向下穿透管理子机构
- 查询性能高

### 考虑的方案

#### 方案 1: 物化路径 (Materialized Path)
- **实现**: `path` 字段存储 `/1/3/7/`
- **查询**: `WHERE path LIKE '/1/2/%'`
- **优点**: 查询简单,性能好,索引友好
- **缺点**: 移动节点需要更新所有子节点的 path

#### 方案 2: 邻接表 (Adjacency List)
- **实现**: `parent_id` 字段指向父节点
- **查询**: 递归查询或 CTE
- **优点**: 移动节点简单
- **缺点**: 查询性能差,需要递归

#### 方案 3: 闭包表 (Closure Table)
- **实现**: 单独的关系表存储所有祖先-后代关系
- **查询**: JOIN 关系表
- **优点**: 查询性能好,移动节点简单
- **缺点**: 存储空间大,维护复杂

### 决策

**选择方案 1: 物化路径**

### 理由

1. **查询性能**: 单表查询,索引友好,性能最优
2. **实现简单**: 不需要额外的关系表
3. **业务特点**: 机构树变动频率低,移动节点的性能损耗可接受
4. **PostgreSQL 支持**: 原生支持 LIKE 索引优化

### 实现细节

```sql
-- 机构表
CREATE TABLE orgs (
  id BIGSERIAL PRIMARY KEY,
  parent_id BIGINT REFERENCES orgs(id),
  path VARCHAR(512),  -- 物化路径: /1/3/7/
  level SMALLINT,     -- 层级深度
  ...
);

-- 索引
CREATE INDEX idx_orgs_path ON orgs USING btree (path);

-- 查询本机构及所有下级
SELECT * FROM orgs WHERE path LIKE '/1/2/%';
```

### 后果

- ✅ 查询性能优秀,满足业务需求
- ✅ 实现简单,维护成本低
- ⚠️ 移动节点需要更新所有子节点,但业务场景少
- ⚠️ path 字段有长度限制,最多支持约 50 层(实际业务不会超过 10 层)

---

## ADR-003: 文件存储方案

**日期**: 2026-05-29  
**状态**: ✅ 已采纳 (一期),🔄 规划中 (二期)  
**决策者**: 架构师

### 背景

系统需要存储 Logo、公章、导出的 PDF/Excel 文件,要求:
- 一期快速上线
- 二期支持多服务器集群部署

### 考虑的方案

#### 方案 1: 本地磁盘存储
- **实现**: 文件存储在 `backend/storage/` 目录
- **优点**: 实现简单,开发快速
- **缺点**: 不支持多服务器集群,不适合云部署

#### 方案 2: 对象存储 (OSS/S3)
- **实现**: 文件上传到云存储服务
- **优点**: 支持集群,CDN 加速,可靠性高
- **缺点**: 需要外部服务,增加成本和复杂度

#### 方案 3: 数据库存储 (BLOB/BYTEA)
- **实现**: 文件以二进制或 Base64 存入数据库
- **优点**: 支持集群,数据一致性好,备份简单
- **缺点**: 数据库体积增大,查询性能略降

### 决策

**一期: 方案 1 (本地磁盘存储)**  
**二期: 方案 3 (数据库存储)**

### 理由

**一期选择本地磁盘**
1. **快速上线**: 实现简单,无需额外配置
2. **单机部署**: 一期主要面向单机 Electron 部署,本地存储最合适
3. **开发效率**: 减少一期开发复杂度

**二期迁移到数据库**
1. **集群支持**: 支持多服务器部署
2. **数据一致性**: 文件和元数据在同一事务中
3. **备份简单**: 数据库备份即包含文件
4. **成本可控**: 不需要额外的对象存储服务

### 实现细节

**一期: 本地存储**
```python
# 文件路径
STORAGE_PATH = "./storage"
LOGO_PATH = f"{STORAGE_PATH}/logos"
SEAL_PATH = f"{STORAGE_PATH}/seals"
EXPORT_PATH = f"{STORAGE_PATH}/exports"

# 文件命名
filename = f"{org_id}_{timestamp}.png"
```

**二期: 数据库存储**
```sql
-- 表结构调整
ALTER TABLE orgs ADD COLUMN logo_data BYTEA;
ALTER TABLE seals ADD COLUMN image_data BYTEA;

-- API 返回文件流
@app.get("/api/orgs/{id}/logo")
def get_logo(id: int):
    org = db.query(Org).filter(Org.id == id).first()
    return Response(content=org.logo_data, media_type="image/png")
```

### 后果

- ✅ 一期快速上线,满足单机部署需求
- ✅ 二期平滑迁移,支持集群部署
- ⚠️ 一期不支持多服务器,需在文档中说明
- ⚠️ 二期迁移需要数据迁移脚本

---

## ADR-004: 模板系统设计

**日期**: 2026-05-29  
**状态**: ✅ 已采纳  
**决策者**: 架构师

### 背景

系统需要支持自定义单据打印样式,要求:
- 各机构可独立定制
- 支持导入导出
- 前端预览,后端生成 PDF

### 考虑的方案

#### 方案 1: XML 模板 + 解析器
- **实现**: 模板用 XML 定义,前后端各实现解析器
- **优点**: 结构清晰,易于解析,支持导入导出
- **缺点**: 需要实现两套解析器(前端 TS + 后端 Python)

#### 方案 2: JSON 模板 + 渲染引擎
- **实现**: 模板用 JSON 定义,前后端共用渲染逻辑
- **优点**: 前后端可共享部分代码
- **缺点**: JSON 不适合表达复杂的嵌套结构

#### 方案 3: HTML 模板 + 模板引擎
- **实现**: 模板直接用 HTML + Jinja2/Handlebars
- **优点**: 灵活性最高
- **缺点**: 安全风险(XSS),用户难以编辑

### 决策

**选择方案 1: XML 模板 + 解析器**

### 理由

1. **结构化**: XML 天然适合表达层级结构(页面/表头/表格/表尾)
2. **可读性**: XML 标签语义清晰,易于理解和维护
3. **导入导出**: XML 文件可直接导入导出,便于跨机构复用
4. **安全性**: 解析器只支持预定义的标签,避免 XSS 风险
5. **编辑器**: 一期提供表单式编辑器,二期可扩展为可视化拖拽

### 实现细节

**XML 结构**
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
      </columns>
    </table>
  </body>
  <footer>
    <seal x="420" y="-30" width="100" height="100"/>
  </footer>
</template>
```

**前端解析器** (TypeScript)
```typescript
class XmlParser {
  parse(xml: string): TemplateObject {
    const parser = new DOMParser()
    const doc = parser.parseFromString(xml, 'text/xml')
    return this.parseNode(doc.documentElement)
  }
}
```

**后端解析器** (Python)
```python
import xml.etree.ElementTree as ET

class XmlParser:
    def parse(self, xml: str) -> dict:
        root = ET.fromstring(xml)
        return self.parse_node(root)
```

### 后果

- ✅ 模板结构清晰,易于维护
- ✅ 支持导入导出,便于复用
- ✅ 安全性高,避免 XSS 风险
- ⚠️ 需要实现两套解析器,增加开发量(但逻辑相似,可复用设计)
- ⚠️ 一期编辑器为表单式,灵活性有限(二期可扩展)

---

## ADR-005: PDF 生成方案

**日期**: 2026-05-29  
**状态**: ✅ 已采纳  
**决策者**: 架构师

### 背景

系统需要将单据导出为 PDF,要求:
- 样式还原度高
- 支持中文
- 性能可接受

### 考虑的方案

#### 方案 1: Playwright (无头浏览器)
- **实现**: HTML → Playwright → PDF
- **优点**: 样式还原度 100%,支持复杂布局,支持中文
- **缺点**: 依赖浏览器,启动慢,资源占用高

#### 方案 2: ReportLab (Python PDF 库)
- **实现**: 代码绘制 PDF
- **优点**: 性能好,资源占用低
- **缺点**: 中文支持复杂,样式还原度低,开发量大

#### 方案 3: WeasyPrint (HTML to PDF)
- **实现**: HTML + CSS → PDF
- **优点**: 支持 HTML/CSS,中文支持好
- **缺点**: CSS 支持不完整,复杂布局可能失真

### 决策

**选择方案 1: Playwright**

### 理由

1. **样式还原**: 浏览器渲染,100% 还原 HTML/CSS 样式
2. **中文支持**: 浏览器原生支持中文字体
3. **开发效率**: 前端预览和后端 PDF 使用相同的 HTML,减少调试成本
4. **灵活性**: 支持复杂布局(表格/图片/公章旋转/透明度)
5. **性能可接受**: 单据生成频率不高,启动慢可接受

### 实现细节

```python
from playwright.sync_api import sync_playwright

def generate_pdf(html: str, output_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(
            path=output_path,
            format='A4',
            print_background=True,
            margin={'top': '20mm', 'bottom': '20mm'}
        )
        browser.close()
```

### 优化策略

1. **浏览器复用**: 启动一次浏览器,复用多次生成
2. **异步生成**: 使用后台任务队列,避免阻塞请求
3. **缓存**: 相同单据的 PDF 缓存,避免重复生成
4. **定时清理**: 定时清理临时 PDF 文件

### 后果

- ✅ 样式还原度高,用户体验好
- ✅ 开发效率高,前后端共用 HTML
- ⚠️ 首次启动慢(约 2-3 秒),但可通过浏览器复用优化
- ⚠️ 资源占用较高,需要合理配置服务器

---

## ADR-006: 认证与授权方案

**日期**: 2026-05-29  
**状态**: ✅ 已采纳  
**决策者**: 架构师

### 背景

系统需要用户认证和权限控制,要求:
- 无状态认证(支持集群)
- 支持角色权限
- 支持机构隔离

### 考虑的方案

#### 方案 1: JWT (JSON Web Token)
- **实现**: 用户登录后返回 JWT,前端每次请求携带
- **优点**: 无状态,支持集群,前端实现简单
- **缺点**: Token 无法主动失效(需黑名单)

#### 方案 2: Session + Redis
- **实现**: 用户登录后创建 Session,存储在 Redis
- **优点**: 可主动失效,安全性高
- **缺点**: 需要 Redis,增加部署复杂度

#### 方案 3: OAuth 2.0
- **实现**: 使用第三方认证服务
- **优点**: 标准化,支持第三方登录
- **缺点**: 复杂度高,不适合内部系统

### 决策

**选择方案 1: JWT**

### 理由

1. **无状态**: 支持多服务器集群,无需共享 Session
2. **简单**: 实现简单,前端只需在请求头携带 Token
3. **性能**: 无需查询 Redis,性能好
4. **业务特点**: 内部系统,Token 失效需求不强(可通过短有效期 + 刷新机制)

### 实现细节

**Token 结构**
```json
{
  "sub": "user_id",
  "username": "admin",
  "org_id": 1,
  "role": "admin",
  "exp": 1234567890
}
```

**认证流程**
```
用户登录
  ↓
验证用户名密码
  ↓
生成 JWT Token (有效期 24 小时)
  ↓
返回 Token 给前端
  ↓
前端存储 Token (LocalStorage)
  ↓
每次请求携带 Token (Authorization: Bearer <token>)
  ↓
后端验证 Token
  ↓
从 Token 中提取用户信息
  ↓
权限校验
```

**权限校验**
```python
# 依赖注入
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    return db.query(User).filter(User.id == user_id).first()

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "权限不足")
    return user
```

### 后果

- ✅ 实现简单,性能好
- ✅ 支持集群部署
- ⚠️ Token 无法主动失效(可通过短有效期缓解)
- ⚠️ Token 泄露风险(需 HTTPS + 短有效期)

---

## ADR-007: 前端状态管理方案

**日期**: 2026-05-29  
**状态**: ✅ 已采纳  
**决策者**: 架构师

### 背景

前端需要管理全局状态(用户信息、机构上下文、字典数据),要求:
- 类型安全
- 易于调试
- 支持持久化

### 考虑的方案

#### 方案 1: Pinia
- **优点**: Vue 3 官方推荐,类型安全,DevTools 支持好
- **缺点**: 相对较新,社区资源少于 Vuex

#### 方案 2: Vuex 4
- **优点**: 社区成熟,资源丰富
- **缺点**: TypeScript 支持不如 Pinia,写法繁琐

#### 方案 3: Provide/Inject + Composition API
- **优点**: 原生方案,无需额外依赖
- **缺点**: 无 DevTools 支持,调试困难

### 决策

**选择方案 1: Pinia**

### 理由

1. **官方推荐**: Vue 3 官方推荐的状态管理方案
2. **类型安全**: 完整的 TypeScript 支持
3. **简洁**: 写法简单,无需 mutations
4. **DevTools**: 完整的 Vue DevTools 支持
5. **持久化**: 插件支持 LocalStorage 持久化

### 实现细节

**认证状态**
```typescript
// stores/auth.ts
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as User | null
  }),
  
  actions: {
    async login(username: string, password: string) {
      const res = await api.login(username, password)
      this.token = res.token
      this.user = res.user
      localStorage.setItem('token', res.token)
    },
    
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    }
  },
  
  getters: {
    isAdmin: (state) => state.user?.role === 'admin'
  }
})
```

### 后果

- ✅ 类型安全,开发体验好
- ✅ 调试方便,DevTools 支持完整
- ✅ 代码简洁,易于维护
- ⚠️ 社区资源相对较少(但官方文档完善)

---

## 总结

本文档记录了项目中的 7 个核心架构决策:

1. **技术栈**: Python FastAPI + Vue 3
2. **机构隔离**: 物化路径方案
3. **文件存储**: 一期本地磁盘,二期数据库
4. **模板系统**: XML 模板 + 解析器
5. **PDF 生成**: Playwright 无头浏览器
6. **认证授权**: JWT 无状态认证
7. **状态管理**: Pinia

这些决策共同构成了项目的技术基础,后续开发应遵循这些决策,如需调整应更新本文档。

---

**文档版本**: v1.0  
**最后更新**: 2026-05-29  
**维护者**: 架构师