/**
 * 认证接口封装（对接 CONTRACTS §1-§3）
 * 通过 useMock('auth') 在 mock / 真实请求间切换，调用方无感知。
 */
import { request } from './request'
import { mockApi } from './mock'
import { useMock } from './config'
import type { LoginPayload, LoginResult, UserInfo } from '@/types/user'

/** §1 登录 */
export function login(payload: LoginPayload): Promise<LoginResult> {
  if (useMock('auth')) return mockApi.login(payload)
  return request<LoginResult>({ url: '/auth/login', method: 'post', data: payload })
}

/** §2 注销 */
export function logout(): Promise<null> {
  if (useMock('auth')) return mockApi.logout()
  return request<null>({ url: '/auth/logout', method: 'post' })
}

/** §3 获取当前用户 */
export function getMe(): Promise<UserInfo> {
  if (useMock('auth')) return mockApi.getMe()
  return request<UserInfo>({ url: '/auth/me', method: 'get' })
}
