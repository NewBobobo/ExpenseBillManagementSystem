/**
 * 机构接口封装（对接 CONTRACTS §4）
 */
import { request } from './request'
import { mockApi } from './mock'
import type { OrgNode } from '@/types/org'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

/** §4 获取当前用户可见的机构树 */
export function getOrgTree(): Promise<OrgNode[]> {
  if (USE_MOCK) return mockApi.getOrgTree()
  return request<OrgNode[]>({
    url: '/orgs/tree',
    method: 'get',
  })
}
