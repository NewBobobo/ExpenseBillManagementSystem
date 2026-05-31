/**
 * 通用 API 类型定义
 * 对齐 CONTRACTS.md「约定」：统一响应包裹 + 分页结构
 */

/** 统一响应包裹：code=0 成功，非 0 为业务错误码 */
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

/** 分页响应 data 结构 */
export interface PageData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/** 业务错误码（对齐 CONTRACTS） */
export enum ApiCode {
  /** 成功 */
  OK = 0,
  /** 未登录 / Token 失效 */
  UNAUTHENTICATED = 40100,
  /** 用户名或密码错误（登录 / 改密旧密码错） */
  LOGIN_BAD_CREDENTIALS = 40101,
  /** 无权限 / 越权操作（角色不足，或操作非可见机构的数据，W2） */
  FORBIDDEN = 40300,
  /** 账号已停用 */
  ACCOUNT_DISABLED = 40301,
  /** 资源不存在（W2） */
  NOT_FOUND = 40400,
  /** 唯一冲突（机构 code / 用户名重复，W2） */
  CONFLICT = 40900,
  /** 删除受阻（机构下存在子机构或用户，W2） */
  DELETE_BLOCKED = 40901,
  /** 参数校验失败（W2） */
  VALIDATION = 42200,
}

