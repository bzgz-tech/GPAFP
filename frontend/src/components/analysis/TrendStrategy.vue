<template>
  <div class="section-container" v-if="predictionTrend">
    <div class="section-header">
      <h2 class="section-title">
        <el-icon class="section-icon"><TrendCharts /></el-icon>
        AI 趋势信号
      </h2>
    </div>
    <el-card shadow="hover" class="strategy-card" :class="predictionTrend.type + '-border'">
      <div class="strategy-content">
        <div class="strategy-left">
          <div class="strategy-icon-box" :class="predictionTrend.type">
            <el-icon v-if="predictionTrend.type === 'danger'" :size="32"><Top /></el-icon>
            <el-icon v-else-if="predictionTrend.type === 'success'" :size="32"><Bottom /></el-icon>
            <el-icon v-else :size="32"><Minus /></el-icon>
          </div>
          <div class="strategy-meta">
            <div class="strategy-label">AI 趋势研判</div>
            <div class="strategy-verdict" :class="predictionTrend.type">{{ predictionTrend.label }}</div>
          </div>
        </div>
        <div class="strategy-divider"></div>
        <div class="strategy-right">
          <div class="strategy-desc">{{ predictionTrend.desc }}</div>
          <div class="strategy-tags">
            <el-tag type="info" effect="light" size="small">
              置信度: 高
            </el-tag>
            <el-tag effect="light" size="small" style="margin-left: 8px;">
              展望: {{ horizon }}日
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Top, Bottom, Minus, TrendCharts } from '@element-plus/icons-vue'

defineProps<{
  predictionTrend: {
    type: string
    label: string
    desc: string
  } | null
  horizon: number
}>()
</script>

<style scoped>
.section-container {
  margin-bottom: 48px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 4px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  color: #409eff;
}

.strategy-card {
  border: none;
  border-radius: 16px;
  background: #fff;
  transition: all 0.3s;
  overflow: hidden;
}

.strategy-card.danger-border {
  /* border-left: 6px solid #f56c6c; removed for consistency */
}
.strategy-card.success-border {
  /* border-left: 6px solid #67c23a; removed for consistency */
}
.strategy-card.info-border {
  /* border-left: 6px solid #909399; removed for consistency */
}

.strategy-content {
  display: flex;
  align-items: stretch;
  padding: 8px;
}

.strategy-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-right: 32px;
  min-width: 140px;
}

.strategy-icon-box {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 12px;
  background: #f5f7fa;
}

.strategy-icon-box.danger {
  background: #fef0f0;
  color: #f56c6c;
}
.strategy-icon-box.success {
  background: #f0f9eb;
  color: #67c23a;
}
.strategy-icon-box.info {
  background: #f4f4f5;
  color: #909399;
}

.strategy-meta {
  text-align: center;
}

.strategy-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.strategy-verdict {
  font-size: 20px;
  font-weight: 700;
}
.strategy-verdict.danger {
  color: #f56c6c;
}
.strategy-verdict.success {
  color: #67c23a;
}
.strategy-verdict.info {
  color: #606266;
}

.strategy-divider {
  width: 1px;
  background: #ebeef5;
  margin: 0 16px;
}

.strategy-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-left: 16px;
}

.strategy-desc {
  font-size: 16px;
  color: #303133;
  line-height: 1.6;
  margin-bottom: 12px;
}

.strategy-tags {
  display: flex;
  align-items: center;
}
</style>
