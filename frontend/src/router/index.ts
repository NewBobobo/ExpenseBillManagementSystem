/**
 * 路由配置 + 全局守卫
 * - 未登录访问受保护页 → 跳登录页（带 redirect）
 * - 已登录访问登录页 → 跳工作台
 * - 刷新后用 token 恢复用户信息（fetchMe）
 * - 按角色拦截 meta.roles（admin / superAdmin）
 *
 * 路由表对应 08-feature-spec 菜单结构；W1 先落地 login / dashboard / orgs，
 * 其余页面随排期补充。
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '工作台', icon: 'Monitor' },
      },
      {
        path: 'expense-items',
        name: 'expense-items',
        component: () => import('@/views/expense-items/ExpenseItemList.vue'),
        meta: { title: '费用项字典', icon: 'Files' },
      },
      {
        path: 'orgs',
        name: 'orgs',
        component: () => import('@/views/orgs/OrgTree.vue'),
        meta: { title: '机构管理', icon: 'OfficeBuilding', roles: ['admin'] },
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/users/UserList.vue'),
        meta: { title: '用户管理', icon: 'User', roles: ['admin'] },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/error/NotFound.vue'),
    meta: { public: true, title: '页面不存在' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // 公开页：已登录访问登录页则回工作台
  if (to.meta.public) {
    if (to.name === 'login' && auth.isLoggedIn) {
      return { name: 'dashboard' }
    }
    return true
  }

  // 受保护页：无 token → 登录页
  if (!auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // 有 token 但无用户信息（刷新场景）：恢复
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.clear()
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }

  // 角色拦截
  const roles = to.meta.roles as string[] | undefined
  if (roles?.length) {
    const ok =
      (roles.includes('admin') && auth.isAdmin) ||
      (roles.includes('superAdmin') && auth.isSuperAdmin)
    if (!ok) return { name: 'dashboard' }
  }

  return true
})

router.afterEach((to) => {
  const base = '费用单管理系统'
  document.title = to.meta.title ? `${to.meta.title} - ${base}` : base
})

export default router
