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
