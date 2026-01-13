<template>
  <el-card shadow="never" class="config-card">
    <el-form :inline="true" class="config-form">
      <div class="form-group">
        <el-form-item label="交易品种">
          <el-select :model-value="symbol" @update:model-value="$emit('update:symbol', $event)" placeholder="选择品种" class="custom-select">
            <el-option label="现货黄金 (XAUUSD)" value="XAUUSD">
              <span style="float: left">现货黄金</span>
              <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px;">XAUUSD</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="分析周期">
          <el-radio-group :model-value="timeframe" @update:model-value="$emit('update:timeframe', $event)" class="custom-radio">
            <el-radio-button label="1d">日线</el-radio-button>
            <el-radio-button label="1h">小时线</el-radio-button>
            <el-radio-button label="1m">分钟线</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </div>
      <div class="form-group">
        <el-form-item label="数据范围">
           <el-select :model-value="timeWindow" @update:model-value="$emit('update:timeWindow', $event)" placeholder="选择区间" class="custom-select-small">
            <el-option label="最近一天" value="1d" />
            <el-option label="最近7天" value="7d" />
            <el-option label="最近一月" value="1m" />
            <el-option label="最近三月" value="3m" />
            <el-option label="最近一年" value="1y" />
          </el-select>
        </el-form-item>
        <el-form-item label="预测展望">
          <el-input-number :model-value="horizon" @update:model-value="$emit('update:horizon', $event)" :min="1" :max="30" :step="1" class="custom-input-number" controls-position="right">
             <template #suffix>天</template>
          </el-input-number>
        </el-form-item>
        <el-form-item class="action-item">
          <el-button type="primary" :loading="loading" @click="$emit('analyze')" :icon="Refresh" round class="analyze-btn">生成分析报告</el-button>
        </el-form-item>
      </div>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { Refresh } from '@element-plus/icons-vue'

defineProps<{
  symbol: string
  timeframe: string
  timeWindow: string
  horizon: number
  loading: boolean
}>()

defineEmits<{
  (e: 'update:symbol', value: string): void
  (e: 'update:timeframe', value: string): void
  (e: 'update:timeWindow', value: string): void
  (e: 'update:horizon', value: number): void
  (e: 'analyze'): void
}>()
</script>

<style scoped>
.config-card {
  margin-bottom: 32px;
  border: none;
  border-radius: 12px;
  background: #fff;
}

.config-form {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

:deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
}

.custom-select {
  width: 180px;
}

.custom-select-small {
  width: 120px;
}

.custom-input-number {
  width: 120px;
}

.analyze-btn {
  padding: 10px 28px;
  font-weight: 500;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
}

.analyze-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}
</style>
