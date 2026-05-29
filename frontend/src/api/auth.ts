/**
 * 认证接口封装（对接 CONTRACTS §1-§3）
 * 通过 VITE_USE_MOCK 在 mock / 真实请求间切换，调用方无感知。
 */
import { request } from './request'
import { mockApi } from './mock'
import type { LoginPayload, LoginResult, UserInfo } from '@/types/user'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

/** §1 登录 */
export function login(payload: LoginPayload): Promise<LoginResult> {
  if (USE_MOCK) return mockApi.login(payload)
  return request<LoginResult>({
    url: '/auth/login',
    method: 'post',
    data: payload,
  })
}

/** §2 注销 */
export function logout(): Promise<null> {
  if (USE_MOCK) return mockApi.logout()
  return request<null>({
    url: '/auth/logout',
    method: 'post',
  })
}

/** §3 获取当前用户 */
export function getMe(): Promise<UserInfo> {
  if (USE_MOCK) return mockApi.getMe()
  return request<UserInfo>({
    url: '/auth/me',
    method: 'get',
  })
}
