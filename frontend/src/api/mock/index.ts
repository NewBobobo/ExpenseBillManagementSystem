/**
 * Mock 数据与模拟请求
 * 后端未就绪期间，FE 按 CONTRACTS §1-§4 字段开发用。
 * 待 BE 在 LOG @FE 接口就绪后，将 .env 的 VITE_USE_MOCK 关掉即可切真实请求。
 *
 * 所有 mock 方法的返回值与真实 request<T>() 一致：返回「已拆包裹的 data」。
 */
import { ApiCode } from '@/types/api'
import type { LoginPayload, LoginResult, UserInfo } from '@/types/user'
import type { OrgNode } from '@/types/org'

/** 模拟网络延迟 */
function delay<T>(data: T, ms = 300): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms))
}

/** 业务错误：模拟非 0 错误码被拦截器 reject 的效果 */
function bizError(code: number, message: string): Promise<never> {
  return Promise.reject(new Error(`[mock ${code}] ${message}`))
}

/** Mock 账号表（对齐 CONTRACTS §1 user 结构） */
const MOCK_USERS: Record<string, { password: string; user: UserInfo; active: boolean }> = {
  admin: {
    password: '123456',
    active: true,
    user: {
      id: 1,
      username: 'admin',
      real_name: '管理员',
      role: 'admin',
      org_id: 1,
      org_name: '总部',
    },
  },
  zhangsan: {
    password: '123456',
    active: true,
    user: {
      id: 2,
      username: 'zhangsan',
      real_name: '张三',
      role: 'user',
      org_id: 3,
      org_name: '上海一店',
    },
  },
  disabled: {
    password: '123456',
    active: false,
    user: {
      id: 9,
      username: 'disabled',
      real_name: '停用账号',
      role: 'user',
      org_id: 3,
      org_name: '上海一店',
    },
  },
}

/** mock token → username 反查，支撑 getMe */
function tokenFor(username: string): string {
  return `mock-token.${username}.${Date.now()}`
}
function usernameFromToken(token: string): string | null {
  const parts = token.split('.')
  return parts[0] === 'mock-token' ? parts[1] ?? null : null
}

export const mockApi = {
  /** §1 POST /api/auth/login */
  login(payload: LoginPayload): Promise<LoginResult> {
    const rec = MOCK_USERS[payload.username]
    if (!rec || rec.password !== payload.password) {
      return bizError(ApiCode.LOGIN_BAD_CREDENTIALS, '用户名或密码错误')
    }
    if (!rec.active) {
      return bizError(ApiCode.ACCOUNT_DISABLED, '账号已停用')
    }
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
    if (!rec) {
      return bizError(ApiCode.UNAUTHENTICATED, '未登录或 Token 失效')
    }
    return delay(rec.user)
  },

  /** §4 GET /api/orgs/tree */
  getOrgTree(): Promise<OrgNode[]> {
    const tree: OrgNode[] = [
      {
        id: 1,
        code: 'HQ',
        name: '总部',
        parent_id: null,
        level: 0,
        logo_path: '/storage/logos/1_demo.png',
        children: [
          {
            id: 3,
            code: 'SH001',
            name: '上海一店',
            parent_id: 1,
            level: 1,
            logo_path: null,
            children: [
              {
                id: 7,
                code: 'SH001-A',
                name: '上海一店-浦东专柜',
                parent_id: 3,
                level: 2,
                logo_path: null,
                children: [],
              },
            ],
          },
          {
            id: 4,
            code: 'BJ001',
            name: '北京一店',
            parent_id: 1,
            level: 1,
            logo_path: null,
            children: [],
          },
        ],
      },
    ]
    return delay(tree)
  },
}
