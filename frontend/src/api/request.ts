/**
 * Axios 实例封装
 * - 请求拦截器：注入 JWT Bearer Token
 * - 响应拦截器：拆解统一响应包裹 {code, message, data}，统一错误处理
 * - 401 / Token 失效：清登录态并跳登录页
 *
 * 契约见 CONTRACTS.md「约定」：统一响应 {code,message,data}，code=0 成功。
 */
import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios'
import { ElMessage } from 'element-plus'
import { ApiCode, type ApiResponse } from '@/types/api'

/** 本地存储 token 的 key（与 auth store 共用） */
export const TOKEN_KEY = 'ebms_token'

const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截器：注入 token
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

/**
 * 处理「未认证」：清 token 并跳登录页。
 * 用动态 import 规避循环依赖（store 依赖 request）。
 */
function handleUnauthenticated() {
  localStorage.removeItem(TOKEN_KEY)
  // 避免在登录页重复跳转
  if (!location.pathname.startsWith('/login')) {
    const redirect = encodeURIComponent(location.pathname + location.search)
    location.href = `/login?redirect=${redirect}`
  }
}

// 响应拦截器：拆包裹 + 统一错误
service.interceptors.response.use(
  (response) => {
    const res = response.data as ApiResponse
    // 文件下载等非标准包裹场景：直接透传
    if (res === null || typeof res !== 'object' || !('code' in res)) {
      return response.data
    }
    if (res.code === ApiCode.OK) {
      return res.data
    }
    // 未登录 / Token 失效
    if (res.code === ApiCode.UNAUTHENTICATED) {
      handleUnauthenticated()
    }
    ElMessage.error(res.message || '请求失败')
    return Promise.reject(new Error(res.message || `业务错误码 ${res.code}`))
  },
  (error) => {
    // HTTP 层错误
    const status = error?.response?.status
    if (status === 401) {
      handleUnauthenticated()
      ElMessage.error('登录已失效，请重新登录')
    } else {
      const msg = error?.response?.data?.message || error.message || '网络异常'
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  },
)

/**
 * 统一请求方法。返回已拆包裹的 data（泛型 T）。
 */
export function request<T = unknown>(config: AxiosRequestConfig): Promise<T> {
  return service.request<unknown, T>(config)
}

export default service
