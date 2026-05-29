/**
 * 权限判断组合式函数
 * 统一菜单 / 按钮级的角色可见性判断，避免逻辑散落各组件。
 */
import { useAuthStore } from '@/stores/auth'

export function usePermission() {
  const auth = useAuthStore()

  /** 当前用户是否满足给定角色要求（roles 为空 = 所有登录用户可见） */
  function canAccess(roles?: Array<'admin' | 'superAdmin'>): boolean {
    if (!roles || roles.length === 0) return true
    return roles.some((r) => {
      if (r === 'admin') return auth.isAdmin
      if (r === 'superAdmin') return auth.isSuperAdmin
      return false
    })
  }

  return {
    canAccess,
    isAdmin: auth.isAdmin,
    isSuperAdmin: auth.isSuperAdmin,
  }
}
