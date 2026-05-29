/**
 * 用户类型定义
 * 对齐 CONTRACTS §1 / §3 的 user 对象，及 03-database-design users 表
 */

/** 角色：管理员 / 普通用户 */
export type UserRole = 'admin' | 'user'

/** 当前登录用户信息（登录响应 user + /auth/me 同构） */
export interface UserInfo {
  id: number
  username: string
  real_name: string
  role: UserRole
  org_id: number
  org_name: string
}

/** 登录请求体（CONTRACTS §1） */
export interface LoginPayload {
  username: string
  password: string
}

/** 登录成功响应 data（CONTRACTS §1） */
export interface LoginResult {
  token: string
  user: UserInfo
}
