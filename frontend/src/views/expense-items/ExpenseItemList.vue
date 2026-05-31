<script setup lang="ts">
/**
 * 费用项字典页（T-014，对接 CONTRACTS §7）
 * - 列表（按 sort_order）；机构筛选（admin 可切可见机构）+ 启停筛选
 * - 新增 / 编辑（弹窗）、启用停用、删除（硬删除，§7.4，均 admin）
 * - 金额按字符串两位小数展示与提交
 */
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import OrgSelect from '@/components/OrgSelect.vue'
import { useAuthStore } from '@/stores/auth'
import { usePermission } from '@/composables/usePermission'
import {
  getExpenseItems,
  createExpenseItem,
  updateExpenseItem,
  deleteExpenseItem,
} from '@/api/expense-items'
import type { ExpenseItem, ExpenseItemUpdatePayload } from '@/types/expense-item'

const auth = useAuthStore()
const { isAdmin } = usePermission()

const loading = ref(false)
const rows = ref<ExpenseItem[]>([])

// 筛选条件
const filterOrgId = ref<number | null>(auth.user?.org_id ?? null)
const filterActive = ref<'' | 'true' | 'false'>('')

async function load() {
  if (filterOrgId.value == null) {
    rows.value = []
    return
  }
  loading.value = true
  try {
    rows.value = await getExpenseItems({
      org_id: filterOrgId.value,
      is_active: filterActive.value === '' ? undefined : filterActive.value === 'true',
    })
  } catch {
    /* 错误已统一提示 */
  } finally {
    loading.value = false
  }
}

onMounted(load)

// ---- 新增 / 编辑弹窗 ----
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const dialogTitle = computed(() => (editingId.value == null ? '新增费用项' : '编辑费用项'))
const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  name: '',
  default_qty: '1.00',
  unit_price: '0.00',
  unit: '',
  sort_order: 0,
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入费用名称', trigger: 'blur' }],
  default_qty: [
    { required: true, message: '请输入默认数量', trigger: 'blur' },
    {
      validator: (_r, v, cb) =>
        Number(v) >= 0 && v !== '' ? cb() : cb(new Error('数量须为非负数')),
      trigger: 'blur',
    },
  ],
  unit_price: [
    { required: true, message: '请输入默认单价', trigger: 'blur' },
    {
      validator: (_r, v, cb) =>
        Number(v) >= 0 && v !== '' ? cb() : cb(new Error('单价须为非负数')),
      trigger: 'blur',
    },
  ],
}

function openCreate() {
  editingId.value = null
  Object.assign(form, { name: '', default_qty: '1.00', unit_price: '0.00', unit: '', sort_order: rows.value.length })
  dialogVisible.value = true
}

function openEdit(row: ExpenseItem) {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    default_qty: row.default_qty,
    unit_price: row.unit_price,
    unit: row.unit ?? '',
    sort_order: row.sort_order,
  })
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = {
      name: form.name.trim(),
      default_qty: Number(form.default_qty).toFixed(2),
      unit_price: Number(form.unit_price).toFixed(2),
      unit: form.unit.trim() || null,
      sort_order: form.sort_order,
    }
    if (editingId.value == null) {
      await createExpenseItem({ org_id: filterOrgId.value!, ...payload })
      ElMessage.success('已新增')
    } else {
      await updateExpenseItem(editingId.value, payload as ExpenseItemUpdatePayload)
      ElMessage.success('已保存')
    }
    dialogVisible.value = false
    load()
  } catch {
    /* 错误已统一提示 */
  } finally {
    submitting.value = false
  }
}

// ---- 启停 ----
async function toggleActive(row: ExpenseItem) {
  const next = !row.is_active
  try {
    await updateExpenseItem(row.id, { is_active: next })
    row.is_active = next
    ElMessage.success(next ? '已启用' : '已停用')
  } catch {
    /* 错误已统一提示 */
  }
}

// ---- 删除（硬删除，§7.4）----
async function onDelete(row: ExpenseItem) {
  try {
    await ElMessageBox.confirm(
      `确认永久删除费用项「${row.name}」？此操作不可恢复，删除后将不在填报中出现。若只想临时隐藏，请改用「停用」。`,
      '删除费用项',
      {
        type: 'warning',
        confirmButtonText: '永久删除',
        cancelButtonText: '取消',
      },
    )
  } catch {
    return
  }
  try {
    await deleteExpenseItem(row.id)
    ElMessage.success('已删除')
    load()
  } catch {
    /* 错误已统一提示 */
  }
}
</script>

<template>
  <div class="expense-page">
    <el-card shadow="never">
      <template #header>
        <div class="toolbar">
          <div class="filters">
            <OrgSelect
              v-if="isAdmin"
              v-model="filterOrgId"
              :clearable="false"
              class="org-select"
              placeholder="选择机构"
              @change="load"
            />
            <span v-else class="org-fixed">{{ auth.user?.org_name }}</span>

            <el-select v-model="filterActive" class="status-select" @change="load">
              <el-option label="全部状态" value="" />
              <el-option label="启用" value="true" />
              <el-option label="停用" value="false" />
            </el-select>

            <el-button :icon="Refresh" @click="load">刷新</el-button>
          </div>

          <el-button v-if="isAdmin" type="primary" :icon="Plus" @click="openCreate">
            新增费用项
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="rows" border stripe>
        <el-table-column type="index" label="#" width="56" align="center" />
        <el-table-column prop="name" label="费用名称" min-width="160" />
        <el-table-column prop="default_qty" label="默认数量" width="110" align="right" />
        <el-table-column prop="unit_price" label="默认单价" width="120" align="right">
          <template #default="{ row }">¥{{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="90" align="center">
          <template #default="{ row }">{{ row.unit || '—' }}</template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="isAdmin" label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link :type="row.is_active ? 'warning' : 'success'" @click="toggleActive(row)">
              {{ row.is_active ? '停用' : '启用' }}
            </el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无费用项" :image-size="80" />
        </template>
      </el-table>
    </el-card>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="460px" @closed="formRef?.resetFields()">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="费用名称" prop="name">
          <el-input v-model="form.name" maxlength="128" placeholder="如：办公用品" />
        </el-form-item>
        <el-form-item label="默认数量" prop="default_qty">
          <el-input v-model="form.default_qty" placeholder="1.00" />
        </el-form-item>
        <el-form-item label="默认单价" prop="unit_price">
          <el-input v-model="form.unit_price" placeholder="0.00">
            <template #prepend>¥</template>
          </el-input>
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="form.unit" maxlength="16" placeholder="如：个 / 次 / 月" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" controls-position="right" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.filters {
  display: flex;
  align-items: center;
  gap: 12px;
}
.org-select {
  width: 220px;
}
.status-select {
  width: 130px;
}
.org-fixed {
  font-weight: 600;
  color: #1f2937;
}
</style>
