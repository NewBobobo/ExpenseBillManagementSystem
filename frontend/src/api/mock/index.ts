/**
 * Mock 聚合入口
 * - 认证 mock（W1，仅 GLOBAL_MOCK=true 时使用，真实联调已通过）
 * - 机构树 mock 委托 orgMock.tree()，与机构 CRUD 共用内存 db 保持自洽
 * - W2 各模块 mock 从此处再导出，api/* 按模块就绪标志选择 mock / 真实
 *
 * 所有 mock 方法返回值与真实 request<T>() 一致：返回「已拆包裹的 data」。
 */
import { ApiCode } from '@/types/api'
import type { LoginPayload, LoginResult, UserInfo } from '@/types/user'
import type { OrgNode } from '@/types/org'
import { delay, bizError } from './helpers'
import { orgMock } from './orgs'

export { orgMock } from './orgs'
export { userMock } from './users'
export { expenseItemMock } from './expense-items'

/** Mock 账号表（对齐 CONTRACTS §1 user 结构） */
const MOCK_USERS: Record<string, { password: string; user: UserInfo; active: boolean }> = {
  admin: {
    password: '123456',
    active: true,
    user: { id: 1, username: 'admin', real_name: '管理员', role: 'admin', org_id: 1, org_name: '总部' },
  },
  zhangsan: {
    password: '123456',
    active: true,
    user: { id: 2, username: 'zhangsan', real_name: '张三', role: 'user', org_id: 3, org_name: '上海一店' },
  },
  disabled: {
    password: '123456',
    active: false,
    user: { id: 9, username: 'disabled', real_name: '停用账号', role: 'user', org_id: 3, org_name: '上海一店' },
  },
}

function tokenFor(username: string): string {
  return `mock-token.${username}.${Date.now()}`
}
function usernameFromToken(token: string): string | null {
  const parts = token.split('.')
  return parts[0] === 'mock-token' ? (parts[1] ?? null) : null
}

export const mockApi = {
  /** §1 POST /api/auth/login */
  login(payload: LoginPayload): Promise<LoginResult> {
    const rec = MOCK_USERS[payload.username]
    if (!rec || rec.password !== payload.password) {
      return bizError(ApiCode.LOGIN_BAD_CREDENTIALS, '用户名或密码错误')
    }
    if (!rec.active) return bizError(ApiCode.ACCOUNT_DISABLED, '账号已停用')
    return delay({ token: tokenFor(rec.user.username), user: rec.user })
  },

  /** §2 POST /api/auth/logout */
  logout(): Promise<null> {
    return delay(null, 100)
  },

  /** §3 GET /api/auth/me */
  getMe(): Promise<UserInfo> {
    const token = localStorage.getItem('ebms_token') || ''
    const username = usernameFromToken(token)
    const rec = username ? MOCK_USERS[username] : null
    if (!rec) return bizError(ApiCode.UNAUTHENTICATED, '未登录或 Token 失效')
    return delay(rec.user)
  },

  /** §4 GET /api/orgs/tree（委托给机构 CRUD mock，保持自洽） */
  getOrgTree(): Promise<OrgNode[]> {
    return orgMock.tree()
  },
}
