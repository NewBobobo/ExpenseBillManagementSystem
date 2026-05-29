<script setup lang="ts">
/**
 * 工作台（首页占位）
 * W1 仅放欢迎信息与机构概览；统计卡片 / 最近单据待单据模块完成后补充。
 */
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '凌晨好'
  if (h < 12) return '上午好'
  if (h < 18) return '下午好'
  return '晚上好'
})
</script>

<template>
  <div class="dashboard">
    <el-card shadow="never">
      <h2 class="welcome">
        {{ greeting }}，{{ auth.user?.real_name || auth.user?.username }}
      </h2>
      <p class="sub">当前机构：{{ auth.user?.org_name }}</p>
    </el-card>

    <el-row :gutter="16" class="cards">
      <el-col :span="8">
        <el-card shadow="never"><div class="stat"><span class="num">—</span><span class="label">本月单据数</span></div></el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never"><div class="stat"><span class="num">—</span><span class="label">本月总金额</span></div></el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never"><div class="stat"><span class="num">—</span><span class="label">待处理</span></div></el-card>
      </el-col>
    </el-row>
    <el-alert
      class="tip"
      type="info"
      :closable="false"
      title="统计数据将在单据模块（W4）接入后展示。"
    />
  </div>
</template>

<style scoped>
.welcome {
  font-size: 20px;
  color: #1f2937;
}
.sub {
  margin-top: 6px;
  color: #6b7280;
}
.cards {
  margin-top: 16px;
}
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 10px 0;
}
.num {
  font-size: 28px;
  font-weight: 600;
  color: #2563eb;
}
.label {
  color: #6b7280;
  font-size: 13px;
}
.tip {
  margin-top: 16px;
}
</style>
