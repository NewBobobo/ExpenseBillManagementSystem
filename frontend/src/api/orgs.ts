/**
 * 机构接口封装（W1 §4 树 + W2 §5 CRUD/Logo）
 * 树读取走 useMock('orgTree')；CRUD/Logo 走 useMock('orgCrud')，可分批切真实。
 */
import { request } from './request'
import { mockApi, orgMock } from './mock'
import { useMock } from './config'
import type { OrgNode, Org, OrgCreatePayload, OrgUpdatePayload } from '@/types/org'

/** §4 获取当前用户可见的机构树 */
export function getOrgTree(): Promise<OrgNode[]> {
  if (useMock('orgTree')) return mockApi.getOrgTree()
  return request<OrgNode[]>({ url: '/orgs/tree', method: 'get' })
}

/** §5.1 新建子机构 */
export function createOrg(payload: OrgCreatePayload): Promise<Org> {
  if (useMock('orgCrud')) return orgMock.create(payload)
  return request<Org>({ url: '/orgs', method: 'post', data: payload })
}

/** §5.2 修改机构 name / code */
export function updateOrg(id: number, payload: OrgUpdatePayload): Promise<Org> {
  if (useMock('orgCrud')) return orgMock.update(id, payload)
  return request<Org>({ url: `/orgs/${id}`, method: 'put', data: payload })
}

/** §5.3 删除机构 */
export function deleteOrg(id: number): Promise<null> {
  if (useMock('orgCrud')) return orgMock.remove(id)
  return request<null>({ url: `/orgs/${id}`, method: 'delete' })
}

/** §5.4 上传/更换 Logo（multipart/form-data，字段名 file） */
export function uploadOrgLogo(id: number, file: File): Promise<{ logo_path: string }> {
  if (useMock('orgCrud')) return orgMock.uploadLogo(id, file)
  const form = new FormData()
  form.append('file', file)
  return request<{ logo_path: string }>({
    url: `/orgs/${id}/logo`,
    method: 'put',
    data: form,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
