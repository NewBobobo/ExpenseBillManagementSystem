<script setup lang="ts">
/**
 * 主布局：左侧固定侧边栏 + 顶栏 + 内容区（router-view）
 */
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
</script>

<template>
  <el-container class="app-layout">
    <el-aside width="220px" class="app-aside">
      <div class="logo-bar">费用单管理系统</div>
      <Sidebar />
    </el-aside>

    <el-container>
      <el-header height="56px" class="app-header-wrap">
        <Header />
      </el-header>
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-layout {
  height: 100%;
}

.app-aside {
  background: #1f2d3d;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo-bar {
  height: 56px;
  line-height: 56px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  background: #18222d;
  letter-spacing: 1px;
}

.app-header-wrap {
  padding: 0;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.app-main {
  background: #f5f7fa;
  padding: 16px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
