<script setup lang="ts">
/**
 * 侧边栏菜单
 * - 按角色过滤菜单（usePermission）
 * - 当前路由高亮（default-active）
 * - 未实现页面以 disabled 占位
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as Icons from '@element-plus/icons-vue'
import { MENU, type MenuItem } from './menu'
import { usePermission } from '@/composables/usePermission'

const route = useRoute()
const router = useRouter()
const { canAccess } = usePermission()

/** 按角色过滤（含子项过滤；子项被过滤空的分组也隐藏） */
const visibleMenu = computed<MenuItem[]>(() => {
  const filter = (items: MenuItem[]): MenuItem[] =>
    items
      .filter((it) => canAccess(it.roles))
      .map((it) => (it.children ? { ...it, children: filter(it.children) } : it))
      .filter((it) => !it.children || it.children.length > 0)
  return filter(MENU)
})

const activeIndex = computed(() => route.path)

function resolveIcon(name?: string) {
  if (!name) return null
  return (Icons as Record<string, unknown>)[name] ?? null
}

function onSelect(index: string) {
  if (index.startsWith('/')) router.push(index)
}
</script>

<template>
  <el-menu
    :default-active="activeIndex"
    class="sidebar-menu"
    background-color="#1f2d3d"
    text-color="#bfcbd9"
    active-text-color="#409eff"
    router
    @select="onSelect"
  >
    <template v-for="item in visibleMenu" :key="item.index">
      <!-- 含子菜单 -->
      <el-sub-menu v-if="item.children" :index="item.index">
        <template #title>
          <el-icon v-if="resolveIcon(item.icon)">
            <component :is="resolveIcon(item.icon)" />
          </el-icon>
          <span>{{ item.title }}</span>
        </template>
        <el-menu-item
          v-for="child in item.children"
          :key="child.index"
          :index="child.index"
          :disabled="child.disabled"
        >
          {{ child.title }}
          <el-tag v-if="child.disabled" size="small" type="info" class="soon-tag">
            待开发
          </el-tag>
        </el-menu-item>
      </el-sub-menu>

      <!-- 单项 -->
      <el-menu-item v-else :index="item.index" :disabled="item.disabled">
        <el-icon v-if="resolveIcon(item.icon)">
          <component :is="resolveIcon(item.icon)" />
        </el-icon>
        <span>{{ item.title }}</span>
      </el-menu-item>
    </template>
  </el-menu>
</template>

<style scoped>
.sidebar-menu {
  height: 100%;
  border-right: none;
}

.soon-tag {
  margin-left: 6px;
  transform: scale(0.85);
}
</style>
