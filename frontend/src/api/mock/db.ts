/**
 * Mock 内存数据库（有状态）
 * W2 的增删改在内存中持久化，使列表/树在同一会话内自洽，便于端到端 UI 验证。
 * 刷新页面即重置为种子数据。
 */
import type { Org } from '@/types/org'
import type { UserRow } from '@/types/user'
import type { ExpenseItem } from '@/types/expense-item'

/** 机构（扁平，含 path/level 用于物化路径判定） */
export const orgs: Org[] = [
  { id: 1, code: 'HQ', name: '总部', parent_id: null, path: '/1/', level: 0, logo_path: '/storage/logos/1_demo.png', created_at: '2026-05-29 10:00:00' },
  { id: 3, code: 'SH001', name: '上海一店', parent_id: 1, path: '/1/3/', level: 1, logo_path: null, created_at: '2026-05-29 10:05:00' },
  { id: 7, code: 'SH001-A', name: '上海一店-浦东专柜', parent_id: 3, path: '/1/3/7/', level: 2, logo_path: null, created_at: '2026-05-29 10:06:00' },
  { id: 4, code: 'BJ001', name: '北京一店', parent_id: 1, path: '/1/4/', level: 1, logo_path: null, created_at: '2026-05-29 10:07:00' },
]

/** 用户（不含 password，密码另存以模拟改密/校验） */
export const users: UserRow[] = [
  { id: 1, username: 'admin', real_name: '管理员', role: 'admin', org_id: 1, org_name: '总部', is_active: true, created_at: '2026-05-29 10:00:00' },
  { id: 2, username: 'zhangsan', real_name: '张三', role: 'user', org_id: 3, org_name: '上海一店', is_active: true, created_at: '2026-05-29 11:00:00' },
  { id: 5, username: 'lisi', real_name: '李四', role: 'admin', org_id: 3, org_name: '上海一店', is_active: true, created_at: '2026-05-29 11:30:00' },
  { id: 9, username: 'disabled', real_name: '停用账号', role: 'user', org_id: 3, org_name: '上海一店', is_active: false, created_at: '2026-05-29 12:00:00' },
]

/** 用户密码表（mock 改密/旧密码校验用） */
export const passwords: Record<number, string> = {
  1: '123456',
  2: '123456',
  5: '123456',
  9: '123456',
}

/** 费用项（金额字符串两位小数） */
export const expenseItems: ExpenseItem[] = [
  { id: 1, org_id: 1, name: '办公用品', default_qty: '1.00', unit_price: '50.00', unit: '个', is_active: true, sort_order: 0 },
  { id: 2, org_id: 1, name: '差旅费', default_qty: '1.00', unit_price: '500.00', unit: '次', is_active: true, sort_order: 1 },
  { id: 3, org_id: 1, name: '水电费', default_qty: '1.00', unit_price: '300.00', unit: '月', is_active: true, sort_order: 2 },
  { id: 4, org_id: 3, name: '门店租金', default_qty: '1.00', unit_price: '8000.00', unit: '月', is_active: true, sort_order: 0 },
  { id: 5, org_id: 3, name: '促销物料', default_qty: '10.00', unit_price: '15.50', unit: '件', is_active: false, sort_order: 1 },
]

/** 自增 id 发号器 */
let seq = 100
export function nextId(): number {
  return ++seq
}

/** 当前时间字符串（YYYY-MM-DD HH:MM:SS） */
export function now(): string {
  const d = new Date()
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

/** 取机构 path（用于物化路径前缀判定） */
export function orgPath(orgId: number): string {
  return orgs.find((o) => o.id === orgId)?.path ?? '/'
}
