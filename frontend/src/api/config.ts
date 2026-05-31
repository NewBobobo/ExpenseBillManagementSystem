/**
 * 接口「就绪」开关：按模块控制走 mock 还是真实请求。
 *
 * 背景：W1（auth / orgs.tree）已与后端真实联调通过；W2 三组接口（机构 CRUD /
 * 用户管理 / 费用项）后端分批交付。用单一全局 VITE_USE_MOCK 会把已验证的 W1 也退回
 * mock，故改为「全局开关 + 按模块就绪标志」：
 *   - VITE_USE_MOCK=true  → 全部走 mock（后端完全没起时用）。
 *   - VITE_USE_MOCK=false → 按下面 BACKEND_READY 决定：某模块 true 走真实，false 仍走 mock。
 *
 * BE 在 LOG @FE 某模块就绪后，把对应项改 true 即可单独切真实联调。
 */
const GLOBAL_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

/** 各业务模块后端是否就绪（仅在 GLOBAL_MOCK=false 时生效） */
const BACKEND_READY = {
  /** W1 认证：已联调通过 */
  auth: true,
  /** W1 机构树读取：已联调通过 */
  orgTree: true,
  /** W2 §5 机构 CRUD（POST/PUT/DELETE/Logo）：BE T-009 已完成，B-002 已修复，后端已重启 */
  orgCrud: true,
  /** W2 §6 用户管理：BE T-010 已完成，后端已重启 */
  users: true,
  /** W2 §7 费用项字典：BE T-011 已完成，后端已重启 */
  expenseItems: true,
} as const

export type MockModule = keyof typeof BACKEND_READY

/** 给定模块当前是否应使用 mock */
export function useMock(module: MockModule): boolean {
  if (GLOBAL_MOCK) return true
  return !BACKEND_READY[module]
}
