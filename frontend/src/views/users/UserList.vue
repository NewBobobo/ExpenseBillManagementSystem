<script setup lang="ts">
/**
 * 用户管理页（T-013，对接 CONTRACTS §6，仅 admin）
 * - 分页表格：username / real_name / role / 机构 / 状态
 * - 机构筛选 + 关键字搜索
 * - 新增 / 编辑用户、重置密码弹窗、停用（软删除）
 * - 绝不显示密码
 */
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import OrgSelect from '@/components/OrgSelect.vue'
import { useAuthStore } from '@/stores/auth'
import {
  getUsers,
  createUser,
  updateUser,
  changeUserPassword,
  resetUserPassword,
  deleteUser,
} from '@/api/users'
import type { UserRole, UserRow } from '@/types/user'

const auth = useAuthStore()

const loading = ref(false)
const rows = ref<UserRow[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

// 筛选
const filterOrgId = ref<number | null>(null)
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    const res = await getUsers({
      org_id: filterOrgId.value ?? undefined,
      keyword: keyword.value.trim() || undefined,
      page: page.value,
      page_size: pageSize.value,
    })
    rows.value = res.items
    total.value = res.total
  } catch {
    /* 错误已统一提示 */
  } finally {
    loading.value = false
  }
}

onMounted(load)

function onSearch() {
  page.value = 1
  load()
}
function onReset() {
  filterOrgId.value = null
  keyword.value = ''
  page.value = 1
  load()
}

const roleLabel = (r: UserRole) => (r === 'admin' ? '管理员' : '用户')

// ---- 新增 / 编辑弹窗 ----
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const dialogTitle = computed(() => (editingId.value == null ? '新增用户' : '编辑用户'))
const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  username: '',
  password: '',
  real_name: '',
  org_id: null as number | null,
  role: 'user' as UserRole,
  is_active: true,
})

const rules = computed<FormRules>(() => ({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  // 仅新建时校验初始密码
  password:
    editingId.value == null
      ? [{ required: true, message: '请输入初始密码', trigger: 'blur' }]
      : [],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  org_id: [{ required: true, message: '请选择归属机构', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}))

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    username: '',
    password: '',
    real_name: '',
    org_id: auth.user?.org_id ?? null,
    role: 'user',
    is_active: true,
  })
  dialogVisible.value = true
}

function openEdit(row: UserRow) {
  editingId.value = row.id
  Object.assign(form, {
    username: row.username,
    password: '',
    real_name: row.real_name,
    org_id: row.org_id,
    role: row.role,
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (editingId.value == null) {
      await createUser({
        username: form.username.trim(),
        password: form.password,
        real_name: form.real_name.trim(),
        org_id: form.org_id!,
        role: form.role,
      })
      ElMessage.success('已新增用户')
    } else {
      // §6.3 仅可改 real_name / role / is_active（username、org_id 不可改）
      await updateUser(editingId.value, {
        real_name: form.real_name.trim(),
        role: form.role,
        is_active: form.is_active,
      })
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

// ---- 修改密码弹窗（管理员手动输入新密码）----
const pwdVisible = ref(false)
const pwdTarget = ref<UserRow | null>(null)
const pwdFormRef = ref<FormInstance>()
const pwdSubmitting = ref(false)
const pwdForm = reactive({ new_password: '', confirm: '' })

const pwdRules = computed<FormRules>(() => ({
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_r, v, cb) =>
        v === pwdForm.new_password ? cb() : cb(new Error('两次输入不一致')),
      trigger: 'blur',
    },
  ],
}))

function openChangePwd(row: UserRow) {
  pwdTarget.value = row
  pwdForm.new_password = ''
  pwdForm.confirm = ''
  pwdVisible.value = true
}

async function onChangePwd() {
  if (!pwdFormRef.value || !pwdTarget.value) return
  const valid = await pwdFormRef.value.validate().catch(() => false)
  if (!valid) return
  pwdSubmitting.value = true
  try {
    // admin 改他人密码：只传 new_password
    await changeUserPassword(pwdTarget.value.id, { new_password: pwdForm.new_password })
    ElMessage.success('密码已修改')
    pwdVisible.value = false
  } catch {
    /* 错误已统一提示 */
  } finally {
    pwdSubmitting.value = false
  }
}

// ---- 一键重置密码（重置为默认值 123qwe）----
async function onResetPwd(row: UserRow) {
  try {
    await ElMessageBox.confirm(
      `确认将用户「${row.real_name}」的密码重置为默认密码 123qwe？`,
      '重置密码',
      { type: 'warning', confirmButtonText: '重置', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    await resetUserPassword(row.id)
    ElMessage.success('密码已重置为 123qwe')
  } catch {
    /* 错误已统一提示 */
  }
}

// ---- 停用（软删除） ----
async function onDisable(row: UserRow) {
  try {
    await ElMessageBox.confirm(`确认停用用户「${row.real_name}」？停用后将无法登录。`, '提示', {
      type: 'warning',
      confirmButtonText: '停用',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteUser(row.id)
    ElMessage.success('已停用')
    load()
  } catch {
    /* 错误已统一提示 */
  }
}
</script>

<template>
  <div class="user-page">
    <el-card shadow="never">
      <template #header>
        <div class="toolbar">
          <div class="filters">
            <OrgSelect v-model="filterOrgId" class="org-select" placeholder="全部机构" />
            <el-input
              v-model="keyword"
              class="kw-input"
              placeholder="用户名 / 姓名"
              clearable
              @keyup.enter="onSearch"
            />
            <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
            <el-button :icon="Refresh" @click="onReset">重置</el-button>
          </div>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增用户</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="rows" border stripe>
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="real_name" label="姓名" min-width="120" />
        <el-table-column label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="org_name" label="所属机构" min-width="140" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="300" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="openChangePwd(row)">修改密码</el-button>
            <el-button link type="warning" @click="onResetPwd(row)">重置密码</el-button>
            <el-button
              v-if="row.is_active && row.id !== auth.user?.id"
              link
              type="danger"
              @click="onDisable(row)"
            >
              停用
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无用户" :image-size="80" />
        </template>
      </el-table>

      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="load"
          @size-change="onSearch"
        />
      </div>
    </el-card>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="editingId != null" maxlength="64" placeholder="登录账号" />
        </el-form-item>
        <el-form-item v-if="editingId == null" label="初始密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="初始登录密码" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" maxlength="64" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="归属机构" prop="org_id">
          <OrgSelect v-model="form.org_id" :disabled="editingId != null" :clearable="false" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="form.role">
            <el-radio value="user">用户</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="editingId != null" label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwdVisible" title="修改密码" width="420px">
      <p class="pwd-tip">为用户「{{ pwdTarget?.real_name }}」设置新密码：</p>
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="90px">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="pwdForm.confirm" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdSubmitting" @click="onChangePwd">确定</el-button>
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
  width: 200px;
}
.kw-input {
  width: 200px;
}
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.pwd-tip {
  margin-bottom: 16px;
  color: #6b7280;
}
</style>
