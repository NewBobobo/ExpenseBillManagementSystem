<script setup lang="ts">
/**
 * 顶栏
 * - 左侧：当前机构名 + 面包屑（当前页标题）
 * - 右侧：用户名 + 角色标签 + 下拉（注销）
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const currentTitle = computed(() => (route.meta.title as string) || '')
const roleLabel = computed(() => {
  if (auth.isSuperAdmin) return '超级管理员'
  return auth.isAdmin ? '管理员' : '用户'
})

async function onLogout() {
  try {
    await ElMessageBox.confirm('确认退出登录？', '提示', {
      type: 'warning',
      confirmButtonText: '退出',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  await auth.logout()
  router.replace('/login')
}
</script>

<template>
  <div class="app-header">
    <div class="header-left">
      <span class="org-name">{{ auth.user?.org_name || '—' }}</span>
      <el-divider direction="vertical" />
      <span class="page-title">{{ currentTitle }}</span>
    </div>

    <div class="header-right">
      <el-dropdown trigger="click" @command="onLogout">
        <span class="user-trigger">
          <span class="user-name">{{ auth.user?.real_name || auth.user?.username }}</span>
          <el-tag size="small" :type="auth.isAdmin ? 'danger' : 'info'" class="role-tag">
            {{ roleLabel }}
          </el-tag>
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.org-name {
  font-weight: 600;
  color: #1f2937;
}

.page-title {
  color: #6b7280;
  font-size: 14px;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  outline: none;
}

.user-name {
  color: #1f2937;
  font-size: 14px;
}

.role-tag {
  transform: scale(0.9);
}
</style>
