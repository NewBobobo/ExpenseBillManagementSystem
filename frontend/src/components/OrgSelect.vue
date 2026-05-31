<script setup lang="ts">
/**
 * 机构选择器（树形下拉）
 * 数据源为 org store 的可见机构树。用于费用项筛选、用户归属选择等。
 * v-model 绑定机构 id（number）。
 */
import { onMounted } from 'vue'
import { useOrgStore } from '@/stores/org'

const modelValue = defineModel<number | null>({ default: null })

withDefaults(
  defineProps<{
    placeholder?: string
    clearable?: boolean
    checkStrictly?: boolean
    disabled?: boolean
  }>(),
  {
    placeholder: '请选择机构',
    clearable: true,
    /** 允许选择任意层级节点（而非仅叶子） */
    checkStrictly: true,
    disabled: false,
  },
)

const orgStore = useOrgStore()

onMounted(() => {
  orgStore.fetchTree()
})

const treeProps = { label: 'name', children: 'children', value: 'id' }
</script>

<template>
  <el-tree-select
    v-model="modelValue"
    :data="orgStore.tree"
    :props="treeProps"
    value-key="id"
    node-key="id"
    :placeholder="placeholder"
    :clearable="clearable"
    :check-strictly="checkStrictly"
    :disabled="disabled"
    :loading="orgStore.loading"
    check-on-click-node
    default-expand-all
    style="width: 100%"
  />
</template>
