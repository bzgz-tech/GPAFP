<template>
  <div class="section-container" v-if="items.length > 0">
    <div class="section-header">
      <h2 class="section-title">
        <el-icon class="section-icon"><Monitor /></el-icon>
        综合信号仪表盘
      </h2>
      <el-tag type="info" effect="light" round size="small" v-if="lastUpdatedText" class="update-tag">
        <el-icon><Clock /></el-icon> 更新于: {{ lastUpdatedText }}
      </el-tag>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="8" v-for="item in items" :key="item.name">
        <div class="signal-card" :class="getSignalClass(item.signal)">
          <div class="signal-card-header">
            <span class="signal-name">
              {{ item.name }}
              <el-tooltip :content="getIndicatorDesc(item.name)" placement="top" effect="dark">
                 <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </span>
            <el-tag :type="getSignalType(item.signal)" effect="dark" round size="small" class="signal-badge">
              {{ getSignalLabel(item.signal) }}
            </el-tag>
          </div>
          <div class="signal-card-body">
              <div class="signal-main">
                  <span class="signal-value">{{ item.value.toFixed(2) }}</span>
                  <span class="signal-unit" v-if="item.unit">{{ item.unit }}</span>
              </div>
              <div class="signal-desc">{{ item.desc }}</div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Monitor, Clock, InfoFilled } from '@element-plus/icons-vue'
import { indicatorDefinitions } from '@/utils/analysisConstants'

defineProps<{
  items: any[]
  lastUpdatedText: string
}>()

const getIndicatorDesc = (name: string) => {
  return indicatorDefinitions[name]?.desc || '暂无描述'
}

const getSignalType = (signal: string) => {
  if (signal === 'buy') return 'danger' // Red for buy/up
  if (signal === 'sell') return 'success' // Green for sell/down
  return 'info'
}

const getSignalLabel = (signal: string) => {
  if (signal === 'buy') return '强力买入'
  if (signal === 'sell') return '强力卖出'
  return '中性持有'
}

const getSignalClass = (signal: string) => {
  if (signal === 'buy') return 'signal-buy'
  if (signal === 'sell') return 'signal-sell'
  return 'signal-neutral'
}
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

.update-tag {
  background-color: transparent;
  border: none;
  color: #909399;
  font-size: 13px;
  display: flex;
  align-items: center;
  white-space: nowrap;
}

/* Signal Cards */
.signal-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #f0f2f5;
  padding: 24px;
  height: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.02);
}

.signal-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.signal-buy {
  background: linear-gradient(145deg, #ffffff 0%, #fff5f5 100%);
}
.signal-buy .signal-value {
  color: #f56c6c;
}
.signal-buy::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: #f56c6c;
}

.signal-sell {
  background: linear-gradient(145deg, #ffffff 0%, #f0f9eb 100%);
}
.signal-sell .signal-value {
  color: #67c23a;
}
.signal-sell::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: #67c23a;
}

.signal-neutral {
  background: linear-gradient(145deg, #ffffff 0%, #f4f4f5 100%);
}
.signal-neutral .signal-value {
  color: #909399;
}
.signal-neutral::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: #909399;
}

.signal-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.signal-name {
  font-size: 16px;
  font-weight: 600;
  color: #606266;
  display: flex;
  align-items: center;
}

.info-icon {
  margin-left: 6px;
  color: #c0c4cc;
  cursor: pointer;
  font-size: 14px;
  transition: color 0.2s;
}
.info-icon:hover {
  color: #909399;
}

.signal-main {
  display: flex;
  align-items: baseline;
  margin-bottom: 12px;
}

.signal-value {
  font-size: 36px;
  font-weight: 700;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  line-height: 1;
  letter-spacing: -0.5px;
}

.signal-unit {
  font-size: 14px;
  color: #909399;
  margin-left: 6px;
  font-weight: 400;
}

.signal-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  min-height: 44px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 1200px) {
  .signal-card {
    margin-bottom: 16px;
  }
}
</style>
