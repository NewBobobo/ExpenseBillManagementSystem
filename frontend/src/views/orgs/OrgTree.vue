<script setup lang="ts">
/**
 * 机构管理（T-012，对接 CONTRACTS §5，仅 admin）
 * 在 W1 机构树展示基础上增加操作：
 * - 新增子机构（§5.1）、改名/改编号（§5.2）、删除（§5.3，受阻 40901 由统一提示给出原因）
 * - Logo 上传/更换（§5.4，multipart，png/jpg ≤2MB）
 * 新建/删除/改名后刷新树并保持选中。
 */
import { computed, onMounted, ref, reactive } from 'vue'
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
  type UploadRawFile,
} from 'element-plus'
import { Plus, Edit, Delete, Refresh, UploadFilled } from '@element-plus/icons-vue'
import { useOrgStore } from '@/stores/org'
import { createOrg, updateOrg, deleteOrg, uploadOrgLogo } from '@/api/orgs'
import type { OrgNode } from '@/types/org'

const orgStore = useOrgStore()
const selectedId = ref<number | null>(null)
const treeProps = { label: 'name', children: 'children' }

/** 当前选中节点（每次从最新树按 id 取，避免刷新后引用失效） */
const selected = computed<OrgNode | null>(() =>
  selectedId.value == null ? null : orgStore.findById(selectedId.value),
)

onMounted(() => orgStore.fetchTree())

function onNodeClick(node: OrgNode) {
  selectedId.value = node.id
}

async function refresh() {
  await orgStore.fetchTree(true)
}

// ---- 新增 / 编辑弹窗 ----
type DialogMode = 'create' | 'edit'
const dialogVisible = ref(false)
const dialogMode = ref<DialogMode>('create')
const parentNode = ref<OrgNode | null>(null)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const submitting = ref(false)
const form = reactive({ code: '', name: '' })

const dialogTitle = computed(() =>
  dialogMode.value === 'create' ? `新增子机构（上级：${parentNode.value?.name ?? ''}）` : '编辑机构',
)

const rules: FormRules = {
  code: [{ required: true, message: '请输入机构编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入机构名称', trigger: 'blur' }],
}

function openCreate(parent: OrgNode) {
  dialogMode.value = 'create'
  parentNode.value = parent
  editingId.value = null
  form.code = ''
  form.name = ''
  dialogVisible.value = true
}

function openEdit(node: OrgNode) {
  dialogMode.value = 'edit'
  editingId.value = node.id
  form.code = node.code
  form.name = node.name
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      const created = await createOrg({
        parent_id: parentNode.value!.id,
        code: form.code.trim(),
        name: form.name.trim(),
      })
      ElMessage.success('已新增机构')
      dialogVisible.value = false
      await refresh()
      selectedId.value = created.id
    } else {
      await updateOrg(editingId.value!, { code: form.code.trim(), name: form.name.trim() })
      ElMessage.success('已保存')
      dialogVisible.value = false
      await refresh()
    }
  } catch {
    /* 错误已统一提示（40900 编号重复 / 40300 越权等） */
  } finally {
    submitting.value = false
  }
}

// ---- 删除 ----
async function onDelete(node: OrgNode) {
  try {
    await ElMessageBox.confirm(
      `确认删除机构「${node.name}」？需无子机构、无用户方可删除。`,
      '提示',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    await deleteOrg(node.id)
    ElMessage.success('已删除')
    if (selectedId.value === node.id) selectedId.value = null
    await refresh()
  } catch {
    /* 受阻 40901 / 越权 40300 的原因由统一拦截器 ElMessage 给出 */
  }
}

// ---- Logo 上传 ----
const uploading = ref(false)

/** 上传前校验：类型 + 大小 */
function beforeLogoUpload(file: UploadRawFile): boolean {
  const okType = ['image/png', 'image/jpeg'].includes(file.type)
  if (!okType) {
    ElMessage.error('仅支持 PNG / JPG 格式')
    return false
  }
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('Logo 不能超过 2MB')
    return false
  }
  return true
}

/** 自定义上传：调用 §5.4 接口 */
async function customUpload(options: { file: File }) {
  if (!selected.value) return
  uploading.value = true
  try {
    await uploadOrgLogo(selected.value.id, options.file)
    ElMessage.success('Logo 已更新')
    await refresh()
  } catch {
    /* 错误已统一提示 */
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="org-page">
    <el-card shadow="never" class="tree-card">
      <template #header>
        <div class="card-head">
          <span>机构树</span>
          <el-button size="small" :icon="Refresh" :loading="orgStore.loading" @click="refresh">
            刷新
          </el-button>
        </div>
      </template>

      <el-tree
        v-loading="orgStore.loading"
        :data="orgStore.tree"
        :props="treeProps"
        node-key="id"
        default-expand-all
        highlight-current
        :expand-on-click-node="false"
        @node-click="onNodeClick"
      >
        <template #default="{ data }">
          <span class="tree-node">
            <span class="node-label">
              <span class="node-name">{{ data.name }}</span>
              <el-tag size="small" type="info" class="node-code">{{ data.code }}</el-tag>
            </span>
            <span class="node-actions" @click.stop>
              <el-tooltip content="新增子机构" placement="top">
                <el-button link type="primary" :icon="Plus" @click="openCreate(data)" />
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <el-button link type="primary" :icon="Edit" @click="openEdit(data)" />
              </el-tooltip>
              <el-tooltip v-if="data.parent_id !== null" content="删除" placement="top">
                <el-button link type="danger" :icon="Delete" @click="onDelete(data)" />
              </el-tooltip>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <el-card shadow="never" class="detail-card">
      <template #header>机构详情</template>
      <el-empty v-if="!selected" description="点击左侧机构查看详情 / 操作" :image-size="80" />
      <template v-else>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="机构名称">{{ selected.name }}</el-descriptions-item>
          <el-descriptions-item label="机构编号">{{ selected.code }}</el-descriptions-item>
          <el-descriptions-item label="层级">{{ selected.level }}</el-descriptions-item>
          <el-descriptions-item label="上级机构 ID">
            {{ selected.parent_id ?? '（顶级）' }}
          </el-descriptions-item>
          <el-descriptions-item label="Logo">
            <div class="logo-box">
              <el-image
                v-if="selected.logo_path"
                :src="selected.logo_path"
                fit="contain"
                class="logo-img"
              >
                <template #error><span class="muted">加载失败</span></template>
              </el-image>
              <span v-else class="muted">未设置</span>
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-ops">
          <el-button :icon="Plus" @click="openCreate(selected)">新增子机构</el-button>
          <el-button :icon="Edit" @click="openEdit(selected)">编辑</el-button>
          <el-upload
            class="logo-upload"
            :show-file-list="false"
            :before-upload="beforeLogoUpload"
            :http-request="customUpload"
            accept="image/png,image/jpeg"
          >
            <el-button :icon="UploadFilled" :loading="uploading">
              {{ selected.logo_path ? '更换 Logo' : '上传 Logo' }}
            </el-button>
          </el-upload>
        </div>
      </template>
    </el-card>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="440px" @closed="formRef?.resetFields()">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="机构编号" prop="code">
          <el-input v-model="form.code" maxlength="32" placeholder="如：SH001（用于单号前缀）" />
        </el-form-item>
        <el-form-item label="机构名称" prop="name">
          <el-input v-model="form.name" maxlength="128" placeholder="如：上海一店" />
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
.org-page {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.tree-card {
  width: 460px;
  flex-shrink: 0;
}
.detail-card {
  flex: 1;
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}
.node-label {
  display: flex;
  align-items: center;
  gap: 8px;
}
.node-code {
  transform: scale(0.85);
}
/* 操作按钮默认隐藏，hover 节点时显示 */
.node-actions {
  opacity: 0;
  transition: opacity 0.15s;
}
.tree-node:hover .node-actions {
  opacity: 1;
}
.detail-ops {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 20px;
}
.logo-box {
  display: flex;
  align-items: center;
}
.logo-img {
  width: 72px;
  height: 72px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
.muted {
  color: #9ca3af;
}
</style>
