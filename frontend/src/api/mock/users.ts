/**
 * 用户管理 mock（CONTRACTS §6）
 * 分页 + 机构筛选 + 关键字；增删改、改密在内存 db 持久化。绝不返回密码。
 */
import { ApiCode } from '@/types/api'
import type { PageData } from '@/types/api'
import { users, passwords, orgs, nextId, now } from './db'
import { delay, bizError } from './helpers'
import type {
  UserRow,
  UserListQuery,
  UserCreatePayload,
  UserUpdatePayload,
  PasswordPayload,
} from '@/types/user'

function orgName(orgId: number): string {
  return orgs.find((o) => o.id === orgId)?.name ?? ''
}

export const userMock = {
  /** §6.1 列表（分页） */
  list(query: UserListQuery = {}): Promise<PageData<UserRow>> {
    const page = query.page ?? 1
    const pageSize = query.page_size ?? 20
    let rows = users.slice()
    if (query.org_id != null) rows = rows.filter((u) => u.org_id === query.org_id)
    if (query.keyword?.trim()) {
      const kw = query.keyword.trim().toLowerCase()
      rows = rows.filter(
        (u) =>
          u.username.toLowerCase().includes(kw) || u.real_name.toLowerCase().includes(kw),
      )
    }
    const total = rows.length
    const start = (page - 1) * pageSize
    const items = rows.slice(start, start + pageSize).map((u) => ({ ...u }))
    return delay({ items, total, page, page_size: pageSize })
  },

  /** §6.2 新建 */
  create(payload: UserCreatePayload): Promise<UserRow> {
    if (!payload.username?.trim()) return bizError(ApiCode.VALIDATION, '用户名必填')
    if (!payload.password) return bizError(ApiCode.VALIDATION, '初始密码必填')
    if (users.some((u) => u.username === payload.username)) {
      return bizError(ApiCode.CONFLICT, '用户名已存在')
    }
    const row: UserRow = {
      id: nextId(),
      username: payload.username.trim(),
      real_name: payload.real_name?.trim() || payload.username,
      role: payload.role,
      org_id: payload.org_id,
      org_name: orgName(payload.org_id),
      is_active: true,
      created_at: now(),
    }
    users.push(row)
    passwords[row.id] = payload.password
    return delay({ ...row })
  },

  /** §6.3 修改 real_name / role / is_active */
  update(id: number, payload: UserUpdatePayload): Promise<UserRow> {
    const row = users.find((u) => u.id === id)
    if (!row) return bizError(ApiCode.NOT_FOUND, '用户不存在')
    if (payload.real_name !== undefined) row.real_name = payload.real_name.trim()
    if (payload.role !== undefined) row.role = payload.role
    if (payload.is_active !== undefined) row.is_active = payload.is_active
    return delay({ ...row })
  },

  /** §6.4 改密码 */
  changePassword(id: number, payload: PasswordPayload): Promise<null> {
    const row = users.find((u) => u.id === id)
    if (!row) return bizError(ApiCode.NOT_FOUND, '用户不存在')
    // 本人改密（带 old_password）须校验旧密码；admin 重置则只传 new_password
    if (payload.old_password !== undefined && passwords[id] !== payload.old_password) {
      return bizError(ApiCode.LOGIN_BAD_CREDENTIALS, '旧密码错误')
    }
    if (!payload.new_password) return bizError(ApiCode.VALIDATION, '新密码必填')
    passwords[id] = payload.new_password
    return delay(null)
  },

  /** §6.5 软删除（设 is_active=false） */
  remove(id: number): Promise<null> {
    const row = users.find((u) => u.id === id)
    if (!row) return bizError(ApiCode.NOT_FOUND, '用户不存在')
    row.is_active = false
    return delay(null)
  },
}
