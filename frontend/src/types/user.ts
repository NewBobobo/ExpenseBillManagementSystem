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

/** 用户列表/详情对象（CONTRACTS §6.1，无 password_hash） */
export interface UserRow {
  id: number
  username: string
  real_name: string
  role: UserRole
  org_id: number
  org_name: string
  is_active: boolean
  created_at: string
}

/** 用户列表查询参数（§6.1） */
export interface UserListQuery {
  org_id?: number
  keyword?: string
  page?: number
  page_size?: number
}

/** 新建用户请求（§6.2） */
export interface UserCreatePayload {
  username: string
  password: string
  real_name: string
  org_id: number
  role: UserRole
}

/** 修改用户请求（§6.3，均可选；不允许改 username/org_id） */
export interface UserUpdatePayload {
  real_name?: string
  role?: UserRole
  is_active?: boolean
}

/** 改密码请求（§6.4）。admin 重置他人只传 new_password；本人改密两者都传。 */
export interface PasswordPayload {
  old_password?: string
  new_password: string
}

