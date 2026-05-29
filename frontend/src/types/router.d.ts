/**
 * vue-router meta 字段类型增强
 */
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    /** 公开页，无需登录 */
    public?: boolean
    /** 浏览器标题 / 菜单文字 */
    title?: string
    /** 菜单图标（Element Plus 图标组件名） */
    icon?: string
    /** 允许的角色：'admin' | 'superAdmin'，为空表示所有登录用户 */
    roles?: Array<'admin' | 'superAdmin'>
  }
}
