/**
 * Mock 公共工具：延迟、业务错误。
 * 业务错误的形态与 request 拦截器拒绝时一致（reject Error），并打 ElMessage，
 * 这样组件层 catch 逻辑在 mock 与真实模式下表现一致。
 */
import { ElMessage } from 'element-plus'

/** 模拟网络延迟后 resolve */
export function delay<T>(data: T, ms = 300): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms))
}

/**
 * 模拟业务错误码：弹 ElMessage + reject（与 request.ts 拦截器对非 0 码的处理一致）。
 */
export function bizError(code: number, message: string): Promise<never> {
  ElMessage.error(message)
  return Promise.reject(new Error(`[mock ${code}] ${message}`))
}
