/**
 * 机构 CRUD mock（CONTRACTS §5）
 * 维护扁平 orgs 列表 + 由其重建机构树；新建回填 path/level；
 * 删除校验无子机构/无用户（40901）；code 唯一（40900）。
 */
import { ApiCode } from '@/types/api'
import { orgs, users, nextId, now } from './db'
import { delay, bizError } from './helpers'
import type { Org, OrgNode, OrgCreatePayload, OrgUpdatePayload } from '@/types/org'

/** 由扁平 orgs 重建机构树（供 §4 tree 读取走 mock 时复用，保证与 CRUD 一致） */
export function buildTree(): OrgNode[] {
  const byId = new Map<number, OrgNode>()
  const sorted = orgs.slice().sort((a, b) => a.level - b.level || a.id - b.id)
  for (const o of sorted) {
    byId.set(o.id, {
      id: o.id,
      code: o.code,
      name: o.name,
      parent_id: o.parent_id,
      level: o.level,
      logo_path: o.logo_path,
      children: [],
    })
  }
  const roots: OrgNode[] = []
  for (const o of sorted) {
    const node = byId.get(o.id)!
    if (o.parent_id == null) {
      roots.push(node)
    } else {
      byId.get(o.parent_id)?.children.push(node)
    }
  }
  return roots
}

export const orgMock = {
  /** §4 机构树（mock 模式下与 CRUD 自洽） */
  tree(): Promise<OrgNode[]> {
    return delay(buildTree())
  },

  /** §5.1 新建子机构（回填 path/level） */
  create(payload: OrgCreatePayload): Promise<Org> {
    if (!payload.name?.trim()) return bizError(ApiCode.VALIDATION, '机构名称必填')
    if (!payload.code?.trim()) return bizError(ApiCode.VALIDATION, '机构编号必填')
    const parent = orgs.find((o) => o.id === payload.parent_id)
    if (!parent) return bizError(ApiCode.NOT_FOUND, '上级机构不存在')
    if (orgs.some((o) => o.code === payload.code)) {
      return bizError(ApiCode.CONFLICT, '机构编号已存在')
    }
    const id = nextId()
    const row: Org = {
      id,
      code: payload.code.trim(),
      name: payload.name.trim(),
      parent_id: parent.id,
      path: `${parent.path}${id}/`,
      level: parent.level + 1,
      logo_path: null,
      created_at: now(),
    }
    orgs.push(row)
    return delay({ ...row })
  },

  /** §5.2 改 name / code */
  update(id: number, payload: OrgUpdatePayload): Promise<Org> {
    const row = orgs.find((o) => o.id === id)
    if (!row) return bizError(ApiCode.NOT_FOUND, '机构不存在')
    if (payload.code !== undefined && payload.code !== row.code) {
      if (orgs.some((o) => o.code === payload.code && o.id !== id)) {
        return bizError(ApiCode.CONFLICT, '机构编号已存在')
      }
      row.code = payload.code.trim()
    }
    if (payload.name !== undefined) row.name = payload.name.trim()
    return delay({ ...row })
  },

  /** §5.3 删除（无子机构、无用户才可删） */
  remove(id: number): Promise<null> {
    const idx = orgs.findIndex((o) => o.id === id)
    if (idx < 0) return bizError(ApiCode.NOT_FOUND, '机构不存在')
    if (orgs.some((o) => o.parent_id === id)) {
      return bizError(ApiCode.DELETE_BLOCKED, '该机构存在子机构，无法删除')
    }
    if (users.some((u) => u.org_id === id)) {
      return bizError(ApiCode.DELETE_BLOCKED, '该机构下存在用户，无法删除')
    }
    orgs.splice(idx, 1)
    return delay(null)
  },

  /** §5.4 上传/更换 Logo（mock 用 DataURL 模拟回写路径） */
  uploadLogo(id: number, file: File): Promise<{ logo_path: string }> {
    const row = orgs.find((o) => o.id === id)
    if (!row) return bizError(ApiCode.NOT_FOUND, '机构不存在')
    if (file.size > 2 * 1024 * 1024) return bizError(ApiCode.VALIDATION, 'Logo 不能超过 2MB')
    return new Promise((resolve) => {
      const reader = new FileReader()
      reader.onload = () => {
        const path = String(reader.result) // DataURL，mock 下直接可显示
        row.logo_path = path
        setTimeout(() => resolve({ logo_path: path }), 200)
      }
      reader.readAsDataURL(file)
    })
  },
}
