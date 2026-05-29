<script setup lang="ts">
/**
 * 机构树展示（T-008，对接 CONTRACTS §4 GET /api/orgs/tree）
 * 本阶段聚焦「展示」：树形渲染 + 选中查看详情。
 * 新建/编辑/删除/Logo 上传留待 W2（07-development-plan 第二阶段）。
 */
import { onMounted, ref } from 'vue'
import { useOrgStore } from '@/stores/org'
import type { OrgNode } from '@/types/org'

const orgStore = useOrgStore()
const selected = ref<OrgNode | null>(null)

const treeProps = { label: 'name', children: 'children' }

onMounted(() => {
  orgStore.fetchTree()
})

function onNodeClick(node: OrgNode) {
  selected.value = node
}

function refresh() {
  orgStore.fetchTree(true)
  selected.value = null
}
</script>

<template>
  <div class="org-page">
    <el-card shadow="never" class="tree-card">
      <template #header>
        <div class="card-head">
          <span>机构树</span>
          <el-button size="small" :loading="orgStore.loading" @click="refresh">
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
            <span class="node-name">{{ data.name }}</span>
            <el-tag size="small" type="info" class="node-code">{{ data.code }}</el-tag>
          </span>
        </template>
      </el-tree>
    </el-card>

    <el-card shadow="never" class="detail-card">
      <template #header>机构详情</template>
      <el-empty v-if="!selected" description="点击左侧机构查看详情" :image-size="80" />
      <el-descriptions v-else :column="1" border>
        <el-descriptions-item label="机构名称">{{ selected.name }}</el-descriptions-item>
        <el-descriptions-item label="机构编号">{{ selected.code }}</el-descriptions-item>
        <el-descriptions-item label="层级">{{ selected.level }}</el-descriptions-item>
        <el-descriptions-item label="上级机构 ID">
          {{ selected.parent_id ?? '（顶级）' }}
        </el-descriptions-item>
        <el-descriptions-item label="Logo">
          <el-image
            v-if="selected.logo_path"
            :src="selected.logo_path"
            fit="contain"
            style="width: 64px; height: 64px"
          >
            <template #error><span class="muted">加载失败</span></template>
          </el-image>
          <span v-else class="muted">未设置</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<style scoped>
.org-page {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.tree-card {
  width: 420px;
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
  gap: 8px;
}
.node-code {
  transform: scale(0.85);
}
.muted {
  color: #9ca3af;
}
</style>
