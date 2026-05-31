/**
 * 机构类型定义
 * 对齐 CONTRACTS §4 GET /api/orgs/tree，及 03-database-design orgs 表
 */

/** 机构树节点（children 递归） */
export interface OrgNode {
  id: number
  code: string
  name: string
  /** 顶级为 null */
  parent_id: number | null
  /** 层级深度，根=0 */
  level: number
  /** Logo 文件路径，可为 null */
  logo_path: string | null
  /** 子节点数组，无子节点时为空数组 */
  children: OrgNode[]
}

/** 机构扁平对象（CRUD 接口返回，CONTRACTS §5.1） */
export interface Org {
  id: number
  code: string
  name: string
  parent_id: number | null
  /** 物化路径，如 /1/3/ */
  path: string
  level: number
  logo_path: string | null
  created_at: string
}

/** 新建子机构请求（§5.1） */
export interface OrgCreatePayload {
  parent_id: number
  code: string
  name: string
}

/** 修改机构请求（§5.2，字段均可选，至少一项） */
export interface OrgUpdatePayload {
  name?: string
  code?: string
}

