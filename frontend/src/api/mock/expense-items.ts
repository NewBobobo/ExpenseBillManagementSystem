/**
 * 费用项字典 mock（CONTRACTS §7）
 * 增删改在内存 db 中持久化；金额按字符串两位小数处理。
 */
import { ApiCode } from '@/types/api'
import { expenseItems, nextId } from './db'
import { delay, bizError } from './helpers'
import type {
  ExpenseItem,
  ExpenseItemCreatePayload,
  ExpenseItemQuery,
  ExpenseItemUpdatePayload,
} from '@/types/expense-item'

/** 规整金额为两位小数字符串 */
function money(v: string | undefined, fallback = '0.00'): string {
  if (v == null || v === '') return fallback
  const n = Number(v)
  return Number.isFinite(n) ? n.toFixed(2) : fallback
}

export const expenseItemMock = {
  /** §7.1 列表（按 sort_order 升序） */
  list(query: ExpenseItemQuery = {}): Promise<ExpenseItem[]> {
    let rows = expenseItems.slice()
    if (query.org_id != null) rows = rows.filter((r) => r.org_id === query.org_id)
    if (query.is_active != null) rows = rows.filter((r) => r.is_active === query.is_active)
    rows.sort((a, b) => a.sort_order - b.sort_order || a.id - b.id)
    return delay(rows.map((r) => ({ ...r })))
  },

  /** §7.2 新增 */
  create(payload: ExpenseItemCreatePayload): Promise<ExpenseItem> {
    if (!payload.name?.trim()) return bizError(ApiCode.VALIDATION, '费用名称必填')
    const row: ExpenseItem = {
      id: nextId(),
      org_id: payload.org_id,
      name: payload.name.trim(),
      default_qty: money(payload.default_qty, '1.00'),
      unit_price: money(payload.unit_price),
      unit: payload.unit ?? null,
      is_active: true,
      sort_order: payload.sort_order ?? expenseItems.length,
    }
    expenseItems.push(row)
    return delay({ ...row })
  },

  /** §7.3 修改 */
  update(id: number, payload: ExpenseItemUpdatePayload): Promise<ExpenseItem> {
    const row = expenseItems.find((r) => r.id === id)
    if (!row) return bizError(ApiCode.NOT_FOUND, '费用项不存在')
    if (payload.name !== undefined) row.name = payload.name.trim()
    if (payload.default_qty !== undefined) row.default_qty = money(payload.default_qty, '1.00')
    if (payload.unit_price !== undefined) row.unit_price = money(payload.unit_price)
    if (payload.unit !== undefined) row.unit = payload.unit
    if (payload.is_active !== undefined) row.is_active = payload.is_active
    if (payload.sort_order !== undefined) row.sort_order = payload.sort_order
    return delay({ ...row })
  },

  /** §7.4 硬删除 */
  remove(id: number): Promise<null> {
    const idx = expenseItems.findIndex((r) => r.id === id)
    if (idx === -1) return bizError(ApiCode.NOT_FOUND, '费用项不存在')
    expenseItems.splice(idx, 1)
    return delay(null)
  },
}
