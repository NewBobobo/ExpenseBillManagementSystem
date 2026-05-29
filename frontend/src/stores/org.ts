/**
 * 机构上下文状态管理
 * - 当前用户可见的机构树（CONTRACTS §4）
 * - 提供扁平化查找、按 id 取节点等便捷方法
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getOrgTree } from '@/api/orgs'
import type { OrgNode } from '@/types/org'

export const useOrgStore = defineStore('org', () => {
  const tree = ref<OrgNode[]>([])
  const loading = ref(false)
  const loaded = ref(false)

  /** 扁平化后的全部节点 */
  const flatList = computed(() => {
    const out: OrgNode[] = []
    const walk = (nodes: OrgNode[]) => {
      for (const n of nodes) {
        out.push(n)
        if (n.children?.length) walk(n.children)
      }
    }
    walk(tree.value)
    return out
  })

  /** 根机构（一般为当前用户所在层级的顶节点） */
  const rootOrg = computed<OrgNode | null>(() => tree.value[0] ?? null)

  /** 拉取机构树 */
  async function fetchTree(force = false) {
    if (loaded.value && !force) return tree.value
    loading.value = true
    try {
      tree.value = await getOrgTree()
      loaded.value = true
      return tree.value
    } finally {
      loading.value = false
    }
  }

  /** 按 id 查节点 */
  function findById(id: number): OrgNode | null {
    return flatList.value.find((n) => n.id === id) ?? null
  }

  function reset() {
    tree.value = []
    loaded.value = false
  }

  return { tree, loading, loaded, flatList, rootOrg, fetchTree, findById, reset }
})
