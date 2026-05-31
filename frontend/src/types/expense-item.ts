/**
 * 费用项字典类型（对齐 CONTRACTS §7）
 * 金额字段 default_qty / unit_price 为字符串化两位小数（NUMERIC，避免 JS 浮点失真）。
 */

export interface ExpenseItem {
  id: number
  org_id: number
  name: string
  /** 默认数量，字符串两位小数，如 "1.00" */
  default_qty: string
  /** 默认单价，字符串两位小数，如 "500.00" */
  unit_price: string
  /** 单位，可为 null */
  unit: string | null
  is_active: boolean
  sort_order: number
}

/** 列表查询参数（§7.1） */
export interface ExpenseItemQuery {
  org_id?: number
  is_active?: boolean
}

/** 新增请求（§7.2） */
export interface ExpenseItemCreatePayload {
  org_id: number
  name: string
  default_qty: string
  unit_price: string
  unit?: string | null
  sort_order?: number
}

/** 修改请求（§7.3，均可选） */
export interface ExpenseItemUpdatePayload {
  name?: string
  default_qty?: string
  unit_price?: string
  unit?: string | null
  is_active?: boolean
  sort_order?: number
}
