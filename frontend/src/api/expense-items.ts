/**
 * 费用项字典接口封装（对接 CONTRACTS §7）
 */
import { request } from './request'
import { expenseItemMock } from './mock'
import { useMock } from './config'
import type {
  ExpenseItem,
  ExpenseItemQuery,
  ExpenseItemCreatePayload,
  ExpenseItemUpdatePayload,
} from '@/types/expense-item'

/** §7.1 列表（按 sort_order 升序） */
export function getExpenseItems(query: ExpenseItemQuery = {}): Promise<ExpenseItem[]> {
  if (useMock('expenseItems')) return expenseItemMock.list(query)
  return request<ExpenseItem[]>({ url: '/expense-items', method: 'get', params: query })
}

/** §7.2 新增 */
export function createExpenseItem(payload: ExpenseItemCreatePayload): Promise<ExpenseItem> {
  if (useMock('expenseItems')) return expenseItemMock.create(payload)
  return request<ExpenseItem>({ url: '/expense-items', method: 'post', data: payload })
}

/** §7.3 修改 */
export function updateExpenseItem(
  id: number,
  payload: ExpenseItemUpdatePayload,
): Promise<ExpenseItem> {
  if (useMock('expenseItems')) return expenseItemMock.update(id, payload)
  return request<ExpenseItem>({ url: `/expense-items/${id}`, method: 'put', data: payload })
}

/** §7.4 软删除 */
export function deleteExpenseItem(id: number): Promise<null> {
  if (useMock('expenseItems')) return expenseItemMock.remove(id)
  return request<null>({ url: `/expense-items/${id}`, method: 'delete' })
}
