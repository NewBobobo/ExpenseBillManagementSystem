/**
 * 认证状态管理
 * - token 持久化（localStorage，key 与 request.ts 共用 TOKEN_KEY）
 * - 当前用户信息
 * - 登录 / 注销 / 拉取当前用户
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as authApi from '@/api/auth'
import { TOKEN_KEY } from '@/api/request'
import type { LoginPayload, UserInfo } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  /** 超级管理员：顶级机构(org_id=1)的管理员。用于「系统设置」可见性。 */
  const isSuperAdmin = computed(() => isAdmin.value && user.value?.org_id === 1)

  function setToken(t: string) {
    token.value = t
    localStorage.setItem(TOKEN_KEY, t)
  }

  function clear() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  /** 登录：保存 token + user */
  async function login(payload: LoginPayload) {
    const res = await authApi.login(payload)
    setToken(res.token)
    user.value = res.user
    return res.user
  }

  /** 注销：通知后端 + 清本地态（后端失败也要清本地） */
  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clear()
    }
  }

  /** 拉取当前用户（刷新页面后用 token 恢复用户信息） */
  async function fetchMe() {
    const me = await authApi.getMe()
    user.value = me
    return me
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    isSuperAdmin,
    setToken,
    clear,
    login,
    logout,
    fetchMe,
  }
})
