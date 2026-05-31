/**
 * 用户管理接口封装（对接 CONTRACTS §6）
 */
import { request } from './request'
import { userMock } from './mock'
import { useMock } from './config'
import type { PageData } from '@/types/api'
import type {
  UserRow,
  UserListQuery,
  UserCreatePayload,
  UserUpdatePayload,
  PasswordPayload,
} from '@/types/user'

/** §6.1 列表（分页） */
export function getUsers(query: UserListQuery = {}): Promise<PageData<UserRow>> {
  if (useMock('users')) return userMock.list(query)
  return request<PageData<UserRow>>({ url: '/users', method: 'get', params: query })
}

/** §6.2 新建用户 */
export function createUser(payload: UserCreatePayload): Promise<UserRow> {
  if (useMock('users')) return userMock.create(payload)
  return request<UserRow>({ url: '/users', method: 'post', data: payload })
}

/** §6.3 修改用户 real_name / role / is_active */
export function updateUser(id: number, payload: UserUpdatePayload): Promise<UserRow> {
  if (useMock('users')) return userMock.update(id, payload)
  return request<UserRow>({ url: `/users/${id}`, method: 'put', data: payload })
}

/** §6.4 修改密码（admin 改他人 / 本人改密） */
export function changeUserPassword(id: number, payload: PasswordPayload): Promise<null> {
  if (useMock('users')) return userMock.changePassword(id, payload)
  return request<null>({ url: `/users/${id}/password`, method: 'put', data: payload })
}

/** §6.6 一键重置密码为系统默认值（123qwe），无请求体 */
export function resetUserPassword(id: number): Promise<null> {
  if (useMock('users')) return userMock.changePassword(id, { new_password: '123qwe' })
  return request<null>({ url: `/users/${id}/reset-password`, method: 'post' })
}

/** §6.5 软删除 */
export function deleteUser(id: number): Promise<null> {
  if (useMock('users')) return userMock.remove(id)
  return request<null>({ url: `/users/${id}`, method: 'delete' })
}
